from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.common.response import success_response
from app.models.user_model import User
from app.services.auth_service import get_current_user
from app.schemas.icon_schema import IconCreate, IconUpdate, IconResponse
from app.repositories.icon_repository import icon_repository

router = APIRouter(prefix="/auth/icons", tags=["Icons"])

@router.get("/", response_model=None)
def list_icons(db: Session = Depends(get_db)):
    data = icon_repository.get_all(db)
    return success_response(data=[IconResponse.model_validate(i).model_dump() for i in data]).model_dump()

@router.post("/", response_model=None, status_code=status.HTTP_201_CREATED)
def create_icon(payload: IconCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    data = icon_repository.create(db, payload, current_user.id)
    return success_response(data=IconResponse.model_validate(data).model_dump(), message="Icon created", code=201).model_dump()

@router.get("/{uuid}", response_model=None)
def get_icon(uuid: str, db: Session = Depends(get_db)):
    data = icon_repository.get_by_uuid(db, uuid)
    if not data:
        raise HTTPException(status_code=404, detail="Icon not found")
    return success_response(data=IconResponse.model_validate(data).model_dump()).model_dump()

@router.put("/{uuid}", response_model=None)
def update_icon(uuid: str, payload: IconUpdate, db: Session = Depends(get_db)):
    db_obj = icon_repository.get_by_uuid(db, uuid)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Icon not found")
    data = icon_repository.update(db, db_obj, payload)
    return success_response(data=IconResponse.model_validate(data).model_dump(), message="Icon updated").model_dump()

@router.delete("/{uuid}", response_model=None)
def delete_icon(uuid: str, db: Session = Depends(get_db)):
    db_obj = icon_repository.get_by_uuid(db, uuid)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Icon not found")
    icon_repository.remove(db, db_obj.id)
    return success_response(message="Icon deleted").model_dump()
