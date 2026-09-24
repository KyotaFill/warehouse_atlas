from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from warehouse_atlas.infrastructure.orm.catalog_models import (
    Product as ProductRow,
)
from warehouse_atlas.infrastructure.orm.catalog_models import (
    ProductBarcode as ProductBarcodeRow,
)


class SqlAlchemyCatalogRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_product(self, product_id: UUID) -> ProductRow | None:
        stmt = select(ProductRow).where(ProductRow.id == product_id)
        return self.session.execute(stmt).scalar_one_or_none()

    def resolve_barcode(self, barcode: str) -> ProductBarcodeRow | None:
        stmt = select(ProductBarcodeRow).where(ProductBarcodeRow.code == barcode)
        return self.session.execute(stmt).scalar_one_or_none()
