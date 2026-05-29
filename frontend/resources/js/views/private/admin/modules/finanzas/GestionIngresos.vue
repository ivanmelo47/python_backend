<template>
    <div class="dashboard-module">
        <Table
            title="Historial de Movimientos"
            :rows="movements"
            :columns="columns"
            :loading="loading"
            :pagination="pagination"
            :search-query="searchQuery"
            :sort-options="sortOptions"
            module-id="finanzas-movimientos"
            v-model:items-per-page="itemsPerPage"
            @update:searchQuery="searchQuery = $event"
            @request-data="fetchData"
            pagination-mode="server"
            search-placeholder="Buscar movimientos..."
        >
            <template #cell-fecha="{ row, value }">
                <div class="flex items-center gap-2">
                    <DynamicIcon
                        v-if="row.cuenta?.icon_data"
                        :name="`db:${row.cuenta.icon_data.name}`"
                        :databaseData="row.cuenta.icon_data"
                        :size="16"
                    />
                    <Icon v-else :name="row.cuenta?.icon || 'calendar'" :size="16" class="text-secondary" />
                    <span class="text-tertiary">{{ formatDate(value) }}</span>
                </div>
            </template>

            <template #cell-descripcion="{ row, value }">
                <div class="flex items-center gap-2">
                    <div
                        v-if="row.categoria_rel?.icon_data"
                        class="category-icon"
                        :style="{ color: row.categoria_rel.color || 'var(--color-tertiary)' }"
                        :title="row.categoria_rel.nombre"
                    >
                        <DynamicIcon
                            :name="`db:${row.categoria_rel.icon_data.name}`"
                            :databaseData="row.categoria_rel.icon_data"
                            :size="14"
                        />
                    </div>
                    <div v-else class="text-tertiary">
                        <Icon name="tag" :size="12" />
                    </div>
                    <span class="font-bold text-primary flex items-center gap-1">
                        {{ value }}
                        <Icon v-if="row.adjuntos_count > 0" name="paperclip" :size="12" class="text-primary opacity-60" />
                    </span>
                </div>
            </template>

            <template #cell-monto="{ row, value }">
                <span
                    :class="[
                        'fw-bold',
                        row.metadata?.rebalance ? 'text-warning' : ((row.tipo === 'ingreso' || row.tipo === 'rendimiento') ? 'text-success' : 'text-danger')
                    ]"
                    :style="{ color: row.metadata?.rebalance ? '#eab308' : ((row.tipo === 'ingreso' || row.tipo === 'rendimiento') ? '#10b981' : '#ef4444') }"
                >
                    {{ (row.tipo === 'ingreso' || row.tipo === 'rendimiento') ? (value < 0 ? '' : '+') : '-' }}{{ formatCurrency(value) }}
                </span>
            </template>

            <template #cell-cuenta="{ row }">
                <div v-if="row.cuenta" class="flex items-center gap-2">
                    <DynamicIcon
                        v-if="row.cuenta.icon_data"
                        :name="`db:${row.cuenta.icon_data.name}`"
                        :databaseData="row.cuenta.icon_data"
                        :size="14"
                        class="text-secondary"
                    />
                    <Icon v-else :name="row.cuenta.icon || 'credit-card'" :size="14" class="text-secondary" />
                    <span class="text-tertiary">
                        {{ row.cuenta.nombre }} <small>({{ row.cuenta.banco }})</small>
                    </span>
                </div>
                <div v-else-if="row.tarjeta" class="flex items-center gap-2">
                    <DynamicIcon
                        v-if="row.tarjeta.icon_data"
                        :name="`db:${row.tarjeta.icon_data.name}`"
                        :databaseData="row.tarjeta.icon_data"
                        :size="14"
                        class="text-secondary"
                    />
                    <Icon v-else :name="row.tarjeta.icon || 'credit-card'" :size="14" class="text-secondary" />
                    <span class="text-tertiary text-danger">
                        💳 {{ row.tarjeta.nombre }} <small>({{ row.tarjeta.banco }})</small>
                    </span>
                </div>
            </template>

            <template #cell-actions="{ row }">
                <button class="dropdown-item" @click.stop="openMovementDetail(row)">
                    <Icon name="paperclip" :size="16" />
                    <span>Archivos / Recibos</span>
                </button>
                <button class="dropdown-item danger" @click.stop="handleDelete(row.uuid)">
                    <Icon name="trash" :size="16" />
                    <span>Eliminar</span>
                </button>
            </template>

            <template #header-icon>
                <Icon name="exchange" :size="20" />
            </template>
        </Table>

        <MovementDetailModal
            :isVisible="showDetailModal"
            :movimiento="selectedMovement"
            @close="showDetailModal = false"
            @updated="fetchData"
        />
    </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue';
