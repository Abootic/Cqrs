# cqrsex/Application/Mapping/UsersMapper.py
from __future__ import annotations
from django.contrib.auth import get_user_model
from cqrsex.Application.CQRS.Users.Commands.Create.Request import CreateUser
from cqrsex.Domain.models.User import User


def to_model_from_create(cmd: CreateUser) -> User:
    """حوّل CreateUser command إلى User model"""
    u = User(
        username=(cmd.username or "").strip(),
        email=(cmd.email or "").strip(),
        user_type=cmd.user_type,
        is_active=True,
    )
    u.set_password((cmd.password or "").strip())
    return u


def to_command_from_model(u: User) -> CreateUser:
    """حوّل User model إلى CreateUser command (عكس العملية)"""
    return CreateUser(
        username=u.username,
        password="",  # ما نرجع الباسوورد، يفضل دايمًا يترك فاضي
        email=u.email,
        user_type=getattr(u, "user_type", "CUSTOMER"),
        allow_anonymous=False,
    )


def to_detail(u: User) -> dict:
    """حوّل User model إلى dict للـ API"""
    return {
        "id": u.id,
        "username": u.username,
        "email": u.email,
        "first_name": u.first_name,
        "last_name": u.last_name,
        "user_type": getattr(u, "user_type", None),
        "is_active": u.is_active,
        "date_joined": u.date_joined.isoformat() if u.date_joined else None,
    }
