<template>
    <Transition name="modal-fade">
        <div v-if="isOpen" class="modal-overlay" @click.self="close">
            <div class="modal-container modal-xl">
                <!-- Header -->
                <div class="modal-header">
                    <div class="header-content">
                        <div class="header-icon">
                            <Icon name="activity" :size="18" />
                        </div>
                        <h3 class="modal-title">
                            Detalle de Sesiones Activas
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
                            <h4 class="section-subtitle">Historial de Accesos</h4>
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

                    <!-- Tabla de usuarios -->
                    <div class="users-list-container">
                        <h4 class="section-subtitle">Usuarios Conectados ({{ activeSessions.length }})</h4>
                        <div class="data-table">
                            <table>
                                <thead>
                                    <tr>
                                        <th>Usuario</th>
                                        <th>Rol</th>
                                        <th>Hora de Login</th>
                                        <th>Navegador / Dispositivo</th>
                                        <th>Dirección IP</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr v-for="session in activeSessions" :key="session.id">
                                        <td class="font-medium text-primary">{{ session.user?.name || 'Desconocido' }}</td>
                                        <td>
                                            <span class="role-badge" :class="getRoleClass(session.user?.role?.name)">
                                                {{ session.user?.role?.name || 'Usuario' }}
                                            </span>
                                        </td>
                                        <td>{{ formatTime(session.login_at) }}</td>
                                        <td class="text-sm">{{ getBrowser(session.user_agent) }}</td>
                                        <td class="text-sm font-mono">{{ session.ip_address }}</td>
                                    </tr>
                                    <tr v-if="activeSessions.length === 0">
                                        <td colspan="5" class="text-center py-4">No hay sesiones activas en este momento.</td>
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
import { computed, watch, ref } from 'vue';
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
    sessions: {
        type: Array,
        default: () => []
    }
});

const emit = defineEmits(['close']);
const close = () => emit('close');

// Filtrar estrictamente a los "Activos"
const activeSessions = computed(() => {
    return props.sessions.filter(item => {
        const status = item.derived_status || (item.logout_at ? 'Inactivo' : 'Activo');
        return status === 'Activo';
    }).sort((a, b) => new Date(b.login_at) - new Date(a.login_at));
});

// Filtro de Periodo
const selectedPeriod = ref('today');

// Preparar Data para la Gráfica
const chartData = computed(() => {
    const data = {
        labels: [],
        datasets: [{
            label: 'Usuarios Logueados',
            backgroundColor: 'rgba(99, 102, 241, 0.2)', // Indigo translúcido para el relleno
            borderColor: 'rgb(99, 102, 241)',
            borderWidth: 2,
            pointBackgroundColor: '#ffffff',
            pointBorderColor: 'rgb(99, 102, 241)',
            pointBorderWidth: 2,
            pointRadius: 4,
            pointHoverRadius: 6,
            fill: true, // "estado financiero" (área bajo la curva)
            tension: 0.4, // Suaviza la línea
            data: [],
            customUsers: []
        }]
    };

    if (props.sessions.length === 0) return data;

    const groupedData = {};
    const labelsOrder = [];
    const now = new Date();
    let currentHour = now.getHours();

    // Rellenamos el eje X base
    if (selectedPeriod.value === 'today') {
        for (let i = 0; i <= currentHour; i++) {
            let hr = i.toString().padStart(2, '0');
            let label = `${hr}:00`;
            groupedData[label] = { count: 0, users: [], label: label };
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
            groupedData[key] = { count: 0, users: [], label: `${day}/${m}` };
            labelsOrder.push(key);
        }
    }

    // Iteramos todas las sesiones y las agregamos a su "canasta" correspondiente
    props.sessions.forEach(session => {
        if (!session.login_at) return;
        const date = new Date(session.login_at);
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
            groupedData[key].users.push(session.user?.name || 'Desconocido');
        }
    });

    // Pasamos datos ordenados a ChartJS
    labelsOrder.forEach(key => {
        data.labels.push(groupedData[key].label);
        data.datasets[0].data.push(groupedData[key].count);
        data.datasets[0].customUsers.push(groupedData[key].users);
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
                title: (context) => `Hora: ${context[0].label}`,
                label: (context) => ` ${context.raw} usuario(s) conectados`,
                afterLabel: (context) => {
                    const idx = context.dataIndex;
                    const users = context.dataset.customUsers[idx];
                    if (users && users.length) {
                        return '\nUsuarios:\n• ' + users.join('\n• ');
                    }
                    return '';
                }
            }
        }
    },
    scales: {
        x: {
            grid: {
                display: false // Oculta líneas verticales para un estilo más limpio
            }
        },
        y: {
            beginAtZero: true,
            ticks: { stepSize: 1, precision: 0 },
            grid: {
                borderDash: [5, 5],
                color: 'rgba(150, 150, 150, 0.1)' // Líneas horizontales punteadas sutiles
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
        day: '2-digit', month: 'short' 
    });
};

const getBrowser = (userAgent) => {
    if (!userAgent) return 'Desconocido';
    const ua = userAgent.toLowerCase();
    if (ua.includes('chrome')) return 'Google Chrome';
    if (ua.includes('firefox')) return 'Mozilla Firefox';
    if (ua.includes('safari')) return 'Apple Safari';
    if (ua.includes('edge')) return 'Microsoft Edge';
    return userAgent.split(' ')[0] || 'Desconocido';
};

const getRoleClass = (roleName) => {
    const role = (roleName || '').toLowerCase();
    if (role.includes('admin') || role.includes('master')) return 'role-admin';
    if (role.includes('manager')) return 'role-manager';
    return 'role-user';
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
}

.role-admin { background: rgba(239, 68, 68, 0.1); color: #ef4444; }
.role-manager { background: rgba(59, 130, 246, 0.1); color: #3b82f6; }
.role-user { background: rgba(16, 185, 129, 0.1); color: #10b981; }

.font-mono { font-family: monospace; }
</style>
