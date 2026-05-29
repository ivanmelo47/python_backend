from pydantic import BaseModel
from typing import Any, Dict, Optional

class MaintenanceResponse(BaseModel):
    maintenance_mode: bool = False
    maintenance_message: str = "Estamos realizando mejoras en la plataforma. Por favor, intenta ingresar más tarde."
    require_geolocation: bool = False

class VisualSettingsResponse(BaseModel):
    visual_footer_desktop: bool = True
    visual_footer_mobile: bool = True
    visual_color_palettes: Any = []
