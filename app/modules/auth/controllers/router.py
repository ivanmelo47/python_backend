from fastapi import APIRouter, Depends, Request, status, BackgroundTasks
from sqlalchemy.orm import Session

from app.common.response import success_response
from app.db.session import get_db
from app.modules.auth.services import auth_service
from app.modules.user_sessions.repositories import user_session_repository
from app.modules.user_sessions.schemas.user_session_schema import UserSessionRead
from app.modules.users.models.user_model import User
from app.modules.users.schemas.user_schema import (
    TokenRefreshRequest,
    UserLogin,
    UserRead,
    UserRegister,
    ForgotPasswordRequest,
    ResetPasswordRequest,
)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=None, status_code=status.HTTP_201_CREATED)
def register(
    payload: UserRegister,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
) -> dict:
    data = auth_service.register_user(db, payload, background_tasks)
    return success_response(
        data=data,
        msg="User registered successfully. Please confirm your email address via the link sent to your inbox.",
        code=201
    ).model_dump()


@router.get("/confirm", response_model=None)
def confirm(token: str, db: Session = Depends(get_db)) -> dict:
    data = auth_service.confirm_user(db, token)
    return success_response(
        data=data,
        msg="Your account has been successfully confirmed and activated!",
        code=200
    ).model_dump()


@router.post("/login", response_model=None)
def login(payload: UserLogin, request: Request, db: Session = Depends(get_db)) -> dict:
    data = auth_service.login_user(db, payload, request)
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


@router.get("/sessions", response_model=None)
def get_sessions(
    current_user: User = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    sessions = user_session_repository.get_sessions_by_user(db, current_user.id)
    data = [UserSessionRead.model_validate(s) for s in sessions]
    return success_response(data=data, msg="Sessions retrieved").model_dump()


@router.delete("/sessions/{session_uuid}", response_model=None)
def revoke_session(
    session_uuid: str,
    _master: User = Depends(auth_service.require_master),
    db: Session = Depends(get_db),
) -> dict:
    session = user_session_repository.revoke_session(db, session_uuid)
    if not session:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Session not found or already revoked")
    return success_response(
        data=UserSessionRead.model_validate(session),
        msg="Session revoked successfully"
    ).model_dump()


@router.post("/forgot-password", response_model=None)
def forgot_password(
    payload: ForgotPasswordRequest,
    background_tasks: BackgroundTasks,
    request: Request,
    db: Session = Depends(get_db),
) -> dict:
    auth_service.request_password_reset(db, payload, background_tasks, request=request)
    return success_response(
        data=None,
        msg="If the email belongs to an active, confirmed account, a password reset link has been sent.",
        code=200
    ).model_dump()


@router.post("/reset-password", response_model=None)
def reset_password(
    payload: ResetPasswordRequest,
    db: Session = Depends(get_db),
) -> dict:
    auth_service.reset_password(db, payload)
    return success_response(
        data=None,
        msg="Your password has been successfully reset. All active sessions have been terminated for security.",
        code=200
    ).model_dump()
