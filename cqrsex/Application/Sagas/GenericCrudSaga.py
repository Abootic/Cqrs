from __future__ import annotations
import logging
import inspect
import pkgutil
import threading
import re
from importlib import import_module
from types import ModuleType
from typing import Any, Callable, Dict, Optional, Tuple, Type, List, DefaultDict, Set
from collections import defaultdict
from injector import inject
from cqrsex.Application.Interfaces.Common.ISaga import ISaga
from cqrsex.Application.Mediator.mediator import Mediator

log = logging.getLogger(__name__)

# Optional explicit overrides:
# ROUTES[(entity_lower, action_lower)] = lambda evt: CommandClass(...)
ROUTES: Dict[Tuple[str, str], Callable[[Any], Any]] = {}

# You can add more CQRS roots if you split features across packages
CQRS_ROOTS: List[str] = ["cqrsex.Application.CQRS"]

# ---- discovery registry (lazy, thread-safe) ----
class _CmdMeta:
    __slots__ = ("cls", "params")
    def __init__(self, cls: Type[Any], params: Set[str]):
        self.cls = cls
        self.params = params

# (entity_lower, action_lower) -> meta
_COMMAND_INDEX: Dict[Tuple[str, str], _CmdMeta] = {}
# entity_lower -> set[action_lower]
_ACTIONS_BY_ENTITY: DefaultDict[str, Set[str]] = defaultdict(set)
_DISCOVERY_DONE = False
_DISCOVERY_LOCK = threading.RLock()

_CAMEL_RE = re.compile(r"""
    (?:[A-Z]+(?=[A-Z][a-z0-9]|[0-9]|\b)) |   # acronyms at start/middle (API, HTTP2)
    (?:[A-Z]?[a-z0-9]+)                    | # normal words
    (?:[A-Z])                                # single trailing capitals
""", re.VERBOSE)

def _norm(s: Optional[str]) -> str:
    return "".join((s or "")).replace("_", "").replace("-", "").strip().lower()

def _split_camel(name: str) -> List[str]:
    return [m.group(0) for m in _CAMEL_RE.finditer(name or "")] or []

def _iter_modules(pkg: ModuleType):
    if not hasattr(pkg, "__path__"):
        return
    yield from pkgutil.walk_packages(pkg.__path__, pkg.__name__ + ".")

def _ctor_param_names(cls: Type[Any]) -> Set[str]:
    try:
        sig = inspect.signature(cls)  # class __init__ signature
        return set(sig.parameters.keys())
    except Exception:
        return set()

def _discover_in_root(root_path: str):
    try:
        root = import_module(root_path)
    except Exception:
        log.exception("Cannot import CQRS root: %s", root_path)
        return
    for info in _iter_modules(root) or []:
        mod_name = info.name
        # only drill into *.Commands.*.Request
        if ".Commands." not in mod_name or not mod_name.endswith(".Request"):
            continue
        try:
            mod = import_module(mod_name)
        except Exception:
            log.debug("Skip import failure: %s", mod_name, exc_info=True)
            continue

        try:
            parts = mod_name.split(".")
            # [..., CQRS, {EntityPlural}, 'Commands', {Action}, 'Request']
            action = parts[-2]
            action_key = _norm(action)

            for attr in dir(mod):
                if attr.startswith("_"):
                    continue
                obj = getattr(mod, attr)
                if not inspect.isclass(obj):
                    continue
                # Class name should begin with Action segment: {Action}{Entity}
                if not _norm(attr).startswith(action_key):
                    continue
                entity_name = attr[len(action):]
                if not entity_name:
                    continue
                entity_key = _norm(entity_name)

                key = (entity_key, action_key)
                _COMMAND_INDEX[key] = _CmdMeta(obj, _ctor_param_names(obj))
                _ACTIONS_BY_ENTITY[entity_key].add(action_key)
        except Exception:
            log.debug("Indexing failed for %s", mod_name, exc_info=True)

def _discover_commands_once():
    global _DISCOVERY_DONE
    if _DISCOVERY_DONE:
        return
    with _DISCOVERY_LOCK:
        if _DISCOVERY_DONE:
            return
        for root in CQRS_ROOTS:
            _discover_in_root(root)
        _DISCOVERY_DONE = True
        log.info("CQRS command discovery: %d commands / %d entities",
                 len(_COMMAND_INDEX), len(_ACTIONS_BY_ENTITY))

def refresh_discovery():
    """Call on code reload if needed."""
    global _DISCOVERY_DONE
    with _DISCOVERY_LOCK:
        _COMMAND_INDEX.clear()
        _ACTIONS_BY_ENTITY.clear()
        _DISCOVERY_DONE = False
    _discover_commands_once()

