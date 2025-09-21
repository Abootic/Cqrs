# cqrsex/Application/CQRS/BlogPosts/Queries/List/Handler.py
from __future__ import annotations
from injector import inject
from cqrsex.Application.Interfaces.Common.IRepositoryManager import IRepositoryManager
from cqrsex.Application.Mediator.contracts import IQueryHandler
from cqrsex.Application.CQRS.BlogPosts.Queries.List.Request import ListBlogPosts
from cqrsex.Application.Mediator.registry import handler_for
from cqrsex.Application.Wrapper.ConcreteResultT import ConcreteResultT
from cqrsex.Application.Common.MessageResult import StatusCode
from cqrsex.Application.Mapping.BlogPostsMapper import BlogPostMapper

MAX_PAGE_SIZE = 200

@handler_for(ListBlogPosts)
class ListBlogPostsHandler(IQueryHandler[ListBlogPosts, ConcreteResultT]):
    @inject
    def __init__(self, repos: IRepositoryManager) -> None:
        self._repos = repos

    def handle(self, q: ListBlogPosts) -> ConcreteResultT:
        try:
            # clamp page size and set deterministic order
            eff_size = min(max(int(q.page_size or 20), 1), MAX_PAGE_SIZE)

            filters = {}
            # IMPORTANT: match your FK name. If your model FK is `author`,
            # Django exposes `author_id` — this is correct. If your FK is
            # named differently (e.g., `user`), change the key to `user_id`.
            if q.author_id is not None:
                filters["author_id"] = q.author_id

            items, total = self._repos.blog_post_read_repository.get_paginated(
                page=max(int(q.page or 1), 1),
                page_size=eff_size,
                order_by=("-id",),   # force stable paging
                **filters,
            )

            # map models -> plain dicts (DTOs) so JSON never drops them
            dtos = [BlogPostMapper.to_summary(x) if hasattr(BlogPostMapper, "to_summary")
                    else BlogPostMapper.to_detail(x)
                    for x in items]

            pagination = {
                "total": total,
                "page": q.page,
                "page_size": eff_size,                         # use clamped size
                "total_pages": (total + eff_size - 1) // eff_size,
            }
            return ConcreteResultT.success(dtos, pagination=pagination)

        except Exception as e:
            return ConcreteResultT.fail(f"Failed to list BlogPosts: {e}", StatusCode.INTERNAL_SERVER_ERROR)
