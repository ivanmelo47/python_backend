<template>
    <Transition name="modal-fade">
        <div v-if="isOpen" class="modal-overlay" @click.self="close">
            <div class="modal-container modal-xl">
                <!-- Header -->
                <div class="modal-header">
                    <div class="header-content">
                        <div class="header-icon">
                            <Icon name="folder" :size="18" />
                        </div>
                        <h3 class="modal-title">
                            Historial de Archivos y Carpetas
                        </h3>
                    </div>
                    <button @click="close" class="close-btn" title="Cerrar">
                        <Icon name="x" :size="20" />
                    </button>
                </div>

                <!-- Body -->
                <div class="modal-body custom-scroll">
                    <!-- Gráfica -->
                    <div class="chart-container">
                        <div class="chart-header">
                            <h4 class="section-subtitle">Aumento de Volumen</h4>
                            <select v-model="selectedPeriod" class="period-select">
                                <option value="today">Día Actual</option>
                                <option value="3days">Últimos 3 días</option>
                                <option value="7days">Últimos 7 días</option>
                                <option value="15days">Últimos 15 días</option>
                                <option value="30days">Últimos 30 días</option>
                            </select>
                        </div>
                        <div class="chart-wrapper">
                            <Line v-if="chartData.labels.length > 0" :data="chartData" :options="chartOptions" />
                            <div v-else class="empty-chart">Cargando datos métricos...</div>
                        </div>
                    </div>

                    <!-- Tabla de items -->
                    <div class="users-list-container">
                        <h4 class="section-subtitle">Últimos Elementos Creados ({{ allItems.length }})</h4>
                        <div class="data-table">
                            <table>
                                <thead>
                                    <tr>
                                        <th>Tipo</th>
                                        <th>Nombre</th>
                                        <th>Agregado Por</th>
                                        <th>Tamaño</th>
                                        <th>Fecha de Creación</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr v-for="item in allItems" :key="item.type + item.id">
                                        <td>
                                            <span class="role-badge" :class="item.type === 'folder' ? 'bg-indigo' : 'bg-green'">
                                                {{ item.type === 'folder' ? 'Carpeta' : (item.extension || 'Archivo').toUpperCase() }}
                                            </span>
                                        </td>
                                        <td class="font-medium text-primary">
                                            <div class="item-name-cell">
                                                <div class="item-mini-icon" v-html="getItemIcon(item)"></div>
                                                <span>{{ item.name || item.original_name || 'Desconocido' }}</span>
                                            </div>
                                        </td>
                                        <td>{{ item.owner?.name || item.creator?.name || 'Desconocido' }}</td>
                                        <td class="text-sm font-mono">{{ formatSize(item.file_size || item.size) }}</td>
                                        <td>{{ formatTime(item.created_at) }}</td>
                                    </tr>
                                    <tr v-if="allItems.length === 0">
                                        <td colspan="5" class="text-center py-4">No se han creado elementos recientes.</td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </Transition>
</template>

<script setup>
import { computed, ref } from 'vue';
import Icon from '@/components/Icon.vue';
import { Line } from 'vue-chartjs';
import {
    Chart as ChartJS,
    Title,
    Tooltip,
    Legend,
    LineElement,
    PointElement,
    CategoryScale,
    LinearScale,
    Filler
} from 'chart.js';

ChartJS.register(Title, Tooltip, Legend, LineElement, PointElement, CategoryScale, LinearScale, Filler);

const props = defineProps({
    isOpen: {
        type: Boolean,
        default: false
    },
    files: {
        type: Array,
        default: () => []
    },
    folders: {
        type: Array,
        default: () => []
    }
});

const emit = defineEmits(['close']);
const close = () => emit('close');

// Combinar y ordenar todos los elementos
const allItems = computed(() => {
    const f = props.files.map(i => ({ ...i, type: 'file' }));
    const d = props.folders.map(i => ({ ...i, type: 'folder' }));
    
    return [...f, ...d].sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
});

