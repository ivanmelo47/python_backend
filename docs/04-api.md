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
- `GET /api/v1/auth/confirm` (Verificación de cuenta)
- `POST /api/v1/auth/login`
- `POST /api/v1/auth/refresh`
- `GET /api/v1/auth/me` (requiere Bearer token)
- `GET /api/v1/auth/sessions` (requiere Bearer token)
- `DELETE /api/v1/auth/sessions/{session_uuid}` (requiere Bearer token, solo Master)
- `POST /api/v1/auth/forgot-password` (Solicitar recuperación)
- `POST /api/v1/auth/reset-password` (Restablecer contraseña con token)

Payload de registro:

```json
{
  "email": "newuser@example.com",
  "full_name": "New User",
  "password": "strongpassword123"
}
```

Respuesta de registro (201 Created):

```json
{
  "status": "success",
  "code": 201,
  "msg": "User registered successfully. Please confirm your email address via the link sent to your inbox.",
  "data": {
    "email": "newuser@example.com",
    "full_name": "New User",
    "is_active": false,
    "confirmed": false,
    "role_id": 3,
    "id": 2,
    "created_at": "..."
  }
}
```

### Verificación de Cuenta

- `GET /api/v1/auth/confirm?token=<token>`

Parámetros de consulta (Query Params):
*   `token` (Requerido): Token genérico de alta entropía generado al registrar al usuario.

Respuesta (200 OK):

```json
{
  "status": "success",
  "code": 200,
  "msg": "Your account has been successfully confirmed and activated!",
  "data": {
    "id": 2,
    "email": "newuser@example.com",
    "full_name": "New User",
    "is_active": true,
    "confirmed": true,
    "role_id": 3,
    "created_at": "..."
  }
}
```

### Restablecimiento de Contraseña (Forgot/Reset)

#### 1. Solicitar restablecimiento de contraseña
*   **Requisito**: La cuenta debe estar confirmada (`confirmed == true`) y activa (`is_active == true`).

- `POST /api/v1/auth/forgot-password`

Payload:

```json
{
  "email": "user@example.com"
}
```

Respuesta (200 OK):

```json
{
  "status": "success",
  "code": 200,
  "msg": "If the email belongs to an active, confirmed account, a password reset link has been sent.",
  "data": null
}
```

#### 2. Restablecer la contraseña usando el token
*   **Nota de Seguridad Premium**: Al restablecer con éxito la contraseña, **todas las sesiones activas anteriores del usuario se cierran automáticamente** invalidando sus refresh tokens.

- `POST /api/v1/auth/reset-password`

Payload:

```json
{
  "token": "R3Y9hKeM4jW...",
  "new_password": "EvenStronger456!"
}
```

Respuesta (200 OK):

```json
{
  "status": "success",
  "code": 200,
  "msg": "Your password has been successfully reset. All active sessions have been terminated for security.",
  "data": null
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

## Sesiones de Usuario

### Obtener historial de sesiones

- `GET /api/v1/auth/sessions` (requiere Bearer token)

Devuelve el historial y estado de las sesiones activas del usuario autenticado.

Respuesta (200 OK):

```json
{
  "status": "success",
  "code": 200,
  "msg": "Sessions retrieved",
  "data": [
    {
      "id": 1,
      "uuid": "3b09fccb-03d1-4df4-bdb4-20339d4cbf21",
      "user_id": 2,
      "logged_in_at": "2026-05-16T23:54:58Z",
      "last_activity_at": "2026-05-17T05:54:58Z",
      "logged_out_at": null,
      "ip_address": "127.0.0.1",
      "user_agent": "Mozilla/5.0...",
      "latitude": null,
      "longitude": null,
      "is_active": true
    }
  ]
}
```

### Revocar Sesión (Solo Master)

- `DELETE /api/v1/auth/sessions/{session_uuid}` (requiere Bearer token de rol Master)

Revoca una sesión específica invalidando inmediatamente su refresh token.

Respuesta (200 OK):

```json
{
  "status": "success",
  "code": 200,
  "msg": "Session revoked successfully",
  "data": {
    "id": 1,
    "uuid": "3b09fccb-03d1-4df4-bdb4-20339d4cbf21",
    "user_id": 2,
    "logged_in_at": "2026-05-16T23:54:58Z",
    "last_activity_at": "2026-05-17T05:54:58Z",
    "logged_out_at": "2026-05-17T06:01:47Z",
    "ip_address": "127.0.0.1",
    "user_agent": "Mozilla/5.0...",
    "latitude": null,
    "longitude": null,
    "is_active": false
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
