from __future__ import annotations
from injector import inject

from cqrsex.Application.Mediator.contracts import ICommandHandler
from cqrsex.Application.CQRS.Users.Commands.Delete.Request import DeleteUser
from cqrsex.Application.Interfaces.Common.IRepositoryManager import IRepositoryManager
from cqrsex.Application.Wrapper.ConcreteResultT import ConcreteResultT
from cqrsex.Application.Mediator.registry import handler_for
from cqrsex.Application.Common.exceptions import NotFoundException, PermissionDeniedException, ServiceException

@handler_for(DeleteUser)
class DeleteUserHandler(ICommandHandler[DeleteUser, ConcreteResultT]):
    @inject
    def __init__(self, repos: IRepositoryManager) -> None:
        self._repos = repos

    def handle(self, cmd: DeleteUser) -> ConcreteResultT:
        if not cmd.acting_is_admin:
            raise PermissionDeniedException("Only admin can delete users")

        u = self._repos.user_read_repository.get_by_id(cmd.id)
        if not u:
            raise NotFoundException("User not found")

        try:
            self._repos.user_write_repository.delete_permanently(u)
        except Exception as e:
            raise ServiceException(f"failed to delete user {cmd.id}: {e}")

        return ConcreteResultT.success(message="Deleted")
