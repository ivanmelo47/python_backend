<template>
    <div class="dashboard-module">
        <Table title="Tarjetas de Crédito" :rows="tarjetas" :columns="columns" :loading="loading"
            :pagination="pagination" :search-query="searchQuery" :sort-options="sortOptions"
            module-id="finanzas-tarjetas" v-model:items-per-page="itemsPerPage"
            @update:searchQuery="searchQuery = $event" @request-data="fetchData" @toggle-status="handleToggleStatus" @row-click="handleViewInfo" pagination-mode="server">
            <template #cell-nombre="{ row }">
                <div class="flex items-center gap-3">
                    <div class="account-icon" :style="{ backgroundColor: 'var(--bg-tertiary)' }">
                        <DynamicIcon v-if="row.icon_data" :name="`db:${row.icon_data.name}`"
                            :databaseData="row.icon_data" :size="24" />
                        <Icon v-else :name="row.icon || 'credit-card'" :size="24" class="text-secondary" />
                    </div>
                    <div>
                        <div class="fw-bold text-primary">{{ row.nombre }}</div>
                        <div class="text-tertiary small">{{ row.banco || 'Sin banco' }}</div>
                    </div>
                </div>
            </template>

            <template #cell-limite_credito="{ value }">
                <span class="text-tertiary">{{ formatCurrency(value) }}</span>
            </template>

            <template #cell-deuda_actual="{ value }">
                <span class="fw-bold text-danger">{{ formatCurrency(value) }}</span>
            </template>

            <template #cell-credito_disponible="{ value }">
                <span class="fw-bold text-success">{{ formatCurrency(value) }}</span>
            </template>

            <template #cell-next_cut_date="{ row }">
                <div class="flex items-center gap-2">
                    <Icon name="scissors" :size="12" class="text-tertiary" />
                    <span
                        :class="{ 'text-warning fw-bold': isNearCut(row.next_cut_date), 'text-primary': !isNearCut(row.next_cut_date) }">
                        {{ row.next_cut_date ? formatDate(row.next_cut_date) : 'No config.' }}
                    </span>
                </div>
            </template>

            <template #cell-next_payment_date="{ row }">
                <div class="flex items-center gap-2">
                    <Icon name="calendar" :size="12" class="text-tertiary" />
                    <span
                        :class="{ 'text-danger fw-bold': isNearPayment(row.next_payment_date), 'text-primary': !isNearPayment(row.next_payment_date) }">
                        {{ row.next_payment_date ? formatDate(row.next_payment_date) : 'No config.' }}
                    </span>
                </div>
            </template>

            <template #cell-actions="{ row }">
                <button v-if="false" class="dropdown-item" @click.stop="openPagarModal(row)">
                    <Icon name="dollar-sign" :size="16" />
                    <span>Abonar / Pagar</span>
                </button>
                <button v-if="false" class="dropdown-item" @click.stop="openCompraModal(row)">
                    <Icon name="plus-circle" :size="16" />
                    <span>Añadir Compra</span>
                </button>
                <button class="dropdown-item" @click.stop="handleViewInfo(row)">
                    <Icon name="info" :size="16" />
                    <span>Ver Detalles</span>
                </button>
                <button class="dropdown-item" @click.stop="handleViewMovements(row)">
                    <Icon name="list" :size="16" />
                    <span>Ver Movimientos</span>
                </button>
                <button class="dropdown-item" @click.stop="handleViewProjection(row)">
                    <Icon name="trendingUp" :size="16" />
                    <span>Proyección de Pagos</span>
                </button>
                <button class="dropdown-item" @click.stop="openEditModal(row)">
                    <Icon name="edit" :size="16" />
                    <span>Editar Tarjeta</span>
                </button>
                <button class="dropdown-item danger" @click.stop="handleDelete(row)">
                    <Icon name="trash" :size="16" />
                    <span>Eliminar Tarjeta</span>
                </button>
            </template>

            <template #header-actions>
                <div class="header-actions-wrapper">
                    <button class="header-dropdown-trigger" :class="{ 'active': showFabMenu }" @click="showFabMenu = !showFabMenu">
                        <Icon :name="showFabMenu ? 'x' : 'plus'" :size="16" /> NUEVO / REGISTRAR
                    </button>
                    <div v-if="showFabMenu" class="header-actions-menu">
                        <button class="dropdown-item item-income" @click="openGlobalPagarModal(); showFabMenu = false">
                            <Icon name="arrowDown" :size="16" class="text-success" />
                            <span>Registrar Abono</span>
                        </button>
                        <button class="dropdown-item item-expense" @click="openGlobalCompraModal(); showFabMenu = false">
                            <Icon name="arrowUp" :size="16" class="text-danger" />
                            <span>Registrar Compra</span>
                        </button>
                        <button class="dropdown-item item-primary" @click="handleViewGeneralProjection(); showFabMenu = false">
                            <Icon name="trendingUp" :size="16" class="text-primary" />
                            <span>Proyección Global</span>
                        </button>
                        <div class="menu-divider"></div>
                        <button class="dropdown-item" @click="openCreateModal(); showFabMenu = false">
                            <Icon name="plus" :size="16" class="text-tertiary" />
                            <span>Nueva Tarjeta</span>
                        </button>
                    </div>
                    <div v-if="showFabMenu" class="menu-overlay-transparent" @click="showFabMenu = false"></div>
                </div>
            </template>
        </Table>

        <!-- Crear/Editar Tarjeta Modal -->
        <CreditCardFormModal
            :is-visible="showFormModal"
            :is-editing="isEditing"
            :is-saving="isSaving"
            :fields="formFields"
            :form="form"
            :errors="formErrors"
            @submit="handleSave"
            @close="showFormModal = false"
        />

        <!-- Pagar Modal -->
        <CardPaymentModal
            :is-visible="showPagarModal"
            :is-saving="isSaving"
            :fields="pagarFields"
            :form="pagarForm"
            :errors="formErrors"
            @submit="handlePagar"
            @close="showPagarModal = false"
        />

        <!-- Compra Modal (Unified New/Historical) -->
        <CardPurchaseModal
            :is-visible="showCompraModal"
            :is-saving="isSaving"
            :fields="compraFields"
            :form="compraForm"
            :errors="formErrors"
            @submit="handleSaveCompra"
            @close="showCompraModal = false"
        />

        <!-- Modal Detalle Movimientos -->
        <ModalForm :is-visible="showMovimientosModal" :title="`Reporte: ${activeCard?.nombre}`" size="lg"
            :hide-footer="true" @close="showMovimientosModal = false">
            <div class="movements-report">
                <div v-if="loadingMovements" class="flex items-center justify-center p-10">
                    <div class="spinner-premium"></div>
                </div>
                <div v-else-if="visibleMovements.length === 0" class="no-data">
                    <Icon name="file-text" :size="48" class="text-tertiary mb-3" />
                    <p>No hay movimientos registrados para esta tarjeta.</p>
                </div>
                <div class="report-layout">
                    <div class="report-main">
                        <div class="report-table-container">
                            <table class="report-table">
                                <colgroup>
                                    <col style="width: 100px;" />
                                    <col style="min-width: 160px;" />
                                    <col style="width: 110px;" />
                                    <col style="width: 175px;" />
                                    <col style="width: 120px;" />
                                    <col style="width: 50px;" />
                                </colgroup>
                                <thead>
                                    <tr>
                                        <th>Fecha</th>
                                        <th>Concepto</th>
                                        <th>Monto</th>
                                        <th>Estado</th>
                                        <th class="text-right">Pendiente</th>
                                        <th class="text-center" width="50"></th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <template v-for="m in visibleMovements" :key="m.uuid">
                                        <tr :class="{ 'is-completed': m.completado, 'is-parent-expandable': m.abonos_count > 0, 'is-selected-row': isParentExpanded(m.uuid) }"
                                            @click="handleToggleParentRow(m)">
                                            <td class="date-col" data-label="Fecha">{{ m.fecha }}</td>
                                            <td class="desc-col" data-label="Concepto">
                                                <div class="concept">
                                                    <span class="main">
                                                        <Icon v-if="m.abonos_count > 0"
                                                            :name="isParentExpanded(m.uuid) ? 'chevronDown' : 'chevronRight'"
                                                            :size="14" class="mr-1 text-tertiary" />
                                                        {{ m.descripcion }}
                                                        <Icon v-if="m.adjuntos_count > 0" name="paperclip" :size="12" class="text-primary opacity-60 ml-1" />
                                                    </span>
                                                    <span class="cat">{{ m.categoria }}</span>
                                                </div>
                                            </td>
                                            <td class="amount-col" data-label="Monto">
                                                <span :class="m.tipo === 'ingreso' ? 'text-success' : 'text-primary'">
                                                    {{ m.tipo === 'ingreso' ? '+' : '-' }}{{ formatCurrency(m.monto) }}
                                                </span>
                                            </td>
                                            <td class="status-col" data-label="Estado">
                                                <div v-if="m.es_msi" class="msi-tracker">
                                                    <div class="tracker-info">
                                                        <span class="progress-text">{{ m.meses_pagados }}/{{ m.total_meses }} meses</span>
                                                        <span class="monthly-text">{{ formatCurrency(m.pago_mensual) }}/mes</span>
                                                    </div>
                                                    <div class="tracker-bar">
                                                        <div class="fill"
                                                            :style="{ width: (m.meses_pagados / m.total_meses * 100) + '%' }">
                                                        </div>
                                                    </div>
                                                </div>
                                                <div v-else-if="m.tipo === 'gasto'" class="status-pill gray">Corriente
                                                </div>
                                                <div v-else class="status-pill green">Abono</div>
                                            </td>
                                            <td class="pending-col text-right" data-label="Pendiente">
                                                <span v-if="m.monto_pendiente > 0" class="text-error fw-bold">
                                                    {{ formatCurrency(m.monto_pendiente) }}
                                                </span>
                                                <span v-else class="text-success fw-bold">
                                                    <Icon name="check-circle" :size="14" class="mr-1" /> Pagado
                                                </span>
                                            </td>
                                            <td class="actions-col text-center">
                                                <div class="flex justify-center gap-1">
                                                    <button class="btn-icon"
                                                        title="Ver detalles / Adjuntos"
                                                        @click.stop="openMovementDetail(m)">
                                                        <Icon name="paperclip" :size="16" />
                                                    </button>
                                                    <button class="btn-icon-danger"
                                                        title="Eliminar movimiento y su historial"
                                                        @click.stop="handleDeleteMovement(m)">
                                                        <Icon name="trash" :size="16" />
                                                    </button>
                                                </div>
                                            </td>
                                        </tr>
                                    </template>
                                </tbody>
                            </table>
                        </div>

                        <div class="report-pagination">
                            <button class="btn btn-sm" :disabled="movementsMeta.current_page <= 1 || loadingMovements"
                                @click="fetchComprasPage(movementsMeta.current_page - 1)">
                                Anterior
                            </button>
                            <span class="text-tertiary">
                                Página {{ movementsMeta.current_page }} de {{ movementsMeta.last_page }}
                                ({{ movementsMeta.total }} compras)
                            </span>
                            <button class="btn btn-sm"
                                :disabled="movementsMeta.current_page >= movementsMeta.last_page || loadingMovements"
                                @click="fetchComprasPage(movementsMeta.current_page + 1)">
                                Siguiente
                            </button>
                        </div>
                    </div>

                    <aside class="abonos-side-panel">
                        <div class="abonos-side-header">
                            <span>Detalle de Abonos</span>
                        </div>

                        <div v-if="!activePanelPurchase" class="abonos-side-empty">
                            Selecciona una compra para ver sus abonos.
                        </div>

                        <div v-else-if="activePanelPurchase.abonos_count === 0" class="abonos-side-empty">
                            Esta compra no tiene abonos asociados.
                        </div>

                        <div v-else-if="isParentLoading(activePanelPurchase.uuid)" class="abonos-side-empty">
                            Cargando abonos...
                        </div>

                        <div v-else class="abonos-dropdown-list">
                            <div class="abonos-side-summary">
                                <div class="summary-label">Compra seleccionada</div>
                                <div class="summary-name">{{ activePanelPurchase.descripcion }}</div>
                                <div class="summary-meta">
                                    <span>{{ activePanelPurchase.fecha }}</span>
                                    <span>{{ formatCurrency(activePanelPurchase.monto) }}</span>
                                </div>
                            </div>

                            <div class="abonos-side-subtitle">
                                {{ activePanelAbonos.length }} abono(s) de la compra seleccionada
                            </div>

                            <div v-for="abono in activePanelAbonos" :key="abono.uuid" class="abono-item">
                                <div class="abono-item-top">
                                    <div class="abono-date">{{ abono.fecha }}</div>
                                    <div class="abono-amount text-success">+{{ formatCurrency(abono.monto) }}</div>
                                </div>

                                <div class="abono-concept">
                                    <span class="main">{{ abono.descripcion }}</span>
                                    <span class="cat">{{ abono.categoria }}</span>
                                </div>

                                <div class="abono-item-bottom">
                                    <span class="status-pill green">Abono</span>
                                    <span class="abono-pending text-success fw-bold">
                                        <Icon name="check-circle" :size="14" class="mr-1" /> Pagado
                                    </span>
                                    <button class="btn-icon-danger" title="Eliminar abono"
                                        @click.stop="handleDeleteMovement(abono)">
                                        <Icon name="trash" :size="16" />
                                    </button>
                                </div>
                            </div>
                        </div>
                    </aside>
                </div>
            </div>
        </ModalForm>

        <!-- Movement Details Modal -->
        <MovementDetailModal
            :isVisible="showDetailModal"
            :movimiento="selectedMovement"
            @close="showDetailModal = false"
            @updated="fetchComprasPage(movementsMeta.current_page)"
        />

        <ModalInformation
            v-if="infoCard"
            :is-open="showInfoModal"
            title="Detalles de la Tarjeta"
            icon="credit-card"
            :data="infoCard"
            :columns="infoColumns"
            show-edit-button
            @edit="showInfoModal = false; openEditModal(infoCard)"
            @close="showInfoModal = false"
        >
            <template #top-header>
                <div class="card-detail-hero">
                    <div class="card-hero-icon">
                        <DynamicIcon
                            v-if="infoCard.icon_data"
                            :name="`db:${infoCard.icon_data.name}`"
                            :databaseData="infoCard.icon_data"
                            :size="32"
                        />
                        <Icon v-else :name="infoCard.icon || 'credit-card'" :size="32" />
                    </div>
                    <div class="card-hero-info">
                        <h4>{{ infoCard.nombre }}</h4>
                        <p>{{ infoCard.banco || 'Institución no especificada' }}</p>
                    </div>
                    <div class="card-hero-badge">
                        <span class="status-badge" :class="infoCard.status ? 'active' : 'archived'">
                            {{ infoCard.status ? 'Tarjeta Activa' : 'Archivada' }}
                        </span>
                    </div>
                </div>
            </template>

            <template #value-limite_credito>
                {{ formatCurrency(infoCard.limite_credito) }}
            </template>

            <template #value-deuda_actual>
                <span class="font-bold text-error">
                    {{ formatCurrency(infoCard.deuda_actual) }}
                </span>
            </template>

            <template #value-credito_disponible>
                <span class="font-bold text-success">
                    {{ formatCurrency(infoCard.credito_disponible) }}
                </span>
            </template>

            <template #value-next_cut_date>
                <span v-if="infoCard.next_cut_date" class="badge warning">{{ formatDate(infoCard.next_cut_date) }}</span>
                <span v-else class="text-tertiary">No configurada</span>
            </template>

            <template #value-next_payment_date>
                <span v-if="infoCard.next_payment_date" class="badge error">{{ formatDate(infoCard.next_payment_date) }}</span>
                <span v-else class="text-tertiary">No configurada</span>
            </template>
        </ModalInformation>

        <ProjectionOverlay
            :show="showProyeccionModal"
            :loading="loadingProjection"
            :title="isConsolidatedProjection ? 'Proyección Consolidada' : 'Proyección de Pagos'"
            :subtitle="!isConsolidatedProjection ? `${activeCard?.nombre} • ${activeCard?.banco}` : 'Todas las tarjetas activas'"
            :icon="isConsolidatedProjection ? 'trending-up' : 'credit-card'"
            tableTitle="Desglose Mensual"
            v-model:viewMode="projectionViewMode"
            @close="showProyeccionModal = false"
            @export="generatePDF"
        >
            <template #metrics>
                <div class="metric-card">
                    <span class="label">PAGO ESTIMADO ESTE MES</span>
                    <span class="value">{{ formatCurrency(currentMonthProjection?.monto || 0) }}</span>
                </div>
                <div class="metric-card highlight">
                    <span class="label">COMPROMISO TOTAL (PARCIALIDADES)</span>
                    <span class="value">{{ formatCurrency(totalInstallmentsCommitment) }}</span>
                </div>
            </template>

            <template #table>
                <table class="mini-table">
                    <thead>
                        <tr>
                            <th>Mes</th>
                            <th class="text-right">Monto</th>
                            <th class="text-center">Estado</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="item in projectionData" :key="item.key" :class="{ 'current': item.is_current }" @click="handleViewMonthDetails(item)">
                            <td>{{ item.label }}</td>
                            <td class="text-right fw-bold">{{ formatCurrency(item.monto) }}</td>
                            <td class="text-center">
                                <span v-if="item.is_current" class="status-pill blue">Actual</span>
                                <span v-else-if="item.is_future" class="status-pill green">Pendiente</span>
                                <span v-else class="status-pill gray">Pasado</span>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </template>

            <template #chart>
                <canvas ref="projectionChartRef"></canvas>
            </template>

            <template #details-header>
                <h4>Detalle de Pagos: {{ selectedMonthDetails?.label }}</h4>
                <span class="total-badge">{{ formatCurrency(selectedMonthDetails?.monto || 0) }}</span>
            </template>

            <template #details-content>
                <div class="details-content-wrapper">
                    <div class="drilldown-list">
                    <div v-for="(item, idx) in selectedMonthDetails?.detalles" :key="idx" class="drilldown-item">
                        <div class="item-left">
                            <div class="item-icon gasto">
                                <Icon name="creditCard" :size="18" />
                            </div>
                            <div class="item-info">
                                <span class="item-name">{{ item.descripcion }}</span>
                                <div class="item-meta">
                                    <span v-if="isConsolidatedProjection" class="card-tag">{{ item.tarjeta }}</span>
                                    <span v-if="item.tipo === 'MSI'" class="installment">Mensualidad {{ item.n_pago }} de {{ item.total_pagos }}</span>
                                    <span v-else-if="item.tipo === 'Credito'" class="installment success">Crédito Aplicado</span>
                                    <span v-else class="installment regular">Pago Único</span>
                                    <span class="dot">•</span>
                                    <span class="date">{{ item.tipo === 'Credito' ? 'Aplicado el ' : 'Comprado el ' }}{{ formatDate(item.fecha_compra) }}</span>
                                </div>
                            </div>
                        </div>
                        <div class="item-right">
                            <div class="amount-bubble" :class="{ 'gasto': item.monto > 0, 'ingreso': item.monto < 0 }">
                                {{ item.monto < 0 ? '-' : '' }}{{ formatCurrency(Math.abs(item.monto)) }}
                            </div>
                        </div>
                    </div>

                    <div v-if="!selectedMonthDetails?.detalles?.length" class="empty-drilldown">
                        <Icon name="info" :size="48" />
                        <p>No hay deudas detalladas para este mes.</p>
                    </div>
                </div>
            </div>
        </template>
        </ProjectionOverlay>

        <!-- Detalle de Mensualidades (Modal Flotante) - REMOVED -->
    </div>
