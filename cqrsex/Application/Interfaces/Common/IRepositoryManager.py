from abc import ABC, abstractmethod
from cqrsex.Application.Interfaces.Repositories.IBlogPostReadRepository import IBlogPostReadRepository
from cqrsex.Application.Interfaces.Repositories.IBlogPostWriteRepository import IBlogPostWriteRepository

class IRepositoryManager(ABC):
    @property
    @abstractmethod
    def blog_post_read_repository(self) -> IBlogPostReadRepository: ...

    @property
    @abstractmethod
    def blog_post_write_repository(self) -> IBlogPostWriteRepository: ...
