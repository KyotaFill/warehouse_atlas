from datetime import UTC, datetime
from decimal import Decimal
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Numeric,
    String,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from warehouse_atlas.infrastructure.db.base import Base


class AuditEvent(Base):
    __tablename__ = "audit_event"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    entity_name: Mapped[str] = mapped_column(String(50), nullable=False)
    entity_id: Mapped[UUID] = mapped_column(nullable=False)
    action: Mapped[str] = mapped_column(String(50), nullable=False)
    actor_id: Mapped[UUID] = mapped_column(ForeignKey("app_user.id"), nullable=False)
    recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )
    payload_before: Mapped[dict[str, Any] | None] = mapped_column(JSONB)
    payload_after: Mapped[dict[str, Any] | None] = mapped_column(JSONB)


class ReorderPolicy(Base):
    __tablename__ = "reorder_policy"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    product_id: Mapped[UUID] = mapped_column(ForeignKey("product.id"), nullable=False)
    warehouse_id: Mapped[UUID] = mapped_column(ForeignKey("warehouse.id"), nullable=False)
    min_qty_base: Mapped[Decimal] = mapped_column(
        Numeric(18, 4), default=Decimal("0"), nullable=False
    )
    reorder_point_base: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
    max_qty_base: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)

    __table_args__ = (
        UniqueConstraint("product_id", "warehouse_id", name="uq_reorder_policy_product_warehouse"),
        CheckConstraint("min_qty_base >= 0", name="ck_reorder_min_non_negative"),
        CheckConstraint("reorder_point_base >= min_qty_base", name="ck_reorder_point_min"),
        CheckConstraint("max_qty_base >= reorder_point_base", name="ck_reorder_max_point"),
    )
