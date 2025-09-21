# cqrsex/Application/Features/BlogPosts/Commands/Delete/Handler.py
from __future__ import annotations
from dataclasses import dataclass
from injector import inject
from cqrsex.Application.Mediator.contracts import ICommandHandler
from cqrsex.Application.CQRS.BlogPosts.Commands.Delete.Request import DeleteBlogPost
from cqrsex.Application.Interfaces.Common.IRepositoryManager import IRepositoryManager
from cqrsex.Application.Mediator.registry import handler_for
from cqrsex.Application.Wrapper.ConcreteResultT import ConcreteResultT
from cqrsex.Application.Common.exceptions import NotFoundException, ServiceException

@dataclass
@handler_for(DeleteBlogPost)
class DeleteBlogPostHandler(ICommandHandler[DeleteBlogPost, ConcreteResultT]):
    @inject
    def __init__(self, repos: IRepositoryManager) -> None:
        self._repos = repos
  
    def handle(self, cmd: DeleteBlogPost) -> ConcreteResultT:
        entity = self._repos.blog_post_read_repository.get_by_id(cmd.id)
        if not entity:
            raise NotFoundException("BlogPost not found")
        try:
            self._repos.blog_post_write_repository.delete_permanently(entity)
        except Exception as e:
            raise ServiceException(f"Failed to delete BlogPost {cmd.id}: {e}")
        return ConcreteResultT.success(message="Deleted")
