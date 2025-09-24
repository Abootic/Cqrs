from __future__ import annotations
from injector import inject
from cqrsex.Application.Mediator.contracts import IQueryHandler
from cqrsex.Application.CQRS.Users.Queries.List.Request import ListUsers
from cqrsex.Application.Interfaces.Common.IRepositoryManager import IRepositoryManager
from cqrsex.Application.Wrapper.ConcreteResultT import ConcreteResultT
from cqrsex.Application.Mediator.registry import handler_for
from cqrsex.Application.Mapping.UsersMapper import to_detail

MAX_PAGE_SIZE = 200

@handler_for(ListUsers)
class ListUsersHandler(IQueryHandler[ListUsers, ConcreteResultT]):
    @inject
    def __init__(self, repos: IRepositoryManager) -> None:
        self._repos = repos

    def handle(self, q: ListUsers) -> ConcreteResultT:
        page = max(int(q.page or 1), 1)
        page_size = min(max(int(q.page_size or 20), 1), MAX_PAGE_SIZE)

        items, total = self._repos.user_read_repository.get_paginated(
            page=page, page_size=page_size, q=q.q, user_type=q.user_type
        )
        data = [to_detail(u) for u in items]
        pagination = {
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size,
        }
        return ConcreteResultT.success(data, pagination=pagination)
