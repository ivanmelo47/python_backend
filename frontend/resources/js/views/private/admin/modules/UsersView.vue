<template>
    <div class="dashboard-module">
        <!-- Render tabs if configured, but NOT on root (shortcuts view) -->
        <ModuleTabs v-if="showTabs && !isRoot" :items="moduleInfo?.children || []" :base-path="moduleInfo?.path" />

        <div v-if="isRoot" class="module-shortcuts-container">
            <ShortcutCarousel :items="moduleInfo?.children || []" />
        </div>

        <!-- This router-view renders the child routes (Gestion, Historial, etc) -->
        <router-view v-else></router-view>
    </div>
</template>

<script setup>
import { computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
// import { sidebarModules } from '@/views/private/admin/config/side-bar'; // Removed
import DynamicIcon from '@/components/DynamicIcon.vue';
import ModuleTabs from '../components/ModuleTabs.vue';
import ShortcutCarousel from '../components/ShortcutCarousel.vue';
import { useAuth } from '@/composables/useAuth';
import { generateNavigation } from '@/utils/navigation-generator';
import adminDashboardRoutes from '@/routes/admin-dashboard';
import { useDynamicRoutes } from '@/composables/useDynamicRoutes';

const route = useRoute();
const router = useRouter();
const { user } = useAuth();
const { mappedRoutes } = useDynamicRoutes();

const moduleInfo = computed(() => {
    const userHierarchy = user.value?.role?.hierarchy || 99;

    const layoutRoute = adminDashboardRoutes[0];
    if (!layoutRoute || !layoutRoute.children) return null;

    // Merge static and dynamic routes
    const allRoutes = [...layoutRoute.children, ...mappedRoutes.value];

    // Generate navigation including hidden sidebar items
    const navTree = generateNavigation(allRoutes, userHierarchy, layoutRoute.path, {
        ignoreSidebarVisibility: true
    });

    const parentPath = route.matched[1]?.path || route.path;
    return navTree.find(m => m.path === parentPath);
});

/**
 * Check if should show tabs based on route config
 */
const showTabs = computed(() => {
    // Check current route or matched parent for showTabs
    const showTabs = route.meta.showTabs || route.matched.find(m => m.meta.showTabs)?.meta.showTabs;
    return !!showTabs;
});

/**
 * Check if we are exactly at the root users path
 */
const isRoot = computed(() => {
    const parentPath = route.matched[1]?.path || route.path;
    const normalized = route.path.endsWith('/') ? route.path.slice(0, -1) : route.path;
    return normalized === parentPath;
});
</script>
