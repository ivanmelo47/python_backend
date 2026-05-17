from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.users.models.user_model import User
from app.modules.users.schemas.user_schema import UserCreate, UserUpdate


def get_by_id(db: Session, user_id: int) -> User | None:
    return db.get(User, user_id)


def get_by_email(db: Session, email: str) -> User | None:
    stmt = select(User).where(User.email == email)
    return db.scalars(stmt).first()


def list_all(db: Session, *, skip: int = 0, limit: int = 100) -> list[User]:
    stmt = select(User).offset(skip).limit(limit)
    return list(db.scalars(stmt).all())


def create(db: Session, payload: UserCreate, *, password_hash: str) -> User:
    user = User(**payload.model_dump(exclude={"password"}), password_hash=password_hash)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def update(db: Session, user: User, payload: UserUpdate) -> User:
    for key, value in payload.model_dump(exclude_unset=True, exclude={"password"}).items():
        setattr(user, key, value)
    db.commit()
    db.refresh(user)
    return user


def delete(db: Session, user: User) -> None:
    db.delete(user)
    db.commit()
