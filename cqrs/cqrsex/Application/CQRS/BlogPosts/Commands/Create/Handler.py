# cqrsex/Application/Features/BlogPosts/Commands/Create/Handler.py
from injector import inject

from cqrsex.Application.Mediator.contracts import ICommandHandler
from cqrsex.Application.CQRS.BlogPosts.Commands.Create.Request import CreateBlogPost
from cqrsex.Application.Interfaces.Common.IRepositoryManager import IRepositoryManager
from cqrsex.Application.Mapping.BlogPostsMapper import BlogPostMapper
from cqrsex.Application.Wrapper.ConcreteResultT import ConcreteResultT

# your exception family (namespaces may differ in your project)
from cqrsex.Application.Common.exceptions import (
    ValidationException,
    ServiceException,
)

class CreateBlogPostHandler(ICommandHandler[CreateBlogPost, ConcreteResultT]):
    @inject
    def __init__(self, repos: IRepositoryManager) -> None:
        self.repos = repos

    def handle(self, cmd: CreateBlogPost) -> ConcreteResultT:
        # ---- validate inputs (raise, don't return) ----
        title = (cmd.title or "").strip()
        if not title:
            raise ValidationException("Title is required")
        if not cmd.author_id:
            raise ValidationException("author_id is required")

        # ---- map to model ----
        model = BlogPostMapper.to_model_from_create(
            title=title,
            body=cmd.body or "",
            author_id=cmd.author_id,
        )

        # ---- write (any exception here will be caught by TransactionBehavior and rolled back) ----
        try:
            saved = self.repos.blog_post_write_repository.add(model)  # returns BlogPost model
        except Exception as e:
            # Optionally wrap low-level errors into a domain/service exception
            raise ServiceException(f"Failed to create blog post: {e}")

        # ---- map to DTO and return success ----
        dto = BlogPostMapper.to_detail(saved)
        return ConcreteResultT.success(dto, "Created")
