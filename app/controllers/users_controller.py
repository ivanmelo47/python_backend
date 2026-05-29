from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.common.dependencies.pagination import PaginationParams, common_pagination
from app.common.response import success_response
from app.db.session import get_db
from app.services.auth_service import get_current_user
from app.models.user_model import User
from app.schemas.user_schema import UserCreate, UserRead, UserUpdate
from app.services import user_service

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/", response_model=None)
def list_users(
    pagination: PaginationParams = Depends(common_pagination),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    del current_user
    data = user_service.list_users(db, skip=pagination.skip, limit=pagination.limit)
    return success_response(data=data).model_dump()


@router.get("/{user_id}", response_model=None)
def get_user(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> dict:
    del current_user
    data = user_service.get_user_or_404(db, user_id)
    return success_response(data=data).model_dump()


@router.post("/", response_model=None, status_code=status.HTTP_201_CREATED)
def create_user(payload: UserCreate, db: Session = Depends(get_db)) -> dict:
    data = user_service.create_user(db, payload)
    return success_response(data=data, message="Created", code=201).model_dump()


@router.patch("/{user_id}", response_model=None)
def update_user(
    user_id: int,
    payload: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    data = user_service.update_user(db, user_id, payload, current_user)
    return success_response(data=data).model_dump()


@router.delete("/{user_id}", status_code=status.HTTP_200_OK)
def delete_user(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> dict:
    del current_user
    user_service.delete_user(db, user_id)
    return success_response(message="Deleted", code=200).model_dump()
