from typing import Optional

from cqrsex.Application.Interfaces.Repositories.IBlogPostWriteRepository import IBlogPostWriteRepository
from cqrsex.Domain.model.BlogPost import BlogPost
from cqrsex.Infrstraction.Repositories.GenericRepository import GenericRepository


class BlogPostWriteRepository(GenericRepository[BlogPost], IBlogPostWriteRepository):
    def __init__(self) -> None:
        super().__init__(BlogPost)

   