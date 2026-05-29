<template>
    <div class="resumen-financiero">
        <!-- Quick Stats Cards -->
        <div class="stats-grid">
            <div 
                v-for="stat in stats" 
                :key="stat.title" 
                class="stat-card glass-panel clickable" 
                :class="stat.type"
                @click="openDetails(stat)"
            >
                <div class="stat-icon">
                    <Icon :name="stat.icon" :size="24" />
                </div>
                <div class="stat-info">
                    <span class="stat-title">{{ stat.title }}</span>
                    <h2 class="stat-value">{{ formatCurrency(stat.value) }}</h2>
                    <span class="stat-delta" :class="stat.trend >= 0 ? 'up' : 'down'">
                        <Icon :name="stat.trend >= 0 ? 'trendingUp' : 'trendingDown'" :size="14" />
                        {{ Math.abs(stat.trend) }}% vs mes anterior
                    </span>
                </div>
                <div class="click-indicator">
                    <Icon name="chevronRight" :size="16" />
                </div>
            </div>
        </div>

        <!-- Main Content Area -->
        <div class="finance-main-grid">
            <!-- Chart Section -->
            <div class="chart-section glass-panel">
                <div class="section-header">
                    <h3>Flujo de Caja (6 meses)</h3>
                    <div class="chart-legend">
                        <span class="legend-item"><span class="dot income"></span> Ingresos</span>
                        <span class="legend-item"><span class="dot expense"></span> Gastos</span>
                    </div>
                </div>
                <div class="chart-container">
                    <Line :data="chartData" :options="chartOptions" />
                </div>
            </div>

            <!-- Recent Movements Sidebar -->
            <div class="upcoming-section glass-panel">
                <div class="section-header">
                    <h3>Movimientos Recientes</h3>
                    <router-link to="/dashboard/finanzas/ingresos" class="view-all">Ver todos</router-link>
                </div>
                <div class="upcoming-list" v-if="recentMovements.length > 0">
                    <div v-for="mov in recentMovements" :key="mov.id" class="expense-item cursor-pointer hover:bg-white/5 transition-colors" @click="openMovementDetail(mov)">
                        <div class="expense-day">
                            <span class="day">{{ formatDateDay(mov.fecha) }}</span>
                            <span class="month">{{ formatDateMonth(mov.fecha) }}</span>
                        </div>
                        <div class="category-mini-icon" v-if="mov.categoria_rel?.icon_data" :style="{ color: mov.categoria_rel.color }">
                            <DynamicIcon 
                                :name="'db:' + mov.categoria_rel.icon_data.name" 
                                :databaseData="mov.categoria_rel.icon_data" 
                                :size="20" 
                            />
                        </div>
                        <div class="expense-detail">
                            <span class="name flex items-center gap-1">
                                {{ mov.descripcion }}
                                <Icon v-if="mov.adjuntos_count > 0" name="paperclip" :size="12" class="text-primary opacity-60" />
                            </span>
                            <span class="category">{{ mov.categoria_rel?.nombre || mov.tipo.toUpperCase() }}</span>
                        </div>
                        <div class="expense-amount" :class="mov.tipo === 'ingreso' || mov.tipo === 'rendimiento' ? 'text-success' : 'text-danger'">
                            {{ mov.tipo === 'ingreso' || mov.tipo === 'rendimiento' ? '+' : '-' }}{{ formatCurrency(mov.monto) }}
                        </div>
                    </div>
                </div>
                <div v-else class="empty-state-text text-center py-4">
                    <span v-if="loading">Cargando...</span>
                    <span v-else>Sin movimientos recientes</span>
                </div>
            </div>
        </div>

        <!-- Details Modal -->
        <Modal 
            :is-visible="showDetailsModal" 
            :title="selectedStat?.title" 
            @close="showDetailsModal = false"
            hide-footer
            :size="(selectedStat?.key === 'deuda' || selectedStat?.key === 'balance') ? 'lg' : 'md'"
        >
            <template #header-icon>
                <Icon :name="selectedStat?.icon || 'info'" :size="20" />
            </template>

            <div v-if="selectedStat?.key === 'gastos' || selectedStat?.key === 'ingresos' || selectedStat?.key === 'balance' || selectedStat?.key === 'deuda'" class="modal-breakdown" :class="{ 'is-drilldown': !!selectedCard }">
                <!-- Level 1: Cards/Categories List -->
                <template v-if="!selectedCard">
                    <div class="breakdown-chart">
                        <Doughnut :data="doughnutData" :options="doughnutOptions" />
                        <div class="chart-center-info">
                            <span class="label">
                                {{ 
                                    selectedStat.key === 'ingresos' ? 'Total Ingresado' : 
                                    (selectedStat.key === 'balance' ? 'Capital Total' : 
                                    (selectedStat.key === 'deuda' ? 'Deuda Total' : 'Total Gastado'))
                                }}
                            </span>
                            <span class="value">{{ formatCurrency(currentTotal) }}</span>
                        </div>
                    </div>

                    <div class="breakdown-list">
                        <div 
                            v-for="item in currentBreakdown" 
                            :key="item.nombre" 
                            class="breakdown-item"
                            :class="{ 'clickable-item': selectedStat.key === 'deuda' }"
                            @click="handleItemClick(item)"
                        >
                            <div class="item-icon" :style="{ backgroundColor: (item.color || '#6366f1') + '20', color: (item.color || '#6366f1') }">
                                <DynamicIcon 
                                    v-if="item.icon_data"
                                    :name="'db:' + item.icon_data.name" 
                                    :databaseData="item.icon_data" 
                                    :size="18" 
                                />
                                <Icon v-else :name="selectedStat.key === 'ingresos' ? 'trendingUp' : (selectedStat.key === 'balance' ? 'credit-card' : (selectedStat.key === 'deuda' ? 'credit-card' : 'tag'))" :size="18" />
                            </div>
                            <div class="item-info">
                                <span class="name">{{ item.nombre }}</span>
                                <span v-if="item.banco" class="subname text-tertiary" style="font-size: 0.7rem;">{{ item.banco }}</span>
                                <div class="progress-bar">
                                    <div class="progress" :style="{ width: (item.total / (currentTotal || 1) * 100) + '%', backgroundColor: (item.color || '#6366f1') }"></div>
                                </div>
                            </div>
                            <div class="item-value">
                                <span class="amount">{{ formatCurrency(item.total) }}</span>
                                <span class="percent">{{ currentTotal > 0 ? Math.round(item.total / currentTotal * 100) : 0 }}%</span>
                            </div>
                            <div v-if="selectedStat.key === 'deuda'" class="item-chevron">
                                <Icon name="chevronRight" :size="14" />
                            </div>
                        </div>
                        
                        <div v-if="!currentBreakdown.length" class="empty-state">
                            <Icon name="coffee" :size="40" class="text-tertiary" />
                            <p>No hay registros disponibles.</p>
                        </div>
                    </div>
                </template>

                <!-- Level 2: Active Debt Breakdown (Only for Credit Cards) -->
                <template v-else>
                    <div class="drilldown-container">
                        <div class="drilldown-header-modern">
                            <button class="btn-back-modern" @click="selectedCard = null">
                                <Icon name="arrowLeft" :size="16" />
                                <span>Volver al resumen</span>
                            </button>
                            
                            <div class="card-identity">
                                <div class="identity-icon" :style="{ background: selectedCard.color + '20', color: selectedCard.color }">
                                    <DynamicIcon 
                                        v-if="selectedCard.icon_data"
                                        :name="'db:' + selectedCard.icon_data.name" 
                                        :databaseData="selectedCard.icon_data" 
                                        :size="24" 
                                    />
                                    <Icon v-else name="credit-card" :size="24" />
                                </div>
                                <div class="identity-text">
                                    <h3>{{ selectedCard.nombre }}</h3>
                                    <span>{{ selectedCard.banco }}</span>
                                </div>
                                <div class="identity-badge">
                                    <span class="label">Deuda Total</span>
                                    <span class="value">{{ formatCurrency(selectedCard.total) }}</span>
                                </div>
                            </div>
                        </div>

                        <div class="drilldown-body">
                            <div v-if="loadingCardMovements" class="flex items-center justify-center p-10">
                                <div class="spinner-premium"></div>
                            </div>
                            <div v-else-if="activePurchases.length === 0" class="no-data">
                                <div class="empty-visual">
                                    <Icon name="check-circle" :size="48" />
                                </div>
                                <h5>Sin compras pendientes</h5>
                                <p>No hay compras activas o MSI generando deuda en esta tarjeta.</p>
                            </div>
                            <div v-else class="report-table-container">
                                <table class="report-table">
                                    <thead>
                                        <tr>
                                            <th>Fecha</th>
                                            <th>Concepto</th>
                                            <th>Monto Original</th>
                                            <th>Progreso</th>
                                            <th class="text-right">Pte. Actual</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        <tr v-for="m in activePurchases" :key="m.uuid">
                                            <td class="date-col" data-label="Fecha">{{ m.fecha }}</td>
                                            <td class="desc-col" data-label="Concepto">
                                                <div class="concept">
                                                    <span class="main">{{ m.descripcion }}</span>
                                                    <span class="cat">{{ m.categoria }}</span>
                                                </div>
                                            </td>
                                            <td class="amount-col" data-label="Monto Original">
                                                <span class="text-primary fw-bold">
                                                    {{ formatCurrency(m.monto) }}
                                                </span>
                                            </td>
                                            <td class="status-col" data-label="Progreso">
                                                <div v-if="m.es_msi" class="msi-tracker">
                                                    <div class="tracker-info">
                                                        <span class="progress-text">{{ m.meses_pagados }}/{{ m.total_meses }} meses</span>
                                                        <span class="monthly-text">{{ formatCurrency(m.pago_mensual) }}/mes</span>
                                                    </div>
                                                    <div class="tracker-bar">
                                                        <div class="fill" :style="{ width: (m.meses_pagados / m.total_meses * 100) + '%' }"></div>
                                                    </div>
                                                </div>
                                                <div v-else class="status-pill gray">Corriente</div>
                                            </td>
                                            <td class="pending-col text-right" data-label="Pte. Actual">
                                                <span class="text-error fw-bold">
                                                    {{ formatCurrency(m.monto_pendiente) }}
                                                </span>
                                            </td>
                                        </tr>
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>
                </template>
            </div>
            
            <div v-else class="modal-simple-info">
                <div class="info-card">
                    <Icon :name="selectedStat?.icon" :size="40" :class="'text-' + selectedStat?.type" />
                    <h3>{{ formatCurrency(selectedStat?.value) }}</h3>
                    <p>Información detallada para {{ selectedStat?.title }} próximamente.</p>
                </div>
            </div>
        </Modal>

        <MovementDetailModal
            :isVisible="showDetailModal"
            :movimiento="selectedMovement"
            @close="showDetailModal = false"
            @updated="fetchResumen"
        />
    </div>
