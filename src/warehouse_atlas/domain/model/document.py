from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from warehouse_atlas.common.constants import Condition, DocumentKind, DocumentStatus
from warehouse_atlas.common.exceptions import ValidationError


@dataclass
class InventoryDocumentLine:
    id: UUID
    document_id: UUID
    line_number: int
    product_id: UUID
    uom_id: UUID
    quantity: Decimal  # Theo đơn vị chứng từ
    quantity_base: Decimal  # Đã nhân hệ số quy đổi ra đơn vị cơ sở
    lot_id: UUID
    from_location_id: UUID | None
    to_location_id: UUID | None
    from_condition: Condition | None
    to_condition: Condition | None
    po_line_id: UUID | None = None
    so_line_id: UUID | None = None
    reference_line_id: UUID | None = None


@dataclass
class InventoryDocument:
    """
    Chứng từ kho (Thực nhập, thực xuất, điều chuyển, kiểm kê điều chỉnh...).
    Chỉ có 1 entity InventoryDocument với 9 DocumentKind khác nhau.
    """

    id: UUID
    warehouse_id: UUID
    code: str
    kind: DocumentKind
    status: DocumentStatus
    created_by: UUID
    created_at: datetime
    approved_by: UUID | None = None
    approved_at: datetime | None = None
    posted_at: datetime | None = None
    version: int = 1
    lines: list[InventoryDocumentLine] = field(default_factory=list)

    def validate_for_approval(self) -> None:
        if self.status != DocumentStatus.DRAFT:
            raise ValidationError(f"Chứng từ trạng thái {self.status.value} không thể duyệt")
        if not self.lines:
            raise ValidationError("Chứng từ phải có ít nhất 1 dòng trước khi duyệt")

    def approve(self, user_id: UUID, approved_at: datetime) -> None:
        self.validate_for_approval()
        self.status = DocumentStatus.APPROVED
        self.approved_by = user_id
        self.approved_at = approved_at
        self.version += 1

    def mark_posted(self, posted_at: datetime) -> None:
        if self.status != DocumentStatus.APPROVED:
            raise ValidationError("Chỉ chứng từ APPROVED mới được ghi sổ")
        self.status = DocumentStatus.POSTED
        self.posted_at = posted_at
        self.version += 1
