<template>
    <div class="dashboard-module">
        <!-- Render tabs if configured, but NOT on root (shortcuts view) -->
        <ModuleTabs v-if="showTabs && !isRoot" :items="moduleInfo?.children || []" :base-path="moduleInfo?.path" />

        <div v-if="isRoot" class="module-shortcuts-container">
            <ShortcutCarousel :items="moduleInfo?.children || []" />

            <!-- Finance Specific Overview (Optional if not a child) -->
            <div class="finance-overview-canvas" v-if="moduleInfo">
                <ResumenFinanciero />
            </div>
        </div>

        <!-- Child Route Rendering -->
        <router-view v-else></router-view>
    </div>
</template>

<script setup>
import { computed } from 'vue';
import { useRoute } from 'vue-router';
import DynamicIcon from '@/components/DynamicIcon.vue';
import ModuleTabs from '../components/ModuleTabs.vue';
import ShortcutCarousel from '../components/ShortcutCarousel.vue';
import ResumenFinanciero from './finanzas/ResumenFinanciero.vue';
import { useAuth } from '@/composables/useAuth';
import { generateNavigation } from '@/utils/navigation-generator';
import adminDashboardRoutes from '@/routes/admin-dashboard';
import { useDynamicRoutes } from '@/composables/useDynamicRoutes';

const route = useRoute();
const { user } = useAuth();
const { mappedRoutes } = useDynamicRoutes();

/**
 * Get module information from dynamic routes tree - Copying UsersView logic
 */
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
 * Check if we should show tabs (based on route meta or parent meta)
 */
const showTabs = computed(() => {
    const showTabs = route.meta.showTabs || route.matched.find(m => m.meta.showTabs)?.meta.showTabs;
    return !!showTabs;
});

/**
 * Check if we are exactly at the module root
 */
const isRoot = computed(() => {
    const parentPath = route.matched[1]?.path || route.path;
    const normalized = route.path.endsWith('/') ? route.path.slice(0, -1) : route.path;
    return normalized === parentPath;
});
</script>

<style lang="scss" scoped>
.finance-overview-canvas {
    grid-column: 1 / -1;
    margin-top: 2rem;
}
</style>
