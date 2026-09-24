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
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from warehouse_atlas.infrastructure.db.base import Base


class Stocktake(Base):
    __tablename__ = "stocktake"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    warehouse_id: Mapped[UUID] = mapped_column(ForeignKey("warehouse.id"), nullable=False)
    location_id: Mapped[UUID] = mapped_column(ForeignKey("location.id"), nullable=False)
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="DRAFT", nullable=False)
    created_by: Mapped[UUID] = mapped_column(ForeignKey("app_user.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )
    closed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    adjustment_document_id: Mapped[UUID | None] = mapped_column(ForeignKey("inventory_document.id"))

    lines: Mapped[list["StocktakeLine"]] = relationship(
        "StocktakeLine", back_populates="stocktake", cascade="all, delete-orphan"
    )

    __table_args__ = (
        CheckConstraint(
            "status IN ('DRAFT','COUNTING','REVIEW','POSTED','CANCELLED')",
            name="ck_stocktake_status",
        ),
    )


class StocktakeLine(Base):
    __tablename__ = "stocktake_line"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    stocktake_id: Mapped[UUID] = mapped_column(ForeignKey("stocktake.id"), nullable=False)
    product_id: Mapped[UUID] = mapped_column(ForeignKey("product.id"), nullable=False)
    location_id: Mapped[UUID] = mapped_column(ForeignKey("location.id"), nullable=False)
    lot_id: Mapped[UUID] = mapped_column(nullable=False)
    condition: Mapped[str] = mapped_column(String(20), default="GOOD", nullable=False)
    snapshot_qty: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
    counted_qty: Mapped[Decimal | None] = mapped_column(Numeric(18, 4))
    difference_qty: Mapped[Decimal | None] = mapped_column(Numeric(18, 4))

    stocktake: Mapped["Stocktake"] = relationship("Stocktake", back_populates="lines")

    __table_args__ = (
        UniqueConstraint(
            "stocktake_id",
            "product_id",
            "location_id",
            "lot_id",
            "condition",
            name="uq_stocktake_line_bucket",
        ),
        ForeignKeyConstraint(
            ["lot_id", "product_id"],
            ["lot.id", "lot.product_id"],
            name="fk_stocktake_line_lot",
        ),
        CheckConstraint("snapshot_qty >= 0", name="ck_stocktake_snapshot_non_negative"),
        CheckConstraint(
            "counted_qty IS NULL OR counted_qty >= 0",
            name="ck_stocktake_counted_non_negative",
        ),
        CheckConstraint(
            "(counted_qty IS NULL) = (difference_qty IS NULL)",
            name="ck_stocktake_diff_parity",
        ),
        CheckConstraint(
            "counted_qty IS NULL OR difference_qty = counted_qty - snapshot_qty",
            name="ck_stocktake_diff_math",
        ),
        CheckConstraint(
            "condition IN ('GOOD','QUARANTINE','DAMAGED')", name="ck_stocktake_condition"
        ),
    )
