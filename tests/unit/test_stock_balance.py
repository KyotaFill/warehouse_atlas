import uuid
from decimal import Decimal

import pytest

from warehouse_atlas.common.constants import Condition
from warehouse_atlas.common.exceptions import InsufficientStockError
from warehouse_atlas.common.types import BucketKey
from warehouse_atlas.domain.model.balance import StockBalance


def test_stock_balance_invariants():
    key = BucketKey(uuid.uuid4(), uuid.uuid4(), uuid.uuid4(), Condition.GOOD)

    # 1. Hợp lệ
    sb = StockBalance(
        id=uuid.uuid4(),
        bucket_key=key,
        on_hand=Decimal("10"),
        reserved=Decimal("3"),
    )
    assert sb.free_qty == Decimal("7")

    # 2. on_hand âm -> Báo lỗi
    with pytest.raises(InsufficientStockError):
        StockBalance(
            id=uuid.uuid4(),
            bucket_key=key,
            on_hand=Decimal("-1"),
            reserved=Decimal("0"),
        )

    # 3. reserved > on_hand -> Báo lỗi
    with pytest.raises(InsufficientStockError):
        StockBalance(
            id=uuid.uuid4(),
            bucket_key=key,
            on_hand=Decimal("5"),
            reserved=Decimal("6"),
        )


def test_stock_balance_reserve_and_consume():
    key = BucketKey(uuid.uuid4(), uuid.uuid4(), uuid.uuid4(), Condition.GOOD)
    sb = StockBalance(
        id=uuid.uuid4(),
        bucket_key=key,
        on_hand=Decimal("10"),
        reserved=Decimal("0"),
    )

    # Giữ 4
    sb.apply_reservation(Decimal("4"))
    assert sb.on_hand == Decimal("10")
    assert sb.reserved == Decimal("4")
    assert sb.free_qty == Decimal("6")

    # Giữ tiếp 7 -> Không đủ, phải lỗi (chỉ còn free 6)
    with pytest.raises(InsufficientStockError):
        sb.apply_reservation(Decimal("7"))

    # Tiêu thụ 4 (xuất kho thực tế)
    sb.consume_reservation(Decimal("4"))
    assert sb.on_hand == Decimal("6")
    assert sb.reserved == Decimal("0")
    assert sb.free_qty == Decimal("6")
