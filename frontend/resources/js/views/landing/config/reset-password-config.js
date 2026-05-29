export const resetPasswordConfig = {
    layout: {
        width: 2,
        align: 'center'
    },
    title: 'Nueva Contraseña',
    subtitle: 'Establece tu nueva contraseña de acceso',
    fields: [
        {
            id: 'password',
            label: 'Nueva Contraseña',
            icon: 'lock',
            type: 'password',
            placeholder: '••••••••',
            colSpan: 12
        },
        {
            id: 'password_confirmation',
            label: 'Confirmar Contraseña',
            icon: 'lock',
            type: 'password',
            placeholder: '••••••••',
            colSpan: 12
        }
    ],
    footer: {
        showLogin: true
    }
};
