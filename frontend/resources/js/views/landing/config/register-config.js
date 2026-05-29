export const registerConfig = {
    layout: {
        width: 2, // 1 to 6 columns of the page grid
        align: 'center' // 'left', 'center', 'right'
    },
    title: 'Crear Cuenta',
    subtitle: 'Regístrate para comenzar a gestionar tus archivos',
    fields: [
        {
            id: 'name',
            label: 'Nombre de Usuario',
            icon: 'user',
            type: 'text',
            placeholder: 'Ej: usuario123',
            colSpan: 6,
            sanitize: 'username'
        },
        {
            id: 'email',
            label: 'Correo Electrónico',
            icon: 'email',
            type: 'email',
            placeholder: 'tu@email.com',
            colSpan: 6
        },
        {
            id: 'password',
            label: 'Contraseña',
            icon: 'lock',
            type: 'password',
            placeholder: '••••••••',
            colSpan: 3
        },
        {
            id: 'password_confirmation',
            label: 'Confirmar',
            icon: 'lock',
            type: 'password',
            placeholder: '••••••••',
            colSpan: 3
        }
    ],
    footer: {
        showLogin: true
    }
};
