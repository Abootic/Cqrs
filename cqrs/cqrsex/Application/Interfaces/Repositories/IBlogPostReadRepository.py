from abc import ABC, abstractmethod
from typing import Iterable, Tuple, Optional

from cqrsex.Application.Interfaces.Common.IGenericRepository import IGenericRepository
from cqrsex.Domain.model.BlogPost import BlogPost

class IBlogPostReadRepository(IGenericRepository[BlogPost]):
    pass