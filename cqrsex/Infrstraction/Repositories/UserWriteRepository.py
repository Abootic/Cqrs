from typing import Any
from cqrsex.Application.Interfaces.Repositories.IUserWriteRepository import IUserWriteRepository
from cqrsex.Domain.models.User import User

class UserWriteRepository(IUserWriteRepository):
    def __init__(self, db_alias: str = "auth_db") -> None:
        self.db_alias = db_alias

    def add(self, user: User) -> Any:
        user.save(using=self.db_alias)
        return user

    def update(self, user: User) -> Any:
        user.save(using=self.db_alias)
        return user

    def delete_permanently(self, user: User) -> None:
        user.delete(using=self.db_alias)
