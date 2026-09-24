from datetime import UTC, date, datetime
from decimal import Decimal
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    ForeignKeyConstraint,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from warehouse_atlas.infrastructure.db.base import Base

if TYPE_CHECKING:
    from warehouse_atlas.infrastructure.orm.catalog_models import Partner, Product
    from warehouse_atlas.infrastructure.orm.warehouse_models import Warehouse


class PurchaseOrder(Base):
    __tablename__ = "purchase_order"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    supplier_id: Mapped[UUID] = mapped_column(ForeignKey("partner.id"), nullable=False)
    warehouse_id: Mapped[UUID] = mapped_column(ForeignKey("warehouse.id"), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="DRAFT", nullable=False)
    expected_on: Mapped[date | None] = mapped_column(Date)
    created_by: Mapped[UUID] = mapped_column(ForeignKey("app_user.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    supplier: Mapped["Partner"] = relationship("Partner")
    warehouse: Mapped["Warehouse"] = relationship("Warehouse")
    lines: Mapped[list["PurchaseOrderLine"]] = relationship(
        "PurchaseOrderLine", back_populates="order"
    )

    __table_args__ = (
        CheckConstraint(
            "status IN ('DRAFT','CONFIRMED','CLOSED','CANCELLED')",
            name="ck_purchase_order_status",
        ),
    )


class PurchaseOrderLine(Base):
    __tablename__ = "purchase_order_line"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    order_id: Mapped[UUID] = mapped_column(
        ForeignKey("purchase_order.id", ondelete="CASCADE"), nullable=False
    )
    line_no: Mapped[int] = mapped_column(Integer, nullable=False)
    product_id: Mapped[UUID] = mapped_column(ForeignKey("product.id"), nullable=False)
    product_uom_id: Mapped[UUID] = mapped_column(nullable=False)
    ordered_qty: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
    factor_to_base_snapshot: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
    closed_qty_base: Mapped[Decimal] = mapped_column(
        Numeric(18, 4), default=Decimal("0"), nullable=False
    )
    close_reason: Mapped[str | None] = mapped_column(Text)

    order: Mapped["PurchaseOrder"] = relationship("PurchaseOrder", back_populates="lines")
    product: Mapped["Product"] = relationship("Product")

    __table_args__ = (
        UniqueConstraint("order_id", "line_no", name="uq_po_line_no"),
        UniqueConstraint("id", "product_id", name="uq_po_line_id_product"),
        ForeignKeyConstraint(
            ["product_uom_id", "product_id"],
            ["product_uom.id", "product_uom.product_id"],
            name="fk_po_line_product_uom",
        ),
        CheckConstraint("line_no > 0", name="ck_po_line_no"),
        CheckConstraint("ordered_qty > 0", name="ck_po_ordered_qty"),
        CheckConstraint("factor_to_base_snapshot > 0", name="ck_po_factor"),
        CheckConstraint("unit_price >= 0", name="ck_po_unit_price"),
        CheckConstraint("closed_qty_base >= 0", name="ck_po_closed_qty_non_negative"),
        CheckConstraint(
            "closed_qty_base <= ordered_qty * factor_to_base_snapshot",
            name="ck_po_closed_qty_max",
        ),
    )


class SalesOrder(Base):
    __tablename__ = "sales_order"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    customer_id: Mapped[UUID] = mapped_column(ForeignKey("partner.id"), nullable=False)
    warehouse_id: Mapped[UUID] = mapped_column(ForeignKey("warehouse.id"), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="DRAFT", nullable=False)
    expected_on: Mapped[date | None] = mapped_column(Date)
    created_by: Mapped[UUID] = mapped_column(ForeignKey("app_user.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    customer: Mapped["Partner"] = relationship("Partner")
    warehouse: Mapped["Warehouse"] = relationship("Warehouse")
    lines: Mapped[list["SalesOrderLine"]] = relationship("SalesOrderLine", back_populates="order")

    __table_args__ = (
        CheckConstraint(
            "status IN ('DRAFT','CONFIRMED','CLOSED','CANCELLED')",
            name="ck_sales_order_status",
        ),
    )


class SalesOrderLine(Base):
    __tablename__ = "sales_order_line"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    order_id: Mapped[UUID] = mapped_column(
        ForeignKey("sales_order.id", ondelete="CASCADE"), nullable=False
    )
    line_no: Mapped[int] = mapped_column(Integer, nullable=False)
    product_id: Mapped[UUID] = mapped_column(ForeignKey("product.id"), nullable=False)
    product_uom_id: Mapped[UUID] = mapped_column(nullable=False)
    ordered_qty: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
    factor_to_base_snapshot: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
    closed_qty_base: Mapped[Decimal] = mapped_column(
        Numeric(18, 4), default=Decimal("0"), nullable=False
    )
    close_reason: Mapped[str | None] = mapped_column(Text)

    order: Mapped["SalesOrder"] = relationship("SalesOrder", back_populates="lines")
    product: Mapped["Product"] = relationship("Product")

    __table_args__ = (
        UniqueConstraint("order_id", "line_no", name="uq_so_line_no"),
        UniqueConstraint("id", "product_id", name="uq_so_line_id_product"),
        ForeignKeyConstraint(
            ["product_uom_id", "product_id"],
            ["product_uom.id", "product_uom.product_id"],
            name="fk_so_line_product_uom",
        ),
        CheckConstraint("line_no > 0", name="ck_so_line_no"),
        CheckConstraint("ordered_qty > 0", name="ck_so_ordered_qty"),
        CheckConstraint("factor_to_base_snapshot > 0", name="ck_so_factor"),
        CheckConstraint("unit_price >= 0", name="ck_so_unit_price"),
        CheckConstraint("closed_qty_base >= 0", name="ck_so_closed_qty_non_negative"),
        CheckConstraint(
            "closed_qty_base <= ordered_qty * factor_to_base_snapshot",
            name="ck_so_closed_qty_max",
        ),
    )
