<template>
    <div class="users-list">
        <Table
            title="Historial de Sesiones"
            :columns="columns"
            :rows="users"
            :pagination="pagination"
            :search-query="searchQuery"
            :sort-options="sortOptions"
            module-id="logins"
            v-model:items-per-page="itemsPerPage"
            @update:searchQuery="searchQuery = $event"
            @request-data="fetchUsers"
            @row-click="handleRowClick"
            :pagination-mode="CONFIG_PAGINATION_MODE === 'server' ? 'server' : 'client'"
            :loading="isLoading"
            search-placeholder="Buscar por usuario o IP..."
            card-title-template="Usuario - {name}"
            :show-header-actions="true"
        >
            <!-- Header Actions -->
            <template #header-actions>
                <!-- No generic actions for history -->
            </template>

            <!-- Custom Cell: Actions -->
            <template #cell-actions="{ row }">
                <button
                    v-if="row.status === 'Activo'"
                    type="button"
                    @click.stop="confirmForceLogout(row)"
                    class="dropdown-item delete"
                    title="Forzar Cierre de Sesión"
                >
                    <Icon name="logout" :size="16" />
                    <span>Forzar Salida</span>
                </button>
                <div v-else class="dropdown-item disabled" style="opacity: 0.5; cursor: not-allowed;">
                    <Icon name="check" :size="16" />
                    <span>Sesión Cerrada</span>
                </div>
            </template>

            <!-- Custom Cell: Location -->
            <template #cell-location="{ row }">
                <div v-if="row.location && row.location.lat && row.location.lon" style="font-size: 0.9em;">
                    <!-- <div style="font-weight: bold;">{{ row.location.city || 'Desconocida' }}</div>
                    <div style="color: #666;">{{ row.location.country || '' }}</div> -->

                    <div style="display: flex; gap: 8px; margin-top: 8px; align-items: center;">
                        <!-- Internal Map Button -->
                        <button
                            type="button"
                            class="map-action-pill"
                            @click.stop="openMap(row)"
                            title="Ver en mapa interactivo"
                        >
                            <Icon name="map" :size="14" />
                            <span>Explorar</span>
                        </button>

                        <!-- External Google Maps Link -->
                        <a
                            :href="`https://www.google.com/maps/search/?api=1&query=${row.location.lat},${row.location.lon}`"
                            target="_blank"
                            class="map-action-link"
                            @click.stop
                            title="Abrir en Google Maps"
                        >
                            <Icon name="external-link" :size="14" />
                            <span>Maps</span>
                        </a>
                    </div>
                </div>
                <div v-else style="color: #999; font-style: italic;">
                    N/A
                </div>
            </template>

            <!-- Custom Cell: Status (Kept as it has Badge logic) -->
            <template #cell-status="{ value }">
                <span
                    class="badge"
                    :class="value === 'Activo' ? 'badge-success' : 'badge-danger'"
                    :style="{
                        padding: '4px 8px',
                        borderRadius: '4px',
                        color: 'white',
                        fontWeight: 'bold',
                        fontSize: '0.8em',
                        backgroundColor: value === 'Activo' ? '#28a745' : '#dc3545'
                    }"
                >
                    {{ value }}
                </span>
            </template>

            <template #cell-source_type="{ value }">
                <span
                    class="badge"
                    :style="{
                        padding: '4px 8px',
                        borderRadius: '4px',
                        color: 'white',
                        fontWeight: 'bold',
                        fontSize: '0.8em',
                        backgroundColor:
                                                        value.startsWith('App móvil')
                                ? '#6f42c1'
                                : value === 'Navegador móvil'
                                  ? '#fd7e14'
                                  : value === 'Navegador PC'
                                    ? '#17a2b8'
                                    : '#6c757d'
                    }"
                >
                    {{ value }}
                </span>
            </template>
        </Table>

        <ModalInformation
            :is-open="showInfoModal"
            title="Detalles de la Sesión"
            :data="selectedUser"
            :columns="[
                { key: 'status', label: 'Estado' },
                { key: 'name', label: 'Nombre Usuario' },
                { key: 'email', label: 'Correo Electrónico' },
                { key: 'role', label: 'Rol asignado' },
                { key: 'ip_address', label: 'IP' },
                { key: 'source_type', label: 'Origen de Acceso' },
                { key: 'client_source', label: 'Fuente Cliente' },
                { key: 'client_platform', label: 'Plataforma Cliente' },
                { key: 'user_agent', label: 'User Agent', fullWidth: true, isNote: true },
                { key: 'location_text', label: 'Ubicación' },
                { key: 'login_at', label: 'Inicio de Sesión' },
                { key: 'logout_at', label: 'Cierre de Sesión' },
                { key: 'duration', label: 'Duración' },
                { key: 'last_activity_at', label: 'Última Actividad' }
            ]"
            @close="showInfoModal = false"
        />

        <FloatingMap
            :isOpen="showMapModal"
            :lat="mapData.lat"
            :lon="mapData.lon"
            :title="mapData.title"
            @close="showMapModal = false"
        />
    </div>
