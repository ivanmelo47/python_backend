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

## Docker

- Levantar en desarrollo (con hot-reload):

```bash
docker-compose up --build
```

Acceder a la API en: `http://localhost:8000` (docs en `/docs`).

Para produccion, quite el `volumes` y el flag `--reload` en `docker-compose.yml` o ejecute la imagen directamente con `docker run`.

Conexión a Base de Datos en el host local

- En Docker Desktop (Windows / Mac) los contenedores pueden resolver el host con `host.docker.internal`. El `docker-compose.yml` ya incluye `extra_hosts` y un archivo de ejemplo `.env.docker.example`.
- En Linux puedes usar `network_mode: host` (descomentar en `docker-compose.yml`) para que el contenedor comparta la red del host — atención: esto hace que los puertos estén en el host y puede no ser deseable en producción.

Pasos recomendados:

1. Copiar el ejemplo y editar credenciales:

```bash
cp .env.docker.example .env.docker
# editar .env.docker -> poner DB_PASSWORD y demás datos reales
```

2. Levantar servicio:

```bash
docker-compose up --build
```

3. Si el contenedor no conecta a tu BD local, verifica:

- Que el servidor de BD acepte conexiones desde la red (no sólo localhost/127.0.0.1).
- En Windows/Mac con Docker Desktop, `DB_HOST=host.docker.internal` debería funcionar.
- En Linux, considera `network_mode: host` o exponer la interfaz del servidor DB.

Red compartida entre proyectos (opcional)

Si tienes la base de datos levantada en otro `docker-compose` o en un stack con una red compartida, puedes conectar `web` a esa red para usar el nombre del servicio directamente (más seguro y sin exponer puertos).

1. Asegúrate de que la red externa exista y se llame `shared_services_network` (o cambia el nombre en `docker-compose.yml`).

2. En `.env.docker` pone `DB_HOST=db` (o el nombre del servicio de la base de datos en el otro `docker-compose`).

3. Arranca tu stack de base de datos (el que contiene el servicio `db`) y luego en este proyecto ejecuta:

```bash
docker-compose up --build
```

Con esto el contenedor `web` resolverá `db` hacia el contenedor de la base de datos en la red compartida.



