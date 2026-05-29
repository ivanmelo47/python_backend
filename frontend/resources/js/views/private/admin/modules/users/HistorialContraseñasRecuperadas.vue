<template>
    <div class="users-list">
        <Table
            title="Historial de Contraseñas Recuperadas"
            :columns="columns"
            :rows="users"
            :pagination="pagination"
            :search-query="searchQuery"
            v-model:items-per-page="itemsPerPage"
            @update:searchQuery="searchQuery = $event"
            @request-data="fetchUsers"
            @row-click="handleRowClick"
            :pagination-mode="CONFIG_PAGINATION_MODE === 'server' ? 'server' : 'client'"
            :loading="isLoading"
            search-placeholder="Buscar anfitrión..."
            card-title-template="Usuario - {email}"
            :show-header-actions="true"
        >
            <!-- Header Actions -->
            <template #header-actions>
                <button class="btn-solid-dark" @click="openCreateModal">
                    <Icon name="plus" :size="16" />
                    NUEVO
                </button>
            </template>

            <!-- Custom Cell: Email -->
            <template #cell-email="{ value }">
                <span class="main-text">{{ value }}</span>
            </template>

            <!-- Custom Cell: Nombre -->
            <template #cell-name="{ value }">
                <span class="main-text">{{ value }}</span>
            </template>

            <!-- Custom Cell: Posicion -->
            <template #cell-role="{ value }">
                <span class="main-text">{{ value }}</span>
            </template>

            <!-- Custom Cell: Estatus -->
            <template #cell-status="{ value }">
                <span :class="['status-badge', value.class]">
                    {{ value.label }}
                </span>
            </template>

            <!-- Custom Cell: Acciones -->
            <template #cell-actions="{ row }">
                <button 
                    v-if="row.status.label === 'Vigente'"
                    class="dropdown-item" 
                    title="Reenviar y Renovar"
                    @click.stop="handleResend(row)"
                >
                    <Icon name="refresh" :size="16" />
                    <span>Reenviar</span>
                </button>
                <div v-else class="dropdown-item disabled" style="opacity: 0.5; cursor: not-allowed;">
                    <Icon :name="row.status.label === 'Usado' ? 'check' : (row.status.label === 'Cancelado' ? 'slash' : 'x')" :size="16" />
                    <span>{{ row.status.label === 'Usado' ? 'Token Usado' : (row.status.label === 'Cancelado' ? 'Token Anulado' : 'Token Expirado') }}</span>
                </div>
            </template>
        </Table>

        <!-- New Request Modal -->
        <ModalForm
            :isVisible="showCreateModal"
            title="Nueva Solicitud de Recuperación"
            :loading="isCreating"
            size="md"
            :columns="1"
            :fields="formFields"
            v-model="createForm"
            :errors="createErrors"
            @close="showCreateModal = false"
            @submit="handleCreateRequest"
            submitLabel="Enviar Enlace"
        >
            <template #header-icon>
                <Icon name="mail" :size="20" />
            </template>
        </ModalForm>

        <ModalInformation
            :is-open="showInfoModal"
            title="Detalles del Usuario"
            :data="selectedUser"
            :columns="[
                { key: 'name', label: 'Nombre Usuario' },
                { key: 'email', label: 'Correo Electrónico' },
                { key: 'role', label: 'Rol asignado' },
                { key: 'created_at', label: 'Fecha de Registro' }
            ]"
            @close="showInfoModal = false"
        />
    </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue';
import Table from '@/views/private/admin/components/Table.vue';
import Icon from '@/components/Icon.vue';
import ModalInformation from '@/views/private/admin/components/ModalInformation.vue';
import ModalForm from '@/views/private/admin/components/ModalForm.vue';
import authApi from '@/services/api/endpoints/auth';
import usersApi from '@/services/api/endpoints/users';
import { useTableData } from '@/composables/useTableData';
import { useTableConfig } from '@/composables/useTableConfig';
import { useAlert } from '@/composables/useAlert';
import { formatDate } from '@/utils/format-date';

const alert = useAlert();

const columns = [
    { key: 'actions', label: 'ACCIONES', headerClass: 'compact', cellClass: 'compact' },
    { key: 'email', label: 'EMAIL' },
    { key: 'name', label: 'NOMBRE' },
    { key: 'role', label: 'POSICIÓN' },
    { key: 'created_at', label: 'FECHA DE REGISTRO' },
    { key: 'expires_at', label: 'FECHA DE EXPIRACIÓN' },
    { key: 'status', label: 'ESTATUS' }
];

// Configuration
const CONFIG_PAGINATION_MODE = 'server'; // 'server' | 'all' (client-mode)