</template>

<script setup>
import { ref } from 'vue';
import Table from '@/views/private/admin/components/Table.vue';
import Icon from '@/components/Icon.vue';
import ModalInformation from '@/views/private/admin/components/ModalInformation.vue';
import authApi from '@/services/api/endpoints/auth';
import { useTableData } from '@/composables/useTableData';
import { useTableConfig } from '@/composables/useTableConfig';
import { useAlert } from '@/composables/useAlert';
import FloatingMap from '@/views/private/admin/components/FloatingMap.vue';

const alert = useAlert();

const columns = [
    { key: 'actions', label: 'ACCIONES', headerClass: 'compact', cellClass: 'compact' },
    {
        key: 'status',
        label: 'ESTADO',
    },
    { key: 'email', label: 'EMAIL', cellClass: 'main-text' },
    { key: 'name', label: 'NOMBRE', cellClass: 'main-text' },
    { key: 'role', label: 'POSICIÓN', cellClass: 'main-text' },
    { key: 'ip_address', label: 'DIRECCIÓN IP' },
    { key: 'source_type', label: 'ORIGEN DE ACCESO' },
    { key: 'location', label: 'UBICACIÓN' }, // New Column
    { key: 'login_at', label: 'INICIO DE SESIÓN' },
    { key: 'logout_at', label: 'CIERRE DE SESIÓN' },
    {
        key: 'duration',
        label: 'DURACIÓN',
        component: 'SessionTimer',
        props: (row) => ({
            start: row.raw_login_at,
            end: row.raw_logout_at
        })
    },
    { key: 'last_activity_at', label: 'ÚLTIMA ACTIVIDAD' },
];

// Configuration
const CONFIG_PAGINATION_MODE = 'server'; // 'server' | 'all' (client-mode)

// State (via Composable)
const { itemsPerPage } = useTableConfig();
const searchQuery = ref('');

const sortOptions = [
    { key: 'login_at', label: 'Inicio de Sesión' },
    { key: 'logout_at', label: 'Cierre de Sesión' },
    { key: 'last_activity_at', label: 'Última Actividad' },
    { key: 'status', label: 'Estado' },
    { key: 'email', label: 'Correo Electrónico' },
    { key: 'name', label: 'Nombre de Usuario' },
    { key: 'role', label: 'Posición/Rol' },
    { key: 'ip_address', label: 'Dirección IP' },
    { key: 'source_type', label: 'Origen de Acceso' },
];

// Modal State
const showInfoModal = ref(false);
const selectedUser = ref(null);

const handleRowClick = (row) => {
    selectedUser.value = row;
    showInfoModal.value = true;
};

// Map Modal State
const showMapModal = ref(false);
const mapData = ref({ lat: 0, lon: 0, title: '' });

const openMap = (row) => {
    if (row.location && row.location.lat && row.location.lon) {
        mapData.value = {
            lat: row.location.lat,
            lon: row.location.lon,
            title: `Ubicación de Acceso: ${row.name || row.email}`
        };
        showMapModal.value = true;
    }
};

const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleString('es-MX', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
    });
};

