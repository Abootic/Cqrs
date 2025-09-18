from typing import Optional, Dict, Any

from cqrsex.Domain.model.BlogPost import BlogPost

class BlogPostMapper:
    @staticmethod
    def to_model_from_create(*, title: str, body: str, author_id: int) -> BlogPost:
        return BlogPost(title=title, body=body or "", author_id=author_id)

    @staticmethod
    def apply_update(model: BlogPost, *, title: Optional[str], body: Optional[str]) -> BlogPost:
        if title is not None:
            model.title = title
        if body is not None:
            model.body = body
        return model

    @staticmethod
    def to_list_item(m: BlogPost) -> Dict[str, Any]:
        return {
            "id": m.id,
            "title": m.title,
            "author_id": m.author_id,
            "created_at": m.created_at,
            "updated_at": m.updated_at,
        }

    @staticmethod
    def to_detail(m: BlogPost) -> Dict[str, Any]:
        return {
            "id": m.id,
            "title": m.title,
            "body": m.body,
            "author_id": m.author_id,
            "created_at": m.created_at,
            "updated_at": m.updated_at,
        }
