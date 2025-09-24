# cqrsex/Infrstraction/Saga/MultiSaga.py
from __future__ import annotations
from typing import Any, Iterable
from cqrsex.Application.Interfaces.Common.ISaga import ISaga

class MultiSaga(ISaga):
    def __init__(self, sagas: Iterable[ISaga]) -> None:
        self._sagas = list(sagas)

    def process(self, event: Any) -> None:
        for s in self._sagas:
            s.process(event)
