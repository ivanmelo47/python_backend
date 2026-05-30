from fastapi import APIRouter, Depends, Request, status, HTTPException, UploadFile
from sqlalchemy.orm import Session
from typing import Optional
import os

from app.common.response import success_response
from app.db.session import get_db
from app.services import auth_service
from app.repositories.icon_repository import icon_repository
from app.schemas.icon_schema import IconResponse
from app.models.user_model import User
from app.common.utils.icon_utils import is_valid_svg, extract_viewbox, convert_image_to_webp

router = APIRouter(prefix="/auth/icons", tags=["icons"])

PUBLIC_ICONS_DIR = "public/icons"
os.makedirs(f"{PUBLIC_ICONS_DIR}/svg", exist_ok=True)


def _public_icon_url(path: str) -> str:
    return f"/public/icons/{path}"


def _delete_public_icon_file(file_path: Optional[str]) -> None:
    if not file_path:
        return

    normalized_path = str(file_path).strip().lstrip("/")
    if not normalized_path.startswith("public/icons/"):
        return

    if os.path.exists(normalized_path):
        os.remove(normalized_path)

async def _parse_icon_request(request: Request):
    content_type = request.headers.get("content-type", "")
    data = {}
    files = {}
    
    if "application/json" in content_type:
        data = await request.json()
    else:
        form = await request.form()
        for key, value in form.multi_items():
            if isinstance(value, UploadFile):
                files[key] = value
            else:
                data[key] = value
                
    return data, files

@router.get("", response_model=None)
def get_icons(
    page: int = 1,
    per_page: int = 10,
    search: Optional[str] = None,
    category: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
):
    skip = (page - 1) * per_page
    show_inactive = (current_user.role and current_user.role.hierarchy == 1)
    
    limit = per_page
    if per_page == -1:
        limit = 5000
        skip = 0

    icons = icon_repository.get_all(
        db, skip=skip, limit=limit, 
        search=search, category=category, 
        show_inactive=show_inactive
    )
    
    total = icon_repository.count_all(
        db, search=search, category=category, show_inactive=show_inactive
    )
    
    # Serializar manualmente o usando schema (si no requiere info extra, usamos schema)
    # En Laravel retornaba data.data, total, etc.
    data = [IconResponse.model_validate(icon).model_dump() for icon in icons]
    
    if per_page == -1:
        return success_response(data=data)
        
    return {
        "success": True,
        "data": {
            "data": data,
            "current_page": page,
            "per_page": per_page,
            "total": total
        }
    }

@router.post("", response_model=None, status_code=201)
async def create_icon(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user)
):
    data, files = await _parse_icon_request(request)
    
    name = data.get("name")
    if not name:
        raise HTTPException(status_code=422, detail="El nombre del icono es obligatorio.")
        
    type_ = data.get("type", "svg")
    storage_mode = data.get("storage_mode", "database")
    color_mode = data.get("color_mode", "currentColor")
    category = data.get("category")
    
    icon_data = {
        "name": name,
        "type": type_,
        "color_mode": color_mode,
        "storage_mode": storage_mode,
        "category": category,
        "is_active": True
    }
    
    if type_ == "svg":
        svg_content = ""
        if "svg_file" in files:
            svg_content = (await files["svg_file"].read()).decode("utf-8")
        else:
            svg_content = data.get("svg_content", "")
            
        if not is_valid_svg(svg_content):
            raise HTTPException(status_code=422, detail="El contenido no es un SVG válido.")
            
        if storage_mode == "file":
            import uuid
            filename = f"icon_svg_{uuid.uuid4().hex[:8]}.svg"
            filepath = f"{PUBLIC_ICONS_DIR}/svg/{filename}"
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(svg_content)
                
            # Asumiendo que servimos la carpeta public en /storage como Laravel o /public
            icon_data["file_path"] = _public_icon_url(f"svg/{filename}")
            icon_data["svg_content"] = None
            icon_data["color_mode"] = "original"
        else:
            icon_data["svg_content"] = svg_content
            icon_data["file_path"] = None
            
        icon_data["viewBox"] = extract_viewbox(svg_content)
    else:
        # Image Type
        if "image_file" not in files:
            raise HTTPException(status_code=422, detail="Debe subir una imagen para este tipo de icono.")
        
        image_bytes = await files["image_file"].read()
        webp_bytes = convert_image_to_webp(image_bytes, quality=80)
        
        import uuid
        filename = f"icon_{uuid.uuid4().hex[:8]}.webp"
        filepath = f"{PUBLIC_ICONS_DIR}/{filename}"
        with open(filepath, "wb") as f:
            f.write(webp_bytes)
            
        icon_data["file_path"] = _public_icon_url(filename)
        
    icon = icon_repository.create(db, icon_data, current_user.id)
    return success_response(
        data=IconResponse.model_validate(icon).model_dump(),
        message="Icono creado exitosamente.",
        code=201
    ).model_dump()

