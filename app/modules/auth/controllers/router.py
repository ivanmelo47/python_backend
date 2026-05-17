from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.common.response import success_response
from app.db.session import get_db
from app.modules.auth.services import auth_service
from app.modules.users.schemas.user_schema import (
    TokenRefreshRequest,
    UserLogin,
    UserRead,
)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=None)
def login(payload: UserLogin, db: Session = Depends(get_db)) -> dict:
    data = auth_service.login_user(db, payload)
    return success_response(data=data, msg="Login successful", code=200).model_dump()


@router.post("/refresh", response_model=None)
def refresh(payload: TokenRefreshRequest, db: Session = Depends(get_db)) -> dict:
    data = auth_service.refresh_token_data(db, payload.refresh_token)
    return success_response(
        data=data, msg="Token refreshed successfuly", code=200
    ).model_dump()


@router.get("/me", response_model=None)
def me(current_user: UserRead = Depends(auth_service.get_current_user)) -> dict:
    return success_response(data=UserRead.model_validate(current_user)).model_dump()
