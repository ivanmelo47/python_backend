# Frontend Vue independiente

Este directorio contiene el frontend separado del backend Laravel.

## Requisitos

- Node.js 20 o superior
- El backend Laravel corriendo en `http://localhost:8000`

## Configuración

1. Copia `.env.example` a `.env`.
2. Ajusta `VITE_API_BASE_URL` para apuntar al backend real.
3. Instala dependencias con `npm install` dentro de `app_front`.

## Scripts

- `npm run dev` - Inicia el servidor de desarrollo
- `npm run build` - Genera el build de producción
- `npm run preview` - Previsualiza el build

## Estructura

- `resources/js` - lógica Vue, rutas, composables y servicios
- `resources/sass` - estilos del frontend
- `index.html` - punto de entrada del SPA
