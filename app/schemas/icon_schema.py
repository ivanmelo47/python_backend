from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

class IconBase(BaseModel):
    name: str
    type: str = "svg"
    storage_mode: str = "database"
    file_path: Optional[str] = None
    svg_content: Optional[str] = None
    viewBox: Optional[str] = None
    color_mode: str = "currentColor"
    category: Optional[str] = None
    is_active: bool = True

class IconCreate(IconBase):
    pass

class IconUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    storage_mode: Optional[str] = None
    file_path: Optional[str] = None
    svg_content: Optional[str] = None
    viewBox: Optional[str] = None
    color_mode: Optional[str] = None
    category: Optional[str] = None
    is_active: Optional[bool] = None

class IconResponse(IconBase):
    id: int
    uuid: str
    created_by: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
