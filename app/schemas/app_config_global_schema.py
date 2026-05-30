from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel

class AppConfigGlobalBase(BaseModel):
    theme: Optional[str] = "dark"
    color_palette: Optional[str] = "default"
    app_scale: Optional[int] = 100
    items_per_page: Optional[int] = 10
    table_configs: Optional[Dict[str, Any]] = None
    table_view_mode: Optional[str] = "list"

class AppConfigGlobalCreate(AppConfigGlobalBase):
    pass

class AppConfigGlobalUpdate(AppConfigGlobalBase):
    pass

class AppConfigGlobalResponse(AppConfigGlobalBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
