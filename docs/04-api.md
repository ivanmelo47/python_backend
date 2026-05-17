# API y endpoints

Prefijo global de API:

- `/api/v1`

## Formato estandar de respuesta

Todas las respuestas exitosas y de error siguen este contrato:

```json
{
  "status": "success",
  "code": 200,
  "msg": "OK",
  "data": {}
}
```

Para errores:

```json
{
  "status": "error",
  "code": 404,
  "msg": "User not found",
  "data": null
}
```

## Healthcheck

- `GET /`

Respuesta ejemplo:

```json
{
  "status": "ok",
  "service": "Python Backend API"
}
```

## Users

- `GET /api/v1/users/` (requiere Bearer token)
- `GET /api/v1/users/{user_id}` (requiere Bearer token)
- `POST /api/v1/users/`
- `PATCH /api/v1/users/{user_id}` (requiere Bearer token)
- `DELETE /api/v1/users/{user_id}` (requiere Bearer token)

Campos principales de user:

- `email`
- `full_name`
- `password` (solo entrada, minimo 8 caracteres)
- `is_active`

## Auth (JWT)

- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `POST /api/v1/auth/refresh`
- `GET /api/v1/auth/me` (requiere Bearer token)

Payload de registro:

```json
{
  "email": "newuser@example.com",
  "full_name": "New User",
  "password": "strongpassword123"
}
```

Respuesta (201 Created):

```json
{
  "status": "success",
  "code": 201,
  "msg": "User registered successfully. Please wait for an administrator to activate your account.",
  "data": {
    "email": "newuser@example.com",
    "full_name": "New User",
    "is_active": false,
    "role_id": 3,
    "id": 2,
    "created_at": "..."
  }
}
```

Payload de login:

```json
{
  "email": "user@example.com",
  "password": "12345678"
}
```

Respuesta de login (resumida):

```json
{
  "status": "success",
  "code": 200,
  "msg": "Login successful",
  "data": {
    "user": {
      "id": 1,
      "email": "user@example.com",
      "full_name": "Usuario Demo",
      "is_active": true
    },
    "token": {
      "access_token": "...",
      "refresh_token": "...",
      "token_type": "bearer",
      "expires_in": 3600
    }
  }
}
```

## Refresh Token

- `POST /api/v1/auth/refresh`

Payload:

```json
{
  "refresh_token": "..."
}
```

Respuesta:

```json
{
  "status": "success",
  "code": 200,
  "msg": "Token refreshed successfully",
  "data": {
    "access_token": "...",
    "refresh_token": "...",
    "token_type": "bearer",
    "expires_in": 3600
  }
}
```

## Products

- `GET /api/v1/products/`
- `GET /api/v1/products/{product_id}`
- `POST /api/v1/products/`
- `PATCH /api/v1/products/{product_id}`
- `DELETE /api/v1/products/{product_id}`

Campos principales de product:

- `name`
- `description`
- `price`
- `owner_id`

## Paginacion

Los listados usan parametros comunes:

- `skip` (default: 0)
- `limit` (default: 100, max: 500)
