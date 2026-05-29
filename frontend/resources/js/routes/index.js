import { createRouter, createWebHashHistory, createWebHistory } from 'vue-router';

// Import route modules
import landingPageRoutes from './landing-page';
import adminDashboardRoutes from './admin-dashboard';

// Combine all routes
const routes = [
    ...landingPageRoutes,
    ...adminDashboardRoutes,

    {
        path: '/403',
        name: 'Forbidden',
        component: () => import('../views/Forbidden.vue'),
        meta: {
            title: 'Acceso Denegado'
        }
    },
    // Catch-all 404 route
    {
        path: '/:pathMatch(.*)*',
        name: 'NotFound',
        component: () => import('../views/NotFound.vue'),
        meta: {
            title: 'Página no encontrada'
        }
    }
];

// Create router instance
const shouldUseHashHistory = import.meta.env.VITE_ROUTER_MODE === 'hash';

const router = createRouter({
    history: shouldUseHashHistory ? createWebHashHistory() : createWebHistory(),
    routes,
    scrollBehavior(to, from, savedPosition) {
        if (savedPosition) {
            return savedPosition;
        }
        return { top: 0 };
    }
});

import { useAuth } from '@/composables/useAuth';
import { useDynamicRoutes } from '@/composables/useDynamicRoutes';

// Navigation guards
router.beforeEach(async (to, from, next) => {
    const { isAuthenticated, user } = useAuth();
    const { isRoutesLoaded, fetchAndRegisterRoutes } = useDynamicRoutes();

    // 1. Check authentication
    if (to.meta.requiresAuth && !isAuthenticated.value) {
        return next('/login');
    }

    // Load dynamic routes if authenticated and not already loaded
    if (isAuthenticated.value && !isRoutesLoaded.value) {
        await fetchAndRegisterRoutes(router);
        // If we were going to a route that might have just been loaded, 
        // we MUST use the full path to force the router to re-evaluate all routes
        if (to.matched.length === 0 || (to.name === 'NotFound' && to.path !== '/404')) {
            return next({ path: to.fullPath, replace: true });
        }
    }

    // Update document title
    // Logic: If it's a NotFound but we just finished loading routes, the 'to' object 
    // might still be the old one. If we already triggered a redirect above, 
    // this guard will run again with the correct 'to'.
    // To avoid the flash, we only set the title if it's NOT a NotFound OR if routes are already loaded.
    if (to.name !== 'NotFound' || isRoutesLoaded.value) {
        document.title = to.meta.title ? `${to.meta.title} - App` : 'Laravel + Vue 3';
    }

    // 2. Check guest access
    if (to.meta.guest && isAuthenticated.value) {
        return next('/dashboard');
    }

    // 3. Check hierarchy permission
    if (to.meta.minHierarchy) {
        const userHierarchy = user.value?.role?.hierarchy || 99;
        if (userHierarchy > to.meta.minHierarchy) {
            // Redirect to 403 or home if not enough power
            return next('/403');
        }
    }

    next();
});

export default router;
