from typing import Iterable, Tuple, Optional

from cqrsex.Application.Interfaces.Repositories.IBlogPostReadRepository import IBlogPostReadRepository
from cqrsex.Domain.model.BlogPost import BlogPost
from cqrsex.Infrstraction.Repositories.GenericRepository import GenericRepository


class BlogPostReadRepository(GenericRepository[BlogPost], IBlogPostReadRepository):
    def __init__(self) -> None:
        super().__init__(BlogPost)
