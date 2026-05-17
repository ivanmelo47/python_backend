from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.common.security.jwt_handler import (
    create_access_token,
    create_refresh_token,
    decode_token,
)
from app.common.security.password import hash_password, verify_password
from app.common.security.token_hash import hash_token, verify_token_hash
from app.db.session import get_db
from app.modules.user_sessions.repositories import user_session_repository
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


def login_user(db: Session, payload: UserLogin, request: Request | None = None) -> AuthPayload:
    user = user_repository.get_by_email(db, payload.email)
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user"
        )

    # Capturar datos del cliente
    ip_address = None
    user_agent = None
    if request:
        forwarded_for = request.headers.get("x-forwarded-for")
        ip_address = forwarded_for.split(",")[0].strip() if forwarded_for else (
            request.client.host if request.client else None
        )
        user_agent = request.headers.get("user-agent")

    # Generar tokens primero para poder hashear el refresh
    access_token, expires_in = create_access_token(subject=str(user.id), email=user.email)
    refresh_token, _ = create_refresh_token(subject=str(user.id), email=user.email)

    # Crear sesión almacenando el hash del refresh token
    session = user_session_repository.create_session(
        db,
        user_id=user.id,
        refresh_token_hash=hash_token(refresh_token),
        ip_address=ip_address,
        user_agent=user_agent,
    )

    # Regenerar refresh token incluyendo el session_id en el payload
    refresh_token, _ = create_refresh_token(
        subject=str(user.id), email=user.email, session_id=session.id
    )
    # Actualizar el hash con el token que incluye el session_id
    session.refresh_token_hash = hash_token(refresh_token)
    db.commit()

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
        session_id: int | None = payload.get("session_id")
    except Exception as exc:  # noqa: BLE001
        raise unauthorized from exc

    user = user_repository.get_by_id(db, user_id)
    if not user or not user.is_active:
        raise unauthorized

    # Validar hash del refresh token contra la sesión registrada
    if session_id is not None:
        db_session = user_session_repository.get_by_id(db, session_id)
        if not db_session or db_session.refresh_token_hash is None:
            # Sesión revocada o no encontrada
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Session has been revoked"
            )
        if not verify_token_hash(refresh_token, db_session.refresh_token_hash):
            raise unauthorized

    # Generar nuevos tokens (rotación)
    access_token, expires_in = create_access_token(subject=str(user.id), email=user.email)
    new_refresh_token, _ = create_refresh_token(
        subject=str(user.id), email=user.email, session_id=session_id
    )

    # Actualizar last_activity_at y rotar el hash
    if session_id is not None:
        user_session_repository.update_last_activity(
            db, session_id, new_refresh_token_hash=hash_token(new_refresh_token)
        )

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


def require_master(current_user: User = Depends(get_current_user)) -> User:
    """Dependency que exige que el usuario autenticado sea Master (role level 1)."""
    if not current_user.role or current_user.role.level != 1:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only Master users can perform this action"
        )
    return current_user
