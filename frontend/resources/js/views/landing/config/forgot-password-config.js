export const forgotPasswordConfig = {
    layout: {
        width: 2,
        align: 'center'
    },
    title: 'Recuperar Cuenta',
    subtitle: 'Ingresa tu correo para recibir un enlace de recuperación',
    fields: [
        {
            id: 'email',
            label: 'Correo Electrónico',
            icon: 'email',
            type: 'email',
            placeholder: 'tu@email.com',
            colSpan: 12
        }
    ],
    footer: {
        showLogin: true
    }
};
