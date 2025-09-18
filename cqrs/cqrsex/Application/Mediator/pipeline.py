# cqrsex/Application/CQRS/pipeline.py
from typing import Callable, Any
from dataclasses import dataclass
import logging

from cqrsex.Application.Interfaces.Common.IUnitOfWork import IUnitOfWork
from cqrsex.Application.Mediator.contracts import ICommand
from cqrsex.Application.Common.exceptions import AppException, ServiceException

logger = logging.getLogger(__name__)

@dataclass
class TransactionBehavior:
    uow_factory: Callable[[], IUnitOfWork]

    def handle(self, request: Any, next_call: Callable[[Any], Any]) -> Any:
        if isinstance(request, ICommand):
            with self.uow_factory() as uow:
                try:
                    result = next_call(request)
                    # If handler chose to return a result object marking failure:
                    if getattr(getattr(result, "status", None), "succeeded", True):
                        uow.commit()
                    else:
                        uow.rollback()
                    return result

                except AppException as ex:
                    # Known business/validation/etc -> rollback and return clean JSON
                    uow.rollback()
                    ex.log()
                    return ex.to_result()

                except Exception as ex:
                    # Unknown exception -> rollback and wrap
                    uow.rollback()
                    logger.exception("Unhandled exception in command handler")
                    return ServiceException("Internal server error").to_result()

        # Queries just pass through (no transaction)
        return next_call(request)
