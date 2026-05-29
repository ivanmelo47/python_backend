from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.icon_model import Icon
from app.schemas.icon_schema import IconCreate, IconUpdate

class IconRepository:
    def get(self, db: Session, id: int) -> Optional[Icon]:
        return db.query(Icon).filter(Icon.id == id).first()

    def get_by_uuid(self, db: Session, uuid: str) -> Optional[Icon]:
        return db.query(Icon).filter(Icon.uuid == uuid).first()

    def get_all(self, db: Session) -> List[Icon]:
        return db.query(Icon).all()

    def create(self, db: Session, obj_in: IconCreate, user_id: int) -> Icon:
        db_obj = Icon(
            name=obj_in.name,
            type=obj_in.type,
            file_path=obj_in.file_path,
            svg_content=obj_in.svg_content,
            viewBox=obj_in.viewBox,
            color_mode=obj_in.color_mode,
            category=obj_in.category,
            created_by=user_id
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(self, db: Session, db_obj: Icon, obj_in: IconUpdate) -> Icon:
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove(self, db: Session, id: int) -> Icon:
        obj = db.query(Icon).get(id)
        db.delete(obj)
        db.commit()
        return obj

icon_repository = IconRepository()
