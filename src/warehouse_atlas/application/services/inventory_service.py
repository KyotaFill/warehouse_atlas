import hashlib
from datetime import UTC, datetime
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import select

from warehouse_atlas.application.dtos.inventory_dto import DocumentLineInputDTO, PostDocumentCommand
from warehouse_atlas.application.services.posting_engine import PostingEngine
from warehouse_atlas.common.constants import Condition, DocumentKind, DocumentStatus
from warehouse_atlas.common.exceptions import DomainError, ValidationError
from warehouse_atlas.domain.model.audit import AuditEvent
from warehouse_atlas.domain.model.document import InventoryDocument, InventoryDocumentLine
from warehouse_atlas.infrastructure.orm.inventory_models import (
    InventoryDocument as InventoryDocumentRow,
)
from warehouse_atlas.infrastructure.orm.inventory_models import (
    InventoryDocumentLine as InventoryDocumentLineRow,
)
from warehouse_atlas.infrastructure.unit_of_work import SqlAlchemyUnitOfWork


class InventoryService:
    """
    Application Service điều phối các ca nghiệp vụ kho:
    - Quản lý vòng đời chứng từ: Tạo DRAFT -> APPROVE -> POST
    - Hạch toán nguyên tử qua PostingEngine và UnitOfWork
    - Xử lý điều chuyển (Transfer), Đổi trạng thái (Reclassify) và Bút toán đảo (Reversal)
    - Đối soát toàn vẹn số dư tồn kho với sổ cái
    """

    def __init__(self, uow_factory=SqlAlchemyUnitOfWork) -> None:
        self.uow_factory = uow_factory

    @staticmethod
    def _compute_payload_hash(lines: list[DocumentLineInputDTO]) -> str:
        """Tạo canonical hash từ nội dung bất biến của các dòng chứng từ."""
        hasher = hashlib.sha256()
        for idx, line in enumerate(
            sorted(
                lines, key=lambda item: (item.line_number, str(item.product_id), str(item.lot_id))
            )
        ):
            hasher.update(
                f"{idx}:{line.product_id}:{line.lot_id}:{line.quantity_base}:"
                f"{line.from_location_id}:{line.from_condition}:"
                f"{line.to_location_id}:{line.to_condition}".encode()
            )
        return hasher.hexdigest()

    def create_transfer_draft(
        self,
        warehouse_id: UUID,
        actor_id: UUID,
        items: list[tuple[UUID, UUID, UUID, Decimal, Condition]],
        # item: (product_id, lot_id, uom_id, qty, condition)
        from_location_id: UUID,
        to_location_id: UUID,
    ) -> UUID:
        """Tạo chứng từ điều chuyển nội bộ giữa 2 vị trí (TRANSFER DRAFT)."""
        if from_location_id == to_location_id:
            raise ValidationError("Vị trí nguồn và vị trí đích điều chuyển không được trùng nhau")

        uow = self.uow_factory()
        with uow:
            doc_id = uuid4()
            code = f"TRF-{datetime.now(UTC).strftime('%y%m%d')}-{str(doc_id)[:6].upper()}"

            doc_row = InventoryDocumentRow(
                id=doc_id,
                warehouse_id=warehouse_id,
                code=code,
                kind=DocumentKind.TRANSFER.value,
                status=DocumentStatus.DRAFT.value,
                created_by=actor_id,
                version=1,
            )
            uow.session.add(doc_row)
            uow.session.flush()

            for line_no, (p_id, lot_id, uom_id, qty, cond) in enumerate(items, start=1):
                line_row = InventoryDocumentLineRow(
                    id=uuid4(),
                    document_id=doc_id,
                    line_no=line_no,
                    product_id=p_id,
                    lot_id=lot_id,
                    product_uom_id=uom_id,
                    qty=qty,
                    factor_to_base_snapshot=Decimal("1"),
                    qty_base=qty,
                    from_location_id=from_location_id,
                    from_condition=cond.value,
                    to_location_id=to_location_id,
                    to_condition=cond.value,
                )
                uow.session.add(line_row)

            uow.commit()
            return doc_id

    def create_reclassify_draft(
        self,
        warehouse_id: UUID,
        actor_id: UUID,
        product_id: UUID,
        lot_id: UUID,
        uom_id: UUID,
        location_id: UUID,
        qty: Decimal,
        from_condition: Condition,
        to_condition: Condition,
        reason: str = "",
    ) -> UUID:
        """Tạo chứng từ chuyển trạng thái chất lượng (GOOD -> QUARANTINE/DAMAGED)."""
        if from_condition == to_condition:
            raise ValidationError("Trạng thái nguồn và đích phải khác nhau")

        uow = self.uow_factory()
        with uow:
            doc_id = uuid4()
            code = f"REC-{datetime.now(UTC).strftime('%y%m%d')}-{str(doc_id)[:6].upper()}"

            doc_row = InventoryDocumentRow(
                id=doc_id,
                warehouse_id=warehouse_id,
                code=code,
                kind=DocumentKind.RECLASSIFY.value,
                status=DocumentStatus.DRAFT.value,
                reason=reason,
                created_by=actor_id,
                version=1,
            )
            uow.session.add(doc_row)
            uow.session.flush()

            line_row = InventoryDocumentLineRow(
                id=uuid4(),
                document_id=doc_id,
                line_no=1,
                product_id=product_id,
                lot_id=lot_id,
                product_uom_id=uom_id,
                qty=qty,
                factor_to_base_snapshot=Decimal("1"),
                qty_base=qty,
                from_location_id=location_id,
                from_condition=from_condition.value,
                to_location_id=location_id,
                to_condition=to_condition.value,
            )
            uow.session.add(line_row)
            uow.commit()
            return doc_id

    def approve_document(self, document_id: UUID, actor_id: UUID) -> None:
        """Duyệt chứng từ: Chuyển DRAFT -> APPROVED."""
        uow = self.uow_factory()
        with uow:
            doc_row = uow.documents.load_document(document_id)
            if not doc_row:
                raise ValidationError("Chứng từ không tồn tại")
            if doc_row.status != DocumentStatus.DRAFT.value:
                raise ValidationError(f"Không thể duyệt chứng từ ở trạng thái {doc_row.status}")

            doc_row.status = DocumentStatus.APPROVED.value
            doc_row.approved_by = actor_id
            doc_row.version += 1
            uow.commit()

    def post_document(self, document_id: UUID, actor_id: UUID, idempotency_key: UUID) -> None:
        """
        Ghi sổ chứng từ nguyên tử (Posting Use Case):
        - Hỗ trợ Idempotency: Gửi lại cùng idempotency_key thì trả về kết quả an toàn.
        - Điều phối qua PostingEngine và commit trong 1 transaction duy nhất.
        """
        uow = self.uow_factory()
        with uow:
            doc_row = uow.documents.load_document(document_id)
            if not doc_row:
                raise ValidationError("Chứng từ không tồn tại")

            # Kiểm tra idempotency
            if doc_row.status == DocumentStatus.POSTED.value:
                if doc_row.idempotency_key == idempotency_key:
                    return  # Đã ghi sổ trước đó với cùng key, hoàn tất an toàn
                raise DomainError("Chứng từ đã được ghi sổ trước đó với khóa idempotency khác")

            # Chuyển đổi sang domain model
            domain_lines = [
                InventoryDocumentLine(
                    id=line.id,
                    document_id=doc_row.id,
                    line_number=line.line_no,
                    product_id=line.product_id,
                    uom_id=line.product_uom_id,
                    quantity=line.qty,
                    quantity_base=line.qty_base,
                    lot_id=line.lot_id,
                    from_location_id=line.from_location_id,
                    to_location_id=line.to_location_id,
                    from_condition=Condition(line.from_condition) if line.from_condition else None,
                    to_condition=Condition(line.to_condition) if line.to_condition else None,
                )
                for line in doc_row.lines
            ]

            domain_doc = InventoryDocument(
                id=doc_row.id,
                warehouse_id=doc_row.warehouse_id,
                code=doc_row.code,
                kind=DocumentKind(doc_row.kind),
                status=DocumentStatus(doc_row.status),
                created_by=doc_row.created_by,
                created_at=doc_row.created_at,
                version=doc_row.version,
                lines=domain_lines,
            )

            # Tính payload hash
            dtos = [
                DocumentLineInputDTO(
                    line_number=line.line_number,
                    product_id=line.product_id,
                    uom_id=line.uom_id,
                    quantity=line.quantity,
                    quantity_base=line.quantity_base,
                    lot_id=line.lot_id,
                    from_location_id=line.from_location_id,
                    to_location_id=line.to_location_id,
                    from_condition=line.from_condition,
                    to_condition=line.to_condition,
                )
                for line in domain_lines
            ]
            payload_hash = self._compute_payload_hash(dtos)

            cmd = PostDocumentCommand(
                document_id=doc_row.id,
                expected_version=doc_row.version,
                idempotency_key=idempotency_key,
                actor_id=actor_id,
                canonical_payload_hash=payload_hash,
                lines=tuple(dtos),
            )

            PostingEngine.post_in_uow(uow, domain_doc, cmd)

            # Ghi audit log
            uow.audit.append(
                AuditEvent(
                    id=uuid4(),
                    entity_name="inventory_document",
                    entity_id=doc_row.id,
                    action="POST",
                    actor_id=actor_id,
                    recorded_at=datetime.now(UTC),
                    payload_after={"code": doc_row.code, "kind": doc_row.kind},
                )
            )

            uow.commit()

    def reverse_document(
        self,
        document_id: UUID,
        reason: str,
        actor_id: UUID,
        idempotency_key: UUID,
    ) -> UUID:
        """
        Bút toán đảo (Reversal Workflow):
        - Tạo chứng từ REVERSAL đảo ngược toàn bộ các cặp (from <-> to) của chứng từ gốc.
        - Không sửa hoặc xóa bất kỳ dòng nào của sổ cũ.
        - Tự động duyệt và ghi sổ trong transaction.
        """
        uow = self.uow_factory()
        with uow:
            orig_doc = uow.documents.load_document(document_id)
            if not orig_doc:
                raise ValidationError("Chứng từ gốc không tồn tại")
            if orig_doc.status != DocumentStatus.POSTED.value:
                raise DomainError("Chỉ có thể đảo chứng từ đã ở trạng thái POSTED")

            # Kiểm tra xem chứng từ này đã bị đảo trước đó chưa
            stmt_check = select(InventoryDocumentRow).where(
                InventoryDocumentRow.reversal_of_id == orig_doc.id
            )
            if uow.session.execute(stmt_check).scalar_one_or_none():
                raise DomainError("Chứng từ này đã được tạo bút toán đảo trước đó")

            reversal_id = uuid4()
            reversal_code = f"REV-{orig_doc.code}"

            reversal_doc = InventoryDocumentRow(
                id=reversal_id,
                warehouse_id=orig_doc.warehouse_id,
                code=reversal_code,
                kind=DocumentKind.REVERSAL.value,
                status=DocumentStatus.APPROVED.value,  # Chuẩn bị để post ngay
                reversal_of_id=orig_doc.id,
                reason=reason,
                created_by=actor_id,
                approved_by=actor_id,
                version=1,
            )
            uow.session.add(reversal_doc)
            uow.session.flush()

            rev_domain_lines = []
            rev_dtos = []

            for line_no, orig_line in enumerate(orig_doc.lines, start=1):
                # Đảo ngược hoàn toàn nguồn và đích
                rev_line_id = uuid4()
                rev_line_row = InventoryDocumentLineRow(
                    id=rev_line_id,
                    document_id=reversal_id,
                    line_no=line_no,
                    product_id=orig_line.product_id,
                    lot_id=orig_line.lot_id,
                    product_uom_id=orig_line.product_uom_id,
                    qty=orig_line.qty,
                    factor_to_base_snapshot=orig_line.factor_to_base_snapshot,
                    qty_base=orig_line.qty_base,
                    from_location_id=orig_line.to_location_id,
                    from_condition=orig_line.to_condition,
                    to_location_id=orig_line.from_location_id,
                    to_condition=orig_line.from_condition,
                    original_line_id=orig_line.id,
                )
                uow.session.add(rev_line_row)

                d_line = InventoryDocumentLine(
                    id=rev_line_id,
                    document_id=reversal_id,
                    line_number=line_no,
                    product_id=orig_line.product_id,
                    uom_id=orig_line.product_uom_id,
                    quantity=orig_line.qty,
                    quantity_base=orig_line.qty_base,
                    lot_id=orig_line.lot_id,
                    from_location_id=orig_line.to_location_id,
                    to_location_id=orig_line.from_location_id,
                    from_condition=Condition(orig_line.to_condition)
                    if orig_line.to_condition
                    else None,
                    to_condition=Condition(orig_line.from_condition)
                    if orig_line.from_condition
                    else None,
                )
                rev_domain_lines.append(d_line)
                rev_dtos.append(
                    DocumentLineInputDTO(
                        line_number=line_no,
                        product_id=d_line.product_id,
                        uom_id=d_line.uom_id,
                        quantity=d_line.quantity,
                        quantity_base=d_line.quantity_base,
                        lot_id=d_line.lot_id,
                        from_location_id=d_line.from_location_id,
                        to_location_id=d_line.to_location_id,
                        from_condition=d_line.from_condition,
                        to_condition=d_line.to_condition,
                    )
                )

            reversal_domain_doc = InventoryDocument(
                id=reversal_id,
                warehouse_id=orig_doc.warehouse_id,
                code=reversal_code,
                kind=DocumentKind.REVERSAL,
                status=DocumentStatus.APPROVED,
                created_by=actor_id,
                created_at=datetime.now(UTC),
                version=1,
                lines=rev_domain_lines,
            )

            payload_hash = self._compute_payload_hash(rev_dtos)

            cmd = PostDocumentCommand(
                document_id=reversal_id,
                expected_version=1,
                idempotency_key=idempotency_key,
                actor_id=actor_id,
                canonical_payload_hash=payload_hash,
                lines=tuple(rev_dtos),
            )

            # Ghi sổ bút toán đảo nguyên tử
            PostingEngine.post_in_uow(uow, reversal_domain_doc, cmd)
            uow.commit()
            return reversal_id
