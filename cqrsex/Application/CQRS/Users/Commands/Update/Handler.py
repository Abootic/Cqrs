from __future__ import annotations
from injector import inject
from django.contrib.auth import get_user_model

from cqrsex.Application.Mediator.contracts import ICommandHandler
from cqrsex.Application.CQRS.Users.Commands.Update.Request import UpdateUser
from cqrsex.Application.Interfaces.Common.IRepositoryManager import IRepositoryManager
from cqrsex.Application.Wrapper.ConcreteResultT import ConcreteResultT
from cqrsex.Application.Mediator.registry import handler_for
from cqrsex.Application.Common.exceptions import (
    ValidationException, NotFoundException, PermissionDeniedException, ServiceException
)
from cqrsex.Application.Mapping.UsersMapper import to_detail

User = get_user_model()

@handler_for(UpdateUser)
class UpdateUserHandler(ICommandHandler[UpdateUser, ConcreteResultT]):
    @inject
    def __init__(self, repos: IRepositoryManager) -> None:
        self._repos = repos

    def handle(self, cmd: UpdateUser) -> ConcreteResultT:
        u = self._repos.user_read_repository.get_by_id(cmd.id)
        if not u:
            raise NotFoundException("User not found")

        # permissions
        if not cmd.acting_is_admin and cmd.acting_user_id != u.id:
            raise PermissionDeniedException("Not allowed")

        # basic updates
        if cmd.email is not None:
            em = cmd.email.strip()
            if not em:
                raise ValidationException("email cannot be empty")
            if self._repos.user_read_repository.exists_email_excluding_id(em, u.id):
                raise ValidationException("email already in use")
            u.email = em

        if cmd.first_name is not None:
            u.first_name = (cmd.first_name or "").strip()

        if cmd.last_name is not None:
            u.last_name = (cmd.last_name or "").strip()

        if cmd.password is not None:
            pw = (cmd.password or "").strip()
            if not pw:
                raise ValidationException("password cannot be empty")
            u.set_password(pw)

        # admin-only
        if cmd.user_type is not None:
            if not cmd.acting_is_admin:
                raise PermissionDeniedException("Only admin can change role")
            if cmd.user_type not in {"ADMIN", "CUSTOMER", "SUPPLIER"}:
                raise ValidationException("invalid user_type")
            u.user_type = cmd.user_type

        if cmd.is_active is not None:
            if not cmd.acting_is_admin:
                raise PermissionDeniedException("Only admin can change active status")
            u.is_active = bool(cmd.is_active)

        try:
            saved = self._repos.user_write_repository.update(u)
        except Exception as e:
            raise ServiceException(f"failed to update user: {e}")

        return ConcreteResultT.success(to_detail(saved), "Updated")
