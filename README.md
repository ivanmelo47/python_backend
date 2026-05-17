# FastAPI Backend Modular

Backend en FastAPI con estructura modular por dominio (`users`, `products`), usando SQLAlchemy y control de migraciones con Alembic.

## Estructura

```
python_backend/
  app/
    api/
      router.py
    core/
      settings.py
    db/
      base.py
      session.py
    common/
      dependencies/
        pagination.py
    modules/
      users/
        controllers/
          router.py
        services/
          user_service.py
        repositories/
          user_repository.py
        models/
          user_model.py
        schemas/
          user_schema.py
      products/
        controllers/
          router.py
        services/
          product_service.py
        repositories/
          product_repository.py
        models/
          product_model.py
        schemas/
          product_schema.py
    main.py
  alembic/
    versions/
  alembic.ini
  manage.py
  .env.example
  requirements.txt
```

## Crear y activar entorno virtual (Windows PowerShell)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

## Instalar dependencias

```powershell
pip install -r requirements.txt
```

## Configurar variables

```powershell
Copy-Item .env.example .env
```

## Ejecutar servidor

```powershell
uvicorn app.main:app --reload

# o desde el manager (puerto manual)
python manage.py ejecutar --puerto 8000
```

API docs: `http://127.0.0.1:8000/docs`

## Autenticacion JWT

- Login: `POST /api/v1/auth/login`
- Usuario autenticado: `GET /api/v1/auth/me`

Variables en `.env`:

- `JWT_SECRET_KEY`
- `JWT_ALGORITHM` (default `HS256`)
- `JWT_ACCESS_TOKEN_EXPIRE_MINUTES`

## Documentacion en Markdown

- Indice general: `docs/README.md`
- Setup: `docs/01-setup.md`
- Arquitectura: `docs/02-arquitectura.md`
- Migraciones: `docs/03-migraciones.md`
- API: `docs/04-api.md`
- Base de datos: `docs/05-base-datos.md`
- Guia de modulos: `docs/06-modulos.md`

## Migraciones (estilo Laravel/Node)

Comandos desde PowerShell con entorno virtual activo:

```powershell
# Abrir manager por secciones:
# 1) Gestion de migraciones DB
# 2) Ejecutar app (host/puerto manual)
python manage.py

# Crear migracion desde cambios en modelos
python manage.py crear -m "create_orders_table"

# Aplicar migraciones pendientes
python manage.py migrar

# Reiniciar base de datos desde cero y migrar
python manage.py reiniciar

# Rollback de una migracion
python manage.py retroceder --paso -1

# Ver estado actual
python manage.py actual

# Ver historial
python manage.py historial
```

El menu interactivo permite elegir acciones numeradas por seccion sin recordar comandos.

La opcion de reinicio elimina y recrea la base de datos, por eso solo debe usarse cuando no necesitas conservar datos.

Nota: La creacion de tablas ahora se controla por migraciones (Alembic), no por `create_all` en el arranque de la app.
