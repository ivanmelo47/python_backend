<template>
    <div class="maintenance-shell dashboard-module">
        <div class="maintenance-hero">
            <div>
                <span class="hero-kicker">Panel de sistema</span>
                <h1>Mantenimiento</h1>
                <p class="subtitle">Gestiona el estado global, mensajes y respaldos del sistema.</p>
            </div>

            <div class="hero-status" :class="maintenanceMode ? 'hero-status-warn' : 'hero-status-ok'">
                <Icon
                    :name="maintenanceMode ? 'tool' : 'check-circle'"
                    :size="28"
                    :class="maintenanceMode ? 'text-warning' : 'text-success'"
                />
                <div>
                    <strong>{{ maintenanceMode ? 'En mantenimiento' : 'Operativo' }}</strong>
                    <p>{{ maintenanceMode ? 'Acceso restringido a Supermaster' : 'Acceso normal habilitado' }}</p>
                </div>
            </div>
        </div>

        <nav class="editor-tabs" aria-label="Secciones de mantenimiento">
            <div class="tabs-group">
                <button
                    v-for="tab in maintenanceTabs"
                    :key="tab.id"
                    type="button"
                    class="tab-btn"
                    :class="{ active: activeTab === tab.id }"
                    @click="activeTab = tab.id"
                >
                    <Icon :name="tab.icon" :size="16" />
                    <span>{{ tab.label }}</span>
                </button>
            </div>
        </nav>

        <div class="maintenance-content mt-6">
            <ControlTab
                v-if="activeTab === 'control'"
                v-model:maintenance-message="maintenanceMessage"
                :maintenance-mode="maintenanceMode"
                :require-geolocation="requireGeolocation"
                :is-loading="isLoading"
                @toggle-maintenance="toggleMaintenance"
                @toggle-geolocation="toggleRequireGeolocation"
                @save-message="saveMessageOnly"
            />

            <BackupsTab
                v-if="activeTab === 'backups'"
                :latest-backup="latestBackup"
                :backup-history="backupHistory"
                :is-loading="isLoading"
                :is-backup-loading="isBackupLoading"
                :backup-status-loading="backupStatusLoading"
                @generate-backup="downloadFullBackup"
                @cancel-backup="handleCancelBackup"
            />

            <RestoreTab
                v-if="activeTab === 'restore'"
                :is-loading="isLoading"
            />

            <MailTab
                v-if="activeTab === 'mail'"
            />

            <OnlyOfficeTab
                v-if="activeTab === 'onlyoffice'"
            />

            <VisualTab
                v-if="activeTab === 'visual'"
            />
        </div>

        <div class="info-box maintenance-info-box mt-8">
            <Icon name="info" :size="20" />
            <p>Nota: Al activar el modo mantenimiento, todos los usuarios (excepto Supermaster) serán desconectados. Asegúrate de tener acceso a la ruta <code>/master-login</code> en caso de emergencia.</p>
        </div>
    </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, inject, watch } from 'vue';
import { api } from '@/services/api';
import { useAlert } from '@/composables/useAlert';
import Icon from '@/components/Icon.vue';

// Tabs
import ControlTab from './maintenance/components/ControlTab.vue';
import BackupsTab from './maintenance/components/BackupsTab.vue';
import RestoreTab from './maintenance/components/RestoreTab.vue';
import MailTab from './maintenance/components/MailTab.vue';
import OnlyOfficeTab from './maintenance/components/OnlyOfficeTab.vue';
import VisualTab from './maintenance/components/VisualTab.vue';

const activeTab = ref(localStorage.getItem('maintenance_active_tab') || 'control');

watch(activeTab, (newTab) => {
    localStorage.setItem('maintenance_active_tab', newTab);
});

const maintenanceTabs = [
    { id: 'control', label: 'Control', icon: 'settings' },
    { id: 'backups', label: 'Respaldos', icon: 'database' },
    { id: 'restore', label: 'Restauración', icon: 'refresh-ccw' },
    { id: 'mail', label: 'Correo', icon: 'mail' },
    { id: 'onlyoffice', label: 'OnlyOffice', icon: 'file-text' },
    { id: 'visual', label: 'Visual', icon: 'eye' }
];

const maintenanceMode = ref(false);
const maintenanceMessage = ref('');
const requireGeolocation = ref(false);
const isLoading = ref(false);
const isBackupLoading = ref(false);
const latestBackup = ref(null);
const backupStatusLoading = ref(false);
const backupHistory = ref([]);
let backupRefreshTimer = null;

const alert = useAlert();
const layoutConfig = inject('layoutConfig');

const fetchStatus = async () => {
    isLoading.value = true;
    try {
        const response = await api.system.getMaintenanceMode();
        maintenanceMode.value = response.data.data.maintenance_mode;
        maintenanceMessage.value = response.data.data.maintenance_message || '';
        requireGeolocation.value = !!response.data.data.require_geolocation;
    } catch (error) {
        console.error('Error:', error);
        alert.toast.error('Error', 'No se pudo obtener el estado del sistema');
    } finally {
        isLoading.value = false;
    }
};

