from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.requests import Request
from fastapi.responses import JSONResponse

from app.api.router import api_router
from app.common.response import error_response, success_response
from app.core.settings import settings
# Import models to ensure they are registered with SQLAlchemy Base
from app.modules.roles.models import role_model  # noqa: F401
from app.modules.users.models import user_model  # noqa: F401
from app.modules.products.models import product_model  # noqa: F401
from app.modules.user_sessions.models import user_session_model  # noqa: F401
from app.modules.users.models import password_reset_log_model  # noqa: F401


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug,
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_: Request, exc: RequestValidationError) -> JSONResponse:
    payload = error_response(msg="Validation error", code=422)
    payload.data = exc.errors()
    return JSONResponse(status_code=422, content=payload.model_dump())


@app.exception_handler(HTTPException)
async def http_exception_handler(_: Request, exc: HTTPException) -> JSONResponse:
    payload = error_response(msg=str(exc.detail), code=exc.status_code)
    return JSONResponse(status_code=exc.status_code, content=payload.model_dump())


@app.exception_handler(Exception)
async def generic_exception_handler(_: Request, exc: Exception) -> JSONResponse:
    payload = error_response(msg=str(exc), code=500)
    return JSONResponse(status_code=500, content=payload.model_dump())

app.include_router(api_router, prefix="/api/v1")


@app.get("/")
def healthcheck() -> dict[str, object]:
    return success_response(data={"service": settings.app_name}).model_dump()