</template>

<script setup>
import { ref, computed, onMounted, reactive } from 'vue';
import MovementDetailModal from './components/MovementDetailModal.vue';
import { Line, Doughnut } from 'vue-chartjs';
import Icon from '@/components/Icon.vue';
import DynamicIcon from '@/components/DynamicIcon.vue';
import Modal from '@/views/private/admin/components/ModalForm.vue';
import { api } from '@/services/api';
import { useTheme } from '@/composables/useTheme';
import { useColorPalette } from '@/composables/useColorPalette';
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend, Filler, ArcElement } from 'chart.js';

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend, Filler, ArcElement);

const { theme } = useTheme();
const { palette } = useColorPalette();

const getCssVar = (name) => {
    return getComputedStyle(document.documentElement).getPropertyValue(name).trim();
};

const summaryData = ref(null);
const loading = ref(true);

// Modal Logic
const showDetailsModal = ref(false);
const selectedStat = ref(null);

const openDetails = (stat) => {
    selectedStat.value = stat;
    selectedCard.value = null;
    showDetailsModal.value = true;
};

// Movement Detail State
const showDetailModal = ref(false);
const selectedMovement = ref(null);

const openMovementDetail = (mov) => {
    selectedMovement.value = mov;
    showDetailModal.value = true;
};

