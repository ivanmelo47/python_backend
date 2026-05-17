# Setup e instalacion

## Requisitos

- Python 3.13+
- PowerShell (Windows)

## Crear entorno virtual

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

## Instalar dependencias

```powershell
pip install -r requirements.txt
```

## Variables de entorno

```powershell
Copy-Item .env.example .env
```

Variables principales en `.env`:

- `APP_NAME`: nombre de la API
- `APP_VERSION`: version de la API
- `DEBUG`: modo debug
- `DATABASE_URL`: cadena de conexion

## Ejecutar la API

```powershell
uvicorn app.main:app --reload

# Alternativa con manager (puerto manual)
python manage.py ejecutar --puerto 8000
```

## URLs utiles

- Swagger UI: `http://127.0.0.1:8000/docs`
- Redoc: `http://127.0.0.1:8000/redoc`