</template>

<script setup>
import { ref, reactive, computed, watch, onMounted, nextTick } from 'vue';
import Table from '@/views/private/admin/components/Table.vue';
import ModalForm from '@/views/private/admin/components/ModalForm.vue';
import Icon from '@/components/Icon.vue';
import ModalInformation from '@/views/private/admin/components/ModalInformation.vue';
import ProjectionOverlay from './components/ProjectionOverlay.vue';
import MovementDetailModal from './components/MovementDetailModal.vue';
import CreditCardFormModal from './components/CreditCardFormModal.vue';
import CardPaymentModal from './components/CardPaymentModal.vue';
import CardPurchaseModal from './components/CardPurchaseModal.vue';
import { formatDate } from '@/utils/format-date';
import DynamicIcon from '@/components/DynamicIcon.vue';
import { api } from '@/services/api';
import { useTableData } from '@/composables/useTableData';
import { useAlert } from '@/composables/useAlert';

const showFabMenu = ref(false);
const alert = useAlert();

const isConsolidatedProjection = ref(false);

// Formatting helpers
const formatCurrency = (val) => new Intl.NumberFormat('es-MX', { style: 'currency', currency: 'MXN' }).format(val);


const isNearCut = (dateString) => {
    if (!dateString) return false;
    const diff = (new Date(dateString) - new Date()) / (1000 * 60 * 60 * 24);
    return diff >= 0 && diff <= 3;
};

