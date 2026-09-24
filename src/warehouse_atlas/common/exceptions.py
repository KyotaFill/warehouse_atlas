from typing import Any


class AppError(Exception):
    """Base application exception with error code and context."""

    def __init__(
        self,
        message: str,
        code: str = "INTERNAL_ERROR",
        context: dict[str, Any] | None = None,
        retryable: bool = False,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.code = code
        self.context = context or {}
        self.retryable = retryable


class DomainError(AppError):
    """Base domain business invariant violation."""

    def __init__(
        self, message: str, code: str = "DOMAIN_ERROR", context: dict[str, Any] | None = None
    ) -> None:
        super().__init__(message, code=code, context=context, retryable=False)


class ValidationError(AppError):
    def __init__(
        self, message: str, field: str | None = None, context: dict[str, Any] | None = None
    ) -> None:
        ctx = context or {}
        if field:
            ctx["field"] = field
        super().__init__(message, code="VALIDATION_ERROR", context=ctx, retryable=False)


class ConcurrencyError(AppError):
    """Optimistic or pessimistic lock failure."""

    def __init__(
        self,
        message: str = "Dữ liệu đã bị thay đổi bởi thao tác khác",
        context: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message, code="CONCURRENCY_CONFLICT", context=context, retryable=True)


class InsufficientStockError(DomainError):
    def __init__(
        self, message: str = "Không đủ số lượng khả dụng", context: dict[str, Any] | None = None
    ) -> None:
        super().__init__(message, code="INSUFFICIENT_STOCK", context=context)


class LotBlockedError(DomainError):
    def __init__(self, lot_code: str, reason: str = "") -> None:
        super().__init__(
            f"Lô {lot_code} đang bị phong tỏa/khóa: {reason}",
            code="LOT_BLOCKED",
            context={"lot_code": lot_code, "reason": reason},
        )


class LocationFrozenError(DomainError):
    def __init__(self, location_id: str, stocktake_id: str) -> None:
        super().__init__(
            f"Vị trí đang bị đóng băng do kiểm kê {stocktake_id}",
            code="LOCATION_FROZEN",
            context={"location_id": location_id, "stocktake_id": stocktake_id},
        )


class UnauthorizedError(AppError):
    def __init__(self, action: str, role: str) -> None:
        super().__init__(
            f"Vai trò {role} không có quyền thực hiện {action}",
            code="UNAUTHORIZED",
            context={"action": action, "role": role},
        )
