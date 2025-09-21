# cqrsex/WebAPI/api_exception_handler.py
from rest_framework.views import exception_handler as drf_default
from rest_framework.response import Response
from cqrsex.Application.Common.exceptions import AppException

def api_exception_handler(exc, context):
    if isinstance(exc, AppException):
        res = exc.to_result().to_dict()
        return Response(res, status=exc.status_code.value)

    # Else let DRF’s default convert (still returns JSON)
    return drf_default(exc, context)
