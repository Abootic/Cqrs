# cqrsex/Application/Mediator/registry.py
from __future__ import annotations
from typing import Any, Callable, Dict, Type

_HANDLERS: Dict[Type[Any], Type[Any]] = {}

def handler_for(request_type: Type[Any]):
    def _wrap(cls: Type[Any]) -> Type[Any]:
        prev = _HANDLERS.get(request_type)
        if prev and prev is not cls:
            raise RuntimeError(
                f"Duplicate handler for {request_type.__name__}: {prev.__name__} vs {cls.__name__}"
            )
        _HANDLERS[request_type] = cls
        return cls
    return _wrap

def build_handler_factories(injector: Any) -> Dict[Type[Any], Callable[[], Any]]:
    return {req: (lambda c=cls, inj=injector: inj.get(c)) for req, cls in _HANDLERS.items()}
