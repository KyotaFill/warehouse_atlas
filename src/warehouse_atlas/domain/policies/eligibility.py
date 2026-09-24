from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from uuid import UUID

from warehouse_atlas.common.constants import Condition


@dataclass(frozen=True, slots=True)
class EligibilityContext:
    business_date: date
    min_shelf_life_days: int = 0
    required_condition: Condition = Condition.GOOD
    disallow_quarantine: bool = True
    disallow_blocked_lots: bool = True
    frozen_location_ids: frozenset[UUID] = frozenset()


@dataclass(frozen=True, slots=True)
class EligibilityResult:
    is_eligible: bool
    reasons: tuple[str, ...]

    @property
    def summary(self) -> str:
        return "Hợp lệ" if self.is_eligible else f"Không đủ điều kiện: {', '.join(self.reasons)}"


class LotEligibility:
    """
    Quy tắc kiểm tra điều kiện xuất lô (Lot Eligibility Rules):
    - Trạng thái lô không bị BLOCK
    - Tình trạng hàng (Condition) phải đúng chuẩn (mặc định GOOD)
    - Hạn sử dụng còn đủ so với min_shelf_life_days
    - Vị trí không bị đóng băng do kiểm kê (frozen locations)
    """

    @staticmethod
    def evaluate(
        condition: Condition,
        is_lot_blocked: bool,
        expires_on: date | None,
        location_id: UUID,
        available_qty: Decimal,
        context: EligibilityContext,
    ) -> EligibilityResult:
        reasons: list[str] = []

        if available_qty <= Decimal("0"):
            reasons.append("Hết số lượng khả dụng")

        if is_lot_blocked and context.disallow_blocked_lots:
            reasons.append("Lô đang bị phong tỏa/khóa")

        if context.disallow_quarantine and condition != context.required_condition:
            reasons.append(
                f"Tình trạng {condition.value} khác yêu cầu {context.required_condition.value}"
            )

        if location_id in context.frozen_location_ids:
            reasons.append("Vị trí đang bị đóng băng do kiểm kê")

        if expires_on is not None:
            days_left = (expires_on - context.business_date).days
            if days_left <= 0:
                reasons.append("Lô đã hết hạn sử dụng")
            elif days_left < context.min_shelf_life_days:
                reasons.append(
                    f"Hạn dùng còn lại ({days_left} ngày) không đạt tối thiểu ({context.min_shelf_life_days} ngày)"
                )

        return EligibilityResult(
            is_eligible=(len(reasons) == 0),
            reasons=tuple(reasons),
        )
