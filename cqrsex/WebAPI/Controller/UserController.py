from __future__ import annotations
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from cqrsex.Bootstrap.container import get_mediator
from cqrsex.Application.CQRS.Users.Queries.List.Request import ListUsers
from cqrsex.Application.CQRS.Users.Queries.Get.Request import GetUser
from cqrsex.Application.CQRS.Users.Commands.Create.Request import CreateUser
from cqrsex.Application.CQRS.Users.Commands.Update.Request import UpdateUser
from cqrsex.Application.CQRS.Users.Commands.Delete.Request import DeleteUser

class UserViewSet(ViewSet):
    # no auth backends => no CSRF/session hurdle; open API
    authentication_classes: list = []
    permission_classes = [AllowAny]

    # helpers (fixed to include self)
    def _is_admin(self, request) -> bool:
        u = getattr(request, "user", None)
        return bool(getattr(u, "is_authenticated", False) and getattr(u, "user_type", "") == "ADMIN")

    def _user_id(self, request) -> int:
        try:
            u = getattr(request, "user", None)
            return int(getattr(u, "id", 0) or 0)
        except Exception:
            return 0

    def list(self, request):
        page = int(request.query_params.get("page", 1))
        page_size = int(request.query_params.get("page_size", 20))
        q = request.query_params.get("q")
        user_type = request.query_params.get("user_type")
        res = get_mediator().send(ListUsers(page=page, page_size=page_size, q=q, user_type=user_type))
        return Response(res.to_dict(), status=res.status.status_code)

    def retrieve(self, request, pk=None):
        res = get_mediator().send(GetUser(id=int(pk)))
        return Response(res.to_dict(), status=res.status.status_code)

    def create(self, request):
        p = request.data or {}
        requested_role = (p.get("user_type") or "CUSTOMER").upper()
        if not self._is_admin(request):  # prevent role escalation on public signup
            requested_role = "CUSTOMER"

        res = get_mediator().send(CreateUser(
            username=(p.get("username") or "").strip(),
            password=p.get("password") or "",
            email=(p.get("email") or "").strip(),
            user_type=requested_role,
            allow_anonymous=True,   # <<< key line
        ))
        return Response(res.to_dict(), status=res.status.status_code)

    def update(self, request, pk=None):
        p = request.data or {}
        res = get_mediator().send(UpdateUser(
            id=int(pk),
            email=p.get("email"),
            first_name=p.get("first_name"),
            last_name=p.get("last_name"),
            password=p.get("password"),
            user_type=p.get("user_type"),
            is_active=p.get("is_active"),
            acting_user_id=self._user_id(request),
            acting_is_admin=self._is_admin(request),
        ))
        return Response(res.to_dict(), status=res.status.status_code)

    def destroy(self, request, pk=None):
        res = get_mediator().send(DeleteUser(
            id=int(pk),
            acting_user_id=self._user_id(request),
            acting_is_admin=self._is_admin(request),
        ))
        return Response(res.to_dict(), status=res.status.status_code)
