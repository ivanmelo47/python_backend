from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.common.dependencies.pagination import PaginationParams, common_pagination
from app.common.response import success_response
from app.db.session import get_db
from app.schemas.product_schema import ProductCreate, ProductRead, ProductUpdate
from app.services import product_service

router = APIRouter(prefix="/products", tags=["products"])


@router.get("/", response_model=None)
def list_products(
    pagination: PaginationParams = Depends(common_pagination),
    db: Session = Depends(get_db),
) -> dict:
    data = product_service.list_products(db, skip=pagination.skip, limit=pagination.limit)
    return success_response(data=data).model_dump()


@router.get("/{product_id}", response_model=None)
def get_product(product_id: int, db: Session = Depends(get_db)) -> dict:
    data = product_service.get_product_or_404(db, product_id)
    return success_response(data=data).model_dump()


@router.post("/", response_model=None, status_code=status.HTTP_201_CREATED)
def create_product(payload: ProductCreate, db: Session = Depends(get_db)) -> dict:
    data = product_service.create_product(db, payload)
    return success_response(data=data, message="Created", code=201).model_dump()


@router.patch("/{product_id}", response_model=None)
def update_product(product_id: int, payload: ProductUpdate, db: Session = Depends(get_db)) -> dict:
    data = product_service.update_product(db, product_id, payload)
    return success_response(data=data).model_dump()


@router.delete("/{product_id}", status_code=status.HTTP_200_OK)
def delete_product(product_id: int, db: Session = Depends(get_db)) -> dict:
    product_service.delete_product(db, product_id)
    return success_response(message="Deleted", code=200).model_dump()
