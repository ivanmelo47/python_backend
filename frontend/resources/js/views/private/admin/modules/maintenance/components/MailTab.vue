<template>
    <div class="maintenance-grid">
        <section class="maintenance-card">
            <div class="card-heading">
                <div>
                    <span class="section-kicker">Configuración de Salida</span>
                    <h2>Servidor SMTP</h2>
                </div>
                <div class="status-chip" :class="isConfigured ? 'status-chip-ok' : 'status-chip-warn'">
                    {{ isConfigured ? 'Configurado' : 'Pendiente' }}
                </div>
            </div>

            <div class="maintenance-form-grid">
                <div class="form-group">
                    <label>Mailer</label>
                    <select v-model="form.mail_mailer" :disabled="isLoading">
                        <option value="smtp">SMTP</option>
                        <option value="ses">Amazon SES</option>
                        <option value="mailgun">Mailgun</option>
                        <option value="postmark">Postmark</option>
                        <option value="sendmail">Sendmail</option>
                    </select>
                </div>

                <div class="form-group">
                    <label>Esquema / Cifrado</label>
                    <select v-model="form.mail_encryption" :disabled="isLoading">
                        <option value="null">Ninguno</option>
                        <option value="tls">TLS</option>
                        <option value="ssl">SSL</option>
                    </select>
                </div>

                <div class="form-group form-group-full">
                    <label>Host Servidor</label>
                    <input 
                        v-model="form.mail_host" 
                        type="text" 
                        placeholder="smtp.gmail.com"
                        :disabled="isLoading"
                    >
                </div>

                <div class="form-group">
                    <label>Puerto</label>
                    <input 
                        v-model="form.mail_port" 
                        type="number" 
                        placeholder="587"
                        :disabled="isLoading"
                    >
                </div>

                <div class="form-group">
                    <label>Usuario (Mailing User)</label>
                    <input 
                        v-model="form.mail_username" 
                        type="text" 
                        placeholder="ejemplo@correo.com"
                        :disabled="isLoading"
                    >
                </div>

                <div class="form-group form-group-full">
                    <label>Contraseña</label>
                    <input 
                        v-model="form.mail_password" 
                        type="password" 
                        placeholder="••••••••••••"
                        :disabled="isLoading"
                    >
                </div>
            </div>

            <div class="summary-note">
                <Icon name="info" :size="14" />
                <span>Estos ajustes sobreescriben los valores definidos en el archivo .env del sistema.</span>
            </div>
        </section>

        <section class="maintenance-card">
            <div class="card-heading">
                <div>
                    <span class="section-kicker">Identidad</span>
                    <h2>Remitente Global</h2>
                </div>
            </div>

            <div class="maintenance-form-grid">
                <div class="form-group form-group-full">
                    <label>Email de envío (From Address)</label>
                    <input 
                        v-model="form.mail_from_address" 
                        type="email" 
                        placeholder="no-reply@tuapp.com"
                        :disabled="isLoading"
                    >
                </div>

                <div class="form-group form-group-full">
                    <label>Nombre del remitente (From Name)</label>
                    <input 
                        v-model="form.mail_from_name" 
                        type="text" 
                        placeholder="Mi Aplicación"
                        :disabled="isLoading"
                    >
                </div>
            </div>

            <div class="flex justify-end mt-8">
                <button 
                    @click="saveSettings" 
                    class="maintenance-action-btn maintenance-action-btn-primary w-full"
                    :disabled="isLoading"
                >
                    <Icon v-if="isLoading" name="loader" class="animate-spin" />
                    <span>{{ isLoading ? 'Guardando...' : 'Guardar Configuración de Correo' }}</span>
                </button>
            </div>

            <div class="info-box border-none shadow-none mt-4 p-0 bg-transparent">
                <p class="text-xs opacity-60">
                    Asegúrate de que el puerto {{ form.mail_port }} esté abierto en tu firewall y que las credenciales sean correctas para evitar errores en el envío de notificaciones.
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
const isConfigured = computed(() => !!form.value.mail_host && !!form.value.mail_username);

const form = ref({
    mail_mailer: 'smtp',
    mail_host: '',
    mail_port: 587,
    mail_username: '',
    mail_password: '',
    mail_encryption: 'tls',
    mail_from_address: '',
    mail_from_name: ''
});

const fetchSettings = async () => {
    isLoading.value = true;
    try {
        const response = await api.system.getMailSettings();
        if (response.data?.data) {
            form.value = { ...form.value, ...response.data.data };
        }
    } catch (error) {
        console.error('Error fetching mail settings:', error);
        alert.toast.error('Error', 'No se pudieron cargar los ajustes de correo');
    } finally {
        isLoading.value = false;
    }
};

const saveSettings = async () => {
    const confirmed = await alert.fire({
        title: '¿Actualizar configuración de correo?',
        text: 'Los cambios se aplicarán de inmediato a todos los envíos del sistema.',
        type: 'warning',
        showCancel: true,
        confirmText: 'Sí, actualizar'
    });

    if (!confirmed) return;

    isLoading.value = true;
    try {
        await api.system.updateMailSettings(form.value);
        alert.toast.success('Éxito', 'Configuración de correo actualizada correctamente');
    } catch (error) {
        console.error('Error saving mail settings:', error);
        alert.toast.error('Error', 'No se pudo guardar la configuración');
    } finally {
        isLoading.value = false;
    }
};

onMounted(fetchSettings);
</script>