@router.get("/{uuid}", response_model=None)
def show_icon(
    uuid: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user)
):
    icon = icon_repository.get_by_uuid(db, uuid)
    if not icon:
        raise HTTPException(status_code=404, detail="Icono no encontrado")
        
    return success_response(data=IconResponse.model_validate(icon).model_dump())

async def _process_icon_update(uuid: str, request: Request, db: Session):
    data, files = await _parse_icon_request(request)
    
    icon = icon_repository.get_by_uuid(db, uuid)
    if not icon:
        raise HTTPException(status_code=404, detail="Icono no encontrado")
        
    update_data = {}
    if "name" in data: update_data["name"] = data["name"]
    if "category" in data: update_data["category"] = data["category"]
    if "color_mode" in data: update_data["color_mode"] = data["color_mode"]
    
    type_ = data.get("type", icon.type)
    update_data["type"] = type_
    
    # Logic from Laravel
    storage_mode = data.get("storage_mode", "file" if icon.type == "svg" and icon.file_path else "database")
    update_data["storage_mode"] = storage_mode
    
    if type_ == "svg":
        svg_content = None
        if "svg_file" in files:
            svg_content = (await files["svg_file"].read()).decode("utf-8")
        elif "svg_content" in data and data["svg_content"]:
            svg_content = data["svg_content"]
        else:
            svg_content = icon.svg_content
            
        if svg_content and not is_valid_svg(svg_content):
            raise HTTPException(status_code=422, detail="El contenido no es un SVG válido.")
            
        if storage_mode == "file" and svg_content:
            import uuid as uid
            filename = f"icon_svg_{uid.uuid4().hex[:8]}.svg"
            filepath = f"{PUBLIC_ICONS_DIR}/svg/{filename}"
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(svg_content)

            _delete_public_icon_file(icon.file_path)
            update_data["file_path"] = _public_icon_url(f"svg/{filename}")
            update_data["svg_content"] = None
            update_data["color_mode"] = "original"
        elif svg_content is not None:
            _delete_public_icon_file(icon.file_path)
            update_data["svg_content"] = svg_content
            update_data["file_path"] = None
        elif storage_mode == "database" and icon.file_path:
            _delete_public_icon_file(icon.file_path)
            update_data["file_path"] = None
            
        if svg_content:
            update_data["viewBox"] = extract_viewbox(svg_content)
            
    else:
        # Image Update
        if "image_file" in files:
            image_bytes = await files["image_file"].read()
            webp_bytes = convert_image_to_webp(image_bytes, quality=80)
            
            import uuid as uid
            filename = f"icon_{uid.uuid4().hex[:8]}.webp"
            filepath = f"{PUBLIC_ICONS_DIR}/{filename}"
            with open(filepath, "wb") as f:
                f.write(webp_bytes)

            _delete_public_icon_file(icon.file_path)
            update_data["file_path"] = _public_icon_url(filename)
            
    updated_icon = icon_repository.update(db, icon, update_data)
    return success_response(
        data=IconResponse.model_validate(updated_icon).model_dump(),
        message="Icono actualizado exitosamente."
    ).model_dump()


@router.put("/{uuid}", response_model=None)
async def update_icon_put(
    uuid: str,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user)
):
    return await _process_icon_update(uuid, request, db)


@router.post("/{uuid}", response_model=None)
async def update_icon_post(
    uuid: str,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user)
):
    # Support Laravel spoofing logic via POST for multipart forms
    data, files = await _parse_icon_request(request)
    if data.get("_method") == "PUT":
        return await _process_icon_update(uuid, request, db)
    raise HTTPException(status_code=405, detail="Method Not Allowed")


@router.delete("/{uuid}", response_model=None)
def delete_icon(
    uuid: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user)
):
    icon = icon_repository.get_by_uuid(db, uuid)
    if not icon:
        raise HTTPException(status_code=404, detail="Icono no encontrado")
        
    if icon.file_path and "public" in icon.file_path:
        old_path = icon.file_path.lstrip("/")
        if os.path.exists(old_path): os.remove(old_path)
        
    icon_repository.remove(db, icon.id)
    return success_response(message="Icono eliminado correctamente").model_dump()


@router.post("/{uuid}/toggle-status", response_model=None)
def toggle_status(
    uuid: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user)
):
    icon = icon_repository.get_by_uuid(db, uuid)
    if not icon:
        raise HTTPException(status_code=404, detail="Icono no encontrado")
        
    updated = icon_repository.toggle_status(db, icon.id)
    return success_response(
        data=IconResponse.model_validate(updated).model_dump(),
        message="Estatus del icono actualizado exitosamente."
    ).model_dump()
