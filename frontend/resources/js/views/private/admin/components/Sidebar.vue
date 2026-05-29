<template>
    <aside class="sidebar" :class="{ 'collapsed': !isOpen }">
        <div class="sidebar-header">
            <router-link to="/dashboard" class="brand">
                <DynamicIcon name="dashboard" :size="32" class="brand-icon" />
                <span class="brand-text">AdminPanel</span>
            </router-link>
        </div>

        <div class="sidebar-nav">
            <ul class="nav-list">
                <li v-for="(module, index) in filteredModules" :key="index" class="nav-item-wrapper">
                    <!-- Standard Link (No Children) -->
                    <router-link v-if="!module.children" :to="module.path" class="nav-item"
                        :exact-active-class="module.exact ? 'active' : ''" :active-class="!module.exact ? 'active' : ''"
                        @click="closeSidebarOnMobile">
                        <div class="icon-wrapper">
                            <DynamicIcon :name="module.icon" :databaseData="module.dbIcon" :size="24" />
                        </div>
                        <span class="nav-text">{{ module.name }}</span>
                    </router-link>

                    <!-- Dropdown Menu (With Children) -->
                    <div v-else class="nav-dropdown">
                        <button class="nav-item dropdown-toggle" :class="{ 'active': isDropdownActive(module, index) }"
                            @click="toggleDropdown(index)">
                            <div class="icon-wrapper">
                                <DynamicIcon :name="module.icon" :databaseData="module.dbIcon" :size="24" />
                            </div>
                            <span class="nav-text" style="flex: 1; text-align: left;">{{ module.name }}</span>
                            <DynamicIcon name="chevronDown" :size="16" class="chevron"
                                :class="{ 'rotate': openDropdowns[index] }" />
                        </button>

                        <div v-show="openDropdowns[index]" class="nav-sublist">
                            <router-link v-for="(child, childIndex) in module.children" :key="childIndex"
                                :to="child.path" class="nav-subitem" active-class="active"
                                @click="handleSubItemClick(index)">
                                <div class="icon-wrapper">
                                    <DynamicIcon :name="child.icon || 'circle'" :databaseData="child.dbIcon"
                                        :size="18" />
                                </div>
                                <span class="nav-text">{{ child.name }}</span>
                            </router-link>
                        </div>
                    </div>
                </li>
            </ul>
        </div>
    </aside>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'; // Consolidated imports
import DynamicIcon from '@/components/DynamicIcon.vue';
// import { sidebarModules } from '@/views/private/admin/config/side-bar'; // Removed static config
import { useRoute, useRouter } from 'vue-router';
import { useAuth } from '@/composables/useAuth';
import { useDynamicRoutes } from '@/composables/useDynamicRoutes';
import { generateNavigation } from '@/utils/navigation-generator';
import adminDashboardRoutes from '@/routes/admin-dashboard'; // Import routes

const props = defineProps({
    isOpen: {
        type: Boolean,
        required: true
    }
});

const emit = defineEmits(['close']);
const route = useRoute();
const router = useRouter();
const { user } = useAuth();
const { mappedRoutes } = useDynamicRoutes(); // Get dynamic routes
const autoCloseDelay = 1000;

const openDropdowns = ref({});

const filteredModules = computed(() => {
    const userHierarchy = user.value?.role?.hierarchy || 99;
    const isSupermaster = user.value?.is_supermaster || false;

    // Generate navigation dynamically from the children of the layout route
    // Assumes adminDashboardRoutes[0] is the main layout
    const layoutRoute = adminDashboardRoutes[0];
    if (!layoutRoute || !layoutRoute.children) return [];

    // Filter static children based on hierarchy AND supermaster status
    const visibleStaticChildren = layoutRoute.children.filter(child => {
        // Check supermaster requirement
        if (child.meta?.supermasterOnly && !isSupermaster) {
            return false;
        }
        return true;
    });

    // Combine static routes with dynamic routes
    const allRoutes = [...visibleStaticChildren, ...mappedRoutes.value];

    return generateNavigation(allRoutes, userHierarchy, layoutRoute.path);
});

const toggleDropdown = (index) => {
    openDropdowns.value[index] = !openDropdowns.value[index];
};

// Check if any child is active to highlight parent
const isDropdownActive = (module, index) => {
    if (!module.children) return false;

    // Check if we are at the root path of the module (e.g., /dashboard/herramientas)
    // or if the URL starts with the module path followed by a slash
    const normalizedPath = module.path.endsWith('/') ? module.path : `${module.path}/`;
    const isRootActive = route.path === module.path || route.path.startsWith(normalizedPath);

    // Or if any child is explicitly active
    const isChildActive = module.children.some(child => {
        const childNormalized = child.path.endsWith('/') ? child.path : `${child.path}/`;
        return route.path === child.path || route.path.startsWith(childNormalized);
    });

    return isRootActive || isChildActive;
};

const closeSidebarOnMobile = () => {
    if (window.innerWidth < 768) {
        emit('close');
    }
};

const handleSubItemClick = (index) => {
    // 1. Close sidebar on mobile immediately (if applicable)
    closeSidebarOnMobile();

    // 2. Auto-close the dropdown ONLY if sidebar is collapsed (mini mode)
    // If expanded, we keep it open so user sees the active submodule context
    if (!props.isOpen) {
        setTimeout(() => {
            openDropdowns.value[index] = false;
        }, autoCloseDelay);
    }
};

// Close dropdowns when navigating away
const checkAndOpenDropdown = () => {
    // If sidebar is collapsed, do not auto-open dropdowns.
    // The active state is sufficient (icon highlight).
    if (!props.isOpen) return;

    filteredModules.value.forEach((module, index) => {
        if (module.children) {
            const isActive = isDropdownActive(module, index);
            if (isActive) {
                openDropdowns.value[index] = true;
            }
        }
    });
};

onMounted(() => {
    checkAndOpenDropdown();
});

watch(
    () => route.path,
    () => {
        // 1. Auto-open active dropdowns
        checkAndOpenDropdown();

        // 2. Close dropdowns that are not active (previous logic)
        filteredModules.value.forEach((module, index) => {
            if (module.children && openDropdowns.value[index]) {
                const isActive = isDropdownActive(module, index);
                if (!isActive) {
                    openDropdowns.value[index] = false;
                }
            }
        });
    }
);

// Watch for sidebar open/close state
watch(
    () => props.isOpen,
    (isOpen) => {
        if (isOpen) {
            // Restore active dropdowns when expanding
            checkAndOpenDropdown();
        } else {
            // Close all dropdowns when collapsing to prevent sticking
            openDropdowns.value = {};
        }
    }
);
</script>
