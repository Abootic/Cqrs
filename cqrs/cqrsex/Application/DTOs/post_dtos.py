from dataclasses import dataclass
from datetime import datetime
from typing import Optional

# ---- Write-side DTOs ----
@dataclass(frozen=True)
class BlogPostCreateDTO:
    title: str
    body: str
    author_id: int

@dataclass(frozen=True)
class BlogPostUpdateDTO:
    id: int
    title: Optional[str] = None
    body: Optional[str] = None

# ---- Read-side DTOs (view models) ----
@dataclass(frozen=True)
class BlogPostListItemDTO:
    id: int
    title: str
    author_id: int
    created_at: datetime
    updated_at: datetime

@dataclass(frozen=True)
class BlogPostDetailDTO:
    id: int
    title: str
    body: str
    author_id: int
    created_at: datetime
    updated_at: datetime
