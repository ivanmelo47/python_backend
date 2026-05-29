import { ref } from 'vue';
import { api } from '@/services/api';

const dynamicRoutes = ref([]);
const mappedRoutes = ref([]); // Routes ready for the sidebar/navigation
const isRoutesLoaded = ref(false);

// Use relative path for glob to ensure Vite discovers the files correctly
// The keys in this object will look like: "../views/private/admin/modules/Chatbot.vue"
const viewModules = import.meta.glob('../views/**/*.vue');

export function useDynamicRoutes() {

    /**
     * Map a dynamic route from database to a Vue Router definition
     */
    const mapRoute = (dbRoute) => {
        const routeMeta = dbRoute.meta || {};
        const rawComponentPath = dbRoute.component_path || '';

        // Normalize the input: remove @/views/, leading slashes, and .vue extension
        let cleanPath = rawComponentPath
            .replace(/^@\/views\//, '')
            .replace(/^\//, '')
            .replace(/\.vue$/, '');

        // 1. Exact Match Strategy
        // We look for a module whose key ends with our cleaned path + .vue
        const targetSuffix = `/${cleanPath}.vue`;
        let componentKey = Object.keys(viewModules).find(key =>
            key.endsWith(targetSuffix) || key === `../views/${cleanPath}.vue`
        );

        // 2. Fuzzy/Filename Match Strategy (if no slashes in cleanPath)
        if (!componentKey && !cleanPath.includes('/')) {
            const fileName = `/${cleanPath}.vue`;
            componentKey = Object.keys(viewModules).find(key => key.endsWith(fileName));
        }

        const componentLoader = componentKey ? viewModules[componentKey] : null;

        if (!componentLoader) {
            console.error(`[DynamicRoutes] ERROR: Componente "${cleanPath}" no encontrado.`);
            console.log('[DynamicRoutes] Sugerencia: Revisa que el archivo exista en resources/js/views/');
            console.log('[DynamicRoutes] Módulos disponibles (primeros 5):', Object.keys(viewModules).slice(0, 5));
        } else if (componentKey) {
            console.debug(`[DynamicRoutes] Componente resuelto: ${cleanPath} -> ${componentKey}`);
        }

        // Sanitize path (for the browser URL)
        let path = dbRoute.path || '';
        if (path.startsWith('@/views')) {
            path = dbRoute.name;
        }

        // Ensure path is relative to /dashboard (remove leading slash and potential /dashboard prefix)
        // because we add it as a child of router.addRoute('Dashboard', ...)
        path = path.replace(/^\//, '').replace(/^dashboard\//, '');

        return {
            id: dbRoute.id, // Store ID for tree building
            parent_id: dbRoute.parent_id, // Store Parent ID
            path: path,
            name: dbRoute.name,
            // Fallback to DynamicRoutesView if not found
            component: componentLoader || (() => import('@/views/private/admin/modules/tools/DynamicRoutesView.vue')),
            meta: {
                ...routeMeta,
                id: dbRoute.id, // Also in meta for easier access
                parent_id: dbRoute.parent_id,
                title: dbRoute.title || routeMeta.title,
                description: dbRoute.description || routeMeta.description,
                requiresAuth: true,
                minHierarchy: dbRoute.minHierarchy || dbRoute.min_hierarchy,
                dbIcon: dbRoute.icon ? {
                    type: dbRoute.icon.type,
                    file_path: dbRoute.icon.file_path,
                    svg_content: dbRoute.icon.svg_content,
                    viewBox: dbRoute.icon.viewBox,
                    // Route-level choice must take precedence for sidebar rendering.
                    color_mode: dbRoute.icon_color_mode || dbRoute.icon.color_mode
                } : null,
                icon: dbRoute.icon ? `db:${dbRoute.name}` : (routeMeta.icon || 'folder'),
                sidebar: routeMeta.sidebar ?? true,
                exact: routeMeta.exact ?? false,
            }
        };
    };

    /**
     * Fetch active routes from API and add them to the router
     */
    const fetchAndRegisterRoutes = async (router) => {
        if (isRoutesLoaded.value) return;

        try {
            console.debug('[DynamicRoutes] Cargando rutas desde la API...');
            const response = await api.dynamicRoutes.getActive();
            if (response.data.success) {
                const routes = response.data.data;
                const flatMapped = routes.map(dbRoute => mapRoute(dbRoute));

                // Build hierarchy
                const roots = [];
                const itemMap = {};

                // Initialize map
                flatMapped.forEach(item => {
                    item.children = [];
                    itemMap[item.id] = item;
                });

                // Link children to parents
                // If a route has parent_id but parent is not present (e.g., inactive parent),
                // we skip it to avoid showing orphan children in sidebar/navigation.
                flatMapped.forEach(item => {
                    if (item.parent_id && itemMap[item.parent_id]) {
                        itemMap[item.parent_id].children.push(item);
                    } else if (!item.parent_id) {
                        roots.push(item);
                    }
                });

                // Register in Vue Router
                // We use a recursive function to register parents before children
                const registerRecursive = (route, parentName) => {
                    if (parentName) {
                        router.addRoute(parentName, route);
                    } else {
                        router.addRoute('Dashboard', route);
                    }

                    if (route.children && route.children.length > 0) {
                        route.children.forEach(child => registerRecursive(child, route.name));
                    }
                };

                roots.forEach(root => registerRecursive(root, 'Dashboard'));

                dynamicRoutes.value = routes;
                mappedRoutes.value = roots; // Store the tree roots
                isRoutesLoaded.value = true;
                console.log('Rutas dinámicas cargadas e inyectadas (Jerárquicas):', routes.length);
            }
        } catch (error) {
            console.error('Error al cargar rutas dinámicas:', error);
        }
    };

    return {
        dynamicRoutes,
        mappedRoutes, // This is now a tree
        isRoutesLoaded,
        fetchAndRegisterRoutes
    };
}
