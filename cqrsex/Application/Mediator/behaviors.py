# cqrsex/Application/Mediator/behaviors.py
from __future__ import annotations

import inspect
import logging
import time
from typing import Any, Awaitable, Callable, Optional

from cqrsex.Application.Mediator.mediator import Behavior
from cqrsex.Application.Mediator.contracts import ICommand
from cqrsex.Application.Interfaces.Common.IUnitOfWork import IUnitOfWork
from cqrsex.Application.Common.exceptions import (
    AppException,
    ForbiddenException,
    ServiceException,
)

log = logging.getLogger(__name__)


# ---------- small helper ----------
def _call_maybe_await(fn: Optional[Callable[..., Any]], *args, **kwargs):
    if fn is None:
        return None
    return fn(*args, **kwargs)


# ---------- behaviors ----------
class TransactionBehavior(Behavior):
    """
    Commands are transactional.
      - Success -> commit
      - AppException -> rollback + return ex.to_result()
      - Unknown -> rollback + ServiceException.to_result()
    Queries pass through.
    """
    def __init__(self, uow_factory: Callable[[], IUnitOfWork]) -> None:
        self._uow_factory = uow_factory

    def handle(self, request: Any, next_call: Callable[[], Any]) -> Any:
        if not isinstance(request, ICommand):
            return next_call()

        with self._uow_factory() as uow:
            try:
                res = next_call()
                if inspect.isawaitable(res):
                    raise RuntimeError("Async handler used in sync pipeline. Use send_async().")
                ok = getattr(getattr(res, "status", None), "succeeded", True)
                (uow.commit() if ok else uow.rollback())
                return res
            except AppException as ex:
                uow.rollback(); ex.log(); return ex.to_result()
            except Exception:
                uow.rollback(); log.exception("Unhandled exception in command handler")
                return ServiceException("Internal server error").to_result()

    async def ahandle(self, request: Any, next_call: Callable[[], Awaitable[Any]]) -> Any:
        if not isinstance(request, ICommand):
            return await next_call()

        uow = self._uow_factory()

        # Prefer async context manager if available
        if hasattr(uow, "__aenter__") and hasattr(uow, "__aexit__"):
            try:
                async with uow:
                    res = await next_call()
                    ok = getattr(getattr(res, "status", None), "succeeded", True)
                    fn = getattr(uow, "commit" if ok else "rollback", None)
                    v = _call_maybe_await(fn)
                    if inspect.isawaitable(v): await v
                    return res
            except AppException as ex:
                rb = getattr(uow, "rollback", None); v = _call_maybe_await(rb)
                if inspect.isawaitable(v): await v
                ex.log(); return ex.to_result()
            except Exception:
                rb = getattr(uow, "rollback", None); v = _call_maybe_await(rb)
                if inspect.isawaitable(v): await v
                log.exception("Unhandled exception in command handler (async)")
                return ServiceException("Internal server error").to_result()

        # Fallback: plain object with commit/rollback
        try:
            res = await next_call()
            ok = getattr(getattr(res, "status", None), "succeeded", True)
            fn = getattr(uow, "commit" if ok else "rollback", None)
            v = _call_maybe_await(fn)
            if inspect.isawaitable(v): await v
            return res
        except AppException as ex:
            v = _call_maybe_await(getattr(uow, "rollback", None))
            if inspect.isawaitable(v): await v
            ex.log(); return ex.to_result()
        except Exception:
            v = _call_maybe_await(getattr(uow, "rollback", None))
            if inspect.isawaitable(v): await v
            log.exception("Unhandled exception in command handler (async)")
            return ServiceException("Internal server error").to_result()


class AuthorizationBehavior(Behavior):
    """Policy gate before handler runs."""

    def __init__(self, get_user: Callable[[], Any], policy: Any) -> None:
        self._get_user = get_user
        self._policy = policy

    def handle(self, request: Any, next_call: Callable[[], Any]) -> Any:
        user = self._get_user()
        if not self._policy.is_allowed(user, request):
            raise ForbiddenException("Not allowed")
        return next_call()

    async def ahandle(self, request: Any, next_call: Callable[[], Awaitable[Any]]) -> Any:
        # Adapt to async get_user/policy if you have them.
        user = self._get_user()
        if not self._policy.is_allowed(user, request):
            raise ForbiddenException("Not allowed")
        return await next_call()


class MetricsBehavior(Behavior):
    """Logs duration of each request."""

    def handle(self, request: Any, next_call: Callable[[], Any]) -> Any:
        t0 = time.perf_counter()
        try:
            return next_call()
        finally:
            ms = (time.perf_counter() - t0) * 1000
            log.info("Handled %s in %.2f ms", type(request).__name__, ms)

    async def ahandle(self, request: Any, next_call: Callable[[], Awaitable[Any]]) -> Any:
        t0 = time.perf_counter()
        try:
            return await next_call()
        finally:
            ms = (time.perf_counter() - t0) * 1000
            log.info("Handled %s in %.2f ms (async)", type(request).__name__, ms)


class IdempotencyBehavior(Behavior):
    """
    For commands with meta.idempotency_key.
    Store must implement:
      - get(key) -> result | None   (sync or async)
      - set(key, result) -> None    (sync or async)
    """
    def __init__(self, store: Any) -> None:
        self._store = store

    def handle(self, request: Any, next_call: Callable[[], Any]) -> Any:
        meta = getattr(request, "meta", None)
        key = getattr(meta, "idempotency_key", None) if meta else None
        if not key:
            return next_call()

        cached = self._store.get(key)
        if inspect.isawaitable(cached):
            raise RuntimeError("Async store used in sync pipeline. Use send_async().")
        if cached is not None:
            return cached

        res = next_call()
        try:
            maybe = self._store.set(key, res)
            if inspect.isawaitable(maybe):
                raise RuntimeError("Async store used in sync pipeline. Use send_async().")
        except Exception:
            log.warning("Idempotency store.set failed", exc_info=True)
        return res

    async def ahandle(self, request: Any, next_call: Callable[[], Awaitable[Any]]) -> Any:
        meta = getattr(request, "meta", None)
        key = getattr(meta, "idempotency_key", None) if meta else None
        if not key:
            return await next_call()

        cached = self._store.get(key)
        cached = await cached if inspect.isawaitable(cached) else cached
        if cached is not None:
            return cached

        res = await next_call()
        try:
            set_result = self._store.set(key, res)
            if inspect.isawaitable(set_result):
                await set_result
        except Exception:
            log.warning("Idempotency store.set failed (async)", exc_info=True)
        return res
