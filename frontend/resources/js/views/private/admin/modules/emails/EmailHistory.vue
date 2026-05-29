<template>
    <div class="users-list">
        <div v-if="!isMaster" class="access-denied">
            <Icon name="lock" :size="48" />
            <h3>Acceso Restringido</h3>
            <p>Este módulo es exclusivo para administradores globales.</p>
        </div>

        <Table 
            v-else 
            title="Historial de Correos" 
            :columns="columns" 
            :rows="emails" 
            :pagination="pagination"
            :search-query="searchQuery" 
            :sort-options="sortOptions"
            module-id="emails"
            v-model:items-per-page="itemsPerPage" 
            @update:searchQuery="searchQuery = $event"
            @request-data="fetchEmails" 
            @row-click="handleRowClick"
            :pagination-mode="CONFIG_PAGINATION_MODE === 'server' ? 'server' : 'client'" 
            :loading="isLoading"
            search-placeholder="Buscar por correo o asunto..." 
            :show-header-actions="true"
        >
            <!-- Custom Cell: Destinatario -->
            <template #cell-recipient="{ row }">
                <div class="user-info">
                    <span class="name">{{ row.recipient_name }}</span>
                    <span class="email">{{ row.recipient_email }}</span>
                </div>
            </template>

            <!-- Custom Cell: Asunto -->
            <template #cell-subject="{ value }">
                <span class="subject-text">{{ value }}</span>
            </template>

            <!-- Custom Cell: Tipo -->
            <template #cell-type="{ value }">
                <span class="badge" :class="getTypeClass(value)">
                    {{ getTypeLabel(value) }}
                </span>
            </template>

            <!-- Custom Cell: Estatus -->
            <template #cell-status="{ value }">
                <span class="badge" :class="getStatusClass(value)">
                    {{ getStatusLabel(value) }}
                </span>
            </template>

            <!-- Custom Cell: Fecha -->
            <template #cell-created_at="{ value }">
                <span class="date-text">{{ formatDate(value) }}</span>
            </template>

            <!-- Custom Cell: Acciones -->
            <template #cell-actions="{ row }">
                <button class="action-btn" @click.stop="openPreview(row)" title="Ver Correo">
                    <Icon name="eye" :size="18" />
                </button>
            </template>
        </Table>

        <ModalEmailPreview 
            v-if="showPreviewModal" 
            :isOpen="showPreviewModal" 
            :emailData="selectedEmail"
            @close="closePreview" 
        />
    </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import Table from '@/views/private/admin/components/Table.vue';
import Icon from '@/components/Icon.vue';
import ModalEmailPreview from './components/ModalEmailPreview.vue';
import { useAuth } from '@/composables/useAuth';
import emailsApi from '@/services/api/endpoints/emails';
import { useTableData } from '@/composables/useTableData';
import { useTableConfig } from '@/composables/useTableConfig';
import { useAlert } from '@/composables/useAlert';
import { formatDate } from '@/utils/format-date';

const { user } = useAuth();
const alert = useAlert();
const isMaster = computed(() => user.value?.role?.name === 'master' || user.value?.role?.hierarchy >= 3);

// Configuration
const CONFIG_PAGINATION_MODE = 'server';
const { itemsPerPage } = useTableConfig();
const searchQuery = ref('');
const showPreviewModal = ref(false);
const selectedEmail = ref(null);

const sortOptions = [
    { key: 'created_at', label: 'Fecha de Envío' },
    { key: 'recipient_email', label: 'Destinatario' },
    { key: 'subject', label: 'Asunto' },
    { key: 'status', label: 'Estado' },
    { key: 'type', label: 'Tipo' },
];

onMounted(() => {
    fetchEmails();
});

const columns = [
    { key: 'recipient', label: 'DESTINATARIO', cellClass: 'main-text' },
    { key: 'subject', label: 'ASUNTO', cellClass: 'main-text' },
    { key: 'type', label: 'TIPO' },
    { key: 'status', label: 'ESTATUS' },
    { key: 'created_at', label: 'FECHA DE ENVÍO' },
    { key: 'actions', label: 'VER', headerClass: 'compact', cellClass: 'compact' }
];

// Composable for Data
const {
    data: emails,
    loading: isLoading,
    pagination,
    fetchData: fetchEmails
} = useTableData(emailsApi.getEmails, {
    mode: CONFIG_PAGINATION_MODE,
    itemsPerPage,
    searchQuery
});

const openPreview = (row) => {
    selectedEmail.value = row;
    showPreviewModal.value = true;
};

const closePreview = () => {
    showPreviewModal.value = false;
    selectedEmail.value = null;
};

const getStatusClass = (status) => {
    switch (status) {
        case 'sent': return 'success';
        case 'failed': return 'danger';
        case 'pending': return 'warning';
        default: return 'secondary';
    }
};

const getStatusLabel = (status) => {
    switch (status) {
        case 'sent': return 'Enviado';
        case 'failed': return 'Fallido';
        case 'pending': return 'Pendiente';
        default: return status || 'Desconocido';
    }
};

const handleRowClick = (row) => {
    openPreview(row);
};

const getTypeClass = (type) => {
    switch (type) {
        case 'confirmation': return 'success';
        case 'login_notification': return 'info';
        case 'password_reset': return 'warning';
        case 'failed_login': return 'danger';
        default: return 'secondary';
    }
};

const getTypeLabel = (type) => {
    switch (type) {
        case 'confirmation': return 'Confirmación';
        case 'login_notification': return 'Login';
        case 'password_reset': return 'Password';
        case 'failed_login': return 'Error';
        case 'general': return 'General';
        default: return type || 'General';
    }
};
</script>

<style scoped lang="scss">
.users-list {
    height: 100%;
    display: flex;
    flex-direction: column;
}

.user-info {
    display: flex;
    flex-direction: column;

    .name {
        font-weight: 600;
        color: var(--text-primary);
    }

    .email {
        font-size: 0.8rem;
        color: var(--text-tertiary);
    }
}

.subject-text {
    font-weight: 500;
}

.badge {
    padding: 0.25rem 0.6rem;
    border-radius: 6px;
    font-size: 0.72rem;
    font-weight: 700;
    text-transform: uppercase;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    min-width: 90px;

    &.success {
        background: rgba(16, 185, 129, 0.15);
        color: #10b981;
    }

    &.info {
        background: rgba(59, 130, 246, 0.15);
        color: #3b82f6;
    }

    &.warning {
        background: rgba(245, 158, 11, 0.15);
        color: #f59e0b;
    }

    &.danger {
        background: rgba(239, 68, 68, 0.15);
        color: #ef4444;
    }

    &.secondary {
        background: var(--bg-tertiary);
        color: var(--text-secondary);
    }
}

.action-btn {
    background: transparent;
    border: none;
    cursor: pointer;
    color: var(--primary);
    padding: 0.4rem;
    border-radius: 8px;
    transition: all 0.2s;

    &:hover {
        background: rgba(var(--primary-rgb), 0.1);
        transform: scale(1.1);
    }
}
</style>
