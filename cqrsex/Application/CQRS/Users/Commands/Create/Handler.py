# cqrsex/Application/CQRS/Users/Commands/Create/Handler.py
from __future__ import annotations
import logging
from injector import inject
from django.db import IntegrityError

from cqrsex.Application.Mediator.contracts import ICommandHandler
from cqrsex.Application.CQRS.Users.Commands.Create.Request import CreateUser
from cqrsex.Application.Interfaces.Common.IRepositoryManager import IRepositoryManager
from cqrsex.Application.Interfaces.Common.ISagaDispatcher import ISagaDispatcher
from cqrsex.Application.Wrapper.ConcreteResultT import ConcreteResultT
from cqrsex.Application.Mediator.registry import handler_for
from cqrsex.Application.Common.exceptions import ValidationException, ServiceException
from cqrsex.Application.Mapping.UsersMapper import to_detail, to_model_from_create

log = logging.getLogger(__name__)

@handler_for(CreateUser)
class CreateUserHandler(ICommandHandler[CreateUser, ConcreteResultT]):
    @inject
    def __init__(self, repos: IRepositoryManager, sagas: ISagaDispatcher) -> None:
        self._repos = repos
        self._sagas = sagas

    def handle(self, cmd: CreateUser) -> ConcreteResultT:
        # validation
        if not cmd.username: raise ValidationException("username is required")
        if not cmd.password: raise ValidationException("password is required")
        if not cmd.email:    raise ValidationException("email is required")
        if cmd.user_type not in {"ADMIN", "CUSTOMER", "SUPPLIER"}:
            raise ValidationException("invalid user_type")

        # pre-uniqueness checks (still keep them for fast fail)
        if self._repos.user_read_repository.exists_by_username(cmd.username.strip()):
            raise ValidationException("username already exists")
        if self._repos.user_read_repository.exists_by_email(cmd.email.strip()):
            raise ValidationException("email already exists")

        try:
            # write user
            user_model = to_model_from_create(cmd)
            saved = self._repos.user_write_repository.add(user_model)

            # emit post-commit event on SAME DB alias as the write repo
            self._sagas.emit(
                entity="User",
                action="Created",
                aggregate_id=saved.id,
                payload={"id": saved.id, "email": saved.email},
                #using=using_alias,
                using="default",
            )

            return ConcreteResultT.success(to_detail(saved), "Created")

        except IntegrityError:
            # DB unique constraint handled as validation error; TransactionBehavior rolls back
            raise ValidationException("email already exists")

        except Exception as e:
            # unexpected — let TransactionBehavior roll back
            raise ServiceException(f"failed to create user: {e}")
