from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.common.security.password import hash_password
from app.modules.users.models.user_model import User
from app.modules.users.repositories import user_repository
from app.modules.users.schemas.user_schema import UserCreate, UserUpdate


def list_users(db: Session, *, skip: int = 0, limit: int = 100) -> list[User]:
    return user_repository.list_all(db, skip=skip, limit=limit)


def get_user_or_404(db: Session, user_id: int) -> User:
    user = user_repository.get_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


def create_user(db: Session, payload: UserCreate) -> User:
    existing = user_repository.get_by_email(db, payload.email)
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already exists")
    password_hash = hash_password(payload.password)
    return user_repository.create(db, payload, password_hash=password_hash)


def update_user(db: Session, user_id: int, payload: UserUpdate, current_user: User) -> User:
    user = get_user_or_404(db, user_id)

    if current_user.id != user.id:
        if current_user.role.level >= user.role.level:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions to edit a user with the same or higher role level",
            )

    if payload.email and payload.email != user.email:
        existing = user_repository.get_by_email(db, payload.email)
        if existing:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already exists")

    if payload.password:
        user.password_hash = hash_password(payload.password)

    return user_repository.update(db, user, payload)


def delete_user(db: Session, user_id: int) -> None:
    user = get_user_or_404(db, user_id)
    user_repository.delete(db, user)
