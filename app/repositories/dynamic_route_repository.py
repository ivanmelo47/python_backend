from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from app.models.dynamic_route_model import DynamicRoute
from app.schemas.dynamic_route_schema import DynamicRouteCreate, DynamicRouteUpdate

class DynamicRouteRepository:
    def get(self, db: Session, id: int) -> Optional[DynamicRoute]:
        return db.query(DynamicRoute).filter(DynamicRoute.id == id).first()

    def get_by_uuid(self, db: Session, uuid: str) -> Optional[DynamicRoute]:
        return db.query(DynamicRoute).options(joinedload(DynamicRoute.icon)).filter(DynamicRoute.uuid == uuid).first()

    def get_all(self, db: Session) -> List[DynamicRoute]:
        return db.query(DynamicRoute).options(joinedload(DynamicRoute.icon)).all()

    def get_active_routes(self, db: Session) -> List[DynamicRoute]:
        active_routes = db.query(DynamicRoute).options(
            joinedload(DynamicRoute.icon)
        ).filter(DynamicRoute.is_active == True).all()

        routes_by_id = {route.id: route for route in active_routes}

        def is_route_visible(route):
            if route.parent_id is None:
                return True
            parent = routes_by_id.get(route.parent_id)
            if not parent:
                return False
            return is_route_visible(parent)

        visible_routes = [route for route in active_routes if is_route_visible(route)]
        return visible_routes

    def create(self, db: Session, obj_in: DynamicRouteCreate) -> DynamicRoute:
        db_obj = DynamicRoute(**obj_in.model_dump())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(self, db: Session, db_obj: DynamicRoute, obj_in: DynamicRouteUpdate) -> DynamicRoute:
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)

        if "is_active" in update_data and update_data["is_active"] is False:
            self.deactivate_descendants(db, db_obj.id)

        return db_obj

    def remove(self, db: Session, id: int) -> DynamicRoute:
        obj = db.query(DynamicRoute).get(id)
        db.delete(obj)
        db.commit()
        return obj

    def toggle_status(self, db: Session, db_obj: DynamicRoute) -> bool:
        new_status = not db_obj.is_active
        db_obj.is_active = new_status
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)

        if new_status is False:
            self.deactivate_descendants(db, db_obj.id)
            
        return new_status

    def deactivate_descendants(self, db: Session, parent_id: int):
        parent_ids = [parent_id]
        while parent_ids:
            children_ids = [
                r.id for r in db.query(DynamicRoute.id).filter(DynamicRoute.parent_id.in_(parent_ids)).all()
            ]
            if not children_ids:
                break
            
            db.query(DynamicRoute).filter(DynamicRoute.id.in_(children_ids)).update(
                {"is_active": False}, synchronize_session=False
            )
            db.commit()
            parent_ids = children_ids

dynamic_route_repository = DynamicRouteRepository()
