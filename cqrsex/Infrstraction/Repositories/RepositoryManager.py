from cqrsex.Application.Interfaces.Common.IRepositoryManager import IRepositoryManager
from cqrsex.Application.Interfaces.Repositories.IBlogPostReadRepository import IBlogPostReadRepository
from cqrsex.Application.Interfaces.Repositories.IBlogPostWriteRepository import IBlogPostWriteRepository

class RepositoryManager(IRepositoryManager):
    def __init__(self, read_repo: IBlogPostReadRepository, write_repo: IBlogPostWriteRepository) -> None:
        self._read = read_repo
        self._write = write_repo

    @property
    def blog_post_read_repository(self) -> IBlogPostReadRepository:
        return self._read

    @property
    def blog_post_write_repository(self) -> IBlogPostWriteRepository:
        return self._write
