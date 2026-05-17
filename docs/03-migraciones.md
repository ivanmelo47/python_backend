# Migraciones

El proyecto usa Alembic como sistema de migraciones.

## Comandos principales

Todos se ejecutan con el entorno virtual activo.

### Menu interactivo

```powershell
python manage.py
```

Al abrirse, el manager tiene secciones:

- gestion de migraciones DB
- ejecutar app (host/puerto manual)

Dentro de la seccion de migraciones permite elegir:

- crear migracion
- aplicar migraciones
- retroceder migracion
- ver revision actual
- ver historial
- ver cabezas

El manager limpia la pantalla entre vistas y, tras ejecutar una accion de migracion,
solicita `Enter` para continuar. Esto evita que la salida se acumule en consola.

## Ejecutar app desde manager

```powershell
python manage.py ejecutar --host 127.0.0.1 --puerto 8000
```

### Crear migracion

```powershell
python manage.py crear -m "nombre_migracion"
```

### Aplicar migraciones pendientes

```powershell
python manage.py migrar
```

### Reiniciar base de datos desde cero

```powershell
python manage.py reiniciar
```

Esto elimina y recrea la base antes de aplicar todas las migraciones.

### Rollback

```powershell
python manage.py retroceder --paso -1
```

### Ver estado actual

```powershell
python manage.py actual
```

### Ver historial

```powershell
python manage.py historial
```

## Buenas practicas

- Crear una migracion por cambio funcional de schema.
- No editar migraciones ya ejecutadas en otros entornos.
- Probar siempre upgrade y downgrade en local.
- Usar nombres claros, por ejemplo: `add_price_index_products`.

## Ubicacion

- Config Alembic: `alembic.ini`
- Entorno Alembic: `alembic/env.py`
- Scripts de migracion: `alembic/versions/`
