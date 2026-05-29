/**
 * Módulos de Navegación del Sidebar
 * Define los enlaces e iconos para la barra lateral del administrador.
 *
 * @property {string} name - El texto de la etiqueta que se muestra en el menú.
 * @property {string} path - La ruta interna de Vue Router para navegar.
 * @property {string} icon - El identificador del icono del set de iconos (dashboard-icons.js).
 * @property {boolean} exact - Controla la coincidencia del estado activo:
 *  - true: Activo SOLO cuando la URL coincide exactamente con 'path' (ej. usado para Dashboard para evitar que se active en sub-páginas).
 *  - false: Activo cuando la URL comienza con 'path' (ej. mantiene 'Usuarios' activo al editar un usuario).
 */
export const sidebarModules = [
    {
        name: "Dashboard",
        path: "/dashboard",
        icon: "dashboard",
        // 'exact: true' previene que esto se active al visitar /dashboard/usuarios
        exact: true,
    },
    {
        name: "Archivos",
        path: "/dashboard/archivos",
        icon: "folder",
        // 'exact: false' permite que esto permanezca activo para sub-rutas como /dashboard/archivos/detalles
        exact: false,
    },
    {
        name: "Usuarios",
        path: "/dashboard/usuarios",
        icon: "users",
        exact: false,
        children: [
            {
                name: "Gestión",
                path: "/dashboard/usuarios/gestion",
                icon: "users",
                description: "Administra cuentas de usuarios y roles.",
                exact: false,
            },
            {
                name: "Contraseñas",
                path: "/dashboard/usuarios/historial-contrasenas",
                icon: "lock",
                description: "Historial de recuperaciones de contraseña.",
                exact: false,
            },
            {
                name: "Accesos",
                path: "/dashboard/usuarios/historial-logins",
                icon: "exchange",
                description: "Registro de inicios de sesión y actividad.",
                exact: false,
            },
        ],
    },
    {
        name: "Herramientas",
        path: "/dashboard/herramientas",
        icon: "tools",
        children: [
            {
                name: "Reportes",
                path: "/dashboard/herramientas/reportes",
                icon: "folder",
                description:
                    "Genera y visualiza informes estadísticos del sistema.",
                exact: false,
            },
            {
                name: "Auditoría",
                path: "/dashboard/herramientas/auditoria",
                icon: "check",
                description:
                    "Seguimiento detallado de todas las acciones del sistema.",
                exact: false,
            },
        ],
    },
    {
        name: "Configuración",
        path: "/dashboard/configuracion",
        icon: "settings",
        exact: false,
    },
    {
        name: "Mantenimiento",
        path: "/dashboard/mantenimiento",
        icon: "tool",
        exact: true,
        supermasterOnly: true,
    },
];
