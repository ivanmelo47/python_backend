<template>
    <div class="maintenance-grid">
        <section class="maintenance-card">
            <div class="card-heading">
                <div>
                    <span class="section-kicker">Configuración del Servidor</span>
                    <h2>OnlyOffice Document Server</h2>
                </div>
                <div class="status-chip" :class="isConfigured ? 'status-chip-ok' : 'status-chip-warn'">
                    {{ isConfigured ? 'Configurado' : 'Pendiente' }}
                </div>
            </div>

            <div class="maintenance-form-grid">
                <div class="form-group form-group-full">
                    <label>URL del Servidor (Document Server URL)</label>
                    <input 
                        v-model="form.onlyoffice_document_server_url" 
                        type="url" 
                        placeholder="https://onlyoffice.midominio.com"
                        :disabled="isLoading"
                    >
                </div>

                <div class="form-group form-group-full">
                    <label>Secreto JWT (JWT Secret)</label>
                    <input 
                        v-model="form.onlyoffice_jwt_secret" 
                        type="password" 
                        placeholder="••••••••••••••••••••"
                        :disabled="isLoading"
                    >
                </div>
            </div>

            <div class="summary-note">
                <Icon name="info" :size="14" />
                <span>Estos ajustes sobreescriben los valores definidos en el archivo .env del sistema (ONLYOFFICE_DOCUMENT_SERVER_URL y ONLYOFFICE_JWT_SECRET).</span>
            </div>

            <div class="flex justify-end mt-8">
                <button 
                    @click="saveSettings" 
                    class="maintenance-action-btn maintenance-action-btn-primary w-full"
                    :disabled="isLoading"
                >
                    <Icon v-if="isLoading" name="loader" class="animate-spin" />
                    <span>{{ isLoading ? 'Guardando...' : 'Guardar Configuración de OnlyOffice' }}</span>
                </button>
            </div>

            <div class="info-box border-none shadow-none mt-4 p-0 bg-transparent">
                <p class="text-xs opacity-60">
                    Asegúrate de que la URL inicie con http:// o https:// y no tenga una barra (/) al final. El JWT Secret debe coincidir exactamente con el configurado en tu Document Server.
                </p>
            </div>
        </section>
    </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { api } from '@/services/api';
import { useAlert } from '@/composables/useAlert';
import Icon from '@/components/Icon.vue';

const alert = useAlert();
const isLoading = ref(false);
const isConfigured = computed(() => !!form.value.onlyoffice_document_server_url && !!form.value.onlyoffice_jwt_secret);

const form = ref({
    onlyoffice_document_server_url: '',
    onlyoffice_jwt_secret: ''
});

const fetchSettings = async () => {
    isLoading.value = true;
    try {
        const response = await api.system.getOnlyOfficeSettings();
        if (response.data?.data) {
            form.value = { ...form.value, ...response.data.data };
        }
    } catch (error) {
        console.error('Error fetching onlyoffice settings:', error);
        alert.toast.error('Error', 'No se pudieron cargar los ajustes de OnlyOffice');
    } finally {
        isLoading.value = false;
    }
};

const saveSettings = async () => {
    const confirmed = await alert.fire({
        title: '¿Actualizar configuración de OnlyOffice?',
        text: 'Los cambios se aplicarán de inmediato a todos los documentos del sistema.',
        type: 'warning',
        showCancel: true,
        confirmText: 'Sí, actualizar'
    });

    if (!confirmed) return;

    isLoading.value = true;
    try {
        await api.system.updateOnlyOfficeSettings(form.value);
        alert.toast.success('Éxito', 'Configuración de OnlyOffice actualizada correctamente');
    } catch (error) {
        console.error('Error saving onlyoffice settings:', error);
        alert.toast.error('Error', 'No se pudo guardar la configuración');
    } finally {
        isLoading.value = false;
    }
};

onMounted(fetchSettings);
</script>
