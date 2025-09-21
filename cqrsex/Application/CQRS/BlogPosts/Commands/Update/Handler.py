# cqrsex/Application/Features/BlogPosts/Commands/Update/Handler.py
from __future__ import annotations
from dataclasses import dataclass
from injector import inject
from cqrsex.Application.Mediator.contracts import ICommandHandler
from cqrsex.Application.CQRS.BlogPosts.Commands.Update.Request import UpdateBlogPost
from cqrsex.Application.Interfaces.Common.IRepositoryManager import IRepositoryManager
from cqrsex.Application.Mapping.BlogPostsMapper import BlogPostMapper
from cqrsex.Application.Mediator.registry import handler_for
from cqrsex.Application.Wrapper.ConcreteResultT import ConcreteResultT
from cqrsex.Application.Common.exceptions import ValidationException, NotFoundException, ServiceException

@dataclass
@handler_for(UpdateBlogPost)
class UpdateBlogPostHandler(ICommandHandler[UpdateBlogPost, ConcreteResultT]):
    @inject
    def __init__(self, repos: IRepositoryManager) -> None:
        self._repos = repos
   
    def handle(self, cmd: UpdateBlogPost) -> ConcreteResultT:
        model = self._repos.blog_post_read_repository.get_by_id(cmd.id)
        if not model:
            raise NotFoundException("BlogPost not found")

        if cmd.title is None and cmd.body is None:
            raise ValidationException("Nothing to update")

        try:
            BlogPostMapper.apply_update(model, title=cmd.title, body=cmd.body)
            updated = self._repos.blog_post_write_repository.update(model)
        except Exception as e:
            raise ServiceException(f"Failed to update BlogPost {cmd.id}: {e}")

        return ConcreteResultT.success(BlogPostMapper.to_detail(updated), "Updated")
