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

O puedes usar el script del proyecto:

```powershell
python create_venv.py
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

Este proyecto ya está preparado para desplegarse como **Stack de Portainer desde Git**.

### Cómo desplegarlo en Portainer

1. En Portainer, ve a **Stacks** → **Add stack** → **Git repository**.
2. Pega la URL del repositorio.
3. Usa `docker-compose.yml` como archivo principal del stack.
4. Carga las variables de entorno en la sección de **Environment variables**.
5. Despliega el stack.

### Variables que debes definir en Portainer

La aplicación espera estas variables:

- `APP_NAME`
- `APP_VERSION`
- `DEBUG`
- `APP_TIMEZONE`
- `JWT_SECRET_KEY`
- `JWT_ALGORITHM`
- `JWT_ACCESS_TOKEN_EXPIRE_MINUTES`
- `JWT_REFRESH_TOKEN_EXPIRE_MINUTES`
- `FRONTEND_URL`
- `DB_SCHEME`
- `DB_HOST`
- `DB_PORT`
- `DB_DATABASE`
- `DB_USERNAME`
- `DB_PASSWORD`
- `DB_TIMEZONE`
- `APP_PORT`
- `MAIL_MAILER`
- `MAIL_SCHEME`
- `MAIL_HOST`
- `MAIL_PORT`
- `MAIL_USERNAME`
- `MAIL_PASSWORD`
- `MAIL_FROM_ADDRESS`
- `MAIL_FROM_NAME`

### Valores recomendados en VPS Ubuntu

Si la base de datos está en el mismo servidor pero fuera de Docker:

- `DB_HOST=host.docker.internal`
- `DB_PORT=3306` o el puerto que expongas en el host

Si la base de datos corre en otro contenedor y la conectas por una red Docker compartida:

- `DB_HOST=db`
- `DB_PORT=3306`

Además, el stack `web` debe conectarse a la red externa `shared_services_network`, y el stack de la base de datos también debe estar unido a esa misma red.

Si el nombre real de la red en tu VPS cambia, puedes definir `DOCKER_NETWORK_NAME` en Portainer y el stack usará ese valor en vez de `shared_services_network`.

Si la base de datos está en otro servidor:

- `DB_HOST=<ip-o-host-remoto>`
- `DB_PORT=<puerto-remoto>`

### Valores mínimos de ejemplo

```text
APP_NAME=Python Backend API
APP_VERSION=1.0.0
DEBUG=true
APP_TIMEZONE=America/Mexico_City
JWT_SECRET_KEY=change-me
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=60
JWT_REFRESH_TOKEN_EXPIRE_MINUTES=70
FRONTEND_URL=http://localhost:3000
DB_SCHEME=mariadb+mariadbconnector
DB_HOST=host.docker.internal
DB_PORT=3306
DB_DATABASE=python_backend
DB_USERNAME=root
DB_PASSWORD=change-me
DB_TIMEZONE=-06:00
APP_PORT=8000
MAIL_MAILER=smtp
MAIL_SCHEME=smtp
MAIL_HOST=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=
MAIL_PASSWORD=
MAIL_FROM_ADDRESS=
MAIL_FROM_NAME=Python Backend API
```

### Verificación

```bash
docker compose ps
docker compose logs -f web
docker compose exec web python manage.py migrar
```

### Servicio en Ubuntu (systemd)

Si quieres que la app nativa siga viva aunque cierres la terminal y que arranque sola después de reiniciar el VPS, instala un servicio `systemd`:

```bash
python deploy.py install-service --port 8000
python deploy.py migrate-ubuntu
python deploy.py status-service
python deploy.py restart-service
python deploy.py stop-service
python deploy.py uninstall-service
```

El servicio usa el Python de `.venv`, no el Python global, y se configura para reiniciarse automáticamente si falla.

Notas:

- `install-service` es la opción para modo producción en Ubuntu.
- `migrate-ubuntu` ejecuta las migraciones usando la `.venv` del proyecto en Ubuntu.
- `reload` no es necesario en el servicio `systemd`; allí conviene reiniciar el servicio cuando hagas cambios.



