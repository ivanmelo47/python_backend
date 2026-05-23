from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.product_model import Product
from app.repositories import product_repository
from app.schemas.product_schema import ProductCreate, ProductUpdate


def list_products(db: Session, *, skip: int = 0, limit: int = 100) -> list[Product]:
    return product_repository.list_all(db, skip=skip, limit=limit)


def get_product_or_404(db: Session, product_id: int) -> Product:
    product = product_repository.get_by_id(db, product_id)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return product


def create_product(db: Session, payload: ProductCreate) -> Product:
    return product_repository.create(db, payload)


def update_product(db: Session, product_id: int, payload: ProductUpdate) -> Product:
    product = get_product_or_404(db, product_id)
    return product_repository.update(db, product, payload)


def delete_product(db: Session, product_id: int) -> None:
    product = get_product_or_404(db, product_id)
    product_repository.delete(db, product)
