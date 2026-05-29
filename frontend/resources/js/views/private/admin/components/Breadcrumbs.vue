<template>
    <nav v-if="showBreadcrumbs" class="breadcrumbs-nav">
        <ul class="breadcrumbs-list">
            <li class="breadcrumb-item">
                <router-link to="/dashboard" class="home-link">
                    <Icon name="dashboard" :size="16" />
                </router-link>
            </li>
            
            <li v-for="(crumb, index) in breadcrumbs" :key="index" class="breadcrumb-item">
                <span class="separator">/</span>
                <router-link 
                    v-if="index < breadcrumbs.length - 1" 
                    :to="crumb.path" 
                    class="breadcrumb-link"
                >
                    {{ crumb.title }}
                </router-link>
                <span v-else class="breadcrumb-current">{{ crumb.title }}</span>
            </li>
        </ul>
    </nav>
</template>

<script setup>
import { computed } from 'vue';
import { useRoute } from 'vue-router';
import Icon from '@/components/Icon.vue';

const route = useRoute();

const breadcrumbs = computed(() => {
    const matched = route.matched;
    const crumbs = [];

    matched.forEach((record) => {
        // Skip root /dashboard if it's the home, otherwise it gets redundant
        if (record.path === '/dashboard') return;
        
        // Skip child routes with empty path (like DashboardHome)
        if (record.path === '/dashboard/' || record.path === '') return;

        if (record.meta && record.meta.title) {
            crumbs.push({
                title: record.meta.title,
                path: record.path
            });
        }
    });

    return crumbs;
});

const showBreadcrumbs = computed(() => {
    // Check if explicitly disabled in meta for current route or any parent
    const disabled = route.matched.some(record => record.meta.breadcrumbs === false);
    return !disabled && breadcrumbs.value.length > 0;
});
</script>

<style lang="scss" scoped>
// Minimal styles here, moving most to _dashboard.scss as requested
</style>
