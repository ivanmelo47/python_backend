export const loginConfig = {
    layout: {
        width: 2, // 1 to 6 columns of the page grid
        align: 'center' // 'left', 'center', 'right'
    },
    title: 'Iniciar Sesión',
    subtitle: 'Bienvenido de nuevo, por favor ingresa tus datos',
    fields: [
        {
            id: 'email',
            label: 'Identificación',
            icon: 'user',
            type: 'text',
            placeholder: 'Correo, usuario o teléfono',
            colSpan: 6 // Out of 6 internal grid columns
        },
        {
            id: 'password',
            label: 'Contraseña',
            icon: 'lock',
            type: 'password',
            placeholder: '••••••••',
            colSpan: 6
        }
    ],
    footer: {
        showRegister: true,
        showForgot: true
    }
};
