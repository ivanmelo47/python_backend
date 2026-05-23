from fastapi import Depends, HTTPException, Request, status, BackgroundTasks
from datetime import datetime, timezone, timedelta
from fastapi.security import OAuth2PasswordBearer
import secrets
from sqlalchemy.orm import Session

from app.common.security.jwt_handler import (
    create_access_token,
    create_refresh_token,
    decode_token,
)
from app.common.security.password import hash_password, verify_password
from app.common.security.token_hash import hash_token, verify_token_hash
from app.common.mail.sender import send_email, get_action_email_template
from app.core.settings import settings
from app.db.session import get_db
from app.repositories import user_session_repository
from app.models.user_model import User
from app.models.password_reset_log_model import PasswordResetLog
from app.repositories import user_repository
from app.schemas.user_schema import (
    AuthPayload,
    AuthTokenData,
    UserCreate,
    UserLogin,
    UserRead,
    UserRegister,
    ForgotPasswordRequest,
    ResetPasswordRequest,
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def register_user(
    db: Session,
    payload: UserRegister,
    background_tasks: BackgroundTasks | None = None,
) -> UserRead:
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

    generated_token = secrets.token_urlsafe(32)

    user = user_repository.create(
        db,
        user_create,
        password_hash=password_hash,
        token=generated_token,
        confirmed=False,
    )

    # Construir URL de confirmación (apuntando al Frontend)
    confirm_url = f"{settings.frontend_url}/confirm?token={generated_token}"

    # Generar contenido HTML y encolar el envío
    email_content = get_action_email_template(
        name=user.full_name,
        title="Confirmación de Cuenta",
        body_text="Gracias por registrarte en nuestra plataforma. Para completar tu registro y activar tu cuenta, por favor confirma tu dirección de correo electrónico haciendo clic en el siguiente botón:",
        button_text="Confirmar mi Cuenta",
        button_url=confirm_url,
        secondary_text="Si no creaste esta cuenta, puedes ignorar este mensaje.",
    )
    
    if background_tasks:
        background_tasks.add_task(
            send_email,
            to_email=user.email,
            subject="Confirma tu cuenta",
            html_content=email_content,
        )
    else:
        # Enviar síncronamente como fallback (ej. en scripts de prueba)
        try:
            send_email(
                to_email=user.email,
                subject="Confirma tu cuenta",
                html_content=email_content,
            )
        except Exception:
            # No detener el registro si falla el correo síncrono (ej. sin internet / mala config)
            pass

    return UserRead.model_validate(user)


def confirm_user(db: Session, token: str) -> UserRead:
    user = user_repository.get_by_token(db, token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired confirmation token",
        )
    if user.confirmed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Account already confirmed",
        )

    user.confirmed = True
    user.is_active = True
    user.token = None  # Consumir el token
    db.commit()
    db.refresh(user)
    return UserRead.model_validate(user)


def login_user(db: Session, payload: UserLogin, request: Request | None = None) -> AuthPayload:
    user = user_repository.get_by_email(db, payload.email)
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
        )

    if not user.confirmed:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Please confirm your email address to activate your account",
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


def request_password_reset(
    db: Session,
    payload: ForgotPasswordRequest,
    background_tasks: BackgroundTasks | None = None,
    request: Request | None = None,
) -> None:
    user = user_repository.get_by_email(db, payload.email)
    if not user:
        # Por seguridad y evitar la enumeración de emails, levantamos el mismo error genérico
        # de "siempre y cuando haya sido confirmada y este activa".
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password reset is only allowed for active and confirmed accounts."
        )

    if not user.confirmed or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password reset is only allowed for active and confirmed accounts."
        )

    # Generar token seguro
    reset_token = secrets.token_urlsafe(32)
    user.token = reset_token
    user.token_generated_at = datetime.now(timezone.utc)

    # Extraer metadatos de auditoría
    ip_address = None
    user_agent = None
    if request:
        ip_address = request.client.host if request.client else None
        user_agent = request.headers.get("user-agent")

    # Registrar el intento en el log de auditoría
    reset_log = PasswordResetLog(
        user_id=user.id,
        token=reset_token,
        ip_address=ip_address,
        user_agent=user_agent,
        status="pending"
    )
    db.add(reset_log)
    db.commit()

    # URL de restablecimiento (apuntando al Frontend)
    reset_url = f"{settings.frontend_url}/reset-password?token={reset_token}"

    email_content = get_action_email_template(
        name=user.full_name,
        title="Restablecer Contraseña",
        body_text="Hemos recibido una solicitud para restablecer la contraseña de tu cuenta. Haz clic en el botón inferior para ingresar tu nueva contraseña. Toma en cuenta que este enlace tiene una validez de 30 minutos:",
        button_text="Restablecer Contraseña",
        button_url=reset_url,
        secondary_text="Este enlace expirará en 30 minutos por razones de seguridad. Si no solicitaste este cambio, puedes ignorar este mensaje de forma segura."
    )

    if background_tasks:
        background_tasks.add_task(
            send_email,
            to_email=user.email,
            subject="Restablece tu contraseña",
            html_content=email_content,
        )
    else:
        try:
            send_email(
                to_email=user.email,
                subject="Restablece tu contraseña",
                html_content=email_content,
            )
        except Exception:
            pass


def reset_password(db: Session, payload: ResetPasswordRequest) -> None:
    user = user_repository.get_by_token(db, payload.token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )

    # Validar si el token ha expirado (más de 30 minutos)
    if not user.token_generated_at:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )

    token_time = user.token_generated_at
    if token_time.tzinfo is None:
        token_time = token_time.replace(tzinfo=timezone.utc)

    time_elapsed = datetime.now(timezone.utc) - token_time
    if time_elapsed > timedelta(minutes=30):
        # Actualizar log a expirado
        log_entry = db.query(PasswordResetLog).filter(PasswordResetLog.token == payload.token).first()
        if log_entry:
            log_entry.status = "expired"
            log_entry.latitude = payload.latitude
            log_entry.longitude = payload.longitude

        # Limpiar token expirado por seguridad
        user.token = None
        user.token_generated_at = None
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )

    if not user.confirmed or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password reset is only allowed for active and confirmed accounts."
        )

    # Actualizar contraseña hasheada
    user.password_hash = hash_password(payload.new_password)
    user.token = None  # Consumir el token
    user.token_generated_at = None

    # Registrar completado en el log de auditoría
    log_entry = db.query(PasswordResetLog).filter(PasswordResetLog.token == payload.token).first()
    if log_entry:
        log_entry.status = "completed"
        log_entry.reset_at = datetime.now(timezone.utc)
        log_entry.latitude = payload.latitude
        log_entry.longitude = payload.longitude

    db.commit()

    # Revocar todas las sesiones del usuario como medida de seguridad corporativa premium
    user_session_repository.revoke_all_user_sessions(db, user.id)
