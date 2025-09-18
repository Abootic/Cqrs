from dataclasses import dataclass
from cqrsex.Application.Mediator.contracts import IQueryHandler
from cqrsex.Application.Common.MessageResult import StatusCode
from cqrsex.Application.CQRS.BlogPosts.Queries.Get.Request import GetBlogPost
from cqrsex.Application.Interfaces.Common.IRepositoryManager import IRepositoryManager
from cqrsex.Application.Interfaces.Repositories.IBlogPostReadRepository import IBlogPostReadRepository
from cqrsex.Application.Mapping.BlogPostsMapper import BlogPostMapper
from cqrsex.Application.Wrapper.ConcreteResultT import ConcreteResultT
from injector import inject

@dataclass
class GetBlogPostHandler(IQueryHandler[GetBlogPost, ConcreteResultT]):
    @inject
    def __init__(self, repos: IRepositoryManager) -> None:
        self.repos = repos

    def handle(self, q: GetBlogPost) -> ConcreteResultT:
        row = self.repos.blog_post_read_repository.get_by_id(q.id)
        if not row:
            return ConcreteResultT.fail("BlogPost not found", StatusCode.NOT_FOUND)
        dto = BlogPostMapper.to_detail(row)
        return ConcreteResultT.success(dto)
