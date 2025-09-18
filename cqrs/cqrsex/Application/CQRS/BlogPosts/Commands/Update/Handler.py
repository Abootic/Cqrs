# cqrsex/Application/Features/BlogPosts/Commands/Update/Handler.py
from dataclasses import dataclass
from injector import inject

from cqrsex.Application.Mediator.contracts import ICommandHandler
from cqrsex.Application.CQRS.BlogPosts.Commands.Update.Request import UpdateBlogPost
from cqrsex.Application.Interfaces.Common.IRepositoryManager import IRepositoryManager
from cqrsex.Application.Mapping.BlogPostsMapper import BlogPostMapper
from cqrsex.Application.Wrapper.ConcreteResultT import ConcreteResultT
from cqrsex.Application.Common.exceptions import ValidationException, NotFoundException, ServiceException

@dataclass
class UpdateBlogPostHandler(ICommandHandler[UpdateBlogPost, ConcreteResultT]):
    @inject
    def __init__(self, repos: IRepositoryManager) -> None:
        self.repos = repos

    def handle(self, cmd: UpdateBlogPost) -> ConcreteResultT:
        # load
        model = self.repos.blog_post_read_repository.get_by_id(cmd.id)
        if not model:
            raise NotFoundException("BlogPost not found")

        # validate
        if cmd.title is None and cmd.body is None:
            raise ValidationException("Nothing to update")
        if cmd.title is not None and not cmd.title.strip():
            raise ValidationException("Title cannot be empty")

        # map + save
        try:
            BlogPostMapper.apply_update(model, title=cmd.title, body=cmd.body)
            updated = self.repos.blog_post_write_repository.update(model)
        except Exception as e:
            # make sure any repo/storage error triggers rollback
            raise ServiceException(f"Failed to update BlogPost {cmd.id}: {e}")

        # success -> TransactionBehavior commits
        dto = BlogPostMapper.to_detail(updated)
        return ConcreteResultT.success(dto, "Updated")