const isNearPayment = (dateString) => {
    if (!dateString) return false;
    const diff = (new Date(dateString) - new Date()) / (1000 * 60 * 60 * 24);
    return diff >= 0 && diff <= 5;
};

// Table Data
const itemsPerPage = ref(10);
const searchQuery = ref('');
const sortOptions = [
    { key: 'nombre', label: 'Nombre' },
    { key: 'deuda_actual', label: 'Deuda' },
];

const { data: tarjetas, loading, pagination, fetchData } = useTableData(api.finanzas.getTarjetas, {
    itemsPerPage,
    searchQuery
});

const columns = [
    { key: 'nombre', label: 'TARJETA' },
    { key: 'limite_credito', label: 'LÍMITE TOTAL' },
    { key: 'deuda_actual', label: 'DEUDA ACTUAL' },
    { key: 'credito_disponible', label: 'DISPONIBLE' },
    { key: 'next_cut_date', label: 'PRÓXIMO CORTE' },
    { key: 'next_payment_date', label: 'PAGO LÍMITE' },
    { key: 'status', label: 'ESTADO', type: 'switch', activeLabel: 'Activa', inactiveLabel: 'Inactiva', headerClass: 'text-center', cellClass: 'text-center' },
    { key: 'actions', label: '', headerClass: 'compact', cellClass: 'compact' },
];

