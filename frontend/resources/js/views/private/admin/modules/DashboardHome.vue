<template>
    <div class="dashboard-home">
        <div class="welcome-section">
            <h2 class="welcome-title">Bienvenido al Panel de Administración, <span>{{ userName }}</span></h2>
            <p class="welcome-subtitle">Selecciona una opción del menú o revisa las métricas principales para comenzar.</p>
        </div>
        
        <div class="dashboard-grid">
            <!-- Admin only: Sesiones Activas -->
            <div class="stat-card clickable-card" v-if="isAdmin" @click="isSessionsModalOpen = true">
                <div class="stat-header">
                    <div class="icon">
                        <Icon name="activity" :size="24" />
                    </div>
                    <span class="trend positive">En vivo</span>
                </div>
                <div class="stat-value" :class="{ 'loading-text': isLoadingSessions }">
                    {{ isLoadingSessions ? '...' : activeSessionsCount }}
                </div>
                <div class="stat-label">SESIONES ACTIVAS</div>
                <div class="stat-footer-text">Click para ver detalle en tiempo real</div>
            </div>

            <!-- Existing cards -->
            <div class="stat-card">
                <div class="stat-header">
                    <div class="icon">
                        <Icon name="users" :size="24" />
                    </div>
                    <span class="trend neutral">Confirmados</span>
                </div>
                <div class="stat-value" :class="{ 'loading-text': isLoadingUsers }">
                    {{ isLoadingUsers ? '...' : activeUsersCount }}
                </div>
                <div class="stat-label">USUARIOS CONFIRMADOS</div>
                <div class="stat-footer-text">Registrados en la plataforma</div>
            </div>
            
            <div class="stat-card clickable-card" @click="openFilesModal">
                <div class="stat-header">
                    <div class="icon">
                        <Icon name="folder" :size="24" />
                    </div>
                    <span class="trend neutral">Esta semana</span>
                </div>
                <div class="stat-value" :class="{ 'loading-text': isLoadingFiles }">
                    {{ isLoadingFiles ? '...' : newFilesCount }}
                </div>
                <div class="stat-label">ARCHIVOS NUEVOS</div>
                <div class="stat-footer-text">Click para ver historial creado</div>
            </div>
            
            <div class="stat-card" v-if="isAdmin">
                <div class="stat-header">
                    <div class="icon">
                        <Icon name="dashboard" :size="24" />
                    </div>
                    <span class="trend" :class="performanceMetrics.overall > 80 ? 'danger-text' : 'positive-text'">
                        {{ performanceMetrics.overall > 80 ? 'Alta Carga' : 'Óptimo' }}
                    </span>
                </div>
                <div class="stat-value" :class="{ 'loading-text': isLoadingPerformance }" style="font-size: 1.8rem;">
                    {{ isLoadingPerformance ? '...' : `${performanceMetrics.cpu}% / ${performanceMetrics.ram}%` }}
                </div>
                <div class="stat-label">Uso CPU / RAM</div>
                <div class="stat-footer-text">Carga del servidor (VPS)</div>
            </div>

            <!-- New Settings Card -->
            <ThemeScaleCard />

            <ModalActiveSessions
                v-if="isAdmin"
                :isOpen="isSessionsModalOpen"
                :sessions="sessionsData"
                @close="isSessionsModalOpen = false"
            />

            <ModalActiveFiles
                :isOpen="isFilesModalOpen"
                :files="filesData"
                :folders="foldersData"
                @close="isFilesModalOpen = false"
            />
        </div>
    </div>
</template>

<script setup>
import { ref, onMounted, computed, onUnmounted } from 'vue';
import Icon from '@/components/Icon.vue';
import ThemeScaleCard from '../components/ThemeScaleCard.vue';
import ModalActiveSessions from '../components/ModalActiveSessions.vue';
import ModalActiveFiles from '../components/ModalActiveFiles.vue';
import { useAuth } from '@/composables/useAuth';
import authApi from '@/services/api/endpoints/auth';
import usersApi from '@/services/api/endpoints/users';
import filesApi from '@/services/api/endpoints/files';
import foldersApi from '@/services/api/endpoints/folders';
import systemApi from '@/services/api/endpoints/system';

