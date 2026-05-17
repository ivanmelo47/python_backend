from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict

T = TypeVar("T")


class StandardResponse(BaseModel, Generic[T]):
    status: str
    code: int
    msg: str
    data: T | None = None

    model_config = ConfigDict(from_attributes=True)


def success_response(data: T | None = None, *, msg: str = "OK", code: int = 200) -> StandardResponse[T]:
    return StandardResponse(status="success", code=code, msg=msg, data=data)


def error_response(*, msg: str, code: int) -> StandardResponse[None]:
    return StandardResponse(status="error", code=code, msg=msg, data=None)
