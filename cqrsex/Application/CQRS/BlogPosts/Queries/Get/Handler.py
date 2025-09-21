# cqrsex/Application/Features/BlogPosts/Queries/Get/Handler.py
from __future__ import annotations
from dataclasses import dataclass
from injector import inject
from cqrsex.Application.Mediator.contracts import IQueryHandler
from cqrsex.Application.Common.MessageResult import StatusCode
from cqrsex.Application.CQRS.BlogPosts.Queries.Get.Request import GetBlogPost
from cqrsex.Application.Interfaces.Common.IRepositoryManager import IRepositoryManager
from cqrsex.Application.Mapping.BlogPostsMapper import BlogPostMapper
from cqrsex.Application.Mediator.registry import handler_for
from cqrsex.Application.Wrapper.ConcreteResultT import ConcreteResultT

@dataclass
@handler_for(GetBlogPost)
class GetBlogPostHandler(IQueryHandler[GetBlogPost, ConcreteResultT]):
    @inject
    def __init__(self, repos: IRepositoryManager) -> None:
        self._repos = repos

    def handle(self, q: GetBlogPost) -> ConcreteResultT:
        row = self._repos.blog_post_read_repository.get_by_id(q.id)
        if not row:
            return ConcreteResultT.fail("BlogPost not found", StatusCode.NOT_FOUND)
        return ConcreteResultT.success(BlogPostMapper.to_detail(row))
