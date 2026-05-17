from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.modules.user_sessions.models.user_session_model import UserSession


def create_session(
    db: Session,
    *,
    user_id: int,
    refresh_token_hash: str | None = None,
    ip_address: str | None = None,
    user_agent: str | None = None,
    latitude: float | None = None,
    longitude: float | None = None,
) -> UserSession:
    session = UserSession(
        user_id=user_id,
        refresh_token_hash=refresh_token_hash,
        ip_address=ip_address,
        user_agent=user_agent,
        latitude=latitude,
        longitude=longitude,
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def update_last_activity(db: Session, session_id: int, new_refresh_token_hash: str | None = None) -> None:
    session = db.get(UserSession, session_id)
    if session and session.refresh_token_hash is not None:  # No actualizar si fue revocada
        session.last_activity_at = datetime.now(timezone.utc)
        if new_refresh_token_hash:
            session.refresh_token_hash = new_refresh_token_hash
        db.commit()


def get_by_id(db: Session, session_id: int) -> UserSession | None:
    return db.get(UserSession, session_id)


def get_by_uuid(db: Session, session_uuid: str) -> UserSession | None:
    return db.query(UserSession).filter(UserSession.uuid == session_uuid).first()


def revoke_session(db: Session, session_uuid: str) -> UserSession | None:
    """Revoca una sesión: invalida el refresh token y marca la fecha de cierre."""
    session = get_by_uuid(db, session_uuid)
    if session and session.refresh_token_hash is not None:
        session.refresh_token_hash = None
        session.logged_out_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(session)
    return session


def get_sessions_by_user(db: Session, user_id: int) -> list[UserSession]:
    return (
        db.query(UserSession)
        .filter(UserSession.user_id == user_id)
        .order_by(UserSession.logged_in_at.desc())
        .all()
    )
