<template>
    <div v-if="show" class="projection-fullscreen-overlay animate-fade-in">
        <div class="overlay-header">
            <div class="header-left">
                <div class="card-icon-small">
                    <slot name="header-icon">
                        <Icon :name="icon" :size="24" />
                    </slot>
                </div>
                <div class="header-titles">
                    <h3>{{ title }}</h3>
                    <span>{{ subtitle }}</span>
                </div>
            </div>
            <div class="header-actions">
                <slot name="extra-controls"></slot>
                <button 
                    class="btn-export-pdf" 
                    @click="$emit('export')" 
                    :disabled="loading"
                >
                    <Icon name="file-text" :size="18" />
                    <span>Exportar PDF</span>
                </button>
                <button class="btn-close-overlay" @click="$emit('close')" aria-label="Cerrar">
                    <Icon name="x" :size="20" />
                </button>
            </div>
        </div>

        <div class="overlay-content">
            <div v-if="loading" class="flex items-center justify-center h-full">
                <div class="spinner-premium"></div>
            </div>
            <div v-else class="projection-grid">
                <!-- Left: Sidebar (Metrics & Table) -->
                <aside class="projection-sidebar">
                    <div class="metrics-row">
                        <slot name="metrics"></slot>
                    </div>

                    <div class="table-card">
                        <div class="card-header">
                            <Icon name="list" :size="14" />
                            <span>{{ tableTitle }}</span>
                        </div>
                        <div class="table-container">
                            <slot name="table"></slot>
                        </div>
                    </div>
                </aside>

                <!-- Right: Main (Chart or Details) -->
                <main class="projection-main">
                    <!-- Chart View -->
                    <div v-show="viewMode === 'chart'" class="chart-view-container animate-slide-up">
                        <div class="view-header">
                            <div class="title-group">
                                <h4>{{ chartTitle }}</h4>
                                <p>{{ chartSubtitle }}</p>
                            </div>
                        </div>
                        <div class="main-chart-wrapper">
                            <slot name="chart"></slot>
                        </div>
                    </div>

                    <!-- Details View -->
                    <div v-if="viewMode === 'details'" class="details-view-container animate-slide-in">
                        <div class="view-header">
                            <button class="btn-back" @click="$emit('update:viewMode', 'chart')">
                                <Icon name="arrow-left" :size="20" />
                            </button>
                            <div class="title-group">
                                <slot name="details-header"></slot>
                            </div>
                        </div>
                        <div class="details-content">
                            <slot name="details-content"></slot>
                        </div>
                    </div>
                </main>
            </div>
        </div>
    </div>
</template>

<script setup>
import Icon from '@/components/Icon.vue';

defineProps({
    show: Boolean,
    loading: Boolean,
    title: String,
    subtitle: String,
    icon: { type: String, default: 'trending-up' },
    tableTitle: { type: String, default: 'Cronograma' },
    chartTitle: { type: String, default: 'Evolución' },
    chartSubtitle: { type: String, default: 'Proyección detallada' },
    viewMode: { type: String, default: 'chart' }
});

defineEmits(['close', 'export', 'update:viewMode']);
</script>

