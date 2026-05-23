from fastapi import APIRouter

from app.controllers.auth_controller import router as auth_router
from app.controllers.products_controller import router as products_router
from app.controllers.users_controller import router as users_router

api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(users_router)
api_router.include_router(products_router)
