

from cqrsex.Application.Interfaces.Common.IRepositoryManager import IRepositoryManager
from cqrsex.Application.Interfaces.Repositories.IBlogPostReadRepository import IBlogPostReadRepository
from cqrsex.Application.Interfaces.Repositories.IBlogPostWriteRepository import IBlogPostWriteRepository


class RepositoryManager(IRepositoryManager):

    def __init__(
        self,
        blog_post_write_repository: IBlogPostWriteRepository,
        blog_post_read_repository: IBlogPostReadRepository,
    ):
       
        self._blog_post_write_repository = blog_post_write_repository
        self._blog_post_read_repository = blog_post_read_repository

    @property
    def blog_post_write_repository(self) -> IBlogPostWriteRepository:
        return self._blog_post_write_repository

    @property
    def blog_post_read_repository(self) -> IBlogPostReadRepository:
        return self._blog_post_read_repository