const { user } = useAuth();
const userName = computed(() => {
    return user.value?.name ? user.value.name.split(' ')[0] : '';
});

const isAdmin = computed(() => {
    if (user.value?.is_supermaster) return true;
    const roleName = (user.value?.role?.name || '').toLowerCase();
    const slug = (user.value?.role?.slug || '').toLowerCase();
    return roleName.includes('admin') || roleName.includes('super') || slug.includes('admin');
});

const activeSessionsCount = ref(0);
const sessionsData = ref([]);
const isSessionsModalOpen = ref(false);
const isLoadingSessions = ref(false);
let sessionsInterval = null;

const checkActiveSessions = async () => {
    if (!isAdmin.value) return;
    try {
        isLoadingSessions.value = true;
        const response = await authApi.getLoginActivities({ per_page: 500 });
        const items = response.data?.data || [];
        sessionsData.value = items;
        
        let count = 0;
        for (const item of items) {
           const status = item.derived_status || (item.logout_at ? 'Inactivo' : 'Activo');
           if (status === 'Activo') {
               count++;
           }
        }
        activeSessionsCount.value = count;
    } catch (error) {
        console.error('Error fetching sessions:', error);
    } finally {
        isLoadingSessions.value = false;
    }
};

const activeUsersCount = ref(0);
const isLoadingUsers = ref(false);

const loadConfirmedUsers = async () => {
    try {
        isLoadingUsers.value = true;
        const response = await usersApi.getUsers({ per_page: 2000 });
        const items = response.data?.data || [];
        let confirmedCount = 0;
        for (const u of items) {
            if (u.is_confirmed) {
                confirmedCount++;
            }
        }
        activeUsersCount.value = confirmedCount;
    } catch (err) {
        console.error('Error fetching users:', err);
    } finally {
        isLoadingUsers.value = false;
    }
};

const newFilesCount = ref(0);
const isLoadingFiles = ref(false);
const isFilesModalOpen = ref(false);
const filesData = ref([]);
const foldersData = ref([]);
let filesInterval = null;

const openFilesModal = () => {
    loadRecentFilesAndFolders();
    isFilesModalOpen.value = true;
};

const loadRecentFilesAndFolders = async () => {
    try {
        isLoadingFiles.value = true;
        let recentCount = 0;
        const now = new Date();
        const yesterday = new Date(now.getTime() - (24 * 60 * 60 * 1000));
        
        // Traer archivos y carpetas de TODAS las ubicaciones (no solo raíz)
        const [filesRes, foldersRes] = await Promise.all([
            filesApi.getFiles({ 
                per_page: 500, 
                sort_by: 'uploaded_at', 
                sort_dir: 'desc', 
                all_folders: 1 
            }),
            foldersApi.getFolders({ 
                per_page: 500, 
                sort_by: 'created_at', 
                sort_dir: 'desc', 
                all_parents: 1 
            })
        ]);
        
        const filesItems = filesRes.data?.data || [];
        const foldersItems = foldersRes.data?.data || [];
        
        filesData.value = filesItems;
        foldersData.value = foldersItems;
        
        for (const f of filesItems) {
            if (new Date(f.created_at) >= yesterday) {
                recentCount++;
            }
        }
        
        for (const folder of foldersItems) {
            if (new Date(folder.created_at) >= yesterday) {
                recentCount++;
            }
        }
        
        newFilesCount.value = recentCount;
    } catch (err) {
        console.error('Error fetching recent items:', err);
    } finally {
        isLoadingFiles.value = false;
    }
};

const performanceMetrics = ref({ cpu: 0, ram: 0, disk: 0, overall: 0 });
const isLoadingPerformance = ref(false);
let performanceInterval = null;

const loadPerformanceMetrics = async () => {
    if (!isAdmin.value) return;
    try {
        isLoadingPerformance.value = true;
        const response = await systemApi.getPerformanceMetrics();
        // El trait ApiResponser suele devolver status: 'éxito'
        if ((response?.data?.status === 'éxito' || response?.data?.status === 'success') && response?.data?.data) {
            performanceMetrics.value = response.data.data;
        }
    } catch (err) {
        console.error('Error fetching performance metrics:', err);
    } finally {
        isLoadingPerformance.value = false;
    }
};

