from enum import Enum


class StatusCode(Enum):
    SUCCESS = 200
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    CONFLICT = 409
    TOO_MANY_REQUESTS = 429   # ✅ add this
    INTERNAL_SERVER_ERROR = 500
# MessageResult.py
# MessageResult.py
class MessageResult:
    def __init__(self, message: str, code):
        self.message = message
        if isinstance(code, int):
            self.code = StatusCode(code)  # Convert int to StatusCode
        else:
            self.code = code  # already StatusCode

    @property
    def succeeded(self) -> bool:
        return self.code == StatusCode.SUCCESS

    @property
    def status_code(self) -> int:
        return self.code.value  # Safe: always a StatusCode now

    def __repr__(self):
        return f"<MessageResult message='{self.message}' code={self.code}>"
