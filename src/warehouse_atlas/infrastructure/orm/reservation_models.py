from datetime import UTC, datetime
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    ForeignKeyConstraint,
    Numeric,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column

from warehouse_atlas.infrastructure.db.base import Base


class StockReservation(Base):
    __tablename__ = "stock_reservation"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    sales_order_line_id: Mapped[UUID] = mapped_column(
        ForeignKey("sales_order_line.id"), nullable=False
    )
    product_id: Mapped[UUID] = mapped_column(ForeignKey("product.id"), nullable=False)
    location_id: Mapped[UUID] = mapped_column(ForeignKey("location.id"), nullable=False)
    lot_id: Mapped[UUID] = mapped_column(nullable=False)
    condition: Mapped[str] = mapped_column(String(20), default="GOOD", nullable=False)
    reserved_qty: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
    consumed_qty: Mapped[Decimal] = mapped_column(
        Numeric(18, 4), default=Decimal("0"), nullable=False
    )
    released_qty: Mapped[Decimal] = mapped_column(
        Numeric(18, 4), default=Decimal("0"), nullable=False
    )
    status: Mapped[str] = mapped_column(String(20), default="ACTIVE", nullable=False)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )

    __table_args__ = (
        ForeignKeyConstraint(
            ["lot_id", "product_id"],
            ["lot.id", "lot.product_id"],
            name="fk_stock_reservation_lot",
        ),
        CheckConstraint("reserved_qty > 0", name="ck_res_qty_positive"),
        CheckConstraint("consumed_qty >= 0", name="ck_res_consumed_non_negative"),
        CheckConstraint("released_qty >= 0", name="ck_res_released_non_negative"),
        CheckConstraint("consumed_qty + released_qty <= reserved_qty", name="ck_res_sum_limits"),
        CheckConstraint(
            "status IN ('ACTIVE','CONSUMED','RELEASED','EXPIRED')", name="ck_res_status"
        ),
        CheckConstraint("condition IN ('GOOD','QUARANTINE','DAMAGED')", name="ck_res_condition"),
    )


class ReservationEvent(Base):
    __tablename__ = "reservation_event"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    reservation_id: Mapped[UUID] = mapped_column(ForeignKey("stock_reservation.id"), nullable=False)
    event_type: Mapped[str] = mapped_column(String(20), nullable=False)
    qty: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
    recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )
    document_line_id: Mapped[UUID | None] = mapped_column(ForeignKey("inventory_document_line.id"))
    actor_id: Mapped[UUID] = mapped_column(ForeignKey("app_user.id"), nullable=False)

    __table_args__ = (
        CheckConstraint("qty > 0", name="ck_res_event_qty"),
        CheckConstraint(
            "event_type IN ('ALLOCATE','CONSUME','RELEASE','EXPIRE')",
            name="ck_res_event_type",
        ),
        CheckConstraint(
            "(event_type = 'CONSUME') = (document_line_id IS NOT NULL)",
            name="ck_res_event_consume_doc_line",
        ),
    )
