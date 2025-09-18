from typing import Any, Callable, Dict, List, Type

class Mediator:
    def __init__(
        self,
        handlers: Dict[Type[Any], Callable[[], Any]],
        behaviors: List[Any],
    ) -> None:
        self._factories = handlers
        self._behaviors = behaviors

    def send(self, request: Any) -> Any:
        req_type = type(request)
        factory = self._factories.get(req_type)
        if factory is None:
            raise RuntimeError(f"No handler registered for {req_type.__name__}")

        handler = factory()

        def call_handler(req: Any):
            return handler.handle(req)

        next_callable: Callable[[Any], Any] = call_handler
        for behavior in reversed(self._behaviors):
            prev_next = next_callable
            next_callable = lambda req, b=behavior, n=prev_next: b.handle(req, n)

        return next_callable(request)
