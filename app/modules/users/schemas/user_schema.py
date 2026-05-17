from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.modules.roles.schemas.role_schema import RoleRead


class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    is_active: bool = True
    role_id: int = 3


class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=128)


class UserRegister(BaseModel):
    email: EmailStr
    full_name: str
    password: str = Field(min_length=8, max_length=128)


class UserUpdate(BaseModel):
    email: EmailStr | None = None
    full_name: str | None = None
    password: str | None = Field(default=None, min_length=8, max_length=128)
    is_active: bool | None = None
    role_id: int | None = None


class UserRead(UserBase):
    id: int
    uuid: str
    created_at: datetime
    role: RoleRead | None = None

    model_config = ConfigDict(from_attributes=True)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class AuthTokenData(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class AuthPayload(BaseModel):
    user: UserRead
    token: AuthTokenData


class TokenRefreshRequest(BaseModel):
    refresh_token: str
