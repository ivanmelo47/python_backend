from fastapi import APIRouter

from app.controllers.auth_controller import router as auth_router
from app.controllers.products_controller import router as products_router
from app.controllers.users_controller import router as users_router
from app.controllers.system_config_controller import router as system_config_router
from app.controllers.icon_controller import router as icon_router
from app.controllers.dynamic_route_controller import router as dynamic_route_router
from app.controllers.roles_controller import router as roles_router

api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(users_router)
api_router.include_router(products_router)
api_router.include_router(system_config_router)
api_router.include_router(icon_router)
api_router.include_router(dynamic_route_router)
api_router.include_router(roles_router)
