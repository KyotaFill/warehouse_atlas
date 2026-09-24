from datetime import UTC, datetime
from decimal import Decimal
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import (
    CheckConstraint,
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
    from warehouse_atlas.infrastructure.orm.catalog_models import Product
    from warehouse_atlas.infrastructure.orm.warehouse_models import Location, Warehouse


class InventoryDocument(Base):
    __tablename__ = "inventory_document"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    warehouse_id: Mapped[UUID] = mapped_column(ForeignKey("warehouse.id"), nullable=False)
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    kind: Mapped[str] = mapped_column(String(30), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="DRAFT", nullable=False)
    partner_id: Mapped[UUID | None] = mapped_column(ForeignKey("partner.id"))
    reversal_of_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("inventory_document.id"), unique=True
    )
    idempotency_key: Mapped[UUID | None] = mapped_column(unique=True)
    posting_payload_hash: Mapped[str | None] = mapped_column(String(64))
    reason: Mapped[str | None] = mapped_column(Text)
    created_by: Mapped[UUID] = mapped_column(ForeignKey("app_user.id"), nullable=False)
    approved_by: Mapped[UUID | None] = mapped_column(ForeignKey("app_user.id"))
    posted_by: Mapped[UUID | None] = mapped_column(ForeignKey("app_user.id"))
    posted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    warehouse: Mapped["Warehouse"] = relationship("Warehouse")
    lines: Mapped[list["InventoryDocumentLine"]] = relationship(
        "InventoryDocumentLine", back_populates="document", cascade="all, delete-orphan"
    )

    __table_args__ = (
        CheckConstraint(
            "kind IN ('OPENING','RECEIPT','SHIPMENT','TRANSFER','RECLASSIFY','ADJUSTMENT','CUSTOMER_RETURN','SUPPLIER_RETURN','REVERSAL')",
            name="ck_doc_kind",
        ),
        CheckConstraint(
            "status IN ('DRAFT','APPROVED','POSTED','CANCELLED')",
            name="ck_doc_status",
        ),
        CheckConstraint(
            "status <> 'POSTED' OR (posted_at IS NOT NULL AND posted_by IS NOT NULL AND idempotency_key IS NOT NULL AND posting_payload_hash IS NOT NULL)",
            name="ck_doc_posted_metadata",
        ),
        CheckConstraint(
            "(kind = 'REVERSAL') = (reversal_of_id IS NOT NULL)",
            name="ck_doc_reversal_parity",
        ),
        CheckConstraint(
            "reversal_of_id IS NULL OR reversal_of_id <> id",
            name="ck_doc_reversal_not_self",
        ),
    )


class InventoryDocumentLine(Base):
    __tablename__ = "inventory_document_line"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    document_id: Mapped[UUID] = mapped_column(ForeignKey("inventory_document.id"), nullable=False)
    line_no: Mapped[int] = mapped_column(Integer, nullable=False)
    product_id: Mapped[UUID] = mapped_column(ForeignKey("product.id"), nullable=False)
    lot_id: Mapped[UUID] = mapped_column(nullable=False)
    product_uom_id: Mapped[UUID] = mapped_column(nullable=False)
    qty: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
    factor_to_base_snapshot: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
    qty_base: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
    from_location_id: Mapped[UUID | None] = mapped_column(ForeignKey("location.id"))
    from_condition: Mapped[str | None] = mapped_column(String(20))
    to_location_id: Mapped[UUID | None] = mapped_column(ForeignKey("location.id"))
    to_condition: Mapped[str | None] = mapped_column(String(20))
    purchase_order_line_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("purchase_order_line.id")
    )
    sales_order_line_id: Mapped[UUID | None] = mapped_column(ForeignKey("sales_order_line.id"))
    original_line_id: Mapped[UUID | None] = mapped_column(ForeignKey("inventory_document_line.id"))

    document: Mapped["InventoryDocument"] = relationship(
        "InventoryDocument", back_populates="lines"
    )
    product: Mapped["Product"] = relationship("Product")

    __table_args__ = (
        UniqueConstraint("document_id", "line_no", name="uq_doc_line_no"),
        UniqueConstraint("id", "product_id", "lot_id", name="uq_doc_line_id_prod_lot"),
        ForeignKeyConstraint(
            ["product_uom_id", "product_id"],
            ["product_uom.id", "product_uom.product_id"],
            name="fk_doc_line_product_uom",
        ),
        ForeignKeyConstraint(
            ["lot_id", "product_id"],
            ["lot.id", "lot.product_id"],
            name="fk_doc_line_lot",
        ),
        CheckConstraint("line_no > 0", name="ck_doc_line_no"),
        CheckConstraint("qty > 0", name="ck_doc_line_qty"),
        CheckConstraint("factor_to_base_snapshot > 0", name="ck_doc_line_factor"),
        CheckConstraint(
            "qty_base = qty * factor_to_base_snapshot",
            name="ck_doc_line_qty_base_math",
        ),
        CheckConstraint(
            "from_location_id IS NOT NULL OR to_location_id IS NOT NULL",
            name="ck_doc_line_has_movement",
        ),
        CheckConstraint(
            "(from_location_id IS NULL) = (from_condition IS NULL)",
            name="ck_doc_line_from_loc_cond",
        ),
        CheckConstraint(
            "(to_location_id IS NULL) = (to_condition IS NULL)",
            name="ck_doc_line_to_loc_cond",
        ),
        CheckConstraint(
            "from_condition IS NULL OR from_condition IN ('GOOD','QUARANTINE','DAMAGED')",
            name="ck_doc_line_from_condition",
        ),
        CheckConstraint(
            "to_condition IS NULL OR to_condition IN ('GOOD','QUARANTINE','DAMAGED')",
            name="ck_doc_line_to_condition",
        ),
        CheckConstraint(
            "NOT (purchase_order_line_id IS NOT NULL AND sales_order_line_id IS NOT NULL)",
            name="ck_doc_line_not_both_po_so",
        ),
    )