// Drilldown Logic
const selectedCard = ref(null);
const cardMovements = ref([]);
const loadingCardMovements = ref(false);

const handleItemClick = (item) => {
    if (selectedStat.value?.key === 'deuda' && item.uuid) {
        selectedCard.value = item;
        fetchCardMovements(item.uuid);
    }
};

const fetchCardMovements = async (uuid) => {
    loadingCardMovements.value = true;
    try {
        const response = await api.finanzas.getTarjetaMovimientos(uuid);
        cardMovements.value = response.data || [];
    } catch (e) {
        console.error("Error loading card debt movements", e);
    } finally {
        loadingCardMovements.value = false;
    }
};

const activePurchases = computed(() => {
    return cardMovements.value.filter(m => m.tipo === 'gasto' && m.monto_pendiente > 0);
});

const currentBreakdown = computed(() => {
    const key = selectedStat.value?.key;
    if (key === 'ingresos') return summaryData.value?.ingresos_por_categoria || [];
    if (key === 'gastos') return summaryData.value?.gastos_por_categoria || [];
    if (key === 'balance') return summaryData.value?.cuentas_detalle || [];
    if (key === 'deuda') return summaryData.value?.tarjetas_detalle || [];
    return [];
});

const currentTotal = computed(() => {
    return currentBreakdown.value.reduce((sum, item) => sum + item.total, 0);
});

