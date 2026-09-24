from uuid import UUID, uuid4

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    ForeignKey,
    ForeignKeyConstraint,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from warehouse_atlas.infrastructure.db.base import Base


class Warehouse(Base):
    __tablename__ = "warehouse"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    timezone: Mapped[str] = mapped_column(String(50), default="Asia/Ho_Chi_Minh", nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    locations: Mapped[list["Location"]] = relationship("Location", back_populates="warehouse")


class Location(Base):
    __tablename__ = "location"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    warehouse_id: Mapped[UUID] = mapped_column(ForeignKey("warehouse.id"), nullable=False)
    parent_id: Mapped[UUID | None] = mapped_column()
    code: Mapped[str] = mapped_column(String(50), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    usage: Mapped[str] = mapped_column(String(20), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    warehouse: Mapped["Warehouse"] = relationship("Warehouse", back_populates="locations")

    __table_args__ = (
        UniqueConstraint("warehouse_id", "code", name="uq_location_warehouse_code"),
        UniqueConstraint("id", "warehouse_id", name="uq_location_id_warehouse"),
        ForeignKeyConstraint(
            ["parent_id", "warehouse_id"],
            ["location.id", "location.warehouse_id"],
            name="fk_location_parent_same_warehouse",
        ),
        CheckConstraint(
            "usage IN ('STRUCTURAL','STORAGE','RECEIVING','DISPATCH','TRANSIT')",
            name="ck_location_usage",
        ),
        CheckConstraint("parent_id IS NULL OR parent_id <> id", name="ck_location_parent_not_self"),
    )
