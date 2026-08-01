from dataclasses import dataclass
from typing import Any


@dataclass
class ServiceResult:

    success: bool

    message: str = ""

    data: Any = None

    errors: list | None = None

    @classmethod
    def ok(cls, data=None, message=""):

        return cls(
            success=True,
            data=data,
            message=message,
            errors=[],
        )

    @classmethod
    def fail(cls, message, errors=None):

        return cls(
            success=False,
            message=message,
            data=None,
            errors=errors or [],
        )
