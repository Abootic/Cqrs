from injector import Module, provider, singleton

from cqrsex.Application.Interfaces.Repositories.IBlogPostReadRepository import IBlogPostReadRepository
from cqrsex.Application.Interfaces.Repositories.IBlogPostWriteRepository import IBlogPostWriteRepository
from cqrsex.Application.Interfaces.Common.IRepositoryManager import IRepositoryManager

from cqrsex.Infrstraction.Repositories.BlogPostReadRepository import BlogPostReadRepository
from cqrsex.Infrstraction.Repositories.BlogPostWriteRepository import BlogPostWriteRepository
from cqrsex.Infrstraction.Repositories.RepositoryManager import RepositoryManager

class RepositoryModule(Module):

    @singleton
    @provider
    def provide_blog_post_read_repository(self) -> IBlogPostReadRepository:
        return BlogPostReadRepository()

    @singleton
    @provider
    def provide_blog_post_write_repository(self) -> IBlogPostWriteRepository:
        return BlogPostWriteRepository()

    @singleton
    @provider
    def provide_repository_manager(
        self,
        read_repo: IBlogPostReadRepository,
        write_repo: IBlogPostWriteRepository,
    ) -> IRepositoryManager:
        # NOTE: pass by POSITION, not keyword, to avoid param-name mismatches
        return RepositoryManager(read_repo, write_repo)
