# cqrsex/WebAPI/middleware.py
import contextvars

_current_request = contextvars.ContextVar("current_request", default=None)

def get_current_user():
    req = _current_request.get()
    return getattr(req, "user", None) if req else None

class CurrentRequestMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        token = _current_request.set(request)
        try:
            return self.get_response(request)
        finally:
            _current_request.reset(token)