// Accounts for payment origin
const cuentasAhorro = ref([]);
const fetchCuentasAhorro = async () => {
    const res = await api.finanzas.getCuentasAhorro({ per_page: 100 });
    cuentasAhorro.value = res.data.data;
};

// Modals state
const showFormModal = ref(false);
const showPagarModal = ref(false);
const showCompraModal = ref(false);
const showMovimientosModal = ref(false);
const isEditing = ref(false);
const isSaving = ref(false);
const loadingMovements = ref(false);
const loadingProjection = ref(false);
const showProyeccionModal = ref(false);
const showDetailsModal = ref(false);
const isFullscreen = ref(false);
const projectionViewMode = ref('chart'); // 'chart' or 'details'

watch(projectionViewMode, (newVal) => {
    if (newVal === 'chart') {
        nextTick(() => {
            renderProjectionChart();
        });
    }
});

const projectionData = ref([]);
const selectedMonthDetails = ref(null);
const projectionChartRef = ref(null);
let projectionChart = null;
const cardMovements = ref([]);
const movementsPerPage = ref(10);
const movementsMeta = ref({
    current_page: 1,
    last_page: 1,
    total: 0,
    from: 0,
    to: 0,
    per_page: 10
});
const expandedParentRows = ref({});
const formErrors = ref({});
const activeCard = ref(null);

// Movement Detail State
const showDetailModal = ref(false);
const selectedMovement = ref(null);

const openMovementDetail = (mov) => {
    selectedMovement.value = mov;
    showDetailModal.value = true;
};

// Info Modal Logic
const showInfoModal = ref(false);
const infoCard = ref(null);
const infoColumns = [
    { key: 'nombre', label: 'Nombre Tarjeta' },
    { key: 'banco', label: 'Banco' },
    { key: 'limite_credito', label: 'Límite Total' },
    { key: 'deuda_actual', label: 'Deuda Actual' },
    { key: 'credito_disponible', label: 'Disponible' },
    { key: 'dia_corte', label: 'Día de Corte' },
    { key: 'dia_pago', label: 'Día de Pago' },
    { key: 'next_cut_date', label: 'Próxima Fecha de Corte' },
    { key: 'next_payment_date', label: 'Próxima Fecha de Pago' },
    { key: 'notas', label: 'Notas', fullWidth: true, isNote: true }
];

const handleViewInfo = (row) => {
    infoCard.value = row;
    showInfoModal.value = true;
};

const visibleMovements = computed(() => {
    return cardMovements.value;
});

const getParentState = (uuid) => expandedParentRows.value[uuid] || { open: false, loading: false, loaded: false, items: [] };

const isParentExpanded = (uuid) => !!getParentState(uuid).open;
const isParentLoading = (uuid) => !!getParentState(uuid).loading;
const getExpandedAbonos = (uuid) => getParentState(uuid).items || [];

const activePanelPurchase = computed(() => {
    const openUuid = Object.keys(expandedParentRows.value).find((uuid) => expandedParentRows.value[uuid]?.open);
    if (!openUuid) return null;
    return cardMovements.value.find((m) => m.uuid === openUuid) || null;
});

const activePanelAbonos = computed(() => {
    if (!activePanelPurchase.value) return [];
    return getExpandedAbonos(activePanelPurchase.value.uuid);
});

const fetchAbonosForPurchase = async (parentUuid, forceReload = false) => {
    const current = getParentState(parentUuid);
    if (current.loaded && !forceReload) {
        return current.items;
    }

    expandedParentRows.value[parentUuid] = {
        ...current,
        loading: true,
    };

    try {
        const res = await api.finanzas.getTarjetaAbonos(activeCard.value.uuid, parentUuid);
        const items = res.data?.data || [];
        expandedParentRows.value[parentUuid] = {
            open: true,
            loading: false,
            loaded: true,
            items,
        };
        return items;
    } catch (e) {
        expandedParentRows.value[parentUuid] = {
            ...current,
            loading: false,
        };
        alert.toast.error('Error', 'No se pudieron cargar los abonos.');
        return [];
    }
};

