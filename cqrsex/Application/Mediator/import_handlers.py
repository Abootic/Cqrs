# cqrsex/Application/Mediator/import_handlers.py
from __future__ import annotations
import importlib, pkgutil
from typing import Iterable

def import_under(package_roots: Iterable[str]) -> None:
    for root in package_roots:
        pkg = importlib.import_module(root)
        if not hasattr(pkg, "__path__"):
            continue
        for _f, modname, _is_pkg in pkgutil.walk_packages(pkg.__path__, root + "."):
            importlib.import_module(modname)
