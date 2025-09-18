# cqrsex/Application/Features/BlogPosts/Commands/Delete/Handler.py
from dataclasses import dataclass
from injector import inject

from cqrsex.Application.Mediator.contracts import ICommandHandler
from cqrsex.Application.CQRS.BlogPosts.Commands.Delete.Request import DeleteBlogPost
from cqrsex.Application.Interfaces.Common.IRepositoryManager import IRepositoryManager
from cqrsex.Application.Wrapper.ConcreteResultT import ConcreteResultT
from cqrsex.Application.Common.exceptions import NotFoundException, ServiceException

@dataclass
class DeleteBlogPostHandler(ICommandHandler[DeleteBlogPost, ConcreteResultT]):
    @inject
    def __init__(self, repos: IRepositoryManager) -> None:
        self.repos = repos

    def handle(self, cmd: DeleteBlogPost) -> ConcreteResultT:
        entity = self.repos.blog_post_read_repository.get_by_id(cmd.id)
        if not entity:
            raise NotFoundException("BlogPost not found")

        try:
            self.repos.blog_post_write_repository.delete_permanently(entity)
        except Exception as e:
            raise ServiceException(f"Failed to delete BlogPost {cmd.id}: {e}")

        return ConcreteResultT.success(message="Deleted")
