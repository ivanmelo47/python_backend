<template>
    <div class="algorithms-list">
        <Table
            title="Algoritmos de Cifrado"
            :columns="columns"
            :rows="algorithms"
            :pagination="pagination"
            :search-query="searchQuery"
            v-model:items-per-page="itemsPerPage"
            @update:searchQuery="searchQuery = $event"
            @request-data="fetchAlgorithms"
            @row-click="handleRowClick"
            :pagination-mode="'client'"
            :loading="isLoading"
            search-placeholder="Buscar algoritmo..."
            card-title-template="Algoritmo - {name}"
            :show-header-actions="false"
        >
            <!-- Custom Cell: Name -->
            <template #cell-name="{ value }">
                <span class="main-text">{{ value }}</span>
            </template>

            <!-- Custom Cell: Description -->
            <template #cell-description="{ value }">
                <span class="main-text">{{ value }}</span>
            </template>

            <!-- Custom Cell: Status -->
            <template #cell-status="{ row }">
                <span class="badge" :class="row.status === 'active' ? 'badge-success' : 'badge-secondary'">
                    {{ row.status === 'active' ? 'Activo' : 'Inactivo' }}
                </span>
            </template>

            <!-- Custom Cell: Acciones -->
            <template #cell-actions="{ row }">
                <button class="dropdown-item" title="Ver detalles">
                    <Icon name="history" :size="16" />
                    <span>Detalles</span>
                </button>
            </template>
        </Table>

        <ModalInformation
            :is-open="showInfoModal"
            title="Detalles del Algoritmo"
            :data="selectedAlgorithm"
            :columns="[
                { key: 'name', label: 'Nombre' },
                { key: 'description', label: 'Descripción' },
                { key: 'status', label: 'Estado' }
            ]"
            show-edit-button
            @edit="showInfoModal = false; openEditModal(selectedAlgorithm)"
            @close="showInfoModal = false"
        >
            <template #value-status v-if="selectedAlgorithm">
                <span class="badge" :class="selectedAlgorithm.status === 'active' ? 'badge-success' : 'badge-secondary'">
                    {{ selectedAlgorithm.status === 'active' ? 'Activo' : 'Inactivo' }}
                </span>
            </template>
        </ModalInformation>
    </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import Table from '@/views/private/admin/components/Table.vue';
import Icon from '@/components/Icon.vue';
import ModalInformation from '@/views/private/admin/components/ModalInformation.vue';
import { useTableData } from '@/composables/useTableData';
import { useTableConfig } from '@/composables/useTableConfig';

const columns = [
    { key: 'actions', label: 'ACCIONES', headerClass: 'compact', cellClass: 'compact' },
    { key: 'name', label: 'NOMBRE' },
    { key: 'description', label: 'DESCRIPCIÓN' },
    { key: 'status', label: 'ESTADO' }
];

// State
const { itemsPerPage } = useTableConfig();
const searchQuery = ref('');
const showInfoModal = ref(false);
const selectedAlgorithm = ref(null);

// Mock Data
const mockAlgorithms = [
    { id: 1, name: 'AES-256-GCM', description: 'Cifrado simétrico avanzado con autenticación.', status: 'active' },
    { id: 2, name: 'RSA-4096', description: 'Cifrado asimétrico para intercambio de claves.', status: 'active' },
    { id: 3, name: 'ChaCha20-Poly1305', description: 'Alternativa rápida y segura a AES.', status: 'inactive' },
    { id: 4, name: 'AES-128-CBC', description: 'Cifrado simétrico estándar (Legacy).', status: 'active' },
];

const handleRowClick = (row) => {
    selectedAlgorithm.value = row;
    showInfoModal.value = true;
};

// Mock API Call
const getAlgorithms = async () => {
    return new Promise((resolve) => {
        setTimeout(() => {
            resolve({ data: mockAlgorithms });
        }, 500);
    });
};

const { 
    data: algorithms, 
    loading: isLoading, 
    pagination, 
    fetchData: fetchAlgorithms 
} = useTableData(getAlgorithms, {
    mode: 'client',
    itemsPerPage,
    searchQuery
});
</script>

<style scoped>
.badge {
    padding: 0.25rem 0.5rem;
    border-radius: 4px;
    font-size: 0.8rem;
    font-weight: bold;
}

.badge-success {
    background: rgba(var(--success-rgb), 0.1);
    color: var(--success);
}

.badge-secondary {
    background: rgba(var(--text-secondary-rgb), 0.1);
    color: var(--text-secondary);
}
</style>
