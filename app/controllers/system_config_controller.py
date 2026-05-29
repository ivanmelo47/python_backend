from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.common.response import success_response
from app.schemas.system_config_schema import MaintenanceResponse, VisualSettingsResponse
from app.repositories.system_config_repository import system_config_repository

router = APIRouter(prefix="/auth/system-config", tags=["System Config"])

@router.get("/maintenance", response_model=None)
def get_maintenance_mode(db: Session = Depends(get_db)):
    mode = system_config_repository.get_value(db, 'maintenance_mode', False)
    message = system_config_repository.get_value(db, 'maintenance_message', 'Estamos realizando mejoras en la plataforma. Por favor, intenta ingresar más tarde.')
    geo = system_config_repository.get_value(db, 'login_require_geolocation', False)
    
    data = MaintenanceResponse(
        maintenance_mode=mode,
        maintenance_message=message,
        require_geolocation=geo
    ).model_dump()
    
    return success_response(data=data, message="Maintenance config").model_dump()

@router.get("/visual", response_model=None)
def get_visual_settings(db: Session = Depends(get_db)):
    desktop = system_config_repository.get_value(db, 'visual_footer_desktop', True)
    mobile = system_config_repository.get_value(db, 'visual_footer_mobile', True)
    palettes = system_config_repository.get_value(db, 'visual_color_palettes', [])
    
    data = VisualSettingsResponse(
        visual_footer_desktop=desktop,
        visual_footer_mobile=mobile,
        visual_color_palettes=palettes
    ).model_dump()
    
    return success_response(data=data, message="Visual config").model_dump()
