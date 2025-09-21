# cqrsex/Application/DTO/errors.py
from pydantic import ValidationError
from cqrsex.Application.Wrapper.ConcreteResultT import ConcreteResultT
from cqrsex.Application.Common.MessageResult import StatusCode

def pydantic_error_to_result(err: ValidationError) -> ConcreteResultT:
    details = []
    for e in err.errors():
        details.append({
            "loc": ".".join(str(p) for p in e.get("loc", [])),
            "msg": e.get("msg"),
            "type": e.get("type"),
        })
    return ConcreteResultT.fail(
        message="Validation failed",
        status=StatusCode.BAD_REQUEST,
        errors=details,
    )