const doughnutData = computed(() => ({
    labels: currentBreakdown.value.map(i => i.nombre),
    datasets: [{
        data: currentBreakdown.value.map(i => i.total),
        backgroundColor: currentBreakdown.value.map(i => i.color || '#6366f1'),
        borderWidth: 0,
        hoverOffset: 15
    }]
}));

const doughnutOptions = reactive({
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
        legend: { display: false },
        tooltip: {
            callbacks: {
                label: (context) => ' ' + formatCurrency(context.raw)
            }
        }
    },
    cutout: '75%'
});

const stats = computed(() => [
    { key: 'balance', title: 'Balance Total', value: summaryData.value?.balance_total || 0, trend: 0, icon: 'wallet', type: 'primary' },
    { key: 'deuda', title: 'Deuda Tarjetas', value: summaryData.value?.deuda_tarjetas || 0, trend: 0, icon: 'credit-card', type: 'danger' },
    { key: 'gastos', title: 'Gastos del Mes', value: summaryData.value?.gastos_mes || 0, trend: 0, icon: 'trendingDown', type: 'danger' },
    { key: 'ingresos', title: 'Ingresos del Mes', value: summaryData.value?.ingresos_mes || 0, trend: 0, icon: 'trendingUp', type: 'success' },
    { key: 'rendimientos', title: 'Rendimientos', value: summaryData.value?.rendimientos_mes || 0, trend: 0, icon: 'star', type: 'warning' },
]);

const recentMovements = computed(() => summaryData.value?.movimientos_recientes || []);

const chartData = computed(() => {
    const flujo = summaryData.value?.flujo_mensual || [];
    const labels = flujo.map(f => f.label);
    const incomeData = flujo.map(f => f.ingresos);
    const expenseData = flujo.map(f => f.gastos);

    const incomeColor = getCssVar('--success') || '#10b981';
    const expenseColor = getCssVar('--danger') || '#ef4444';

    return {
        labels,
        datasets: [
            {
                label: 'Ingresos',
                data: incomeData,
                borderColor: incomeColor,
                backgroundColor: incomeColor + '1A',
                fill: true,
                tension: 0.4,
                pointRadius: 4,
            },
            {
                label: 'Gastos',
                data: expenseData,
                borderColor: expenseColor,
                backgroundColor: expenseColor + '1A',
                fill: true,
                tension: 0.4,
                pointRadius: 4,
            }
        ]
    };
});

onMounted(async () => {
    try {
        const response = await api.finanzas.getResumen();
        summaryData.value = response.data;
    } catch (err) {
        console.error('Error al cargar resumen financiero', err);
    } finally {
        loading.value = false;
    }
});

const chartOptions = computed(() => {
    const textColor = getCssVar('--text-secondary') || '#94a3b8';
    const gridColor = theme.value === 'dark' ? 'rgba(255,255,255,0.05)' : 'rgba(0,0,0,0.05)';

    return {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: { display: false },
            tooltip: {
                mode: 'index',
                intersect: false,
                padding: 12,
            }
        },
        scales: {
            y: {
                grid: { color: gridColor },
                ticks: { 
                    color: textColor,
                    callback: (value) => '$' + value.toLocaleString()
                }
            },
            x: {
                grid: { display: false },
                ticks: { color: textColor }
            }
        }
    };
});

