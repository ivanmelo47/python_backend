from fastapi import APIRouter

from app.modules.auth.controllers.router import router as auth_router
from app.modules.products.controllers.router import router as products_router
from app.modules.users.controllers.router import router as users_router

api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(users_router)
api_router.include_router(products_router)
