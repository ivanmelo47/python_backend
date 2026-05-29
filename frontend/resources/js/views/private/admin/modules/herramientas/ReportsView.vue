<template>
    <div class="dashboard-module">
        <div class="module-header">
            <h2 class="module-title">Reportes del Sistema</h2>
            <div class="module-actions">
                <!-- Action buttons -->
            </div>
        </div>
        
        <div class="module-content">
            <div class="empty-state">
                <Icon name="folder" :size="48" class="empty-icon" />
                <h3>Módulo de Reportes</h3>
                <p>Aquí podrás visualizar y exportar reportes del sistema.</p>
            </div>
        </div>
    </div>
</template>

<script setup>
import Icon from '../../../../../components/Icon.vue';
</script>