const formatCurrency = (val) => {
    return new Intl.NumberFormat('es-MX', { style: 'currency', currency: 'MXN' }).format(val);
};

const formatDateDay = (dateStr) => {
    if (!dateStr) return '--';
    const date = new Date(dateStr);
    return date.getDate().toString().padStart(2, '0');
};

const formatDateMonth = (dateStr) => {
    if (!dateStr) return '---';
    const date = new Date(dateStr);
    const months = ['ENE', 'FEB', 'MAR', 'ABR', 'MAY', 'JUN', 'JUL', 'AGO', 'SEP', 'OCT', 'NOV', 'DIC'];
    return months[date.getMonth()];
};
</script>

<style lang="scss" scoped>
.resumen-financiero {
    display: flex;
    flex-direction: column;
    gap: 2rem;
}

.stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
    gap: 1.5rem;
}

.stat-card {
    background: var(--bg-secondary);
    border: 1px solid var(--border-color);
    padding: 1.5rem;
    border-radius: 20px;
    display: flex;
    align-items: center;
    gap: 1.25rem;
    transition: all 0.3s ease;
    position: relative;
    overflow: hidden;

    &.clickable {
        cursor: pointer;
        &:hover {
            transform: translateY(-5px);
            border-color: var(--primary);
            .click-indicator { opacity: 1; transform: translateX(0); }
        }
    }

    &.primary { border-left: 4px solid var(--primary); }
    &.success { border-left: 4px solid var(--success); }
    &.danger { border-left: 4px solid var(--danger); }
    &.warning { border-left: 4px solid var(--warning); }
}

.stat-icon {
    width: 3.5rem;
    height: 3.5rem;
    background: var(--bg-tertiary);
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: var(--text-secondary);
}

.stat-info {
    .stat-title { font-size: 0.85rem; color: var(--text-tertiary); text-transform: uppercase; }
    .stat-value { font-size: 1.5rem; font-weight: 800; color: var(--text-primary); margin: 0; }
    .stat-delta { font-size: 0.8rem; display: flex; align-items: center; gap: 0.25rem; &.up { color: var(--success); } &.down { color: var(--danger); } }
}

.click-indicator { position: absolute; right: 1rem; opacity: 0; transform: translateX(10px); transition: all 0.3s ease; color: var(--primary); }

.finance-main-grid {
    display: grid;
    grid-template-columns: 2fr 1fr;
    gap: 1.5rem;
    @media (max-width: 1200px) { grid-template-columns: 1fr; }
}

.glass-panel {
    background: var(--bg-secondary);
    border: 1px solid var(--border-color);
    border-radius: 24px;
    padding: 1.5rem;
}

.section-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1.5rem;
    h3 { font-size: 1.1rem; color: var(--text-primary); font-weight: 700; margin: 0; }
}

.chart-container { height: 300px; }

.upcoming-list { display: flex; flex-direction: column; gap: 1rem; }

.expense-item {
    display: flex;
    align-items: center;
    gap: 1rem;
    padding: 1rem;
    background: var(--bg-tertiary);
    border-radius: 16px;
    transition: all 0.2s ease;
    &:hover { background: var(--bg-secondary); transform: translateX(4px); }
    .expense-day {
        display: flex; flex-direction: column; align-items: center; width: 45px; padding: 5px; background: var(--bg-primary); border-radius: 8px;
        .day { font-weight: 700; font-size: 1.1rem; color: var(--primary); }
        .month { font-size: 0.65rem; text-transform: uppercase; color: var(--text-tertiary); }
    }
    .expense-detail { flex: 1; display: flex; flex-direction: column; .name { font-weight: 600; color: var(--text-primary); } .category { font-size: 0.75rem; color: var(--text-tertiary); } }
    .expense-amount { font-weight: 700; font-size: 0.95rem; }
}

/* Modal Styles */
.modal-breakdown {
    display: grid;
    grid-template-columns: 1fr 1.2fr;
    gap: 2rem;
    padding: 1rem 0;
    &.is-drilldown { grid-template-columns: 1fr; }
    @media (max-width: 768px) { grid-template-columns: 1fr; }
}

