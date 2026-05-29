<template>
    <div id="app">
        <GlobalAlert />
        <router-view />
    </div>
</template>

<script setup>
import GlobalAlert from '@/components/GlobalAlert.vue';
import { useScale } from '@/composables/useScale';

const { scale } = useScale(); // Initialize scale on app load
// Root component for the application
</script>

<style scoped>
#app {
    min-height: 100vh;
    animation: fadeIn 0.5s ease;
}

@keyframes fadeIn {
    from {
        opacity: 0;
    }

    to {
        opacity: 1;
    }
}
</style>