def _resolve_by_fqcn(fqcn: str) -> Optional[_CmdMeta]:
    try:
        mod_path, cls_name = fqcn.rsplit(".", 1)
        mod = import_module(mod_path)
        cls = getattr(mod, cls_name)
        if not inspect.isclass(cls):
            return None
        return _CmdMeta(cls, _ctor_param_names(cls))
    except Exception:
        log.debug("Failed to import command by fqcn: %s", fqcn, exc_info=True)
        return None

def _resolve_by_entity_action(entity: str, action: str) -> Optional[_CmdMeta]:
    _discover_commands_once()
    return _COMMAND_INDEX.get((_norm(entity), _norm(action)))

def _parse_event(evt: Any) -> Tuple[Optional[str], Optional[str], Optional[str], dict, Optional[str]]:
    """
    Return (entity, action, db_alias, payload, command_fqcn).
    Priority:
      1) evt.command (FQCN)
      2) evt.entity + evt.action
      3) evt.event_type -> split tokens, try every split present in index
    """
    payload = getattr(evt, "payload", {}) or {}
    db_alias = getattr(evt, "db_alias", None)
    cmd_fqcn = getattr(evt, "command", None)

    entity = getattr(evt, "entity", None)
    action = getattr(evt, "action", None)
    if entity and action:
        return str(entity), str(action), db_alias, payload, cmd_fqcn

    et = (getattr(evt, "event_type", "") or "").strip()
    if not et:
        return None, None, db_alias, payload, cmd_fqcn

    tokens = _split_camel(et)
    if len(tokens) >= 2:
        _discover_commands_once()
        # prefer longer action tail first
        for i in range(1, len(tokens)):
            e = "".join(tokens[:len(tokens) - i])
            a = "".join(tokens[len(tokens) - i:])
            if (_norm(e), _norm(a)) in _COMMAND_INDEX:
                return e, a, db_alias, payload, cmd_fqcn

    return None, None, db_alias, payload, cmd_fqcn

def _build_kwargs(meta: _CmdMeta, evt: Any, payload: dict, db_alias: Optional[str]) -> Dict[str, Any]:
    kwargs: Dict[str, Any] = dict(payload) if payload else {}

    # Helpful defaults, but only if ctor accepts them
    if "allow_anonymous" in meta.params:
        kwargs.setdefault("allow_anonymous", True)
    if db_alias and "db_alias" in meta.params:
        kwargs.setdefault("db_alias", db_alias)

    # Common id propagation
    agg_id = getattr(evt, "aggregate_id", None)
    if agg_id is not None and "id" in meta.params and "id" not in kwargs:
        kwargs["id"] = agg_id

    # Filter to known params (safety)
    return {k: v for k, v in kwargs.items() if k in meta.params}

class GenericCrudSaga(ISaga):
    """
    Dynamic saga that routes write events to actual CQRS commands discovered in codebase.
    No synonyms or guesses: if a command exists, it runs; otherwise it's skipped.
    """
    @inject
    def __init__(self, mediator: Mediator) -> None:
        self._mediator = mediator

    def process(self, event: Any):
        entity, action, db_alias, payload, cmd_fqcn = _parse_event(event)

        # 1) explicit FQCN wins
        if cmd_fqcn:
            meta = _resolve_by_fqcn(cmd_fqcn)
            if not meta:
                log.warning("[Saga] command fqcn not found: %s", cmd_fqcn)
                return
        else:
            if not entity or not action:
                log.debug("[Saga] ignored event (no entity/action): %r", event)
                return
            # Override hook first
            factory = ROUTES.get((_norm(entity), _norm(action)))
            if factory:
                try:
                    cmd = factory(event)
                    log.info("[Saga] Dispatch %s (override)", type(cmd).__name__)
                    self._mediator.send(cmd)
                except Exception:
                    log.exception("[Saga] override failed for (%s, %s)", entity, action)
                finally:
                    return
            meta = _resolve_by_entity_action(entity, action)
            if not meta:
                log.info("[Saga] No command for (%s, %s); skipping.", entity, action)
                return

        try:
            kwargs = _build_kwargs(meta, event, payload, db_alias)
            cmd = meta.cls(**kwargs)
        except Exception:
            log.warning("Failed constructing %s with kwargs=%s", getattr(meta.cls, "__name__", meta.cls), kwargs, exc_info=True)
            return

        log.info("[Saga] Dispatch %s (entity=%s action=%s)", type(cmd).__name__, entity, action)
        self._mediator.send(cmd)
