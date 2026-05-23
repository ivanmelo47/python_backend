from datetime import datetime

from pydantic import BaseModel


class UserSessionRead(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    uuid: str
    user_id: int
    logged_in_at: datetime
    last_activity_at: datetime | None
    logged_out_at: datetime | None
    ip_address: str | None
    user_agent: str | None
    latitude: float | None
    longitude: float | None

    @property
    def is_active(self) -> bool:
        return self.logged_out_at is None