const handleToggleParentRow = async (mov) => {
    if (mov.tipo !== 'gasto' || !mov.abonos_count) return;

    // Keep only one dropdown open to avoid the table growing too much.
    const onlyCurrent = {};
    Object.keys(expandedParentRows.value).forEach((key) => {
        if (key === mov.uuid) {
            onlyCurrent[key] = expandedParentRows.value[key];
        }
    });
    expandedParentRows.value = onlyCurrent;

    const current = getParentState(mov.uuid);
    if (current.open) {
        expandedParentRows.value[mov.uuid] = {
            ...current,
            open: false,
        };
        return;
    }

    if (!current.loaded) {
        await fetchAbonosForPurchase(mov.uuid);
        return;
    }

    expandedParentRows.value[mov.uuid] = {
        ...current,
        open: true,
    };
};

const fetchComprasPage = async (page = 1) => {
    loadingMovements.value = true;
    expandedParentRows.value = {};
    try {
        const res = await api.finanzas.getTarjetaCompras(activeCard.value.uuid, {
            page,
            per_page: movementsPerPage.value
        });
        cardMovements.value = res.data?.data || [];
        movementsMeta.value = {
            ...movementsMeta.value,
            ...(res.data?.meta || {})
        };
        movementsMeta.value.current_page = res.data?.meta?.current_page || page;
    } catch (e) {
        alert.toast.error('Error', 'No se pudo cargar el historial de compras.');
    } finally {
        loadingMovements.value = false;
    }
};

// Forms
const form = reactive({
    uuid: '', nombre: '', banco: '', icon_id: null, limite_credito: '', deuda_actual: '0', dia_corte: '', dia_pago: '', notas: '', status: true
});

const pagarForm = reactive({
    monto: '', cuenta_origen_id: '', fecha: new Date().toISOString().split('T')[0], descripcion: ''
});

const compraForm = reactive({
    monto: '',
    fecha: new Date().toISOString().split('T')[0],
    descripcion: '',
    a_meses: false,
    es_msi: true,
    monto_final: '',
    plazo: 12,
    desglosar_pagos: true
});

// Fields definitions
const formFields = computed(() => [
    { key: 'nombre', label: 'Nombre Tarjeta', type: 'text', required: true, span: 2 },
    { key: 'banco', label: 'Banco', type: 'text', span: 2 },
    { key: 'icon_id', label: 'Icono', type: 'icon-select', span: 4 },
    { key: 'limite_credito', label: 'Límite de Crédito', type: 'number', required: true, span: 2 },
    { key: 'deuda_actual', label: 'Deuda Inicial', type: 'number', required: true, span: 2, placeholder: 'Negativo (-) para Saldo a Favor' },
    { key: 'dia_corte', label: 'Día de Corte (1-31)', type: 'number', span: 2, min: 1, max: 31 },
    { key: 'dia_pago', label: 'Día Límite de Pago (1-31)', type: 'number', span: 2, min: 1, max: 31 },
    { key: 'status', label: '¿Tarjeta Activa?', type: 'switch', span: 2, options: { activeLabel: 'Activa', inactiveLabel: 'Inactiva' } },
    { key: 'notas', label: 'Notas', type: 'textarea', span: 4 },
]);

const pagarFields = computed(() => {
    const fields = [
        { key: 'fecha', label: 'Fecha de Pago', type: 'date', required: true, span: 4 },
        { key: 'monto', label: 'Monto a Pagar ($)', type: 'custom', required: true, span: 4 },
        {
            key: 'cuenta_origen_id',
            label: 'Origen del Dinero',
            type: 'select',
            span: 4,
            options: [
                { id: '', name: '💰 Exterior / Efectivo físico' },
                ...cuentasAhorro.value
                    .filter(c => c.status === true || c.status === 1 || c.status === 'activa')
                    .map(c => ({ id: c.uuid, name: `🏦 ${c.nombre} (${formatCurrency(c.saldo_actual)})` }))
            ]
        },
        { key: 'descripcion', label: 'Concepto (Opcional)', type: 'text', span: 4 },
    ];

    if (!activeCard.value) {
        fields.unshift({
            key: 'tarjeta_uuid',
            label: 'Tarjeta a Pagar',
            type: 'select',
            required: true,
            span: 4,
            options: tarjetas.value
                .filter(t => t.status === true || t.status === 1 || t.status === 'activa')
                .map(t => ({ id: t.uuid, name: `💳 ${t.nombre} (${t.banco})` }))
        });
    }

    return fields;
});

const compraFields = computed(() => {
    const fields = [
        { key: 'descripcion', label: 'Concepto de la compra', type: 'text', required: true, placeholder: 'Ej. Pantalla Liverpool', span: 4 },
        { key: 'fecha', label: 'Fecha de Compra *', type: 'date', required: true, span: 2 },
        { key: 'monto', label: 'Precio de Contado (Original) *', type: 'custom', required: true, span: 2 },
        { key: 'plan_financiero', label: 'Configuración del Pago', type: 'custom', span: 4 },
    ];

    if (!activeCard.value) {
        fields.unshift({
            key: 'tarjeta_uuid',
            label: 'Seleccionar Tarjeta',
            type: 'select',
            required: true,
            span: 4,
            options: tarjetas.value
                .filter(t => t.status === true || t.status === 1 || t.status === 'activa')
                .map(t => ({ id: t.uuid, name: `💳 ${t.nombre} (${t.banco})` }))
        });
    }

    return fields;
});

// Actions
const openCreateModal = () => {
    isEditing.value = false;
    formErrors.value = {};
    Object.keys(form).forEach(k => form[k] = '');
    form.deuda_actual = '0';
    form.status = true;
    showFormModal.value = true;
};

const openEditModal = (row) => {
    isEditing.value = true;
    formErrors.value = {};
    Object.assign(form, {
        ...row,
        status: !!row.status
    });
    showFormModal.value = true;
};

const openPagarModal = (row) => {
    activeCard.value = row;
    pagarForm.monto = row.monto_a_pagar || 0;
    pagarForm.cuenta_origen_id = '';
    pagarForm.descripcion = `Pago Tarjeta ${row.nombre}`;
    pagarForm.fecha = new Date().toISOString().split('T')[0];
    showPagarModal.value = true;
};

const openGlobalPagarModal = () => {
    activeCard.value = null;
    const firstCard = tarjetas.value[0];
    pagarForm.tarjeta_uuid = firstCard?.uuid || '';
    pagarForm.monto = firstCard?.monto_a_pagar || 0;
    pagarForm.cuenta_origen_id = '';
    pagarForm.descripcion = 'Abono a Tarjeta';
    pagarForm.fecha = new Date().toISOString().split('T')[0];
    showPagarModal.value = true;
};

