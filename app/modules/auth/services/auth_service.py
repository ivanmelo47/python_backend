from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.common.security.jwt_handler import (
    create_access_token,
    create_refresh_token,
    decode_token,
)
from app.common.security.password import hash_password, verify_password
from app.db.session import get_db
from app.modules.users.models.user_model import User
from app.modules.users.repositories import user_repository
from app.modules.users.schemas.user_schema import (
    AuthPayload,
    AuthTokenData,
    UserCreate,
    UserLogin,
    UserRead,
    UserRegister,
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def register_user(db: Session, payload: UserRegister) -> UserRead:
    existing = user_repository.get_by_email(db, payload.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Email already registered"
        )
    
    password_hash = hash_password(payload.password)
    
    user_create = UserCreate(
        email=payload.email,
        full_name=payload.full_name,
        password=payload.password,
        is_active=False,
        role_id=3
    )
    
    user = user_repository.create(db, user_create, password_hash=password_hash)
    return UserRead.model_validate(user)


def login_user(db: Session, payload: UserLogin) -> AuthPayload:
    user = user_repository.get_by_email(db, payload.email)
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user"
        )

    access_token, expires_in = create_access_token(subject=str(user.id), email=user.email)
    refresh_token, _ = create_refresh_token(subject=str(user.id), email=user.email)

    return AuthPayload(
        user=UserRead.model_validate(user),
        token=AuthTokenData(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=expires_in,
        ),
    )


def refresh_token_data(db: Session, refresh_token: str) -> AuthTokenData:
    unauthorized = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired refresh token"
    )

    try:
        payload = decode_token(refresh_token)
        if payload.get("type") != "refresh":
            raise unauthorized

        sub = payload.get("sub")
        email = payload.get("email")
        if not sub or not email:
            raise unauthorized

        user_id = int(sub)
    except Exception as exc:  # noqa: BLE001
        raise unauthorized from exc

    user = user_repository.get_by_id(db, user_id)
    if not user or not user.is_active:
        raise unauthorized

    access_token, expires_in = create_access_token(subject=str(user.id), email=user.email)
    # We could also rotate the refresh token here if desired (sliding session)
    new_refresh_token, _ = create_refresh_token(subject=str(user.id), email=user.email)

    return AuthTokenData(
        access_token=access_token,
        refresh_token=new_refresh_token,
        expires_in=expires_in,
    )


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    unauthorized = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")

    try:
        payload = decode_token(token)
        sub = payload.get("sub")
        if not sub:
            raise unauthorized
        user_id = int(sub)
    except Exception as exc:  # noqa: BLE001
        raise unauthorized from exc

    user = user_repository.get_by_id(db, user_id)
    if not user:
        raise unauthorized

    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user")

    return user
