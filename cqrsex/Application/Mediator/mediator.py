# cqrsex/Application/Mediator/mediator.py
from __future__ import annotations
from typing import Any, Callable, Dict, List, Optional, Awaitable, Type
import inspect

Factory = Callable[[], Any]
Resolver = Callable[[Type[Any]], Any] 

class Behavior:
    def handle(self, request: Any, next_call: Callable[[], Any]) -> Any:
        return next_call()
    async def ahandle(self, request: Any, next_call: Callable[[], Awaitable[Any]]) -> Any:
        return await next_call()

class Mediator:
    def __init__(
        self,
        handlers: Dict[Type[Any], Factory],
        *,
        resolver: Optional[Resolver] = None,     # optional DI resolver for future
        behaviors: Optional[List[Behavior]] = None,
        cache_handlers: bool = True,
    ) -> None:
        self._factories = handlers
        self._behaviors = list(behaviors or [])
        self._resolver = resolver
        self._cache = cache_handlers
        self._cache_map: Dict[Type[Any], Any] = {}

    def _get_handler(self, req_type: Type[Any]) -> Any:
        fac = self._factories.get(req_type)
        if fac is None:
            available = ", ".join(t.__name__ for t in self._factories.keys())
            raise RuntimeError(f"No handler registered for {req_type.__name__}. Registered: [{available}]")
        if not self._cache:
            return fac()
        inst = self._cache_map.get(req_type)
        if inst is None:
            inst = fac()
            self._cache_map[req_type] = inst
        return inst

    def send(self, request: Any) -> Any:
        handler = self._get_handler(type(request))
        def call(): return handler.handle(request)
        nxt = call
        for b in reversed(self._behaviors):
            prev = nxt
            nxt = (lambda bb=b, pn=prev: lambda: bb.handle(request, pn))()
        res = nxt()
        if inspect.isawaitable(res):
            raise RuntimeError("Handler returned coroutine. Use send_async for async handlers.")
        return res

    async def send_async(self, request: Any) -> Any:
        handler = self._get_handler(type(request))
        async def final():
            h = getattr(handler, "handle", None)
            return await h(request) if inspect.iscoroutinefunction(h) else h(request)
        nxt: Callable[[], Awaitable[Any]] = final
        for b in reversed(self._behaviors):
            prev = nxt
            async def wrap(bb=b, pn=prev):
                async def _inner(): return await bb.ahandle(request, pn)
                return _inner
            nxt = await wrap()
        return await nxt()