const openGlobalCompraModal = () => {
    activeCard.value = null;
    formErrors.value = {};
    Object.keys(compraForm).forEach(k => {
        if (k === 'fecha') compraForm[k] = new Date().toISOString().split('T')[0];
        else if (k === 'es_msi') compraForm[k] = true;
        else if (k === 'plazo') compraForm[k] = 12;
        else if (k === 'desglosar_pagos') compraForm[k] = true;
        else if (k === 'tarjeta_uuid') compraForm[k] = tarjetas.value[0]?.uuid || '';
        else compraForm[k] = '';
    });
    showCompraModal.value = true;
};

const openCompraModal = (row) => {
    activeCard.value = row;
    formErrors.value = {};
    Object.keys(compraForm).forEach(k => {
        if (k === 'fecha') compraForm[k] = new Date().toISOString().split('T')[0];
        else if (k === 'es_msi') compraForm[k] = true;
        else if (k === 'plazo') compraForm[k] = 12;
        else if (k === 'desglosar_pagos') compraForm[k] = true;
        else compraForm[k] = '';
    });
    showCompraModal.value = true;
};

const handleSave = async () => {
    isSaving.value = true;
    formErrors.value = {};
    try {
        if (isEditing.value) {
            await api.finanzas.updateTarjeta(form.uuid, form);
            alert.toast.success('Actualizado', 'Tarjeta modificada.');
        } else {
            await api.finanzas.storeTarjeta(form);
            alert.toast.success('Creado', 'Tarjeta agregada.');
        }
        showFormModal.value = false;
        fetchData();
    } catch (error) {
        if (error.response?.data?.errors) formErrors.value = error.response.data.errors;
    } finally {
        isSaving.value = false;
    }
};

const handleToggleStatus = async ({ row }) => {
    try {
        const isActive = row.status === true || row.status === 'activa' || row.status === 1;
        const newStatus = !isActive;

        await api.finanzas.updateTarjeta(row.uuid, {
            ...row,
            status: newStatus
        });

        row.status = newStatus ? 'activa' : 'cancelada'; // Sync with backend string representation
        alert.toast.success(
            newStatus ? 'Tarjeta activada' : 'Tarjeta desactivada',
            `La tarjeta "${row.nombre}" ha sido ${newStatus ? 'habilitada' : 'archivada'}.`
        );
    } catch (error) {
        alert.toast.error('Error', 'No se pudo cambiar el estado de la tarjeta.');
    }
};

const handlePagar = async () => {
    isSaving.value = true;
    formErrors.value = {};
    console.log("Iniciando proceso de pago...", pagarForm);
    try {
        const tarjetaUuid = activeCard.value ? activeCard.value.uuid : pagarForm.tarjeta_uuid;

        if (!tarjetaUuid) {
            alert.toast.error('Error', 'Debe seleccionar una tarjeta.');
            isSaving.value = false;
            return;
        }

        // Validation: Cannot pay more than account balance
        if (pagarForm.cuenta_origen_id && pagarForm.cuenta_origen_id !== 'externo') {
            const selectedAccount = cuentasAhorro.value.find(a => a.uuid === pagarForm.cuenta_origen_id);
            if (selectedAccount && parseFloat(pagarForm.monto) > parseFloat(selectedAccount.saldo_actual)) {
                const formattedBalance = new Intl.NumberFormat('es-MX', { style: 'currency', currency: 'MXN' }).format(selectedAccount.saldo_actual);
                formErrors.value = {
                    monto: [`Saldo insuficiente en la cuenta seleccionada. Saldo actual: ${formattedBalance}`]
                };
                isSaving.value = false;
                return;
            }
        }

        console.log("Enviando petición a la API para tarjeta:", tarjetaUuid);
        const response = await api.finanzas.pagarTarjeta(tarjetaUuid, pagarForm);
        console.log("Respuesta de la API:", response.data);

        alert.toast.success('Pago Registrado', 'La deuda ha sido actualizada.');
        showPagarModal.value = false;
        fetchData();
        fetchCuentasAhorro();
    } catch (error) {
        console.error("Error al procesar el pago:", error);
        if (error.response?.data?.errors) formErrors.value = error.response.data.errors;
        else alert.toast.error('Error', error.response?.data?.message || 'No se pudo completar el pago. Revise la consola.');
    } finally {
        isSaving.value = false;
    }
};

const handleSaveCompra = async () => {
    isSaving.value = true;
    try {
        const tarjetaUuid = activeCard.value ? activeCard.value.uuid : compraForm.tarjeta_uuid;
        await api.finanzas.compraHistoricaTarjeta(tarjetaUuid, compraForm);
        alert.toast.success('Éxito', 'Compra registrada correctamente.');

        window.dispatchEvent(new CustomEvent('finanzas:movimientos-updated'));

        if (showMovimientosModal.value && activeCard.value?.uuid === tarjetaUuid) {
            await fetchComprasPage(movementsMeta.value.current_page || 1);
        }

        showCompraModal.value = false;
        fetchData();
    } catch (e) {
        formErrors.value = e.response?.data?.errors || {};
        alert.toast.error('Error', 'No se pudo registrar la compra.');
    } finally {
        isSaving.value = false;
    }
};

const handleDelete = async (row) => {
    const confirmed = await alert.fire({
        title: '¿Eliminar Tarjeta?',
        text: `Se eliminará "${row.nombre}" y TODO su historial.`,
        type: 'warning',
        showCancel: true,
        confirmText: 'Eliminar',
        cancelText: 'Cancelar'
    });
    if (confirmed) {
        try {
            await api.finanzas.deleteTarjeta(row.uuid);
            alert.toast.success('Eliminada', 'Tarjeta borrada.');
            fetchData();
        } catch (e) {
            alert.toast.error('Error', 'No se pudo eliminar.');
        }
    }
};

const handleViewMovements = async (row) => {
    activeCard.value = row;
    showMovimientosModal.value = true;
    cardMovements.value = [];
    movementsMeta.value = {
        current_page: 1,
        last_page: 1,
        total: 0,
        from: 0,
        to: 0,
        per_page: movementsPerPage.value
    };
    expandedParentRows.value = {};
    await fetchComprasPage(1);
};