<style lang="scss" scoped>
/* Copied and adjusted from CuentasAhorro.vue / TarjetasCredito.vue */
.projection-fullscreen-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: var(--bg-primary);
    z-index: 9999;
    display: flex;
    flex-direction: column;
    overflow: hidden;

    .overlay-header {
        padding: 0.8rem 2rem;
        background: var(--bg-secondary);
        border-bottom: 1px solid var(--border-color);
        display: flex;
        justify-content: space-between;
        align-items: center;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);

        .header-left {
            display: flex;
            align-items: center;
            gap: 1.5rem;

            .card-icon-small {
                width: 40px;
                height: 40px;
                background: var(--bg-tertiary);
                border-radius: 10px;
                display: flex;
                align-items: center;
                justify-content: center;
                color: var(--primary);
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
            }

            .header-titles {
                h3 {
                    margin: 0;
                    font-size: 1.2rem;
                    font-weight: 800;
                    letter-spacing: -0.02em;
                    color: var(--text-primary);
                }
                span {
                    color: var(--text-tertiary);
                    font-size: 0.8rem;
                    font-weight: 500;
                }
            }
        }

        .header-actions {
            display: flex;
            align-items: center;
            gap: 1rem;

            .btn-export-pdf {
                background: rgba(var(--primary-rgb), 0.1);
                border: 1px solid rgba(var(--primary-rgb), 0.2);
                color: var(--primary);
                padding: 0.6rem 1.2rem;
                border-radius: 10px;
                font-weight: 600;
                display: flex;
                align-items: center;
                gap: 0.6rem;
                transition: all 0.2s ease;

                &:hover:not(:disabled) {
                    background: var(--primary);
                    color: white;
                    transform: translateY(-2px);
                }

                &:disabled { opacity: 0.5; cursor: not-allowed; }
            }

            .btn-close-overlay {
                background: transparent;
                border: none;
                color: var(--text-secondary);
                cursor: pointer;
                padding: 0.5rem;
                border-radius: 0.5rem;
                display: flex;
                align-items: center;
                justify-content: center;
                transition: all 0.2s;

                &:hover {
                    background: var(--bg-tertiary);
                    color: var(--text-primary);
                }
            }
        }
    }

    .overlay-content {
        flex: 1;
        padding: 1.5rem;
        background: var(--bg-primary);
        display: flex;
        flex-direction: column;
        overflow: hidden;
        min-height: 0;

        .projection-grid {
            display: grid;
            grid-template-columns: 350px 1fr;
            grid-template-rows: 1fr;
            gap: 1.5rem;
            max-width: 1600px;
            margin: 0 auto;
            flex: 1;
            width: 100%;
            min-height: 0;
            height: 100%;

            @media (max-width: 1200px) {
                grid-template-columns: 1fr;
                flex: none;
                height: auto;
                overflow-y: auto;
            }

            .projection-sidebar {
                display: flex;
                flex-direction: column;
                gap: 0.75rem;

                .metrics-row {
                    display: grid;
                    grid-template-columns: 1fr;
                    gap: 1rem;
                }

                .table-card {
                    background: var(--bg-secondary);
                    border-radius: 20px;
                    border: 1px solid var(--border-color);
                    display: flex;
                    flex-direction: column;
                    overflow: hidden;
                    flex: 1;
                    min-height: 0;

                    .card-header {
                        padding: 0.8rem 1.2rem;
                        background: var(--bg-tertiary);
                        border-bottom: 1px solid var(--border-color);
                        display: flex;
                        align-items: center;
                        gap: 0.75rem;
                        font-size: 0.8rem;
                        font-weight: 800;
                        color: var(--text-secondary);
                        text-transform: uppercase;
                    }

                    .table-container {
                        flex: 1;
                        overflow-y: auto;
                    }
                }
            }

            .projection-main {
                background: var(--bg-secondary);
                border-radius: 20px;
                border: 1px solid var(--border-color);
                box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
                overflow: hidden;
                display: flex;
                flex-direction: column;
                min-height: 0;

                .chart-view-container, .details-view-container {
                    flex: 1;
                    display: flex;
                    flex-direction: column;
                    min-height: 0;
                }

                .view-header {
                    padding: 0.8rem 1.5rem;
                    border-bottom: 1px solid var(--border-color);
                    display: flex;
                    align-items: center;
                    gap: 1.5rem;

                    .btn-back {
                        background: var(--bg-tertiary);
                        border: none;
                        width: 36px;
                        height: 36px;
                        border-radius: 10px;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        color: var(--text-primary);
                        transition: all 0.2s ease;

                        &:hover {
                            background: var(--primary);
                            color: white;
                        }
                    }

                    .title-group {
                        h4 {
                            margin: 0;
                            font-size: 1.1rem;
                            font-weight: 800;
                            color: var(--text-primary);
                        }
                        p {
                            margin: 0.1rem 0 0;
                            font-size: 0.8rem;
                            color: var(--text-tertiary);
                        }
                    }
                }

                .main-chart-wrapper {
                    flex: 1;
                    padding: 1.2rem;
                    min-height: 0;
                }

                .details-content {
                    flex: 1;
                    padding: 1.2rem;
                    display: flex;
                    flex-direction: column;
                    overflow: hidden;
                    min-height: 0;

                    .month-summary-cards {
                        display: grid;
                        grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
                        gap: 1.5rem;
                        margin-bottom: 2rem;
                        flex-shrink: 0;

                        .s-card {
                            background: var(--bg-tertiary);
                            padding: 1.2rem;
                            border-radius: 16px;
                            display: flex;
                            flex-direction: column;
                            gap: 0.4rem;
                            transition: transform 0.2s;

                            &:hover { transform: translateY(-3px); }

                            .label { font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.05em; color: var(--text-tertiary); font-weight: 700; }
                            .value { font-size: 1.2rem; font-weight: 800; color: var(--text-primary); }
                        }
                    }

                    .movements-drilldown {
                        flex: 1;
                        display: flex;
                        flex-direction: column;
                        min-height: 0;
                        h5 { font-size: 0.8rem; font-weight: 800; color: var(--text-tertiary); margin-bottom: 1.5rem; letter-spacing: 0.1em; flex-shrink: 0; }

                        :deep(.drilldown-list) {
                            flex: 1;
                            overflow-y: auto;
                            display: flex;
                            flex-direction: column;
                            gap: 1rem;
                            padding-right: 0.5rem;

                            /* Custom scrollbar for drilldown list */
                            &::-webkit-scrollbar { width: 6px; }
                            &::-webkit-scrollbar-track { background: transparent; }
                            &::-webkit-scrollbar-thumb { background: rgba(var(--primary-rgb), 0.1); border-radius: 10px; }
                            &::-webkit-scrollbar-thumb:hover { background: rgba(var(--primary-rgb), 0.2); }
                        }
                    }
                }
            }
        }
    }
}

