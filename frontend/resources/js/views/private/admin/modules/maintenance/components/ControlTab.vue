<template>
    <div class="maintenance-grid">
        <section class="maintenance-card maintenance-summary">
            <div class="card-heading">
                <div>
                    <span class="section-kicker">Estado general</span>
                    <h2>Control principal</h2>
                </div>
                <span class="status-chip" :class="maintenanceMode ? 'status-chip-warn' : 'status-chip-ok'">
                    {{ maintenanceMode ? 'Mantenimiento activo' : 'Sistema activo' }}
                </span>
            </div>

            <div class="status-indicator">
                <Icon
                    :name="maintenanceMode ? 'tool' : 'check-circle'"
                    :size="42"
                    :class="maintenanceMode ? 'text-warning' : 'text-success'"
                />
                <div class="status-text">
                    <h3>El sistema está {{ maintenanceMode ? 'en Mantenimiento' : 'Operativo' }}</h3>
                    <p>{{ maintenanceMode ? 'El acceso está restringido solo a Supermasters.' : 'Todos los usuarios tienen acceso normal al sistema.' }}</p>
                </div>
            </div>

            <div class="summary-note">
                {{ maintenanceMode ? 'Cualquier cambio se aplicará de inmediato a todos los usuarios.' : 'Puedes activar el modo mantenimiento cuando necesites intervenir el sistema.' }}
            </div>
        </section>

        <section class="maintenance-card maintenance-controls">
            <div class="card-heading">
                <div>
                    <span class="section-kicker">Configuración</span>
                    <h2>Controles del sistema</h2>
                </div>
            </div>

            <div class="action-area">
                <div class="toggle-wrapper">
                    <span class="label">Activar modo mantenimiento</span>
                    <label class="switch">
                        <input
                            type="checkbox"
                            :checked="maintenanceMode"
                            @change="$emit('toggle-maintenance', $event)"
                            :disabled="isLoading"
                        >
                        <span class="slider round"></span>
                    </label>
                </div>

                <div class="toggle-wrapper mt-4">
                    <span class="label">Requerir ubicación exacta en login</span>
                    <label class="switch">
                        <input
                            type="checkbox"
                            :checked="requireGeolocation"
                            @change="$emit('toggle-geolocation', $event)"
                            :disabled="isLoading"
                        >
                        <span class="slider round"></span>
                    </label>
                </div>

                <div class="message-wrapper mt-6">
                    <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                        Mensaje para los usuarios
                    </label>
                    <textarea
                        :value="maintenanceMessage"
                        @input="$emit('update:maintenanceMessage', $event.target.value)"
                        placeholder="Ingresa un mensaje personalizado para mostrar en el login..."
                        :disabled="isLoading"
                    ></textarea>
                    <div class="flex justify-end mt-2" v-if="maintenanceMode">
                        <button
                            @click="$emit('save-message')"
                            class="maintenance-action-btn maintenance-action-btn-secondary"
                            :disabled="isLoading"
                        >
                            Actualizar mensaje
                        </button>
                    </div>
                </div>
            </div>
        </section>
    </div>
</template>

<script setup>
import Icon from '@/components/Icon.vue';

defineProps({
    maintenanceMode: Boolean,
    maintenanceMessage: String,
    requireGeolocation: Boolean,
    isLoading: Boolean
});

defineEmits(['toggle-maintenance', 'toggle-geolocation', 'update:maintenanceMessage', 'save-message']);
</script>
