from warehouse_atlas.intelligence.routing.route_planner import (
    Coordinate,
    PickStopItem,
    RoutePlanner,
)


def test_route_planner_optimization():
    # Điểm xuất phát (cửa kho / staging dock): (0, 0)
    dock = Coordinate(0.0, 0.0)

    # Các điểm dừng theo thứ tự đơn hàng bị xáo trộn (zigzag):
    # Điểm 1: (10, 0)
    # Điểm 2: (1, 0) - rất gần dock
    # Điểm 3: (100, 0)
    # Điểm 4: (2, 0) - gần dock
    stops = [
        PickStopItem("1", "loc1", "LOC-1", Coordinate(10.0, 0.0), "SKU1", "L1", 1.0),
        PickStopItem("2", "loc2", "LOC-2", Coordinate(1.0, 0.0), "SKU2", "L2", 1.0),
        PickStopItem("3", "loc3", "LOC-3", Coordinate(100.0, 0.0), "SKU3", "L3", 1.0),
        PickStopItem("4", "loc4", "LOC-4", Coordinate(2.0, 0.0), "SKU4", "L4", 1.0),
    ]

    result = RoutePlanner.plan(dock, stops)

    assert result.is_fallback_to_baseline is False
    assert result.total_distance_meters < result.baseline_distance_meters
    assert result.improvement_percentage > 0.0
    # Thứ tự tối ưu phải đi tuần tự: (1, 0) -> (2, 0) -> (10, 0) -> (100, 0)
    assert [s.stop_id for s in result.stops_in_order] == ["2", "4", "1", "3"]
