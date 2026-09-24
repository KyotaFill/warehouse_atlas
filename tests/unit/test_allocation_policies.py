import uuid
from datetime import date, datetime, timezone
from decimal import Decimal

from warehouse_atlas.common.constants import Condition
from warehouse_atlas.common.types import BucketKey
from warehouse_atlas.domain.policies.allocation import (
    AllocationCandidate,
    FefoPolicy,
    FifoPolicy,
)


def test_fefo_prioritizes_earlier_expiry():
    p_id = uuid.uuid4()
    loc_id = uuid.uuid4()

    # Lô A: Nhập trước (10 ngày trước), hết hạn muộn (2026-12-31), còn 6
    cand_a = AllocationCandidate(
        bucket_id=uuid.uuid4(),
        bucket_key=BucketKey(p_id, loc_id, uuid.uuid4(), Condition.GOOD),
        available_qty=Decimal("6"),
        expires_on=date(2026, 12, 31),
        received_at=datetime(2026, 9, 1, tzinfo=timezone.utc),
        lot_code="LOT-A",
    )

    # Lô B: Nhập sau (hôm qua), hết hạn sớm hơn (2026-10-31), còn 8
    cand_b = AllocationCandidate(
        bucket_id=uuid.uuid4(),
        bucket_key=BucketKey(p_id, loc_id, uuid.uuid4(), Condition.GOOD),
        available_qty=Decimal("8"),
        expires_on=date(2026, 10, 31),
        received_at=datetime(2026, 9, 10, tzinfo=timezone.utc),
        lot_code="LOT-B",
    )

    # Cần 10:
    # FEFO phải lấy: B (8 cái) + A (2 cái)
    fefo = FefoPolicy()
    plan_fefo = fefo.allocate([cand_a, cand_b], Decimal("10"))

    assert plan_fefo.is_fulfilled is True
    assert plan_fefo.total_allocated == Decimal("10")
    assert len(plan_fefo.allocations) == 2
    assert plan_fefo.allocations[0].lot_code == "LOT-B"
    assert plan_fefo.allocations[0].allocated_qty == Decimal("8")
    assert plan_fefo.allocations[1].lot_code == "LOT-A"
    assert plan_fefo.allocations[1].allocated_qty == Decimal("2")

    # FIFO phải lấy: A (6 cái) + B (4 cái)
    fifo = FifoPolicy()
    plan_fifo = fifo.allocate([cand_a, cand_b], Decimal("10"))

    assert plan_fifo.is_fulfilled is True
    assert plan_fifo.total_allocated == Decimal("10")
    assert len(plan_fifo.allocations) == 2
    assert plan_fifo.allocations[0].lot_code == "LOT-A"
    assert plan_fifo.allocations[0].allocated_qty == Decimal("6")
    assert plan_fifo.allocations[1].lot_code == "LOT-B"
    assert plan_fifo.allocations[1].allocated_qty == Decimal("4")