class StockMovement(Base):
    __tablename__ = "stock_movement"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    document_line_id: Mapped[UUID] = mapped_column(unique=True, nullable=False)
    product_id: Mapped[UUID] = mapped_column(ForeignKey("product.id"), nullable=False)
    lot_id: Mapped[UUID] = mapped_column(nullable=False)
    from_location_id: Mapped[UUID | None] = mapped_column(ForeignKey("location.id"))
    from_condition: Mapped[str | None] = mapped_column(String(20))
    to_location_id: Mapped[UUID | None] = mapped_column(ForeignKey("location.id"))
    to_condition: Mapped[str | None] = mapped_column(String(20))
    qty_base: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
    reverses_movement_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("stock_movement.id"), unique=True
    )
    actor_id: Mapped[UUID] = mapped_column(ForeignKey("app_user.id"), nullable=False)
    recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )

    __table_args__ = (
        ForeignKeyConstraint(
            ["document_line_id", "product_id", "lot_id"],
            [
                "inventory_document_line.id",
                "inventory_document_line.product_id",
                "inventory_document_line.lot_id",
            ],
            name="fk_movement_doc_line",
        ),
        ForeignKeyConstraint(
            ["lot_id", "product_id"],
            ["lot.id", "lot.product_id"],
            name="fk_movement_lot",
        ),
        CheckConstraint("qty_base > 0", name="ck_movement_qty_base"),
        CheckConstraint(
            "from_location_id IS NOT NULL OR to_location_id IS NOT NULL",
            name="ck_movement_has_movement",
        ),
        CheckConstraint(
            "(from_location_id IS NULL) = (from_condition IS NULL)",
            name="ck_movement_from_loc_cond",
        ),
        CheckConstraint(
            "(to_location_id IS NULL) = (to_condition IS NULL)",
            name="ck_movement_to_loc_cond",
        ),
        CheckConstraint(
            "from_condition IS NULL OR from_condition IN ('GOOD','QUARANTINE','DAMAGED')",
            name="ck_movement_from_condition",
        ),
        CheckConstraint(
            "to_condition IS NULL OR to_condition IN ('GOOD','QUARANTINE','DAMAGED')",
            name="ck_movement_to_condition",
        ),
        CheckConstraint(
            "reverses_movement_id IS NULL OR reverses_movement_id <> id",
            name="ck_movement_not_reverse_self",
        ),
    )


class StockBalance(Base):
    __tablename__ = "stock_balance"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    product_id: Mapped[UUID] = mapped_column(ForeignKey("product.id"), nullable=False)
    location_id: Mapped[UUID] = mapped_column(ForeignKey("location.id"), nullable=False)
    lot_id: Mapped[UUID] = mapped_column(nullable=False)
    condition: Mapped[str] = mapped_column(String(20), nullable=False)
    on_hand: Mapped[Decimal] = mapped_column(Numeric(18, 4), default=Decimal("0"), nullable=False)
    reserved: Mapped[Decimal] = mapped_column(Numeric(18, 4), default=Decimal("0"), nullable=False)
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    product: Mapped["Product"] = relationship("Product")
    location: Mapped["Location"] = relationship("Location")

    __table_args__ = (
        UniqueConstraint(
            "product_id",
            "location_id",
            "lot_id",
            "condition",
            name="uq_stock_balance_bucket",
        ),
        ForeignKeyConstraint(
            ["lot_id", "product_id"],
            ["lot.id", "lot.product_id"],
            name="fk_stock_balance_lot",
        ),
        CheckConstraint(
            "condition IN ('GOOD','QUARANTINE','DAMAGED')",
            name="ck_stock_balance_condition",
        ),
        CheckConstraint("on_hand >= 0", name="ck_stock_balance_on_hand_non_negative"),
        CheckConstraint("reserved >= 0", name="ck_stock_balance_reserved_non_negative"),
        CheckConstraint("reserved <= on_hand", name="ck_stock_balance_reserved_max"),
    )
