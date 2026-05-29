<template>
    <div class="layout-dashboard">
        <!-- 1. Sidebar -->
        <Sidebar :is-open="isSidebarOpen" @close="closeSidebarOnMobile" />

        <!-- 2. Main Wrapper -->
        <div class="main-wrapper" :class="{ 'expanded': !isSidebarOpen, 'fit-screen': fitContentToScreen }">
            <!-- 3. Header -->
            <Navbar @toggle-sidebar="toggleSidebar" />

            <!-- 4. Content Content -->
            <Breadcrumbs />

            <main class="dashboard-content">
                <router-view></router-view>
            </main>

            <!-- 5. Footer -->
            <Footer v-show="shouldShowFooter" />
        </div>

        <!-- Mobile Backdrop -->
        <div v-if="isSidebarOpen" class="sidebar-mobile-backdrop" @click="isSidebarOpen = false"></div>
    </div>
</template>

<script setup>
import { ref, computed, provide, watch } from 'vue';
import { useRoute } from 'vue-router';
import Sidebar from '@/views/private/admin/components/Sidebar.vue';
import Navbar from '@/views/private/admin/components/Navbar.vue';
import Footer from '@/views/private/admin/components/Footer.vue';
import Breadcrumbs from '@/views/private/admin/components/Breadcrumbs.vue';
import { api } from '@/services/api';

// Determine initial state: closed on mobile, or user preference on desktop
const isMobile = window.innerWidth < 768;
const storedState = localStorage.getItem('sidebar-state');
const initialState = isMobile ? false : (storedState !== 'closed');

const isSidebarOpen = ref(initialState);
const route = useRoute();

// Allows modules to temporarily override fit-screen behavior.
const fitContentOverride = ref(null);

const fitContentToScreen = computed({
    get() {
        if (fitContentOverride.value !== null) {
            return fitContentOverride.value;
        }

        if (route.meta && route.meta.fitScreen !== undefined) {
            return route.meta.fitScreen;
        }

        return true;
    },
    set(value) {
        fitContentOverride.value = !!value;
    }
});

watch(
    () => route.fullPath,
    () => {
        fitContentOverride.value = null;
    }
);

// Provide this state to children (like Table.vue)
provide('layoutConfig', {
    fitContentToScreen,
    isSidebarOpen
});

const toggleSidebar = () => {
    isSidebarOpen.value = !isSidebarOpen.value;
    localStorage.setItem('sidebar-state', isSidebarOpen.value ? 'open' : 'closed');
};

const closeSidebarOnMobile = () => {
    if (window.innerWidth < 768) {
        isSidebarOpen.value = false;
    }
};

// Visual Settings logic
const visualSettings = ref({
    footerDesktop: true,
    footerMobile: true
});

const currentWindowWidth = ref(window.innerWidth);

const updateWindowWidth = () => {
    currentWindowWidth.value = window.innerWidth;
};

const shouldShowFooter = computed(() => {
    const isMobileView = currentWindowWidth.value < 768;
    return isMobileView ? visualSettings.value.footerMobile : visualSettings.value.footerDesktop;
});

// Update visual settings when saved from Maintenance
const handleVisualSettingsUpdate = (e) => {
    visualSettings.value = {
        footerDesktop: e.detail.visual_footer_desktop,
        footerMobile: e.detail.visual_footer_mobile
    };
};

import { onMounted, onUnmounted } from 'vue';

onMounted(async () => {
    window.addEventListener('resize', updateWindowWidth);
    window.addEventListener('visual-settings-updated', handleVisualSettingsUpdate);
    
    try {
        const response = await api.system.getVisualSettings();
        if (response.data && response.data.data) {
            visualSettings.value = {
                footerDesktop: response.data.data.visual_footer_desktop,
                footerMobile: response.data.data.visual_footer_mobile
            };
        }
    } catch (e) {
        console.error('Failed to load visual settings', e);
    }
});

onUnmounted(() => {
    window.removeEventListener('resize', updateWindowWidth);
    window.removeEventListener('visual-settings-updated', handleVisualSettingsUpdate);
});
</script>
