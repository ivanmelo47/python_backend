# Guia de modulos

Esta guia define como crear nuevos modulos de forma consistente.

## Plantilla recomendada

```text
app/modules/<module_name>/
  controllers/
    router.py
  services/
    <module_name>_service.py
  repositories/
    <module_name>_repository.py
  models/
    <module_name>_model.py
  schemas/
    <module_name>_schema.py
```

## Responsabilidad por capa

- controllers: endpoints HTTP y validacion de entrada/salida.
- services: reglas de negocio y coordinacion.
- repositories: consultas SQLAlchemy y persistencia.
- models: entidades ORM.
- schemas: DTOs Pydantic.

## Checklist para agregar un modulo

1. Crear carpetas y archivos base del modulo.
2. Definir `models` y relacionarlos si aplica.
3. Crear `schemas` de entrada/salida.
4. Implementar `repositories`.
5. Implementar `services`.
6. Exponer rutas en `controllers/router.py`.
7. Registrar router en `app/api/router.py`.
8. Crear migracion con `python manage.py make -m "..."`.
9. Aplicar migracion con `python manage.py migrate`.
