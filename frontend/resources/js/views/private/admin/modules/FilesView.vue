<template>
    <div class="dashboard-module">
        <div class="module-header">
            <h2 class="module-title">Gestor de Archivos</h2>
            <div class="module-actions">
                <!-- Global actions can go here if needed -->
            </div>
        </div>

        <div class="module-content explorer-wrapper">
            <FileExplorer />
        </div>
    </div>
</template>

<script setup>
import FileExplorer from './files/FileExplorer.vue';
</script>

<style lang="scss" scoped>
.dashboard-module {
    display: flex;
    flex-direction: column;
    min-height: 0;
}

.explorer-wrapper {
    background: var(--bg-primary);
    border-radius: 12px;
    border: 1px solid var(--border-color);
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    flex: 1;
    min-height: 0;
    display: flex;
}
</style>