const handleDeleteMovement = async (mov) => {
    const isGasto = mov.tipo === 'gasto';
    const message = isGasto
        ? 'Esto eliminará la compra y TODO su historial de abonos relacionados. ¿Continuar?'
        : '¿Deseas eliminar este abono? La deuda de la tarjeta se ajustará automáticamente.';

    if (await alert.fire({
        title: 'Eliminar Movimiento',
        text: message,
        type: 'warning',
        showCancel: true,
        confirmText: 'Sí, eliminar'
    })) {
        try {
            await api.finanzas.deleteTarjetaMovimiento(activeCard.value.uuid, mov.uuid);
            alert.toast.success('Eliminado', 'Movimiento borrado correctamente.');
            await fetchComprasPage(movementsMeta.value.current_page || 1);
            if (mov.tipo === 'ingreso' && mov.parent_uuid) {
                await fetchAbonosForPurchase(mov.parent_uuid, true);
                expandedParentRows.value[mov.parent_uuid] = {
                    ...getParentState(mov.parent_uuid),
                    open: true,
                };
            }
            fetchData(); // Recargar tarjetas (para la deuda actual)
        } catch (e) {
            alert.toast.error('Error', 'No se pudo eliminar el movimiento.');
        }
    }
};

const totalInstallmentsCommitment = computed(() => {
    return projectionData.value
        .filter(item => item.is_future || item.is_current)
        .reduce((sum, item) => sum + item.monto, 0);
});

const currentMonthProjection = computed(() => {
    return projectionData.value.find(item => item.is_current);
});

const handleViewGeneralProjection = async () => {
    isConsolidatedProjection.value = true;
    activeCard.value = null;
    showProyeccionModal.value = true;
    loadingProjection.value = true;
    projectionViewMode.value = 'chart';
    projectionData.value = [];

    try {
        const response = await api.finanzas.getProyeccionGeneralTarjetas();
        projectionData.value = response.data || [];
        setTimeout(() => {
            renderProjectionChart();
        }, 100);
    } catch (e) {
        alert.toast.error('Error', 'No se pudo cargar la proyección consolidada.');
    } finally {
        loadingProjection.value = false;
    }
};

const handleViewProjection = async (row) => {
    isConsolidatedProjection.value = false;
    activeCard.value = row;
    showProyeccionModal.value = true;
    loadingProjection.value = true;
    projectionViewMode.value = 'chart';
    projectionData.value = [];

    try {
        const res = await api.finanzas.getTarjetaProyeccion(row.uuid);
        projectionData.value = res.data || [];
        
        // Wait for DOM and render chart
        setTimeout(() => {
            renderProjectionChart();
        }, 100);
    } catch (e) {
        alert.toast.error('Error', 'No se pudo cargar la proyección de pagos.');
    } finally {
        loadingProjection.value = false;
    }
};

const toggleFullscreen = () => {
    // Deprecated in favor of the new fullscreen overlay
};

const handleViewMonthDetails = (data) => {
    selectedMonthDetails.value = data;
    projectionViewMode.value = 'details';
};

const generatePDF = async () => {
    if (!projectionData.value.length) return;

    alert.showLoading('Generando reporte PDF...', 'Por favor espera un momento.');

    try {
        // Wait a tick to ensure chart is rendered if we were in details mode
        if (projectionViewMode.value !== 'chart') {
            projectionViewMode.value = 'chart';
            await nextTick();
            // Give extra time for chart animation/rendering
            await new Promise(r => setTimeout(r, 500));
        }

        const { jsPDF } = await import('jspdf');
        const autoTable = (await import('jspdf-autotable')).default || (await import('jspdf-autotable'));
        const doc = new jsPDF('p', 'mm', 'a4');
        const pageWidth = doc.internal.pageSize.getWidth();
        const margin = 15;

        // 1. Header & Title
        doc.setFillColor(30, 41, 59); // Slate-800
        doc.rect(0, 0, pageWidth, 40, 'F');
        
        doc.setTextColor(255, 255, 255);
        doc.setFontSize(22);
        doc.setFont('helvetica', 'bold');
        doc.text(isConsolidatedProjection.value ? 'REPORTE CONSOLIDADO DE PAGOS' : 'REPORTE DE PROYECCIÓN DE PAGOS', margin, 20);
        
        doc.setFontSize(10);
        doc.setFont('helvetica', 'normal');
        if (isConsolidatedProjection.value) {
            doc.text('Todas las tarjetas de crédito activas', margin, 28);
        } else {
            doc.text(`${activeCard.value?.nombre} • ${activeCard.value?.banco}`, margin, 28);
        }
        doc.text(`Generado el: ${new Date().toLocaleString('es-MX')}`, margin, 34);

        let currentY = 55;

        // 2. Summary Metrics Cards
        doc.setTextColor(30, 41, 59);
        doc.setFontSize(12);
        doc.setFont('helvetica', 'bold');
        doc.text('RESUMEN GENERAL', margin, currentY);
        currentY += 10;

        const metricsData = [
            ['Deuda Actual:', formatCurrency(activeCard.value?.deuda_actual || 0)],
            ['Crédito Disponible:', formatCurrency(activeCard.value?.credito_disponible || 0)],
            ['Compromiso Total (Parcialidades):', formatCurrency(totalInstallmentsCommitment.value)]
        ];

        autoTable(doc, {
            startY: currentY,
            head: [],
            body: metricsData,
            theme: 'plain',
            styles: { fontSize: 10, cellPadding: 2 },
            columnStyles: { 0: { fontStyle: 'bold', width: 60 } }
        });

        currentY = doc.lastAutoTable.finalY + 15;

        // 3. Chart Capture
        if (projectionChartRef.value && projectionViewMode.value === 'chart') {
            const chartCanvas = projectionChartRef.value;
            const chartImg = chartCanvas.toDataURL('image/png', 1.0);
            
            doc.setFontSize(12);
            doc.setFont('helvetica', 'bold');
            doc.text('VISUALIZACIÓN DE FLUJO DE CAJA', margin, currentY);
            currentY += 5;

            const imgWidth = pageWidth - (margin * 2);
            const imgHeight = (chartCanvas.height * imgWidth) / chartCanvas.width;
            
            // Add a dark background to the chart so white labels are visible
            doc.setFillColor(15, 23, 42); // Midnight Blue
            doc.roundedRect(margin, currentY, imgWidth, imgHeight, 3, 3, 'F');
            
            doc.addImage(chartImg, 'PNG', margin, currentY, imgWidth, imgHeight);
            currentY += imgHeight + 15;
        }

        // 4. Detailed Table
        if (currentY > 230) { doc.addPage(); currentY = 20; }
        
        doc.setFontSize(12);
        doc.setFont('helvetica', 'bold');
        doc.text('CRONOGRAMA DETALLADO DE PAGOS', margin, currentY);
        currentY += 5;

        const tableBody = [];
        projectionData.value.forEach(month => {
            // Month Header Row - High Contrast
            tableBody.push([
                { content: month.label.toUpperCase(), colSpan: 3, styles: { fillColor: [30, 41, 59], textColor: 255, fontStyle: 'bold', fontSize: 9 } },
                { content: formatCurrency(month.monto), styles: { fillColor: [30, 41, 59], textColor: 255, fontStyle: 'bold', halign: 'right', fontSize: 9 } }
            ]);

            // Concept Rows
            if (month.detalles && month.detalles.length > 0) {
                month.detalles.forEach(det => {
                    const concepto = det.tipo === 'MSI' 
                        ? `${det.descripcion} (Mensualidad ${det.n_pago}/${det.total_pagos})`
                        : `${det.descripcion} (Pago Único)`;
                    
                    tableBody.push([
                        '',
                        concepto,
                        det.fecha_compra ? formatDate(det.fecha_compra) : '-',
                        { content: formatCurrency(det.monto), styles: { halign: 'right', fontStyle: 'bold' } }
                    ]);
                });
            } else {
                tableBody.push(['', 'Sin movimientos proyectados', '', '-']);
            }
        });

        autoTable(doc, {
            startY: currentY,
            head: [['', 'Concepto', 'Fecha Compra', 'Monto']],
            body: tableBody,
            styles: { fontSize: 8, cellPadding: 3, textColor: [51, 65, 85] }, // Slate-700
            headStyles: { fillColor: [15, 23, 42], textColor: 255, fontStyle: 'bold' },
            alternateRowStyles: { fillColor: [248, 250, 252] },
            columnStyles: { 
                0: { width: 8 },
                1: { width: 95 },
                2: { width: 35 },
                3: { halign: 'right' }
            }
        });

        // 5. Footer on all pages
        const pageCount = doc.internal.getNumberOfPages();
        for (let i = 1; i <= pageCount; i++) {
            doc.setPage(i);
            doc.setFontSize(8);
            doc.setTextColor(148, 163, 184);
            doc.text(`Página ${i} de ${pageCount}`, pageWidth / 2, 285, { align: 'center' });
            doc.text('Plataforma Gestor de Archivos - Módulo de Finanzas', margin, 285);
        }

        doc.save(`Reporte_Pagos_${activeCard.value?.nombre}_${new Date().toISOString().split('T')[0]}.pdf`);
        
        alert.closeLoading();
        alert.toast.success('¡PDF Generado!', 'El reporte se ha descargado correctamente.');
    } catch (error) {
        console.error('Error generating PDF:', error);
        alert.closeLoading();
        alert.toast.error('Error', 'No se pudo generar el reporte PDF.');
    }
};

