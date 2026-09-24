#!/usr/bin/env python3
"""
Seed dữ liệu danh mục & hạ tầng kho nền tảng P0 cho Warehouse Atlas.
Bao gồm: Users, Roles, Warehouses, Locations, Categories, UOMs, Partners, Products, UOM Conversions.
"""

import hashlib
import sys
from decimal import Decimal
from pathlib import Path
from uuid import uuid4

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from warehouse_atlas.infrastructure.db.connection import get_db_session
from warehouse_atlas.infrastructure.orm.catalog_models import (
    Category,
    Partner,
    Product,
    ProductBarcode,
    ProductUom,
    Uom,
)
from warehouse_atlas.infrastructure.orm.user_models import AppRole, AppUser, UserRole
from warehouse_atlas.infrastructure.orm.warehouse_models import Location, Warehouse


def hash_pw(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def seed_data() -> None:
    print("=== Khởi tạo dữ liệu nền tảng P0 cho Warehouse Atlas ===")
    with get_db_session() as session:
        # 1. Roles
        roles = {
            "ADMIN": AppRole(id=uuid4(), code="ADMIN", name="Quản trị hệ thống"),
            "MANAGER": AppRole(id=uuid4(), code="MANAGER", name="Quản lý kho"),
            "OPERATOR": AppRole(id=uuid4(), code="OPERATOR", name="Nhân viên vận hành kho"),
        }
        for r in roles.values():
            session.merge(r)
        session.flush()

        # 2. Users
        users = [
            AppUser(
                id=uuid4(),
                username="admin",
                password_hash=hash_pw("admin123"),
                display_name="Quản Trị Viên",
            ),
            AppUser(
                id=uuid4(),
                username="manager",
                password_hash=hash_pw("manager123"),
                display_name="Trần Quản Lý",
            ),
            AppUser(
                id=uuid4(),
                username="receiver",
                password_hash=hash_pw("receiver123"),
                display_name="Nguyễn Nhận Hàng",
            ),
            AppUser(
                id=uuid4(),
                username="picker",
                password_hash=hash_pw("picker123"),
                display_name="Lê Nhặt Hàng",
            ),
        ]
        for u in users:
            session.merge(u)
        session.flush()

        # User roles
        user_map = {u.username: u.id for u in users}
        session.merge(UserRole(user_id=user_map["admin"], role_id=roles["ADMIN"].id))
        session.merge(UserRole(user_id=user_map["manager"], role_id=roles["MANAGER"].id))
        session.merge(UserRole(user_id=user_map["receiver"], role_id=roles["OPERATOR"].id))
        session.merge(UserRole(user_id=user_map["picker"], role_id=roles["OPERATOR"].id))
        session.flush()

        # 3. Warehouses
        wh_main = Warehouse(
            id=uuid4(), code="WH-MAIN", name="Tổng kho Phân Phối HCM", timezone="Asia/Ho_Chi_Minh"
        )
        wh_sub = Warehouse(
            id=uuid4(), code="WH-SUB", name="Kho Vệ Tinh Bình Dương", timezone="Asia/Ho_Chi_Minh"
        )
        session.merge(wh_main)
        session.merge(wh_sub)
        session.flush()

        # 4. Locations in WH-MAIN
        loc_dock_rec = Location(
            id=uuid4(),
            warehouse_id=wh_main.id,
            code="DOCK-REC",
            name="Cửa nhập hàng",
            usage="RECEIVING",
        )
        loc_dock_disp = Location(
            id=uuid4(),
            warehouse_id=wh_main.id,
            code="DOCK-DISP",
            name="Cửa xuất hàng",
            usage="DISPATCH",
        )
        session.merge(loc_dock_rec)
        session.merge(loc_dock_disp)
        session.flush()

        loc_zone_a = Location(
            id=uuid4(),
            warehouse_id=wh_main.id,
            code="ZONE-A",
            name="Khu lưu trữ A",
            usage="STRUCTURAL",
        )
        session.merge(loc_zone_a)
        session.flush()

        loc_a_01 = Location(
            id=uuid4(),
            warehouse_id=wh_main.id,
            parent_id=loc_zone_a.id,
            code="A-01-01",
            name="Kệ A Tầng 1 Ô 1",
            usage="STORAGE",
        )
        loc_a_02 = Location(
            id=uuid4(),
            warehouse_id=wh_main.id,
            parent_id=loc_zone_a.id,
            code="A-01-02",
            name="Kệ A Tầng 1 Ô 2",
            usage="STORAGE",
        )
        session.merge(loc_a_01)
        session.merge(loc_a_02)
        session.flush()

        # 5. Categories
        cat_dairy = Category(id=uuid4(), code="DAIRY", name="Sữa & Sản phẩm từ sữa")
        cat_bev = Category(id=uuid4(), code="BEV", name="Nước giải khát")
        cat_conf = Category(id=uuid4(), code="CONF", name="Bánh kẹo đóng gói")
        session.merge(cat_dairy)
        session.merge(cat_bev)
        session.merge(cat_conf)
        session.flush()

        # 6. UOMs
        uom_hop = Uom(id=uuid4(), code="HOP", name="Hộp", decimal_places=0)
        uom_chai = Uom(id=uuid4(), code="CHAI", name="Chai/Lon", decimal_places=0)
        uom_thung = Uom(id=uuid4(), code="THUNG", name="Thùng", decimal_places=0)
        session.merge(uom_hop)
        session.merge(uom_chai)
        session.merge(uom_thung)
        session.flush()

        # 7. Partners
        sup_vinamilk = Partner(
            id=uuid4(),
            code="SUP-VINAMILK",
            name="CTCP Sữa Việt Nam (Vinamilk)",
            is_supplier=True,
            is_customer=False,
        )
        cust_coop = Partner(
            id=uuid4(),
            code="CUST-COOP",
            name="Hệ thống Siêu thị Co.opmart",
            is_supplier=False,
            is_customer=True,
        )
        session.merge(sup_vinamilk)
        session.merge(cust_coop)
        session.flush()

        # 8. Products
        prod_milk = Product(
            id=uuid4(),
            sku="SKU-MILK-1L",
            name="Sữa tươi tiệt trùng Vinamilk 100% 1L",
            category_id=cat_dairy.id,
            base_uom_id=uom_hop.id,
            track_expiry=True,
            min_shelf_life_days=30,
        )
        session.merge(prod_milk)
        session.flush()

        # Product UOM Conversions
        uom_conv_base = ProductUom(
            id=uuid4(), product_id=prod_milk.id, uom_id=uom_hop.id, factor_to_base=Decimal("1")
        )
        uom_conv_case = ProductUom(
            id=uuid4(), product_id=prod_milk.id, uom_id=uom_thung.id, factor_to_base=Decimal("12")
        )
        session.merge(uom_conv_base)
        session.merge(uom_conv_case)
        session.flush()

        # Barcode
        barcode = ProductBarcode(id=uuid4(), code="8934673123456", product_uom_id=uom_conv_case.id)
        session.merge(barcode)

        session.commit()
        print("✓ Nạp thành công dữ liệu nền tảng P0 vào PostgreSQL!")


if __name__ == "__main__":
    seed_data()
