<template>
    <div class="module-tabs">
        <router-link 
            v-for="item in items" 
            :key="item.path"
            :to="resolvePath(item.path)"
            class="tab-item"
            :class="{ active: isActive(item.path) }"
        >
            <DynamicIcon :name="item.icon || 'circle'" :databaseData="item.dbIcon" :size="18" class="tab-icon" />
            <span>{{ item.name }}</span>
        </router-link>
    </div>
</template>

<script setup>
import { useRoute } from 'vue-router';
import DynamicIcon from '@/components/DynamicIcon.vue';

const route = useRoute();

const props = defineProps({
    items: {
        type: Array,
        required: true
    },
    basePath: {
        type: String,
        default: ''
    }
});

const resolvePath = (path) => {
    // If it's an absolute path, return it
    if (path.startsWith('/')) return path;
    
    // If we have a base path, prepend it
    if (props.basePath) {
        return `${props.basePath}/${path}`.replace(/\/+/g, '/');
    }
    
    // Otherwise return as is (relative)
    return path;
};

const isActive = (path) => {
    // Compare full active path vs resolved tab path
    const resolved = resolvePath(path);
    // Remove trailing slashes for clean comparison
    const currentPath = route.path.endsWith('/') ? route.path.slice(0, -1) : route.path;
    const targetPath = resolved.endsWith('/') ? resolved.slice(0, -1) : resolved;
    
    // Check if current route starts with this tab's path (for nested routes inside the tab)
    return currentPath === targetPath || currentPath.startsWith(targetPath + '/');
};
</script>

<style lang="scss" scoped>
.module-tabs {
    display: flex;
    align-items: center;
    background: var(--bg-secondary);
    padding: 0.35rem;
    border-radius: 1rem;
    margin-bottom: 1.5rem;
    width: 100%;
    overflow-x: auto;
    overflow-y: hidden;
    white-space: nowrap;
    gap: 0.25rem;
    
    // Hide scrollbar but allow scrolling
    scrollbar-width: none; // Firefox
    &::-webkit-scrollbar {
        display: none; // Chrome/Safari/Edge
    }

    // Smooth scroll for touch devices
    -webkit-overflow-scrolling: touch;
    
    .tab-item {
        display: flex;
        align-items: center;
        gap: 0.65rem;
        padding: 0.6rem 1.2rem;
        border-radius: 0.75rem;
        color: var(--text-secondary);
        font-weight: 600;
        font-size: 0.9rem;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        text-decoration: none;
        white-space: nowrap;
        user-select: none;
        flex-shrink: 0; // Prevent tabs from shrinking
        
        &:hover {
            color: var(--text-primary);
            background: rgba(var(--primary-rgb), 0.05);
        }
        
        &.active {
            background: var(--primary);
            color: #ffffff;
            box-shadow: 0 4px 12px rgba(var(--primary-rgb), 0.25);
            
            .tab-icon {
                color: #ffffff;
            }
            
            &:hover {
                background: var(--primary);
                opacity: 0.9;
            }
        }
        
        .tab-icon {
            color: var(--text-tertiary);
            transition: color 0.3s ease;
        }
    }
}

// Media query to adjust spacing on mobile
@media (max-width: 768px) {
    .module-tabs {
        padding: 0.25rem;
        border-radius: 0.85rem;
        
        .tab-item {
            padding: 0.5rem 0.85rem;
            font-size: 0.85rem;
            gap: 0.5rem;
        }
    }
}
</style>
