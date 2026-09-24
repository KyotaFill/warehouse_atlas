from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from typing import Protocol
from uuid import UUID

from warehouse_atlas.common.types import BucketKey


@dataclass(frozen=True, slots=True)
class AllocationCandidate:
    """Ứng viên lô/vị trí đã vượt qua bước kiểm tra LotEligibility."""
    bucket_id: UUID
    bucket_key: BucketKey
    available_qty: Decimal
    expires_on: date | None
    received_at: datetime
    lot_code: str


@dataclass(frozen=True, slots=True)
class LotAllocation:
    bucket_id: UUID
    bucket_key: BucketKey
    lot_code: str
    allocated_qty: Decimal


@dataclass(frozen=True, slots=True)
class AllocationPlan:
    allocations: tuple[LotAllocation, ...]
    total_allocated: Decimal
    policy_code: str
    is_fulfilled: bool


class AllocationPolicy(Protocol):
    """Giao diện đa hình chung cho chiến lược cấp phát (FEFO / FIFO)."""

    def allocate(
        self, candidates: list[AllocationCandidate], requested_qty: Decimal
    ) -> AllocationPlan:
        ...


class FefoPolicy:
    """
    First-Expired, First-Out (ưu tiên hạn dùng trước).
    Sắp xếp: expires_on tăng dần -> received_at tăng dần -> bucket_id.
    """

    def allocate(
        self, candidates: list[AllocationCandidate], requested_qty: Decimal
    ) -> AllocationPlan:
        # Lọc các ứng viên có available_qty > 0
        valid_candidates = [c for c in candidates if c.available_qty > Decimal("0")]

        # Sắp xếp FEFO: Lô có hạn tăng dần; lô không có hạn xếp cuối
        # Nếu cùng hạn dùng thì so theo received_at (FIFO phụ)
        sorted_candidates = sorted(
            valid_candidates,
            key=lambda c: (
                c.expires_on is None,  # Có hạn trước (False < True)
                c.expires_on,
                c.received_at,
                c.bucket_id,
            ),
        )

        allocations: list[LotAllocation] = []
        remaining_need = requested_qty

        for candidate in sorted_candidates:
            if remaining_need <= Decimal("0"):
                break
            take_qty = min(candidate.available_qty, remaining_need)
            allocations.append(
                LotAllocation(
                    bucket_id=candidate.bucket_id,
                    bucket_key=candidate.bucket_key,
                    lot_code=candidate.lot_code,
                    allocated_qty=take_qty,
                )
            )
            remaining_need -= take_qty

        total = sum((a.allocated_qty for a in allocations), Decimal("0"))
        return AllocationPlan(
            allocations=tuple(allocations),
            total_allocated=total,
            policy_code="FEFO",
            is_fulfilled=(total == requested_qty),
        )


class FifoPolicy:
    """
    First-In, First-Out (ưu tiên ngày nhận trước).
    Sắp xếp: received_at tăng dần -> bucket_id.
    """

    def allocate(
        self, candidates: list[AllocationCandidate], requested_qty: Decimal
    ) -> AllocationPlan:
        valid_candidates = [c for c in candidates if c.available_qty > Decimal("0")]
        sorted_candidates = sorted(
            valid_candidates,
            key=lambda c: (c.received_at, c.bucket_id),
        )

        allocations: list[LotAllocation] = []
        remaining_need = requested_qty

        for candidate in sorted_candidates:
            if remaining_need <= Decimal("0"):
                break
            take_qty = min(candidate.available_qty, remaining_need)
            allocations.append(
                LotAllocation(
                    bucket_id=candidate.bucket_id,
                    bucket_key=candidate.bucket_key,
                    lot_code=candidate.lot_code,
                    allocated_qty=take_qty,
                )
            )
            remaining_need -= take_qty

        total = sum((a.allocated_qty for a in allocations), Decimal("0"))
        return AllocationPlan(
            allocations=tuple(allocations),
            total_allocated=total,
            policy_code="FIFO",
            is_fulfilled=(total == requested_qty),
        )