const fetchLatestBackupStatus = async () => {
    backupStatusLoading.value = true;
    try {
        const response = await api.system.getLatestFullBackup();
        latestBackup.value = response.data?.data?.backup || null;
    } catch (error) {
        console.error('Error fetching backup status:', error);
    } finally {
        backupStatusLoading.value = false;
    }
};

const fetchBackupHistory = async () => {
    try {
        const response = await api.system.getFullBackupHistory();
        backupHistory.value = response.data?.data?.backups || [];
    } catch (error) {
        console.error('Error fetching backup history:', error);
    }
};

const toggleMaintenance = async (e) => {
    const newValue = e.target.checked;
    e.target.checked = !newValue; // Revert visually to wait for confirmation

    const action = newValue ? 'activar' : 'desactivar';
    const confirmed = await alert.fire({
        title: `¿${action.charAt(0).toUpperCase() + action.slice(1)} Mantenimiento?`,
        text: `Esto afectará a todos los usuarios del sistema.`,
        type: 'warning',
        showCancel: true,
        confirmText: `Sí, ${action}`,
        cancelText: 'Cancelar'
    });

    if (!confirmed) return;

    isLoading.value = true;
    try {
        await api.system.toggleMaintenanceMode({
            status: newValue,
            message: maintenanceMessage.value,
            require_geolocation: requireGeolocation.value,
        });

        await fetchStatus();
        if (maintenanceMode.value) {
            alert.toast.info('Mantenimiento Activado', 'El sistema ahora está restringido.');
        } else {
            alert.toast.success('Sistema Operativo', 'El sistema vuelve a estar disponible.');
        }
    } catch (error) {
        alert.toast.error('Error', 'No se pudo cambiar el estado.');
        await fetchStatus();
    } finally {
        isLoading.value = false;
    }
};

const saveMessageOnly = async () => {
    isLoading.value = true;
    try {
        await api.system.toggleMaintenanceMode({
            status: maintenanceMode.value,
            message: maintenanceMessage.value,
            require_geolocation: requireGeolocation.value,
        });
        alert.toast.success('Mensaje Actualizado', 'El mensaje se ha guardado.');
    } catch (error) {
        alert.toast.error('Error', 'No se pudo guardar el mensaje');
    } finally {
        isLoading.value = false;
    }
};

const toggleRequireGeolocation = async (e) => {
    const newValue = e.target.checked;
    isLoading.value = true;
    try {
        await api.system.toggleMaintenanceMode({
            status: maintenanceMode.value,
            message: maintenanceMessage.value,
            require_geolocation: newValue,
        });
        requireGeolocation.value = newValue;
        alert.toast.success('Configuración actualizada', 'Prioridad de ubicación actualizada.');
    } catch (error) {
        alert.toast.error('Error', 'No se pudo actualizar la ubicación.');
        await fetchStatus();
    } finally {
        isLoading.value = false;
    }
};

const downloadFullBackup = async () => {
    const confirmed = await alert.fire({
        title: 'Generar respaldo completo',
        text: 'Se creará en segundo plano y se enviará un enlace por correo. ¿Continuar?',
        type: 'warning',
        showCancel: true,
        confirmText: 'Sí, generar',
        cancelText: 'Cancelar'
    });

    if (!confirmed) return;

    isBackupLoading.value = true;
    try {
        await api.system.requestFullBackup();
        await fetchLatestBackupStatus();
        await fetchBackupHistory();
        alert.toast.success('Respaldo en cola', 'Te avisaremos por correo cuando esté listo.');
    } catch (error) {
        alert.toast.error('Error', 'No se pudo encolar el respaldo.');
    } finally {
        isBackupLoading.value = false;
    }
};

const handleCancelBackup = async () => {
    const confirmed = await alert.fire({
        title: '¿Cancelar proceso atascado?',
        text: 'Esto marcará como fallido cualquier proceso de respaldo que se haya quedado colgado, permitiéndote generar uno nuevo.',
        type: 'warning',
        showCancel: true,
        confirmText: 'Sí, cancelar proceso',
        cancelText: 'Volver'
    });

    if (!confirmed) return;

    isBackupLoading.value = true;
    try {
        await api.system.cancelActiveBackups();
        alert.toast.success('Cancelado', 'Los procesos colgados se han marcado como fallidos.');
        await fetchBackupHistory();
        await fetchLatestBackupStatus();
    } catch (error) {
        console.error('Cancel backup error:', error);
        alert.toast.error('Error', error?.response?.data?.message || 'No se pudo cancelar el respaldo.');
    } finally {
        isBackupLoading.value = false;
    }
};

onMounted(async () => {
    if (layoutConfig?.fitContentToScreen) layoutConfig.fitContentToScreen.value = false;

    await fetchStatus();
    await fetchLatestBackupStatus();
    await fetchBackupHistory();

    backupRefreshTimer = window.setInterval(async () => {
        await fetchLatestBackupStatus();
        await fetchBackupHistory();
    }, 10000);
});

onUnmounted(() => {
    if (layoutConfig?.fitContentToScreen) layoutConfig.fitContentToScreen.value = true;
    if (backupRefreshTimer) {
        window.clearInterval(backupRefreshTimer);
        backupRefreshTimer = null;
    }
    // Clear active tab when leaving the view
    localStorage.removeItem('maintenance_active_tab');
});
</script>