const calculateDuration = (startStr, endStr) => {
    if (!startStr) return 'N/A';
    const start = new Date(startStr);
    const end = endStr ? new Date(endStr) : new Date(); // If active, calc vs NOW

    const diffMs = end - start;
    if (diffMs < 0) return '0 s';

    const seconds = Math.floor(diffMs / 1000);
    const minutes = Math.floor(seconds / 60);
    const hours = Math.floor(minutes / 60);
    const days = Math.floor(hours / 24);

    if (days > 0) return `${days} días ` + (hours % 24 > 0 ? `${hours % 24} h` : '');
    if (hours > 0) return `${hours} h ` + (minutes % 60 > 0 ? `${minutes % 60} min` : '');
    if (minutes > 0) return `${minutes} min`;
    return `${seconds} s`;
};

const detectLoginSource = (clientSource, clientPlatform, userAgent) => {
    if (clientSource === 'mobile-app') {
        if (clientPlatform === 'android') return 'App móvil Android';
        if (clientPlatform === 'ios') return 'App móvil iOS';
        return 'App móvil';
    }

    if (!userAgent) return 'Desconocido';

    const ua = String(userAgent).toLowerCase();
    const isMobileDevice = /(android|iphone|ipad|ipod|mobile)/.test(ua);
    const isBrowser = /(mozilla|chrome|safari|firefox|edg|opr\/|opera)/.test(ua);
    const isMobileApp = /(okhttp|reactnative|react-native|expo|hermes|cfnetwork|alamofire|darwin)/.test(ua);
    const isAndroidApp = /(okhttp|android)/.test(ua);
    const isIosApp = /(cfnetwork|darwin|ios|iphone|ipad)/.test(ua);

    if (isMobileApp && isAndroidApp) return 'App móvil Android';
    if (isMobileApp && isIosApp) return 'App móvil iOS';
    if (isMobileApp) return 'App móvil';
    if (isBrowser && isMobileDevice) return 'Navegador móvil';
    if (isBrowser) return 'Navegador PC';

    return 'Cliente/API';
};

// Data Transformer
const transformUser = (item) => ({
    id: item.id, // ID is needed for backend action
    uuid: item.uuid,
    status: item.derived_status || (item.logout_at ? 'Inactivo' : 'Activo'), // Fallback just in case
    email: item.user?.email || 'N/A',
    name: item.user?.name || 'N/A',
    role: item.user?.role?.name || 'N/A',
    ip_address: item.ip_address || 'N/A',
    source_type: detectLoginSource(item.client_source, item.client_platform, item.user_agent),
    client_source: item.client_source || 'N/A',
    client_platform: item.client_platform || 'N/A',
    user_agent: item.user_agent || 'N/A',
    location: item.location, // Pass raw location object
    location_text: item.location && item.location.city ? `${item.location.city}, ${item.location.country}` : 'N/A', // For Modal
    login_at: formatDate(item.login_at),
    logout_at: formatDate(item.derived_logout_at || item.logout_at), // Use derived logout time if available
    duration: calculateDuration(item.login_at, item.derived_logout_at || item.logout_at),
    last_activity_at: formatDate(item.last_activity_at),
    // Raw data for modal/logic
    raw_login_at: item.login_at,
    raw_logout_at: item.derived_logout_at || item.logout_at
});

// Use Composable
const {
    data: users,
    loading: isLoading,
    pagination,
    fetchData: fetchUsers
} = useTableData(authApi.getLoginActivities, {
    transformer: transformUser,
    mode: CONFIG_PAGINATION_MODE,
    itemsPerPage,
    searchQuery
});

const confirmForceLogout = async (row) => {
    const confirmed = await alert.fire({
        title: '¿Forzar salida?',
        text: `¿Estás seguro de que deseas cerrar la sesión de ${row.email}? El usuario perderá acceso inmediatamente.`,
        type: 'warning',
        showCancel: true,
        confirmText: 'Sí, cerrar sesión',
        cancelText: 'Cancelar'
    });

    if (!confirmed) return;

    try {
        await authApi.forceLogout(row.id);
        fetchUsers();
        alert.toast.success('Éxito', 'Sesión cerrada correctamente');
    } catch (error) {
        if (error.response?.status === 403) {
            alert.toast.error('Acceso Denegado', error.response.data.message || 'No tienes permisos para realizar esta acción.');
        } else {
            console.error('Error forcing logout:', error);
            alert.toast.error('Error', 'Hubo un error al intentar cerrar la sesión.');
        }
    }
};

</script>
