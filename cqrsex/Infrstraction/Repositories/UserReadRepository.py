from typing import List, Tuple, Optional
from django.db.models import Q
from cqrsex.Application.Interfaces.Repositories.IUserReadRepository import IUserReadRepository
from cqrsex.Domain.models.User import User

class UserReadRepository(IUserReadRepository):
    def __init__(self, db_alias: str = "auth_db") -> None:
        self.db_alias = db_alias

    def get_by_id(self, id: int) -> Optional[User]:
        return User.objects.using(self.db_alias).filter(id=id).first()

    def get_by_username(self, username: str) -> Optional[User]:
        s = (username or "").strip()
        if not s:
            return None
        return User.objects.using(self.db_alias).filter(username__iexact=s).first()

    def get_by_email(self, email: str) -> Optional[User]:
        s = (email or "").strip()
        if not s:
            return None
        return User.objects.using(self.db_alias).filter(email__iexact=s).first()

    def exists_by_username(self, username: str) -> bool:
        s = (username or "").strip()
        return bool(s) and User.objects.using(self.db_alias).filter(username__iexact=s).exists()

    def exists_by_email(self, email: str) -> bool:
        s = (email or "").strip()
        return bool(s) and User.objects.using(self.db_alias).filter(email__iexact=s).exists()

    def exists_email_excluding_id(self, email: str, exclude_id: int) -> bool:
        s = (email or "").strip()
        if not s:
            return False
        return User.objects.using(self.db_alias).filter(email__iexact=s).exclude(id=exclude_id).exists()

    def get_paginated(
        self, *, page: int, page_size: int, q: str | None = None, user_type: str | None = None
    ) -> Tuple[List[User], int]:
        qs = User.objects.using(self.db_alias).all().order_by("-id")
        if q:
            s = q.strip()
            qs = qs.filter(Q(username__icontains=s) | Q(email__icontains=s))
        if user_type:
            qs = qs.filter(user_type=user_type)

        total = qs.count()
        start = max(page - 1, 0) * page_size
        end = start + page_size
        return list(qs[start:end]), total
