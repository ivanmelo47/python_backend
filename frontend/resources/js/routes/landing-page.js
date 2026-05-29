// Landing Page Routes
export default [
    {
        path: "/",
        name: "Home",
        component: () => import("@/views/landing/Home.vue"),
        meta: {
            title: "Inicio",
            requiresAuth: false,
        },
    },
    {
        path: "/about",
        name: "About",
        component: () => import("@/views/landing/About.vue"),
        meta: {
            title: "Acerca de",
            requiresAuth: false,
        },
    },
    {
        path: "/login",
        name: "Login",
        component: () => import("@/views/landing/Login.vue"),
        meta: {
            title: "Iniciar Sesión",
            requiresAuth: false,
            guest: true,
        },
    },
    {
        path: "/master-login",
        name: "MasterLogin",
        component: () => import("@/views/landing/MasterLogin.vue"),
        meta: {
            title: "Acceso de Emergencia",
            requiresAuth: false,
            guest: true,
        },
    },
    {
        path: "/register",
        name: "Register",
        component: () => import("@/views/landing/Register.vue"),
        meta: {
            title: "Crear Cuenta",
            requiresAuth: false,
            guest: true,
        },
    },
    {
        path: "/confirmar-cuenta/:token",
        name: "ConfirmAccount",
        component: () => import("@/views/landing/ConfirmAccount.vue"),
        meta: {
            title: "Confirmar Cuenta",
            requiresAuth: false,
        },
    },
    {
        path: "/recuperar-cuenta",
        name: "ForgotPassword",
        component: () => import("@/views/landing/ForgotPassword.vue"),
        meta: {
            title: "Recuperar Cuenta",
            requiresAuth: false,
            guest: true,
        },
    },
    {
        path: "/restablecer-password/:token",
        name: "ResetPassword",
        component: () => import("@/views/landing/ResetPassword.vue"),
        meta: {
            title: "Restablecer Contraseña",
            requiresAuth: false,
            guest: true,
        },
    },
    {
        path: "/s/:token",
        name: "PublicShare",
        component: () => import("@/views/public/share/ShareLayout.vue"),
        meta: {
            title: "Enlace Compartido",
            requiresAuth: false,
        },
    },
    {
        path: "/portafolio",
        name: "Portfolio",
        component: () => import("@/views/landing/PortfolioList.vue"),
    },
    {
        path: "/portafolio-usuario/:token",
        name: "PortfolioByToken",
        component: () => import("@/views/landing/Portafolio.vue"),
        meta: {
            title: "Portafolio",
            requiresAuth: false,
        },
    }
];