// Filtro de Periodo
const selectedPeriod = ref('7days'); // Defaulting to 7 days to show more data initially

// Preparar Data para la Gráfica
const chartData = computed(() => {
    const data = {
        labels: [],
        datasets: [
            {
                label: 'Archivos/Carpetas Creadas',
                backgroundColor: 'rgba(249, 115, 22, 0.2)', // Orange theme (var(--primary) like)
                borderColor: 'rgb(249, 115, 22)',
                borderWidth: 2,
                pointBackgroundColor: '#ffffff',
                pointBorderColor: 'rgb(249, 115, 22)',
                pointBorderWidth: 2,
                pointRadius: 4,
                pointHoverRadius: 6,
                fill: true,
                tension: 0.4,
                data: [],
                customItems: []
            }
        ]
    };

    if (allItems.value.length === 0) return data;

    const groupedData = {};
    const labelsOrder = [];
    const now = new Date();
    let currentHour = now.getHours();

    // Rellenamos el eje X base
    if (selectedPeriod.value === 'today') {
        for (let i = 0; i <= currentHour; i++) {
            let hr = i.toString().padStart(2, '0');
            let label = `${hr}:00`;
            groupedData[label] = { count: 0, items: [], label: label };
            labelsOrder.push(label);
        }
    } else {
        const days = parseInt(selectedPeriod.value.replace('days', ''));
        now.setHours(0,0,0,0);
        for (let i = days - 1; i >= 0; i--) {
            let d = new Date(now);
            d.setDate(d.getDate() - i);
            let y = d.getFullYear();
            let m = (d.getMonth() + 1).toString().padStart(2, '0');
            let day = d.getDate().toString().padStart(2, '0');
            let key = `${y}-${m}-${day}`;
            groupedData[key] = { count: 0, items: [], label: `${day}/${m}` };
            labelsOrder.push(key);
        }
    }

    // Iteramos e insertamos
    allItems.value.forEach(item => {
        if (!item.created_at) return;
        const date = new Date(item.created_at);
        let key = null;

        if (selectedPeriod.value === 'today') {
            if (date.toDateString() === new Date().toDateString()) {
                let hr = date.getHours().toString().padStart(2, '0');
                key = `${hr}:00`;
            }
        } else {
            let y = date.getFullYear();
            let m = (date.getMonth() + 1).toString().padStart(2, '0');
            let day = date.getDate().toString().padStart(2, '0');
            key = `${y}-${m}-${day}`;
        }

        if (key && groupedData[key]) {
            groupedData[key].count += 1;
            const typeLabel = item.type === 'folder' ? 'Carpeta' : (item.extension || 'Archivo').toUpperCase();
            const nameLabel = item.name || item.original_name || 'Desconocido';
            groupedData[key].items.push(`[${typeLabel}] ${nameLabel}`);
        }
    });

    labelsOrder.forEach(key => {
        data.labels.push(groupedData[key].label);
        data.datasets[0].data.push(groupedData[key].count);
        data.datasets[0].customItems.push(groupedData[key].items);
    });

    return data;
});

const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
        legend: { display: false },
        tooltip: {
            mode: 'index',
            intersect: false,
            callbacks: {
                title: (context) => `Fecha/Hora: ${context[0].label}`,
                label: (context) => ` ${context.raw} elemento(s) creado(s)`,
                afterLabel: (context) => {
                    const idx = context.dataIndex;
                    const itemsArr = context.dataset.customItems[idx];
                    if (itemsArr && itemsArr.length) {
                        // Max 5 items per tooltip to prevent huge overflow
                        const slice = itemsArr.slice(0, 5);
                        let text = '\nHan creado:\n• ' + slice.join('\n• ');
                        if (itemsArr.length > 5) {
                            text += `\n... y ${itemsArr.length - 5} más`;
                        }
                        return text;
                    }
                    return '';
                }
            }
        }
    },
    scales: {
        x: {
            grid: { display: false }
        },
        y: {
            beginAtZero: true,
            ticks: { stepSize: 1, precision: 0 },
            grid: {
                borderDash: [5, 5],
                color: 'rgba(150, 150, 150, 0.1)'
            }
        }
    },
    interaction: {
        mode: 'nearest',
        axis: 'x',
        intersect: false
    }
};