onMounted(async () => {
    loadConfirmedUsers();
    loadRecentFilesAndFolders();
    if (isAdmin.value) {
        await checkActiveSessions();
        await loadPerformanceMetrics();
        sessionsInterval = setInterval(checkActiveSessions, 60000);
        performanceInterval = setInterval(loadPerformanceMetrics, 60000);
    }
    // Refresh files/folders counts every 2 minutes
    filesInterval = setInterval(loadRecentFilesAndFolders, 120000);
});

onUnmounted(() => {
    if (sessionsInterval) clearInterval(sessionsInterval);
    if (performanceInterval) clearInterval(performanceInterval);
    if (filesInterval) clearInterval(filesInterval);
});
</script>

<style scoped>
.dashboard-home {
    display: flex;
    flex-direction: column;
    gap: 2rem;
    overflow-y: auto;
    overflow-x: hidden;
    height: 100%;
    /* Empuja el scrollbar hacia el borde del contenedor padre si éste tiene padding */
    margin-right: -1rem;
    padding-right: 1rem;
    padding-bottom: 2rem;
}

/* Custom Scrollbar */
.dashboard-home::-webkit-scrollbar {
    width: 6px;
}

.dashboard-home::-webkit-scrollbar-track {
    background: transparent;
}

.dashboard-home::-webkit-scrollbar-thumb {
    background-color: var(--text-secondary);
    border-radius: 10px;
    opacity: 0.5;
}

.dashboard-home::-webkit-scrollbar-thumb:hover {
    background-color: var(--text-primary);
}

.welcome-section {
    margin-bottom: 1rem;
}

.welcome-title {
    font-size: 1.5rem;
    font-weight: 600;
    margin: 0 0 0.5rem 0;
    color: var(--text-primary);
}

.welcome-subtitle {
    font-size: 1rem;
    color: var(--text-secondary);
    margin: 0;
}

.dashboard-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 1.5rem;
    align-items: stretch;
}

/* Enhancing default stat-card nicely without overriding core variables */
:deep(.stat-card) {
    display: flex;
    flex-direction: column;
    transition: transform 0.2s cubic-bezier(0.4, 0, 0.2, 1), box-shadow 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

:deep(.stat-card:hover) {
    transform: translateY(-2px);
    box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.1);
}

:deep(.stat-card .stat-label) {
    text-transform: uppercase;
    letter-spacing: 0.5px;
    font-weight: 600;
    font-size: 0.8rem;
}

:deep(.stat-card .stat-value) {
    font-weight: 800;
}

.clickable-card {
    cursor: pointer;
    position: relative;
}

.clickable-card::after {
    content: '';
    position: absolute;
    inset: 0;
    border-radius: inherit;
    box-shadow: 0 0 0 2px var(--primary) inset;
    opacity: 0;
    transition: opacity 0.2s ease;
    pointer-events: none;
}

.clickable-card:hover::after {
    opacity: 1;
}

.trend {
    font-size: 0.75rem;
    font-weight: 600;
    padding: 0.35rem 0.85rem;
    border-radius: 9999px; /* Pill shape */
}

.trend.positive {
    background: rgba(16, 185, 129, 0.1);
    color: var(--success, #10b981);
}

.trend.positive-text {
    color: var(--success, #10b981);
    font-weight: 600;
    font-size: 0.85rem;
}

.trend.neutral {
    background: var(--bg-tertiary, rgba(200, 200, 200, 0.1));
    color: var(--text-secondary);
}

.stat-footer-text {
    font-size: 0.8rem;
    color: var(--text-secondary);
    margin-top: auto; /* Push to bottom */
    padding-top: 1rem;
    border-top: 1px solid var(--border-color, rgba(150, 150, 150, 0.2));
    opacity: 0.8;
}

.loading-text {
    opacity: 0.5;
    animation: pulse 1.5s infinite;
}

@keyframes pulse {
    0% {
        opacity: 0.5;
    }

    50% {
        opacity: 1;
    }

    100% {
        opacity: 0.5;
    }
}
</style>
