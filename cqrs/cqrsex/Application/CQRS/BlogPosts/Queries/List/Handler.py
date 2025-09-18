# cqrsex/Application/Features/BlogPosts/Queries/List/Handler.py
from injector import inject
from cqrsex.Application.Interfaces.Common.IRepositoryManager import IRepositoryManager
from cqrsex.Application.Mediator.contracts import IQueryHandler
from cqrsex.Application.CQRS.BlogPosts.Queries.List.Request import ListBlogPosts
from cqrsex.Application.Wrapper.ConcreteResultT import ConcreteResultT

class ListBlogPostsHandler(IQueryHandler[ListBlogPosts, ConcreteResultT]):
    @inject
    def __init__(self, repos: IRepositoryManager) -> None:
        self.repos = repos

    def handle(self, q: ListBlogPosts) -> ConcreteResultT:
        items, total = self.repos.blog_post_read_repository.get_paginated(
            page=q.page, page_size=q.page_size, author_id=q.author_id
        )
        pagination = {
            "total": total,
            "page": q.page,
            "page_size": q.page_size,
            "total_pages": (total + q.page_size - 1) // q.page_size,
        }
        return ConcreteResultT.success(items, pagination=pagination)