import Chart from 'chart.js/auto';

const renderProjectionChart = () => {
    if (!projectionChartRef.value) return;
    
    if (projectionChart) {
        projectionChart.destroy();
    }

    const style = getComputedStyle(document.documentElement);
    const primaryRGB = style.getPropertyValue('--primary-rgb').trim() || '59, 130, 246';
    const textTertiaryRGB = style.getPropertyValue('--text-tertiary-rgb').trim() || '148, 163, 184';

    const ctx = projectionChartRef.value.getContext('2d');
    
    // Gradient for the bars
    const gradient = ctx.createLinearGradient(0, 0, 0, 400);
    gradient.addColorStop(0, `rgba(${primaryRGB}, 0.8)`);
    gradient.addColorStop(1, `rgba(${primaryRGB}, 0.1)`);

    const labels = projectionData.value.map(item => item.label);
    const values = projectionData.value.map(item => item.monto);
    const backgroundColors = projectionData.value.map(item => 
        item.is_current ? '#eab308' : (item.is_future ? `rgba(${primaryRGB}, 0.6)` : `rgba(${textTertiaryRGB}, 0.2)`)
    );

    projectionChart = new Chart(ctx, {
        type: 'bar',
        plugins: [{
            id: 'topLabels',
            afterDatasetsDraw(chart) {
                const { ctx, data } = chart;
                ctx.save();
                ctx.font = 'bold 13px "Inter", sans-serif';
                ctx.fillStyle = 'rgba(255, 255, 255, 0.9)';
                ctx.textAlign = 'left';
                ctx.textBaseline = 'middle';

                const formatCompact = (val) => {
                    if (val >= 1000000) return '$' + (val / 1000000).toFixed(1) + 'M';
                    if (val >= 1000) return '$' + (val / 1000).toFixed(1) + 'k';
                    return '$' + Math.round(val);
                };

                chart.getDatasetMeta(0).data.forEach((bar, index) => {
                    const value = data.datasets[0].data[index];
                    if (value > 0) {
                        const text = formatCompact(value);
                        
                        ctx.save();
                        ctx.translate(bar.x, bar.y - 12);
                        ctx.rotate(-Math.PI / 2);
                        ctx.fillText(text, 0, 0);
                        ctx.restore();
                    }
                });
                ctx.restore();
            }
        }],
        data: {
            labels,
            datasets: [{
                label: 'Monto a Pagar',
                data: values,
                backgroundColor: backgroundColors,
                borderRadius: 8,
                borderSkipped: false,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            layout: {
                padding: { top: 45 }
            },
            onClick: (event, elements) => {
                if (elements.length > 0) {
                    const index = elements[0].index;
                    const data = projectionData.value[index];
                    if (data && data.detalles && data.detalles.length > 0) {
                        handleViewMonthDetails(data);
                    }
                }
            },
            plugins: {
                legend: { display: false },
                tooltip: {
                    backgroundColor: 'rgba(15, 23, 42, 0.9)',
                    titleFont: { size: 14, weight: 'bold' },
                    padding: 12,
                    displayColors: false,
                    callbacks: {
                        label: (context) => `Total: ${formatCurrency(context.raw)}`
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: { color: 'rgba(255, 255, 255, 0.05)' },
                    ticks: {
                        color: 'rgba(255, 255, 255, 0.5)',
                        callback: (value) => formatCurrency(value)
                    }
                },
                x: {
                    grid: { display: false },
                    ticks: { color: 'rgba(255, 255, 255, 0.5)', maxRotation: 45, minRotation: 45 }
                }
            }
        }
    });
};

onMounted(() => {
    fetchCuentasAhorro();
});

// Watcher para actualizar el monto sugerido cuando cambia la tarjeta seleccionada en el modal global
watch(() => pagarForm.tarjeta_uuid, (newUuid) => {
    if (!activeCard.value && newUuid) {
        const card = tarjetas.value.find(t => t.uuid === newUuid);
        if (card) {
            pagarForm.monto = card.monto_a_pagar || 0;
            pagarForm.descripcion = `Pago Tarjeta ${card.nombre}`;
        }
    }
});
</script>


