<template>
    <div class="dashboard-module">
        <div class="module-header">
            <h2 class="module-title">Auditoría de Acciones</h2>
            <div class="module-actions">
                <!-- Action buttons -->
            </div>
        </div>
        
        <div class="module-content">
            <div class="empty-state">
                <Icon name="users" :size="48" class="empty-icon" />
                <h3>Registro de Auditoría</h3>
                <p>Consulta el historial de acciones realizadas por los usuarios.</p>
            </div>
        </div>
    </div>
</template>

<script setup>
import Icon from '../../../../../components/Icon.vue';
</script>
