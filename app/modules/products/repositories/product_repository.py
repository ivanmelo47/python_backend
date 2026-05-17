from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.products.models.product_model import Product
from app.modules.products.schemas.product_schema import ProductCreate, ProductUpdate


def get_by_id(db: Session, product_id: int) -> Product | None:
    return db.get(Product, product_id)


def list_all(db: Session, *, skip: int = 0, limit: int = 100) -> list[Product]:
    stmt = select(Product).offset(skip).limit(limit)
    return list(db.scalars(stmt).all())


def create(db: Session, payload: ProductCreate) -> Product:
    product = Product(**payload.model_dump())
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


def update(db: Session, product: Product, payload: ProductUpdate) -> Product:
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(product, key, value)
    db.commit()
    db.refresh(product)
    return product


def delete(db: Session, product: Product) -> None:
    db.delete(product)
    db.commit()