// State (via Composable)
const { itemsPerPage } = useTableConfig();
const searchQuery = ref('');

// Modal State
const showInfoModal = ref(false);
const selectedUser = ref(null);

// New Request Modal State
const showCreateModal = ref(false);
const isCreating = ref(false);
const createForm = reactive({
    user_id: ''
});
const createErrors = ref({});
const userOptions = ref([]);

const formFields = computed(() => [
    {
        key: 'user_id',
        label: 'Seleccionar Usuario',
        type: 'select',
        placeholder: 'Seleccione un usuario...',
        required: true,
        span: 1,
        options: userOptions.value
    }
]);


const handleRowClick = (row) => {
    selectedUser.value = row;
    showInfoModal.value = true;
};

const handleResend = async (row) => {
    if (!confirm(`¿Estás seguro de reenviar el token a ${row.email}? Esto invalidará el token actual y generará uno nuevo.`)) {
        return;
    }

    try {
        await authApi.resendResetLink(row.id);
        alert.toast.success('Éxito', 'Token reenviado exitosamente.');
        fetchUsers(); // Refresh table
    } catch (error) {
        console.error(error);
        const msg = error.response?.data?.message || 'Error al reenviar el token.';
        alert.toast.error('Error', msg);
    }
};

const openCreateModal = async () => {
    createForm.user_id = '';
    createErrors.value = {};
    showCreateModal.value = true;

    if (userOptions.value.length === 0) {
        try {
            // Fetch selectable users (already filtered by backend)
            const response = await usersApi.getSelectableUsers();
            
            // Expected response: { status: 'success', data: [...] }
            const usersData = response.data?.data || response.data || [];
            
            userOptions.value = usersData.map(u => ({
                id: u.id,
                name: `${u.name} (${u.email})`
            }));
        } catch (error) {
            console.error(error);
            alert.toast.error('Error', 'No se pudieron cargar los usuarios.');
        }
    }
};

const handleCreateRequest = async () => {
    if (!createForm.user_id) {
        createErrors.value = { user_id: ['Debe seleccionar un usuario.'] };
        return;
    }

    isCreating.value = true;

    try {
        await authApi.sendAdminResetLink(createForm.user_id);
        alert.toast.success('Enviado', 'Enlace de recuperación enviado exitosamente.');
        showCreateModal.value = false;
        fetchUsers();
    } catch (error) {
        console.error(error);
        const msg = error.response?.data?.message || 'Error al enviar la solicitud.';
        if (error.response?.data?.errors) {
            createErrors.value = error.response.data.errors;
        } else {
            alert.toast.error('Error', msg);
        }
    } finally {
        isCreating.value = false;
    }
};



const getStatus = (item) => {
    if (item.is_anulled) {
        return { label: 'Cancelado', class: 'status-anulled' };
    }

    if (item.is_used) {
        return { label: 'Usado', class: 'status-used' };
    }
    
    const expiryDate = new Date(item.expires_at);
    const now = new Date();
    
    if (expiryDate < now) {
        return { label: 'Expirado', class: 'status-expired' };
    }
    
    return { label: 'Vigente', class: 'status-active' };
    };

// Data Transformer
const transformUser = (item) => ({
    id: item.uuid,
    email: item.user?.email || 'N/A',
    name: item.user?.name || 'N/A',
    role: item.user?.role?.name || 'N/A',
    // Preserve other item properties if needed
    created_at: formatDate(item.created_at),
    expires_at: formatDate(item.expires_at),
    status: getStatus(item)
});

// Use Composable
const { 
    data: users, 
    loading: isLoading, 
    pagination, 
    fetchData: fetchUsers 
} = useTableData(authApi.getPasswordResetTokens, {
    transformer: transformUser,
    mode: CONFIG_PAGINATION_MODE,
    itemsPerPage,
    searchQuery
});

</script>

<style scoped>
.status-badge {
    padding: 4px 8px;
    border-radius: 4px;
    font-size: 0.85em;
    font-weight: 500;
    display: inline-block;
}

.status-active {
    background-color: rgba(34, 197, 94, 0.1);
    color: #22c55e;
    border: 1px solid rgba(34, 197, 94, 0.2);
}

.status-used {
    background-color: rgba(59, 130, 246, 0.1);
    color: #3b82f6;
    border: 1px solid rgba(59, 130, 246, 0.2);
}

.status-expired {
    background-color: rgba(239, 68, 68, 0.1);
    color: #ef4444;
    border: 1px solid rgba(239, 68, 68, 0.2);
}

.status-anulled {
    background-color: rgba(100, 116, 139, 0.1);
    color: #64748b;
    border: 1px solid rgba(100, 116, 139, 0.2);
}
</style>