.breakdown-chart {
    position: relative; height: 250px; display: flex; align-items: center; justify-content: center;
    .chart-center-info { position: absolute; text-align: center; .label { font-size: 0.75rem; color: var(--text-tertiary); } .value { font-size: 1.25rem; font-weight: 800; } }
}

.breakdown-list { display: flex; flex-direction: column; gap: 1rem; max-height: 400px; overflow-y: auto; padding-right: 0.5rem; }

.breakdown-item {
    display: flex; align-items: center; gap: 1rem; padding: 0.75rem; border-radius: 16px; background: var(--bg-tertiary);
    &.clickable-item { cursor: pointer; &:hover { background: var(--bg-secondary); transform: translateX(5px); } }
    .item-icon { width: 40px; height: 40px; border-radius: 12px; display: flex; align-items: center; justify-content: center; }
    .item-info { flex: 1; .name { font-size: 0.9rem; font-weight: 600; } .progress-bar { height: 6px; background: var(--bg-secondary); border-radius: 100px; overflow: hidden; .progress { height: 100%; border-radius: 100px; } } }
    .item-value { text-align: right; .amount { font-size: 0.9rem; font-weight: 700; } .percent { font-size: 0.75rem; color: var(--text-tertiary); } }
}

/* Drilldown (Level 2) Styles */
.drilldown-container { width: 100%; animation: fadeIn 0.4s ease; }

.drilldown-header-modern {
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
    margin-bottom: 2rem;

    .btn-back-modern {
        background: var(--primary);
        color: white;
        border: none;
        display: flex;
        align-items: center;
        gap: 0.5rem;
        font-weight: 700;
        cursor: pointer;
        padding: 0.6rem 1.2rem;
        border-radius: 12px;
        width: fit-content;
        transition: all 0.3s ease;
        &:hover { transform: translateX(-5px); box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3); }
    }

    .card-identity {
        display: flex;
        align-items: center;
        gap: 1.5rem;
        background: var(--bg-tertiary);
        padding: 1.5rem;
        border-radius: 20px;
        border: 1px solid var(--border-color);

        .identity-icon { width: 48px; height: 48px; border-radius: 12px; display: flex; align-items: center; justify-content: center; }
        .identity-text { flex: 1; h3 { font-size: 1.25rem; font-weight: 800; margin: 0; } span { color: var(--text-tertiary); font-size: 0.85rem; } }
        .identity-badge { text-align: right; .label { font-size: 0.7rem; color: var(--text-tertiary); display: block; } .value { font-size: 1.1rem; font-weight: 800; color: var(--error); } }
    }
}

.report-table-container {
    background: var(--bg-tertiary);
    border-radius: 16px;
    border: 1px solid var(--border-color);
    overflow: hidden;
    width: 100%;
}

.report-table {
    width: 100%;
    border-collapse: collapse;
    th { background: rgba(0,0,0,0.2); padding: 1rem; text-align: left; font-size: 0.75rem; color: var(--text-tertiary); text-transform: uppercase; }
    td { padding: 1rem; border-bottom: 1px solid var(--border-color); font-size: 0.9rem; }
    tr:last-child td { border-bottom: none; }

    .concept { .main { font-weight: 700; display: block; } .cat { font-size: 0.75rem; color: var(--text-tertiary); } }
    .msi-tracker { width: 180px; .tracker-info { display: flex; justify-content: space-between; font-size: 0.7rem; margin-bottom: 4px; .progress-text { font-weight: 800; color: var(--primary); } } .tracker-bar { height: 6px; background: var(--bg-secondary); border-radius: 10px; overflow: hidden; .fill { height: 100%; background: var(--primary); } } }
    .status-pill { padding: 4px 10px; border-radius: 6px; font-size: 0.7rem; font-weight: 800; &.gray { background: var(--bg-secondary); color: var(--text-secondary); } }
}

.spinner-premium { width: 40px; height: 40px; border: 3px solid var(--bg-tertiary); border-top-color: var(--primary); border-radius: 50%; animation: spin 1s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }
@keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }

.modal-simple-info { padding: 3rem 1rem; text-align: center; .info-card { display: flex; flex-direction: column; align-items: center; gap: 1rem; h3 { font-size: 2rem; font-weight: 800; } } }
</style>
