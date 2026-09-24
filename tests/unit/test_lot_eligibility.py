import uuid
from datetime import date
from decimal import Decimal

from warehouse_atlas.common.constants import Condition
from warehouse_atlas.domain.policies.eligibility import (
    EligibilityContext,
    LotEligibility,
)


def test_lot_eligibility_checks():
    today = date(2026, 9, 24)
    loc_normal = uuid.uuid4()
    loc_frozen = uuid.uuid4()

    ctx = EligibilityContext(
        business_date=today,
        min_shelf_life_days=30,
        required_condition=Condition.GOOD,
        frozen_location_ids=frozenset([loc_frozen]),
    )

    # 1. Hợp lệ hoàn toàn (hết hạn sau 60 ngày)
    res_ok = LotEligibility.evaluate(
        condition=Condition.GOOD,
        is_lot_blocked=False,
        expires_on=date(2026, 11, 24),
        location_id=loc_normal,
        available_qty=Decimal("15"),
        context=ctx,
    )
    assert res_ok.is_eligible is True

    # 2. Bị block
    res_blocked = LotEligibility.evaluate(
        condition=Condition.GOOD,
        is_lot_blocked=True,
        expires_on=date(2026, 11, 24),
        location_id=loc_normal,
        available_qty=Decimal("15"),
        context=ctx,
    )
    assert res_blocked.is_eligible is False
    assert any("phong tỏa" in r for r in res_blocked.reasons)

    # 3. Hạn dùng không đủ tối thiểu 30 ngày (còn 10 ngày)
    res_short_shelf = LotEligibility.evaluate(
        condition=Condition.GOOD,
        is_lot_blocked=False,
        expires_on=date(2026, 10, 4),
        location_id=loc_normal,
        available_qty=Decimal("15"),
        context=ctx,
    )
    assert res_short_shelf.is_eligible is False
    assert any("tối thiểu" in r for r in res_short_shelf.reasons)

    # 4. Vị trí bị đóng băng kiểm kê
    res_frozen = LotEligibility.evaluate(
        condition=Condition.GOOD,
        is_lot_blocked=False,
        expires_on=date(2026, 11, 24),
        location_id=loc_frozen,
        available_qty=Decimal("15"),
        context=ctx,
    )
    assert res_frozen.is_eligible is False
    assert any("đóng băng" in r for r in res_frozen.reasons)
