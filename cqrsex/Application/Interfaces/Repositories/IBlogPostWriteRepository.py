from abc import ABC, abstractmethod
from typing import Optional

from cqrsex.Application.Interfaces.Common.IGenericRepository import IGenericRepository
from cqrsex.Domain.model.BlogPost import BlogPost

class IBlogPostWriteRepository(IGenericRepository[BlogPost]):
   pass
