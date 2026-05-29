from pydantic import BaseModel, ConfigDict
from typing import Optional, Any, Dict
from datetime import datetime
from app.schemas.icon_schema import IconResponse

class DynamicRouteBase(BaseModel):
    parent_id: Optional[int] = None
    path: str
    name: str
    component_path: str
    title: str
    description: Optional[str] = None
    icon_id: Optional[int] = None
    role_id: Optional[int] = None
    icon_color_mode: str = "currentColor"
    min_hierarchy: int = 3
    is_active: bool = True
    meta: Optional[Dict[str, Any]] = None

class DynamicRouteCreate(DynamicRouteBase):
    pass

class DynamicRouteUpdate(BaseModel):
    parent_id: Optional[int] = None
    path: Optional[str] = None
    name: Optional[str] = None
    component_path: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    icon_id: Optional[int] = None
    role_id: Optional[int] = None
    icon_color_mode: Optional[str] = None
    min_hierarchy: Optional[int] = None
    is_active: Optional[bool] = None
    meta: Optional[Dict[str, Any]] = None

class DynamicRouteResponse(DynamicRouteBase):
    id: int
    uuid: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    # Optional nested relations
    icon: Optional[IconResponse] = None
    
    model_config = ConfigDict(from_attributes=True)
