# In result_t.py (contains the base ResultT class)
# developed by aboud alsurmin
# email-> sarmi2077@gmail.com
#whatsapp ->0542386454
#
from typing import Any, Dict
from abc import ABC, abstractmethod

from cqrsex.Application.Common.MessageResult import MessageResult

class ResultT(ABC):
    """Base ResultT class that represents a result with status and data."""
    def __init__(self, status: MessageResult, data: Any = None):
        self.status = status
        self.data = data

    @classmethod
    @abstractmethod
    def success(cls, data: Any, message: str = "Success") :
        """Method to handle success result creation."""
        pass

    @classmethod
    @abstractmethod
    def fail(cls, message: str, code: int) :
        """Method to handle failure result creation."""
        pass

    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """Method to convert the result into a dictionary."""
        pass
