from typing import Optional
from sqlalchemy.orm import Session
from app.models.app_config_global_model import AppConfigGlobal
from app.schemas.app_config_global_schema import AppConfigGlobalUpdate

class AppConfigGlobalRepository:
    def get_by_user_id(self, db: Session, user_id: int) -> Optional[AppConfigGlobal]:
        return db.query(AppConfigGlobal).filter(AppConfigGlobal.user_id == user_id).first()

    def update_or_create(self, db: Session, user_id: int, obj_in: AppConfigGlobalUpdate) -> AppConfigGlobal:
        db_obj = self.get_by_user_id(db, user_id)
        if not db_obj:
            db_obj = AppConfigGlobal(user_id=user_id)
            db.add(db_obj)
        
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
            
        db.commit()
        db.refresh(db_obj)
        return db_obj

app_config_global_repository = AppConfigGlobalRepository()
