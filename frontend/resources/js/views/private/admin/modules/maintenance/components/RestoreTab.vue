<template>
    <div class="maintenance-card">
        <div class="restore-panel">
            <div class="restore-panel-header">
                <div>
                    <span class="section-kicker section-kicker-danger">Restauración</span>
                    <h3>Subir ZIP para restaurar</h3>
                </div>
                <span class="restore-warning">Cierra tu sesión al confirmar</span>
            </div>

            <p class="restore-description">
                Esta acción borrará completamente la base de datos configurada y la reconstruirá desde un ZIP local, un enlace directo, o un respaldo previamente generado en el servidor. También restaurará los archivos persistentes incluidos en el respaldo.
            </p>

            <div class="restore-form-grid">
                <div class="restore-field restore-field-wide">
                    <label>Archivo ZIP de respaldo</label>
                    <input
                        type="file"
                        accept=".zip,application/zip"
                        class="form-input w-full rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring focus:ring-primary focus:ring-opacity-50 dark:bg-gray-800 dark:border-gray-600"
                        @change="handleRestoreFileChange"
                        :disabled="isRestoreLoading"
                    >
                    <p class="restore-file-name">{{ restoreFileName || 'Ningún archivo seleccionado' }}</p>
                </div>

                <div class="restore-field restore-field-wide">
                    <label>Enlace directo de respaldo (opcional)</label>
                    <input
                        v-model="restoreDownloadUrl"
                        type="url"
                        class="form-input w-full rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring focus:ring-primary focus:ring-opacity-50 dark:bg-gray-800 dark:border-gray-600"
                        placeholder="https://dominio.com/respaldo.zip"
                        :disabled="isRestoreLoading"
                    >
                    <p class="restore-file-name">Si usas enlace, debe descargar el ZIP directamente al abrirlo en el navegador.</p>
                </div>

                <div class="restore-field restore-field-wide">
                    <label>Elegir respaldo local existente (opcional)</label>
                    <select
                        v-model="restoreLocalFile"
                        class="form-input w-full rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring focus:ring-primary focus:ring-opacity-50 dark:bg-gray-800 dark:border-gray-600"
                        :disabled="isRestoreLoading || isLoadingLocalBackups"
                    >
                        <option value="">Ningún respaldo local seleccionado</option>
                        <option v-for="backup in localBackups" :key="backup.name" :value="backup.name">
                            {{ backup.name }} ({{ backup.size_formatted }} - {{ backup.date }})
                        </option>
                    </select>
                    <p class="restore-file-name">Selecciona un respaldo que ya se encuentre en el servidor (generado por el sistema o subido vía SFTP).</p>
                </div>

                <div class="restore-field">
                    <label>Correo para notificación</label>
                    <input
                        v-model="restoreNotificationEmail"
                        type="email"
                        class="form-input w-full rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring focus:ring-primary focus:ring-opacity-50 dark:bg-gray-800 dark:border-gray-600"
                        placeholder="correo@dominio.com"
                        :disabled="isRestoreLoading"
                    >
                    <p class="restore-file-name">Recibirás un aviso cuando la restauración termine.</p>
                </div>

                <div class="restore-field">
                    <label>Contraseña del Supermaster</label>
                    <input
                        v-model="restorePassword"
                        type="password"
                        class="form-input w-full rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring focus:ring-primary focus:ring-opacity-50 dark:bg-gray-800 dark:border-gray-600"
                        placeholder="Confirma con tu contraseña actual"
                        :disabled="isRestoreLoading"
                    >
                </div>
            </div>

            <div class="flex justify-end mt-4">
                <button
                    @click="requestRestore"
                    class="maintenance-action-btn maintenance-action-btn-danger"
                    :disabled="isLoading || isRestoreLoading || (!restoreSelectedFile && !restoreDownloadUrl.trim() && !restoreLocalFile)"
                >
                    <Icon v-if="isRestoreLoading" name="refresh" :size="16" class="spinning" />
                    {{ isRestoreLoading ? 'Enviando restauración...' : 'Restaurar sistema desde ZIP' }}
                </button>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import Icon from '@/components/Icon.vue';
import { useAlert } from '@/composables/useAlert';
import { api } from '@/services/api';

const props = defineProps({
    isLoading: Boolean
});

const alert = useAlert();

const isRestoreLoading = ref(false);
const isLoadingLocalBackups = ref(false);
const localBackups = ref([]);
const restoreSelectedFile = ref(null);
const restoreFileName = ref('');
const restorePassword = ref('');
const restoreNotificationEmail = ref('');
const restoreDownloadUrl = ref('');
const restoreLocalFile = ref('');

const fetchLocalBackups = async () => {
    isLoadingLocalBackups.value = true;
    try {
        const response = await api.system.getLocalBackups();
        localBackups.value = response.data?.data?.local_backups || [];
    } catch (error) {
        console.error('Error fetching local backups:', error);
    } finally {
        isLoadingLocalBackups.value = false;
    }
};

onMounted(() => {
    fetchLocalBackups();
    try {
        const storedUser = JSON.parse(localStorage.getItem('user') || '{}');
        if (storedUser?.email) {
            restoreNotificationEmail.value = storedUser.email;
        }
    } catch (e) {}
});

const handleRestoreFileChange = (event) => {
    const file = event.target.files?.[0] || null;
    restoreSelectedFile.value = file;
    restoreFileName.value = file ? file.name : '';
};

const requestRestore = async () => {
    const confirmed = await alert.fire({
        title: 'Restaurar sistema desde ZIP',
        text: 'Esto borrará la base de datos actual, cargará la nueva y cerrará tu sesión. ¿Deseas continuar?',
        type: 'warning',
        showCancel: true,
        confirmText: 'Sí, restaurar',
        cancelText: 'Cancelar'
    });

    if (!confirmed) return;

    if (!restoreSelectedFile.value && !restoreDownloadUrl.value.trim() && !restoreLocalFile.value) {
        alert.toast.error('Respaldo requerido', 'Debes seleccionar un ZIP, un enlace directo de descarga o un archivo local.');
        return;
    }

    if (!restorePassword.value.trim()) {
        alert.toast.error('Contraseña requerida', 'Debes confirmar con tu contraseña de Supermaster.');
        return;
    }

    const formData = new FormData();
    if (restoreSelectedFile.value) {
        formData.append('backup_zip', restoreSelectedFile.value);
    }
    if (restoreDownloadUrl.value.trim()) {
        formData.append('backup_url', restoreDownloadUrl.value.trim());
    }
    if (restoreLocalFile.value) {
        formData.append('local_backup_file', restoreLocalFile.value);
    }
    formData.append('supermaster_password', restorePassword.value);
    formData.append('notification_email', restoreNotificationEmail.value);

    isRestoreLoading.value = true;
    try {
        await api.system.requestFullRestore(formData);
        alert.toast.success('Restauración en cola', 'La sesión se cerrará y el sistema comenzará a restaurarse.');
        
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        window.location.href = '/login';
    } catch (error) {
        console.error('Restore error:', error);
        alert.toast.error('Error', error?.response?.data?.message || 'No se pudo iniciar la restauración.');
    } finally {
        isRestoreLoading.value = false;
    }
};
</script>
