from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.common.response import error_response, success_response
from app.core.settings import settings
# Import models to ensure they are registered with SQLAlchemy Base
from app.models import role_model  # noqa: F401
from app.models import user_model  # noqa: F401
from app.models import product_model  # noqa: F401
from app.models import user_session_model  # noqa: F401
from app.models import password_reset_log_model  # noqa: F401
from app.models import system_config_model  # noqa: F401


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug,
)

# Allow CORS from frontend development server and any other origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://192.168.1.149:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_: Request, exc: RequestValidationError) -> JSONResponse:
    payload = error_response(message="Validation error", code=422)
    payload.data = exc.errors()
    return JSONResponse(status_code=422, content=payload.model_dump())


@app.exception_handler(HTTPException)
async def http_exception_handler(_: Request, exc: HTTPException) -> JSONResponse:
    payload = error_response(message=str(exc.detail), code=exc.status_code)
    return JSONResponse(status_code=exc.status_code, content=payload.model_dump())


@app.exception_handler(Exception)
async def generic_exception_handler(_: Request, exc: Exception) -> JSONResponse:
    payload = error_response(message=str(exc), code=500)
    return JSONResponse(status_code=500, content=payload.model_dump())

from fastapi.staticfiles import StaticFiles
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
PUBLIC_DIR = BASE_DIR / "public"
os.makedirs(PUBLIC_DIR / "icons" / "svg", exist_ok=True)
app.mount("/api/v1/public", StaticFiles(directory=str(PUBLIC_DIR)), name="public")

app.include_router(api_router, prefix="/api/v1")


@app.get("/")
def healthcheck() -> dict[str, object]:
    return success_response(data={"service": settings.app_name}).model_dump()