import Table from '@/views/private/admin/components/Table.vue';
import Icon from '@/components/Icon.vue';
import DynamicIcon from '@/components/DynamicIcon.vue';
import { api } from '@/services/api';
import { useTableData } from '@/composables/useTableData';
import { useAlert } from '@/composables/useAlert';
import { formatDate } from '@/utils/format-date';
import MovementDetailModal from './components/MovementDetailModal.vue';

const alert = useAlert();

// Sort Options
const sortOptions = [
    { key: 'fecha', label: 'Fecha' },
    { key: 'descripcion', label: 'Concepto' },
    { key: 'tipo', label: 'Tipo' },
    { key: 'monto', label: 'Monto' }
];

const itemsPerPage = ref(10);
const searchQuery = ref('');

// Data & Table
const {
    data: movements,
    loading,
    pagination,
    fetchData
} = useTableData(api.finanzas.getMovimientos, {
    itemsPerPage: itemsPerPage,
    searchQuery: searchQuery,
});

const showDetailModal = ref(false);
const selectedMovement = ref(null);

const openMovementDetail = (row) => {
    selectedMovement.value = row;
    showDetailModal.value = true;
};

const columns = [
    { key: 'fecha', label: 'FECHA' },
    { key: 'descripcion', label: 'CONCEPTO / FUENTE' },
    { key: 'cuenta', label: 'CUENTA' },
    { key: 'monto', label: 'MONTO', cellClass: 'text-right' },
    { key: 'actions', label: '', headerClass: 'compact', cellClass: 'compact' },
];

const formatCurrency = (val) => {
    return new Intl.NumberFormat('es-MX', { style: 'currency', currency: 'MXN' }).format(val);
};

const handleDelete = async (uuid) => {
    const confirmed = await alert.fire({
        title: '¿Eliminar registro?',
        text: 'Se revertirá el impacto en el saldo de la cuenta. Esta acción no se puede deshacer.',
        type: 'warning',
        showCancel: true,
        confirmText: 'Sí, eliminar',
        cancelText: 'Cancelar'
    });

    if (confirmed) {
        try {
            await api.finanzas.deleteMovimiento(uuid);
            alert.toast.success('Eliminado', 'Registro borrado y saldo ajustado.');
            fetchData();
        } catch (e) {
            alert.toast.error('Error', 'No se pudo eliminar.');
        }
    }
}

const handleMovimientosUpdated = () => {
    fetchData();
};

onMounted(() => {
    window.addEventListener('finanzas:movimientos-updated', handleMovimientosUpdated);
});

onBeforeUnmount(() => {
    window.removeEventListener('finanzas:movimientos-updated', handleMovimientosUpdated);
});
</script>

<style lang="scss" scoped>
.dashboard-module {
    animation: fadeIn 0.5s ease;
}

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}

.category-icon {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 24px;
    height: 24px;
    background: rgba(var(--primary-rgb), 0.1);
    border-radius: 6px;
    flex-shrink: 0;
}
</style>
