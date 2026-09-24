from dataclasses import dataclass
import math
from typing import Any


@dataclass(frozen=True, slots=True)
class Coordinate:
    x: float
    y: float

    def distance_to(self, other: "Coordinate") -> float:
        return math.hypot(self.x - other.x, self.y - other.y)


@dataclass(frozen=True, slots=True)
class PickStopItem:
    stop_id: str
    location_id: str
    location_code: str
    coord: Coordinate
    sku: str
    lot_code: str
    quantity: float


@dataclass(frozen=True, slots=True)
class RoutePlanResult:
    stops_in_order: tuple[PickStopItem, ...]
    total_distance_meters: float
    baseline_distance_meters: float
    improvement_percentage: float
    algorithm: str
    is_fallback_to_baseline: bool


class RoutePlanner:
    """
    Thuật toán lập lộ trình lấy hàng trong kho (Warehouse Pick Route Planner).
    So sánh Heuristic (Nearest Neighbor + 2-opt) với Baseline (thứ tự dòng đơn gốc).
    Nếu Heuristic xấu hơn, fallback về Baseline.
    """

    @staticmethod
    def calculate_tour_distance(start_coord: Coordinate, stops: list[PickStopItem]) -> float:
        if not stops:
            return 0.0
        dist = start_coord.distance_to(stops[0].coord)
        for i in range(len(stops) - 1):
            dist += stops[i].coord.distance_to(stops[i + 1].coord)
        return dist

    @classmethod
    def plan(
        cls,
        start_coord: Coordinate,
        stops: list[PickStopItem],
    ) -> RoutePlanResult:
        if not stops:
            return RoutePlanResult(
                stops_in_order=(),
                total_distance_meters=0.0,
                baseline_distance_meters=0.0,
                improvement_percentage=0.0,
                algorithm="NONE",
                is_fallback_to_baseline=True,
            )

        # Baseline: Đi theo đúng thứ tự dòng đơn truyền vào
        baseline_stops = list(stops)
        baseline_distance = cls.calculate_tour_distance(start_coord, baseline_stops)

        # Heuristic 1: Nearest Neighbor
        unvisited = list(stops)
        proposed_stops: list[PickStopItem] = []
        current_coord = start_coord

        while unvisited:
            next_stop = min(unvisited, key=lambda s: current_coord.distance_to(s.coord))
            proposed_stops.append(next_stop)
            current_coord = next_stop.coord
            unvisited.remove(next_stop)

        # Heuristic 2: 2-Opt local search improvement nếu có từ 4 điểm trở lên
        if len(proposed_stops) >= 4:
            improved = True
            while improved:
                improved = False
                for i in range(len(proposed_stops) - 1):
                    for j in range(i + 2, len(proposed_stops)):
                        # Thử đảo ngược đoạn từ i đến j
                        new_stops = (
                            proposed_stops[:i]
                            + list(reversed(proposed_stops[i:j + 1]))
                            + proposed_stops[j + 1:]
                        )
                        new_dist = cls.calculate_tour_distance(start_coord, new_stops)
                        curr_dist = cls.calculate_tour_distance(start_coord, proposed_stops)
                        if new_dist < curr_dist - 1e-4:
                            proposed_stops = new_stops
                            improved = True
                            break
                    if improved:
                        break

        proposed_distance = cls.calculate_tour_distance(start_coord, proposed_stops)

        # So sánh với baseline: Nếu heuristic xấu hơn, giữ baseline
        if proposed_distance > baseline_distance or math.isclose(proposed_distance, baseline_distance):
            return RoutePlanResult(
                stops_in_order=tuple(baseline_stops),
                total_distance_meters=baseline_distance,
                baseline_distance_meters=baseline_distance,
                improvement_percentage=0.0,
                algorithm="BASELINE",
                is_fallback_to_baseline=True,
            )

        improvement = ((baseline_distance - proposed_distance) / baseline_distance) * 100.0
        return RoutePlanResult(
            stops_in_order=tuple(proposed_stops),
            total_distance_meters=round(proposed_distance, 2),
            baseline_distance_meters=round(baseline_distance, 2),
            improvement_percentage=round(improvement, 2),
            algorithm="NEAREST_NEIGHBOR_2OPT",
            is_fallback_to_baseline=False,
        )
