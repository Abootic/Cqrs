# cqrsex/Application/Features/BlogPosts/Commands/Create/Handler.py
from __future__ import annotations
from injector import inject
from cqrsex.Application.Mediator.contracts import ICommandHandler
from cqrsex.Application.CQRS.BlogPosts.Commands.Create.Request import CreateBlogPost
from cqrsex.Application.Interfaces.Common.IRepositoryManager import IRepositoryManager
from cqrsex.Application.Mapping.BlogPostsMapper import BlogPostMapper
from cqrsex.Application.Mediator.registry import handler_for
from cqrsex.Application.Wrapper.ConcreteResultT import ConcreteResultT
from cqrsex.Application.Common.exceptions import ServiceException
@handler_for(CreateBlogPost)
class CreateBlogPostHandler(ICommandHandler[CreateBlogPost, ConcreteResultT]):
    @inject
    def __init__(self, repos: IRepositoryManager) -> None:
        self._repos = repos
 
    def handle(self, cmd: CreateBlogPost) -> ConcreteResultT:
     

        model = BlogPostMapper.to_model_from_create(
            title=cmd.title,
            body=cmd.body,
            author_id=cmd.author_id,
        )
        try:
            saved = self._repos.blog_post_write_repository.add(model)
        except Exception as e:
            raise ServiceException(f"Failed to create blog post: {e}")

        return ConcreteResultT.success(BlogPostMapper.to_detail(saved), "Created")