// Utils
const formatTime = (dateString) => {
    if (!dateString) return '---';
    const date = new Date(dateString);
    return date.toLocaleString('es-ES', { 
        hour: '2-digit', minute: '2-digit', 
        day: '2-digit', month: 'short', year: 'numeric'
    });
};

const formatSize = (bytes) => {
    if (bytes === 0 || !bytes) return '---';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};

const getItemIcon = (item) => {
    let svg = '';
    if (item.type === 'folder') {
        svg = item.icon?.svg_content;
    } else {
        svg = item.configuration?.icon?.svg_content || item.icon?.svg_content;
    }
    
    if (!svg) {
        // Fallback simple icons if no SVG in DB
        return item.type === 'folder' 
            ? '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"></path></svg>'
            : '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2"><path d="M13 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z"></path><polyline points="13 2 13 9 20 9"></polyline></svg>';
    }
    
    // Ensure size is consistent
    return svg.replace('<svg ', '<svg width="18" height="18" ');
};

</script>

<style scoped>
.modal-fade-enter-active,
.modal-fade-leave-active {
    transition: opacity 0.2s ease, transform 0.2s ease;
}

.modal-fade-enter-from,
.modal-fade-leave-to {
    opacity: 0;
    transform: scale(0.95);
}

.modal-xl {
    max-width: 900px !important;
    width: 95%;
}

.custom-scroll {
    overflow-y: auto;
    max-height: 75vh;
}

.chart-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 1px solid var(--border-color);
    margin-bottom: 1rem;
    padding-bottom: 0.5rem;
}

.section-subtitle {
    font-size: 1.1rem;
    font-weight: 600;
    color: var(--text-primary);
    margin: 0;
}

.period-select {
    padding: 0.25rem 0.5rem;
    border-radius: 6px;
    background-color: var(--bg-tertiary, rgba(255, 255, 255, 0.05));
    border: 1px solid var(--border-color);
    color: var(--text-primary);
    font-size: 0.85rem;
    cursor: pointer;
    outline: none;
    transition: all 0.2s;
}

.period-select:focus {
    border-color: var(--primary);
}

.chart-container {
    margin-bottom: 2rem;
}

.chart-wrapper {
    height: 250px;
    width: 100%;
    position: relative;
    background: var(--bg-secondary);
    border-radius: 12px;
    padding: 1rem;
    border: 1px solid var(--border-color);
}

.empty-chart {
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    color: var(--text-secondary);
    font-size: 0.9rem;
    font-style: italic;
}

.users-list-container {
    margin-top: 1rem;
}

table {
    width: 100%;
    border-collapse: collapse;
}

th, td {
    padding: 12px 16px;
    text-align: left;
    border-bottom: 1px solid var(--border-color);
}

th {
    background-color: var(--bg-tertiary, rgba(200, 200, 200, 0.05));
    color: var(--text-secondary);
    font-weight: 600;
    font-size: 0.85rem;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

td {
    color: var(--text-primary);
    font-size: 0.9rem;
}

tbody tr:hover {
    background-color: var(--bg-secondary);
}

.role-badge {
    padding: 4px 10px;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 600;
    color: #fff;
}

.bg-indigo { background: rgba(99, 102, 241, 0.9); }
.bg-green { background: rgba(16, 185, 129, 0.9); }

.item-name-cell {
    display: flex;
    align-items: center;
    gap: 0.75rem;
}

.item-mini-icon {
    display: flex;
    align-items: center;
    justify-content: center;
    color: var(--text-secondary);
    width: 18px;
    height: 18px;
    flex-shrink: 0;
}

:deep(.item-mini-icon svg) {
    width: 18px;
    height: 18px;
}

.font-mono { font-family: monospace; }
</style>
