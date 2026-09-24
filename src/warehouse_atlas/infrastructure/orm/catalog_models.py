from datetime import UTC, datetime
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from warehouse_atlas.infrastructure.db.base import Base


class Category(Base):
    __tablename__ = "category"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class Uom(Base):
    __tablename__ = "uom"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    decimal_places: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    __table_args__ = (
        CheckConstraint("decimal_places BETWEEN 0 AND 4", name="ck_uom_decimal_places"),
    )


class Product(Base):
    __tablename__ = "product"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    sku: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    category_id: Mapped[UUID] = mapped_column(ForeignKey("category.id"), nullable=False)
    base_uom_id: Mapped[UUID] = mapped_column(ForeignKey("uom.id"), nullable=False)
    track_expiry: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    min_shelf_life_days: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    category: Mapped["Category"] = relationship("Category")
    base_uom: Mapped["Uom"] = relationship("Uom")
    uom_conversions: Mapped[list["ProductUom"]] = relationship(
        "ProductUom", back_populates="product"
    )

    __table_args__ = (
        CheckConstraint("min_shelf_life_days >= 0", name="ck_product_min_shelf_life_days"),
    )


class ProductUom(Base):
    __tablename__ = "product_uom"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    product_id: Mapped[UUID] = mapped_column(ForeignKey("product.id"), nullable=False)
    uom_id: Mapped[UUID] = mapped_column(ForeignKey("uom.id"), nullable=False)
    factor_to_base: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)

    product: Mapped["Product"] = relationship("Product", back_populates="uom_conversions")
    uom: Mapped["Uom"] = relationship("Uom")

    __table_args__ = (
        UniqueConstraint("product_id", "uom_id", name="uq_product_uom_product_uom"),
        UniqueConstraint("id", "product_id", name="uq_product_uom_id_product"),
        CheckConstraint("factor_to_base > 0", name="ck_product_uom_factor_to_base"),
    )


class ProductBarcode(Base):
    __tablename__ = "product_barcode"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    code: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    product_uom_id: Mapped[UUID] = mapped_column(ForeignKey("product_uom.id"), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    product_uom: Mapped["ProductUom"] = relationship("ProductUom")


class Partner(Base):
    __tablename__ = "partner"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    is_supplier: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_customer: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    phone: Mapped[str | None] = mapped_column(String(50))
    email: Mapped[str | None] = mapped_column(String(100))
    address: Mapped[str | None] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    __table_args__ = (CheckConstraint("is_supplier OR is_customer", name="ck_partner_type"),)


class SupplierProduct(Base):
    __tablename__ = "supplier_product"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    supplier_id: Mapped[UUID] = mapped_column(ForeignKey("partner.id"), nullable=False)
    product_id: Mapped[UUID] = mapped_column(ForeignKey("product.id"), nullable=False)
    supplier_sku: Mapped[str | None] = mapped_column(String(100))
    lead_time_days: Mapped[int] = mapped_column(Integer, nullable=False)
    moq_base: Mapped[Decimal] = mapped_column(Numeric(18, 4), default=Decimal("0"), nullable=False)
    order_multiple_base: Mapped[Decimal] = mapped_column(
        Numeric(18, 4), default=Decimal("1"), nullable=False
    )
    quoted_unit_cost: Mapped[Decimal | None] = mapped_column(Numeric(18, 4))
    is_preferred: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    supplier: Mapped["Partner"] = relationship("Partner")
    product: Mapped["Product"] = relationship("Product")

    __table_args__ = (
        UniqueConstraint("supplier_id", "product_id", name="uq_supplier_product"),
        CheckConstraint("lead_time_days >= 0", name="ck_supplier_product_lead_time"),
        CheckConstraint("moq_base >= 0", name="ck_supplier_product_moq"),
        CheckConstraint("order_multiple_base > 0", name="ck_supplier_product_multiple"),
        CheckConstraint(
            "quoted_unit_cost IS NULL OR quoted_unit_cost >= 0", name="ck_supplier_product_cost"
        ),
    )
