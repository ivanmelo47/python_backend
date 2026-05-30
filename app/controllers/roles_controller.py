from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.common.response import success_response
from app.models.user_model import User
from app.services.auth_service import get_current_user
from app.models.role_model import Role
from app.schemas.role_schema import RoleRead

router = APIRouter(prefix="/auth/roles", tags=["Roles"])

@router.get("", response_model=None)
def list_all_roles(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    roles = db.query(Role).order_by(Role.hierarchy.asc()).all()
    # Serialize to standard dict using RoleRead
    data = [RoleRead.model_validate(r).model_dump() for r in roles]
    return success_response(data=data).model_dump()
