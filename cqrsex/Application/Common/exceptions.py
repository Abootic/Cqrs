# cqrsex/Application/Common/exceptions.py
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, Optional
import logging

from cqrsex.Application.Wrapper.ConcreteResultT import ConcreteResultT, StatusCode

logger = logging.getLogger(__name__)

@dataclass
class AppException(Exception):
    message: str
    status_code: StatusCode = StatusCode.INTERNAL_SERVER_ERROR
    code: str = "error"
    details: Optional[Dict[str, Any]] = field(default=None)

    def __post_init__(self):
        super().__init__(self.message)

    def to_result(self) -> ConcreteResultT:
        payload = {"code": self.code}
        if self.details:
            payload["details"] = self.details
        return ConcreteResultT.fail(self.message, self.status_code, payload)

    def log(self, level: int = logging.WARNING) -> "AppException":
        logger.log(level, "%s (%s): %s | details=%s",
                   self.__class__.__name__, self.status_code.name, self.message, self.details)
        return self

class ValidationException(AppException):
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None, code: str = "validation_error"):
        super().__init__(message, StatusCode.BAD_REQUEST, code, details)

class NotFoundException(AppException):
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None, code: str = "not_found"):
        super().__init__(message, StatusCode.NOT_FOUND, code, details)

class ConflictException(AppException):
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None, code: str = "conflict"):
        super().__init__(message, StatusCode.CONFLICT, code, details)

class PermissionDeniedException(AppException):
    def __init__(self, message: str = "Permission denied", details: Optional[Dict[str, Any]] = None, code: str = "forbidden"):
        super().__init__(message, StatusCode.FORBIDDEN, code, details)

class ForbiddenException(PermissionDeniedException):
    def __init__(self, message: str = "Forbidden", details: Optional[Dict[str, Any]] = None, code: str = "forbidden"):
        super().__init__(message, details, code)

class AuthenticationException(AppException):
    def __init__(self, message: str = "Authentication required", details: Optional[Dict[str, Any]] = None, code: str = "unauthorized"):
        super().__init__(message, StatusCode.UNAUTHORIZED, code, details)

class ConcurrencyException(AppException):
    def __init__(self, message: str = "Concurrency conflict", details: Optional[Dict[str, Any]] = None, code: str = "concurrency"):
        super().__init__(message, StatusCode.CONFLICT, code, details)

class ServiceException(AppException):
    def __init__(self, message: str = "Internal service error", details: Optional[Dict[str, Any]] = None, code: str = "service_error"):
        super().__init__(message, StatusCode.INTERNAL_SERVER_ERROR, code, details)

class ExternalServiceException(AppException):
    def __init__(self, message: str = "Upstream service error", details: Optional[Dict[str, Any]] = None, code: str = "external_service"):
        super().__init__(message, StatusCode.BAD_GATEWAY, code, details)

class RollbackException(AppException):
    pass

def ensure(condition: bool, message: str, *, code: str = "validation_error", details: Optional[Dict[str, Any]] = None):
    if not condition:
        raise ValidationException(message, details, code)

def raise_if_none(value: Any, *, message: str = "Resource not found", code: str = "not_found"):
    if value is None:
        raise NotFoundException(message, {"value": None}, code)
    return value
