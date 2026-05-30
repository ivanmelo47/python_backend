from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict

T = TypeVar("T")


class StandardResponse(BaseModel, Generic[T]):
    success: bool
    status: str
    code: int
    message: str
    data: T | None = None

    model_config = ConfigDict(from_attributes=True)


def success_response(data: T | None = None, *, message: str = "OK", code: int = 200) -> StandardResponse[T]:
    return StandardResponse(success=True, status="success", code=code, message=message, data=data)


def error_response(*, message: str, code: int) -> StandardResponse[None]:
    return StandardResponse(success=False, status="error", code=code, message=message, data=None)
