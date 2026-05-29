from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.common.response import success_response
from app.models.user_model import User
from app.services.auth_service import get_current_user
from app.schemas.dynamic_route_schema import DynamicRouteCreate, DynamicRouteUpdate, DynamicRouteResponse
from app.repositories.dynamic_route_repository import dynamic_route_repository

router = APIRouter(prefix="/auth", tags=["Dynamic Routes"])

@router.get("/dynamic-routes", response_model=None)
def list_all_routes(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    data = dynamic_route_repository.get_all(db)
    return success_response(data=[DynamicRouteResponse.model_validate(r).model_dump() for r in data]).model_dump()

@router.get("/active-dynamic-routes", response_model=None)
def list_active_routes(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    data = dynamic_route_repository.get_active_routes(db)
    return success_response(data=[DynamicRouteResponse.model_validate(r).model_dump() for r in data]).model_dump()

@router.post("/dynamic-routes", response_model=None, status_code=status.HTTP_201_CREATED)
def create_route(payload: DynamicRouteCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    data = dynamic_route_repository.create(db, payload)
    return success_response(data=DynamicRouteResponse.model_validate(data).model_dump(), message="Ruta creada", code=201).model_dump()

@router.get("/dynamic-routes/{uuid}", response_model=None)
def get_route(uuid: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    data = dynamic_route_repository.get_by_uuid(db, uuid)
    if not data:
        raise HTTPException(status_code=404, detail="Route not found")
    return success_response(data=DynamicRouteResponse.model_validate(data).model_dump()).model_dump()

@router.put("/dynamic-routes/{uuid}", response_model=None)
def update_route(uuid: str, payload: DynamicRouteUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_obj = dynamic_route_repository.get_by_uuid(db, uuid)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Route not found")
    data = dynamic_route_repository.update(db, db_obj, payload)
    return success_response(data=DynamicRouteResponse.model_validate(data).model_dump(), message="Ruta actualizada").model_dump()

@router.delete("/dynamic-routes/{uuid}", response_model=None)
def delete_route(uuid: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_obj = dynamic_route_repository.get_by_uuid(db, uuid)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Route not found")
    dynamic_route_repository.remove(db, db_obj.id)
    return success_response(message="Ruta eliminada").model_dump()

@router.patch("/dynamic-routes/{uuid}/status", response_model=None)
def toggle_route_status(uuid: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_obj = dynamic_route_repository.get_by_uuid(db, uuid)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Route not found")
    new_status = dynamic_route_repository.toggle_status(db, db_obj)
    return success_response(message="Estado actualizado", data={"is_active": new_status}).model_dump()
