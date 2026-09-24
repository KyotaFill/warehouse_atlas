from datetime import UTC, date, datetime
from decimal import Decimal
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from warehouse_atlas.infrastructure.db.base import Base

if TYPE_CHECKING:
    from warehouse_atlas.infrastructure.orm.catalog_models import Partner, Product


class Lot(Base):
    __tablename__ = "lot"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    product_id: Mapped[UUID] = mapped_column(ForeignKey("product.id"), nullable=False)
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    manufacturer_lot_code: Mapped[str | None] = mapped_column(String(100))
    supplier_id: Mapped[UUID | None] = mapped_column(ForeignKey("partner.id"))
    manufactured_on: Mapped[date | None] = mapped_column(Date)
    expires_on: Mapped[date | None] = mapped_column(Date)
    received_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    unit_cost: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
    recall_status: Mapped[str] = mapped_column(String(20), default="ACTIVE", nullable=False)
    block_reason: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )

    product: Mapped["Product"] = relationship("Product")
    supplier: Mapped["Partner | None"] = relationship("Partner")

    __table_args__ = (
        UniqueConstraint("id", "product_id", name="uq_lot_id_product"),
        CheckConstraint("unit_cost >= 0", name="ck_lot_unit_cost"),
        CheckConstraint("recall_status IN ('ACTIVE','BLOCKED')", name="ck_lot_recall_status"),
        CheckConstraint(
            "manufactured_on IS NULL OR expires_on IS NULL OR manufactured_on <= expires_on",
            name="ck_lot_dates",
        ),
    )
