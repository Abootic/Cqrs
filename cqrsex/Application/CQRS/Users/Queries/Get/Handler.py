from __future__ import annotations
from injector import inject
from cqrsex.Application.Mediator.contracts import IQueryHandler
from cqrsex.Application.CQRS.Users.Queries.Get.Request import GetUser
from cqrsex.Application.Interfaces.Common.IRepositoryManager import IRepositoryManager
from cqrsex.Application.Wrapper.ConcreteResultT import ConcreteResultT
from cqrsex.Application.Mediator.registry import handler_for
from cqrsex.Application.Mapping.UsersMapper import to_detail
from cqrsex.Application.Common.MessageResult import StatusCode

@handler_for(GetUser)
class GetUserHandler(IQueryHandler[GetUser, ConcreteResultT]):
    @inject
    def __init__(self, repos: IRepositoryManager) -> None:
        self._repos = repos

    def handle(self, q: GetUser) -> ConcreteResultT:
        u = self._repos.user_read_repository.get_by_id(q.id)
        if not u:
            return ConcreteResultT.fail("User not found", StatusCode.NOT_FOUND)
        return ConcreteResultT.success(to_detail(u))
