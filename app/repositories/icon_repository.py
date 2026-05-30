from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.icon_model import Icon

class IconRepository:
    def get(self, db: Session, id: int) -> Optional[Icon]:
        return db.query(Icon).filter(Icon.id == id).first()

    def get_by_uuid(self, db: Session, uuid: str) -> Optional[Icon]:
        return db.query(Icon).filter(Icon.uuid == uuid).first()

    def get_all(
        self, db: Session, 
        skip: int = 0, limit: int = 100, 
        search: Optional[str] = None, 
        category: Optional[str] = None,
        show_inactive: bool = False
    ) -> List[Icon]:
        query = db.query(Icon)
        if not show_inactive:
            query = query.filter(Icon.is_active == True)
            
        if search:
            query = query.filter((Icon.name.ilike(f"%{search}%")) | (Icon.category.ilike(f"%{search}%")))
            
        if category:
            query = query.filter(Icon.category == category)
            
        return query.order_by(Icon.name.asc()).offset(skip).limit(limit).all()

    def count_all(
        self, db: Session,
        search: Optional[str] = None, 
        category: Optional[str] = None,
        show_inactive: bool = False
    ) -> int:
        query = db.query(Icon)
        if not show_inactive:
            query = query.filter(Icon.is_active == True)
            
        if search:
            query = query.filter((Icon.name.ilike(f"%{search}%")) | (Icon.category.ilike(f"%{search}%")))
            
        if category:
            query = query.filter(Icon.category == category)
            
        return query.count()

    def create(self, db: Session, obj_in: dict, user_id: int) -> Icon:
        db_obj = Icon(**obj_in, created_by=user_id)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(self, db: Session, db_obj: Icon, obj_in: dict) -> Icon:
        for field, value in obj_in.items():
            setattr(db_obj, field, value)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove(self, db: Session, id: int) -> Icon:
        obj = db.query(Icon).get(id)
        if obj:
            db.delete(obj)
            db.commit()
        return obj

    def toggle_status(self, db: Session, id: int) -> Optional[Icon]:
        icon = self.get(db, id)
        if icon:
            icon.is_active = not icon.is_active
            db.commit()
            db.refresh(icon)
        return icon

icon_repository = IconRepository()
