import os
import sys

from sqlalchemy import or_

# Asegurar que el directorio raíz está en el path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.session import SessionLocal
from app.models import (
    user_model, icon_model, role_model, dynamic_route_model,
    product_model, user_session_model, system_config_model,
    app_config_global_model, password_reset_log_model
)
from app.models.dynamic_route_model import DynamicRoute

SEEDER_TITLE = "Seed de rutas de herramientas"
SEEDER_DESCRIPTION = "Crea Herramientas, Gestión de Iconos y Rutas Híbridas"

SEEDER_ROWS = [
    {
        "path": "herramientas",
        "name": "HerramientasView",
        "component_path": "private/admin/modules/HerramientasView.vue",
        "title": "Herramientas",
        "description": "Herramientas y utilidades del sistema (Contenedor)",
        "icon_color_mode": "original",
        "min_hierarchy": 1,
        "is_active": True,
        "meta": {"order": 40},
    },
    {
        "path": "herramientas/iconos",
        "name": "IconManagerView",
        "component_path": "private/admin/modules/tools/IconManager.vue",
        "title": "Gestión de Iconos",
        "description": "Administra iconos SVG del sistema",
        "icon_color_mode": "original",
        "min_hierarchy": 1,
        "is_active": True,
        "meta": {"order": 1},
    },
    {
        "path": "herramientas/rutas",
        "name": "DynamicRoutesView",
        "component_path": "private/admin/modules/tools/DynamicRoutesView.vue",
        "title": "Rutas Híbridas",
        "description": "Administra rutas dinámicas desde la base de datos",
        "icon_color_mode": "original",
        "min_hierarchy": 1,
        "is_active": True,
        "meta": {"order": 2},
    },
]

SEEDER_CONFLICT_FIELDS = ("name", "path", "component_path", "title")


def _route_from_row(row: dict, parent_id: int | None = None) -> DynamicRoute:
    return DynamicRoute(
        parent_id=parent_id,
        path=row["path"],
        name=row["name"],
        component_path=row["component_path"],
        title=row["title"],
        description=row["description"],
        icon_color_mode=row["icon_color_mode"],
        min_hierarchy=row["min_hierarchy"],
        is_active=row["is_active"],
        meta=row["meta"],
    )


def preview_conflicts() -> list[str]:
    db = SessionLocal()
    try:
        conditions = []
        for row in SEEDER_ROWS:
            row_conditions = []
            for field_name in SEEDER_CONFLICT_FIELDS:
                value = row.get(field_name)
                if value:
                    row_conditions.append(getattr(DynamicRoute, field_name) == value)
            if row_conditions:
                conditions.append(or_(*row_conditions))

        if not conditions:
            return []

        existing = db.query(DynamicRoute).filter(or_(*conditions)).all()
        conflicts = {
            f"{route.name} | {route.path} | {route.title} | {route.component_path}"
            for route in existing
        }
        return sorted(conflicts)
    finally:
        db.close()


def run():
    db = SessionLocal()
    try:
        conditions = []
        for row in SEEDER_ROWS:
            row_conditions = []
            for field_name in SEEDER_CONFLICT_FIELDS:
                value = row.get(field_name)
                if value:
                    row_conditions.append(getattr(DynamicRoute, field_name) == value)
            if row_conditions:
                conditions.append(or_(*row_conditions))

        if conditions:
            db.query(DynamicRoute).filter(or_(*conditions)).delete(synchronize_session=False)
            db.commit()

        parent = _route_from_row(SEEDER_ROWS[0])
        db.add(parent)
        db.commit()
        db.refresh(parent)
        print("Creada ruta padre: Herramientas")

        child1 = _route_from_row(SEEDER_ROWS[1], parent_id=parent.id)
        child2 = _route_from_row(SEEDER_ROWS[2], parent_id=parent.id)
        db.add(child1)
        db.add(child2)
        db.commit()
        print("¡Nuevas rutas creadas correctamente!")
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def seed_routes():
    run()


if __name__ == "__main__":
    run()
