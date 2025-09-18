from typing import Any, Dict, Optional

from cqrsex.Application.Common.MessageResult import MessageResult, StatusCode
from cqrsex.Application.Interfaces.Common.IResultT import ResultT


class ConcreteResultT(ResultT):
    def __init__(self, status: MessageResult, data: Any = None, pagination: Optional[Dict[str, Any]] = None):
        super().__init__(status, data)
        self.pagination = pagination

    @classmethod
    def success(
        cls,
        data: Any = None,
        message: str = "Success",
        pagination: Optional[Dict[str, Any]] = None
    ) -> 'ConcreteResultT':
        status = MessageResult(message=message, code=StatusCode.SUCCESS)
        return cls(status=status, data=data, pagination=pagination)

    @classmethod
    def fail(
        cls,
        message: str,
        code: StatusCode = StatusCode.INTERNAL_SERVER_ERROR,
        data: Any = None,
        pagination: Optional[Dict[str, Any]] = None
    ) -> 'ConcreteResultT':
        status = MessageResult(message=message, code=code)
        return cls(status=status, data=data, pagination=pagination)


    def to_dict(self) -> Dict[str, Any]:
        result = {
            "succeeded": self.status.succeeded,
            "message": self.status.message,
            "status_code": self.status.code.value,
            "data": self.data
        }
        if self.pagination:
            result["pagination"] = self.pagination
        return result
