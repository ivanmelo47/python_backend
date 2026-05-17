# Arquitectura y estructura

## Enfoque

El proyecto usa una arquitectura modular por dominio.
Cada modulo contiene su propia capa de:

- controllers
- services
- repositories
- models
- schemas

## Estructura base

```text
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
    auth/
      controllers/
      services/
    users/
      controllers/
      services/
      repositories/
      models/
      schemas/
    products/
      controllers/
      services/
      repositories/
      models/
      schemas/
  main.py
```

## Flujo por request

1. El request entra por `controllers/router.py`.
2. El controller delega la regla de negocio en `services`.
3. El service usa `repositories` para acceso a datos.
4. El repository trabaja sobre `models` SQLAlchemy.
5. El contrato de entrada/salida se define en `schemas` Pydantic.

## Logica compartida

`app/common` guarda piezas reutilizables entre modulos:

- dependencias FastAPI (ejemplo: paginacion)
- utilidades transversales
- excepciones comunes (si se agregan)
