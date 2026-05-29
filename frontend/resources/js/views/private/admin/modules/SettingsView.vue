<template>
    <div class="dashboard-module">

        <!-- Tabs -->
        <ModuleTabs
            v-if="showTabs && !isRoot"
            :items="moduleInfo?.children || []"
            :base-path="moduleInfo?.path"
        />

        <!-- Root: shortcuts -->
        <div v-if="isRoot" class="module-shortcuts-grid">
            <router-link
                v-for="child in moduleInfo?.children"
                :key="child.path"
                :to="child.path"
                class="shortcut-card"
            >
                <div class="shortcut-icon-wrapper">
                    <DynamicIcon
                        :name="child.icon || 'circle'"
                        :databaseData="child.dbIcon"
                        :size="40"
                    />
                </div>

                <div class="shortcut-content">
                    <h3>{{ child.name }}</h3>
                    <p>{{ child.description }}</p>
                </div>
            </router-link>
        </div>

        <!-- Child views -->
        <router-view v-else></router-view>
    </div>
</template>

<script setup>
import { computed } from 'vue';
import { useRoute } from 'vue-router';
import DynamicIcon from '@/components/DynamicIcon.vue';
import ModuleTabs from '../components/ModuleTabs.vue';
import { useAuth } from '@/composables/useAuth';
import { generateNavigation } from '@/utils/navigation-generator';
import adminDashboardRoutes from '@/routes/admin-dashboard';
import { useDynamicRoutes } from '@/composables/useDynamicRoutes';

const route = useRoute();
const { user } = useAuth();
const { mappedRoutes } = useDynamicRoutes();

const moduleInfo = computed(() => {
    const userHierarchy = user.value?.role?.hierarchy || 99;

    // Find Dashboard layout children
    const layoutRoute = adminDashboardRoutes[0];
    if (!layoutRoute || !layoutRoute.children) return null;

    // Merge static and dynamic routes
    const allRoutes = [...layoutRoute.children, ...mappedRoutes.value];

    // Generate full navigation tree
    const navTree = generateNavigation(allRoutes, userHierarchy, layoutRoute.path, {
        ignoreSidebarVisibility: true
    });

    // Find the current module (Configuracion)
    const parentPath = route.matched[1]?.path || route.path;
    const module = navTree.find(m => m.path === parentPath);

    return module || null;
});

const showTabs = computed(() => {
    return !!(route.meta.showTabs || route.matched.find(m => m.meta.showTabs)?.meta.showTabs);
});

const isRoot = computed(() => {
    const parentPath = route.matched[1]?.path || route.path;
    const normalized = route.path.endsWith('/') ? route.path.slice(0, -1) : route.path;
    return normalized === parentPath;
});
</script>
