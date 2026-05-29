// Dashboard Routes
export default [
    {
        path: "/dashboard",
        name: "Dashboard", // Add this
        component: () => import("@/views/private/admin/Dashboard.vue"),
        meta: {
            title: "Dashboard",
            requiresAuth: true,
            minHierarchy: 4,
            icon: "dashboard", // Sidebar Icon
            sidebar: true, // Show in Sidebar
            exact: true, // Active only on exact match
            order: 1,
        },
        children: [
            {
                path: "",
                name: "DashboardHome",
                component: () =>
                    import("@/views/private/admin/modules/DashboardHome.vue"),
                meta: {
                    title: "Dashboard",
                    icon: "dashboard",
                    sidebar: true,
                    exact: true,
                    order: 1,
                },
            },
            {
                path: "gestion-portafolios/editar/:id",
                name: "PortafolioEditor",
                component: () =>
                    import("@/views/private/admin/modules/portafolio/PortafolioEditorView.vue"),
                meta: {
                    title: "Editor de Portafolio",
                    requiresAuth: true,
                    minHierarchy: 4,
                    sidebar: false,
                    fitScreen: false,
                    exact: true,
                },
            },
        ],
    },
];