.metric-card {
    background: var(--bg-tertiary);
    padding: 1.2rem 1.5rem;
    border-radius: 16px;
    display: flex;
    flex-direction: column;
    gap: 0.4rem;
    border: 1px solid var(--border-color);
    transition: all 0.2s;

    &:hover { border-color: var(--primary); transform: translateY(-2px); }

    &.highlight { background: linear-gradient(135deg, rgba(var(--primary-rgb), 0.1), transparent); border-left: 4px solid var(--primary); }

    .label { font-size: 0.65rem; font-weight: 800; color: var(--text-tertiary); text-transform: uppercase; letter-spacing: 0.05em; }
    .value { font-size: 1.3rem; font-weight: 900; color: var(--text-primary); letter-spacing: -0.02em; }
}

.animate-fade-in { animation: fadeIn 0.3s ease-out; }
.animate-slide-up { animation: slideUp 0.4s cubic-bezier(0.4, 0, 0.2, 1); }
.animate-slide-in { animation: slideIn 0.3s ease-out; }

@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
@keyframes slideUp { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
@keyframes slideIn { from { opacity: 0; transform: translateX(20px); } to { opacity: 1; transform: translateX(0); } }

:deep(.mini-table) {
    width: 100%;
    border-collapse: collapse;

    thead th {
        position: sticky;
        top: 0;
        background: var(--bg-tertiary);
        padding: 0.75rem 1.5rem;
        text-align: left;
        font-size: 0.7rem;
        font-weight: 800;
        color: var(--text-tertiary);
        text-transform: uppercase;
        border-bottom: 1px solid var(--border-color);
        z-index: 10;
    }

    tbody tr {
        border-bottom: 1px solid var(--border-color);
        transition: all 0.2s;
        cursor: pointer;

        &:hover { background: rgba(var(--primary-rgb), 0.04); }
        &.current { background: rgba(var(--primary-rgb), 0.08); border-left: 4px solid var(--primary); }

        td {
            padding: 0.8rem 1.5rem;
            font-size: 0.85rem;
            color: var(--text-secondary);
        }
    }
}

:deep(.month-summary-cards) {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
    gap: 1.5rem;
    margin-bottom: 2.5rem;

    .s-card {
        background: var(--bg-tertiary);
        padding: 1.2rem;
        border-radius: 16px;
        display: flex;
        flex-direction: column;
        gap: 0.4rem;
        transition: transform 0.2s;

        &:hover { transform: translateY(-3px); }

        .label { font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.05em; color: var(--text-tertiary); font-weight: 700; }
        .value { font-size: 1.2rem; font-weight: 800; color: var(--text-primary); }

        &.income .value, &.ingreso .value { color: var(--success); }
        &.expense .value, &.gasto .value { color: var(--error); }
        &.yield .value, &.rendimiento .value { color: var(--warning); }
        &.total {
            background: var(--primary);
            .label { color: rgba(255, 255, 255, 0.7); }
            .value { color: white; }
        }
    }
}

:deep(.movements-drilldown) {
    h5 { font-size: 0.8rem; font-weight: 800; color: var(--text-tertiary); margin-bottom: 1.5rem; letter-spacing: 0.1em; }
}

:deep(.drilldown-list) {
    flex: 1;
    overflow-y: auto;
    display: flex;
    flex-direction: column;
    gap: 1rem;
    padding-right: 0.5rem;

    /* Custom scrollbar for drilldown list */
    &::-webkit-scrollbar { width: 6px; }
    &::-webkit-scrollbar-track { background: transparent; }
    &::-webkit-scrollbar-thumb { background: rgba(var(--primary-rgb), 0.1); border-radius: 10px; }
    &::-webkit-scrollbar-thumb:hover { background: rgba(var(--primary-rgb), 0.2); }

    .drilldown-item {
        background: var(--bg-tertiary);
        border-radius: 16px;
        padding: 1rem 1.2rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        border: 1px solid rgba(255, 255, 255, 0.03);
        position: relative;
        overflow: hidden;

        &::before {
            content: '';
            position: absolute;
            left: 0;
            top: 0;
            bottom: 0;
            width: 4px;
            opacity: 0;
            transition: opacity 0.3s;
        }

        &.ingreso::before, &.ingresos::before { background: var(--success); }
        &.gasto::before, &.gastos::before { background: var(--error); }
        &.rendimiento::before { background: #eab308; }

        &:hover { 
            transform: translateX(8px); 
            border-color: rgba(var(--primary-rgb), 0.3); 
            background: var(--bg-secondary);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
            &::before { opacity: 1; }
        }

        &.has-expansion { cursor: pointer; }
        &.is-expanded { 
            border-bottom-left-radius: 0; 
            border-bottom-right-radius: 0; 
            background: var(--bg-secondary);
            border-color: rgba(var(--primary-rgb), 0.2);
            &::before { opacity: 1; }
        }

        .item-left {
            display: flex;
            align-items: center;
            gap: 1.2rem;

            .item-icon {
                width: 42px;
                height: 42px;
                border-radius: 12px;
                display: flex;
                align-items: center;
                justify-content: center;
                transition: transform 0.3s;

                &.ingreso, &.ingresos { background: linear-gradient(135deg, rgba(var(--success-rgb), 0.2), rgba(var(--success-rgb), 0.05)); color: var(--success); }
                &.gasto, &.gastos { background: linear-gradient(135deg, rgba(var(--error-rgb), 0.2), rgba(var(--error-rgb), 0.05)); color: var(--error); }
                &.rendimiento { background: linear-gradient(135deg, rgba(234, 179, 8, 0.2), rgba(234, 179, 8, 0.05)); color: #eab308; }
            }
        }

        &:hover .item-icon { transform: scale(1.1); }

        .item-info {
            display: flex;
            flex-direction: column;
            .item-name { font-weight: 700; color: var(--text-primary); font-size: 0.95rem; letter-spacing: -0.01em; }
            .item-meta { 
                display: flex;
                align-items: center;
                gap: 0.5rem;
                font-size: 0.75rem; 
                color: var(--text-tertiary); 
                margin-top: 2px;
                .ms-1 { transition: transform 0.3s; }
            }
        }

        &.is-expanded .ms-1 { transform: rotate(180deg); }

        .amount-bubble {
            padding: 0.5rem 1rem;
            border-radius: 12px;
            font-weight: 800;
            font-size: 0.95rem;
            letter-spacing: -0.02em;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);

            &.ingreso, &.rendimiento, &.ingresos { background: rgba(var(--success-rgb), 0.1); color: var(--success); border: 1px solid rgba(var(--success-rgb), 0.2); }
            &.gasto, &.gastos { background: rgba(var(--error-rgb), 0.1); color: var(--error); border: 1px solid rgba(var(--error-rgb), 0.2); }
        }
    }

    .item-expansion-content {
        background: rgba(255, 255, 255, 0.02);
        backdrop-filter: blur(4px);
        margin: 0 0.5rem 0.5rem;
        border-radius: 0 0 16px 16px;
        padding: 0.5rem;
        border: 1px solid rgba(var(--primary-rgb), 0.1);
        border-top: none;
        max-height: 250px;
        overflow-y: auto;

        /* Custom scrollbar for expansion content */
        &::-webkit-scrollbar { width: 4px; }
        &::-webkit-scrollbar-track { background: transparent; }
        &::-webkit-scrollbar-thumb { background: rgba(var(--primary-rgb), 0.2); border-radius: 10px; }

        .expansion-row {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 0.7rem 1rem;
            border-radius: 8px;
            margin-bottom: 2px;
            transition: background 0.2s;
            font-size: 0.8rem;
            color: var(--text-secondary);

            &:hover { background: rgba(255, 255, 255, 0.03); }
            &:last-child { margin-bottom: 0; }

            .row-date {
                display: flex;
                align-items: center;
                gap: 0.75rem;
                color: var(--text-tertiary);
                .icon { opacity: 0.6; }
            }

            .row-amount {
                font-weight: 700;
                color: var(--text-primary);
                font-family: 'Inter', sans-serif;
            }
        }
    }
}
</style>
