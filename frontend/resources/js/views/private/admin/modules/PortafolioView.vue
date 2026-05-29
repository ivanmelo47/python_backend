<template>
    <section class="portfolio-admin">
        <nav class="portfolio-nav">
            <button type="button" class="nav-pill" :class="{ active: navFilter === 'all' }" @click="navFilter = 'all'">
                Gestion general
            </button>
            <button
                type="button"
                class="nav-pill"
                :class="{ active: navFilter === 'published' }"
                @click="navFilter = 'published'"
            >
                Publicados
            </button>
            <button
                type="button"
                class="nav-pill"
                :class="{ active: navFilter === 'draft' }"
                @click="navFilter = 'draft'"
            >
                Borradores
            </button>
        </nav>

        <Table
            title="Portafolios"
            :columns="columns"
            :rows="rowsForTable"
            :search-query="searchQuery"
            v-model:items-per-page="itemsPerPage"
            @update:searchQuery="searchQuery = $event"
            @request-data="refreshData"
            @row-click="handleRowClick"
            @toggle-status="handleToggleStatus"
            pagination-mode="client"
            :loading="isLoading"
            search-placeholder="Buscar portafolio..."
            card-title-template="Portafolio - {name}"
            :show-header-actions="true"
        >
            <template #header-actions>
                <div class="header-actions-wrap">
                    <span class="header-counter">{{ rowsForTable.length }} registros</span>
                    <button class="btn-solid-dark" @click="openCreateView">+ NUEVO</button>
                </div>
            </template>

            <template #cell-name="{ value }">
                <span class="main-text">{{ value }}</span>
            </template>

            <template #cell-ownerName="{ value }">
                <span class="main-text">{{ value }}</span>
            </template>

            <template #cell-token="{ value }">
                <span class="token-pill">{{ value }}</span>
            </template>


            <template #cell-publicUrl="{ row }">
                <a
                    class="public-link"
                    :href="buildPublicUrl(row.token)"
                    target="_blank"
                    rel="noopener noreferrer"
                    @click.stop
                >
                    {{ buildPublicUrl(row.token) }}
                </a>
            </template>

            <template #cell-actions="{ row }">
                <button class="dropdown-item" @click.stop="copyPublicUrl(row.token)">
                    <span>Copiar URL</span>
                </button>
                <button class="dropdown-item" @click.stop="openEditView(row)">
                    <span>Editar</span>
                </button>
                <button class="dropdown-item delete" @click.stop="removePortfolio(row.id)">
                    <span>Eliminar</span>
                </button>
            </template>
        </Table>

        <div v-if="isBasicModalOpen" class="basic-modal-overlay">
            <article class="basic-modal-card">
                <header class="basic-system-header">
                    <div class="basic-header-content">
                        <span class="basic-header-icon" aria-hidden="true">i</span>
                        <div>
                            <h3 class="basic-header-title">Datos basicos del portafolio</h3>
                            <p class="basic-header-subtitle">Paso 1 de 2. Configura la informacion principal.</p>
                        </div>
                    </div>
                    <button type="button" class="basic-close-btn" @click="closeBasicModal" aria-label="Cerrar modal">
                        x
                    </button>
                </header>

                <form class="basic-modal-form" @submit.prevent="proceedToBlocks">
                    <div class="basic-modal-body">
                        <div class="basic-form-grid">
                            <label>
                                Nombre del portafolio
                                <input v-model.trim="draftBasic.name" type="text" required maxlength="80" />
                            </label>

                            <label>
                                Nombre del usuario
                                <input v-model.trim="draftBasic.ownerName" type="text" required maxlength="80" />
                            </label>

                            <label class="full-width">
                                Descripcion corta
                                <textarea v-model.trim="draftBasic.summary" rows="3" maxlength="180" required></textarea>
                            </label>

                            <label>
                                Token (6 caracteres)
                                <div class="token-input-row">
                                    <input
                                        v-model.trim="draftBasic.token"
                                        type="text"
                                        minlength="6"
                                        maxlength="6"
                                        required
                                        @input="draftBasic.token = sanitizeToken(draftBasic.token)"
                                    />
                                    <button type="button" class="btn" @click="draftBasic.token = assignNewToken()">
                                        Generar
                                    </button>
                                </div>
                            </label>

                            <label>
                                Estado
                                <select v-model="draftBasic.status">
                                    <option value="draft">Borrador</option>
                                    <option value="published">Publicado</option>
                                </select>
                            </label>

                            <label class="full-width">
                                URL publica final
                                <input :value="buildPublicUrl(draftBasic.token)" type="text" readonly />
                            </label>

                            <p v-if="formError" class="form-error full-width">{{ formError }}</p>
                        </div>
                    </div>

                    <footer class="basic-system-footer">
                        <button type="button" class="btn" @click="closeBasicModal">Cancelar</button>
                        <button type="submit" class="btn btn--primary">Crear y editar</button>
                    </footer>
                </form>
            </article>
        </div>

    </section>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue';
import { useRouter } from 'vue-router';
import Table from '@/views/private/admin/components/Table.vue';
import { useTableConfig } from '@/composables/useTableConfig';
import { api } from '@/services/api';
import { useAlert } from '@/composables/useAlert';
import { FRONTEND_BASE_URL } from '@/services/api/url';

const { itemsPerPage } = useTableConfig();
const router = useRouter();
const alert = useAlert();
const searchQuery = ref('');
const isBasicModalOpen = ref(false);
const navFilter = ref('all');
const formError = ref('');
const isLoading = ref(false);

const columns = [
    { key: 'actions', label: 'ACCIONES', headerClass: 'compact', cellClass: 'compact' },
    { key: 'name', label: 'PORTAFOLIO' },
    { key: 'ownerName', label: 'USUARIO' },
    { key: 'token', label: 'TOKEN' },
    { 
        key: 'status', 
        label: 'ESTADO', 
        type: 'switch', 
        activeLabel: 'Publicado', 
        inactiveLabel: 'Borrador',
        headerClass: 'text-center',
        cellClass: 'text-center'
    },
    { key: 'publicUrl', label: 'URL PUBLICA' }
];

const portfolios = ref([

]);

const draftBasic = reactive({
    name: '',
    ownerName: '',
    summary: '',
    token: '',
    status: 'draft'
});

const draftBlocks = reactive(defaultBlocks());

onMounted(() => {
    fetchPortfolios();
});

const rowsForTable = computed(() => {
    const rows = portfolios.value.map(item => ({
        ...item,
        publicUrl: buildPublicUrl(item.token)
    }));

    if (navFilter.value === 'all') {
        return rows;
    }

    return rows.filter(item => item.status === navFilter.value);
});

function refreshData() {
    return fetchPortfolios();
}

function handleRowClick(row) {
    router.push({
        name: 'PortafolioEditor',
        params: { id: String(row.id) }
    });
}

function buildPublicUrl(token) {
    const origin = FRONTEND_BASE_URL || (typeof window !== 'undefined' ? window.location.origin : 'https://tu-dominio.com');
    const cleaned = sanitizeToken(token || '______');
    return `${origin}/portafolio-usuario/${cleaned}`;
}

function mapApiPortfolio(item) {
    return {
        id: item.id,
        name: item.name,
        ownerName: item.owner_name,
        summary: item.summary,
        token: item.token,
        status: item.status,
        blocks: item.blocks || defaultBlocks()
    };
}

async function fetchPortfolios() {
    isLoading.value = true;

    try {
        const params = {
            per_page: 200,
            search: searchQuery.value,
            ...(navFilter.value !== 'all' ? { status: navFilter.value } : {})
        };

        const response = await api.portfolios.getPortfolios(params);
        const rows = Array.isArray(response?.data?.data) ? response.data.data : [];
        portfolios.value = rows.map(mapApiPortfolio);
    } catch (error) {
        console.error('Error loading portfolios', error);
        alert.toast.error('Error', 'No se pudieron cargar los portafolios.');
    } finally {
        isLoading.value = false;
    }
}

function sanitizeToken(value) {
    return String(value || '')
        .toUpperCase()
        .replace(/[^A-Z0-9]/g, '')
        .slice(0, 6);
}

function generateToken() {
    const alphabet = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789';
    let token = '';

    while (token.length < 6) {
        token += alphabet[Math.floor(Math.random() * alphabet.length)];
    }

    return token;
}

function assignNewToken() {
    let attempts = 0;
    let token = generateToken();

    while (isTokenTaken(token) && attempts < 20) {
        token = generateToken();
        attempts += 1;
    }

    return token;
}

function defaultBlocks() {
    return {
        profile: {
            name: 'Tu Nombre Apellido',
            role: 'Desarrollador Full Stack',
            summary:
                'Desarrollador orientado a producto, enfocado en crear soluciones robustas que combinan rendimiento, claridad visual y buena experiencia de usuario.'
        },
        avatarUrl: 'https://i.pravatar.cc/420?img=68',
        metrics: [
            { value: '6+', label: 'anos de experiencia' },
            { value: '25+', label: 'proyectos entregados' },
            { value: '100%', label: 'enfoque en calidad' }
        ],
        skills: [
            'Arquitectura modular',
            'Resolucion de problemas',
            'Comunicacion con negocio',
            'Liderazgo tecnico',
            'Testing y mejora continua',
            'Optimizacion de rendimiento'
        ],
        technologies: ['Laravel', 'PHP 8.4', 'Vue 3', 'Vite', 'Sass', 'MySQL', 'Docker', 'Nginx', 'JWT', 'Git'],
        projects: [
            {
                id: 1,
                title: 'Gestor inteligente de archivos',
                description: 'Control de documentos, permisos por roles y flujo de trabajo para equipos internos.',
                detailedDescription:
                    'Sistema documental con control de permisos por rol, versionado, auditoria y busquedas rapidas para equipos con alto volumen de informacion.',
                type: 'Web Platform',
                repoUrl: 'https://github.com/tu-usuario/gestor-archivos',
                liveUrl: 'https://gestor-archivos.tu-dominio.com',
                images: [
                    'https://picsum.photos/seed/gestor-1/960/620',
                    'https://picsum.photos/seed/gestor-2/960/620',
                    'https://picsum.photos/seed/gestor-3/960/620'
                ],
                imagesText:
                    'https://picsum.photos/seed/gestor-1/960/620\nhttps://picsum.photos/seed/gestor-2/960/620\nhttps://picsum.photos/seed/gestor-3/960/620'
            }
        ],
        jobs: [
            { id: 1, role: 'Senior Software Developer', company: 'Tech Studio', period: '2023 - Actualidad' },
            { id: 2, role: 'Full Stack Developer', company: 'Digital Factory', period: '2020 - 2023' },
            { id: 3, role: 'Backend Developer', company: 'Solutions Lab', period: '2018 - 2020' }
        ],
        education: [
            { id: 1, title: 'Ingenieria en Sistemas', institution: 'Universidad Tecnologica', period: '2014 - 2018' },
            { id: 2, title: 'Diplomado en Arquitectura de Software', institution: 'Academia Tech', period: '2019' }
        ],
        courses: [
            { id: 1, title: 'Escalabilidad y performance web', provider: 'Plataforma Online Pro' },
            { id: 2, title: 'Clean Architecture aplicada', provider: 'Code Academy' },
            { id: 3, title: 'Diseno UX para desarrolladores', provider: 'UX Institute' }
        ],
        contact: {
            email: 'tuemail@dominio.com'
        }
    };
}

function applyBlocks(blocks) {
    const source = blocks || defaultBlocks();
    Object.keys(draftBlocks).forEach(key => {
        draftBlocks[key] = source[key] ?? defaultBlocks()[key];
    });
}

function isTokenTaken(token) {
    const normalized = sanitizeToken(token);
    return portfolios.value.some(item => item.token === normalized);
}

function resetForm() {
    draftBasic.name = '';
    draftBasic.ownerName = '';
    draftBasic.summary = '';
    draftBasic.token = '';
    draftBasic.status = 'draft';
    applyBlocks(defaultBlocks());
    formError.value = '';
}

function openCreateView() {
    resetForm();
    draftBasic.token = assignNewToken();
    isBasicModalOpen.value = true;
}

function openEditView(item) {
    router.push({
        name: 'PortafolioEditor',
        params: { id: String(item.id) }
    });
}

function closeBasicModal() {
    isBasicModalOpen.value = false;
    resetForm();
}

function proceedToBlocks() {
    const sanitizedToken = sanitizeToken(draftBasic.token);

    if (sanitizedToken.length !== 6) {
        formError.value = 'El token debe tener exactamente 6 caracteres.';
        return;
    }

    if (isTokenTaken(sanitizedToken)) {
        formError.value = 'Ese token ya existe. Genera uno nuevo o cambia el valor.';
        return;
    }

    const normalizedPayload = {
        name: draftBasic.name,
        owner_name: draftBasic.ownerName,
        summary: draftBasic.summary,
        token: sanitizedToken,
        status: draftBasic.status,
        blocks: JSON.parse(JSON.stringify(draftBlocks))
    };

    createPortfolio(normalizedPayload);
}

async function createPortfolio(payload) {
    try {
        const response = await api.portfolios.createPortfolio(payload);
        const created = mapApiPortfolio(response.data.data);

        portfolios.value.unshift(created);
        formError.value = '';
        isBasicModalOpen.value = false;
        resetForm();

        router.push({
            name: 'PortafolioEditor',
            params: { id: String(created.id) }
        });
    } catch (error) {
        if (error.response?.data?.errors?.token?.[0]) {
            formError.value = error.response.data.errors.token[0];
            return;
        }

        formError.value = error.response?.data?.message || 'No se pudo crear el portafolio.';
    }
}

async function removePortfolio(id) {
    const confirmed = await alert.fire({
        title: '¿Eliminar portafolio?',
        text: 'Esta accion no se puede deshacer.',
        type: 'warning',
        showCancel: true,
        confirmText: 'Si, eliminar',
        cancelText: 'Cancelar'
    });

    if (!confirmed) {
        return;
    }

    try {
        await api.portfolios.deletePortfolio(id);
        portfolios.value = portfolios.value.filter(item => item.id !== id);
        alert.toast.success('Eliminado', 'Portafolio eliminado correctamente.');
    } catch (error) {
        alert.toast.error('Error', 'No se pudo eliminar el portafolio.');
    }
}

async function handleToggleStatus({ row }) {
    const originalStatus = row.status;
    const isPublished = originalStatus === 'published';
    const newStatus = isPublished ? 'draft' : 'published';
    const actionText = isPublished ? 'pasar a borrador' : 'publicar';

    const confirmed = await alert.fire({
        title: `¿${isPublished ? 'Despublicar' : 'Publicar'} portafolio?`,
        text: `¿Estás seguro de que deseas ${actionText} "${row.name}"?`,
        type: 'warning',
        showCancel: true,
        confirmText: `Sí, ${actionText}`,
        cancelText: 'Cancelar'
    });

    if (!confirmed) {
        // Table component handles local state, but we might need to refresh if it was changed
        return;
    }

    try {
        await api.portfolios.updatePortfolio(row.id, { status: newStatus });
        row.status = newStatus;
        alert.toast.success(
            isPublished ? 'Borrador' : 'Publicado', 
            `El portafolio ahora está ${newStatus === 'published' ? 'publicado' : 'en modo borrador'}.`
        );
    } catch (error) {
        console.error('Error toggling status', error);
        alert.toast.error('Error', 'No se pudo actualizar el estado del portafolio.');
        // Revert local state if needed (Table handles it partially, but rows are in portfolios.value)
        const p = portfolios.value.find(item => item.id === row.id);
        if (p) p.status = originalStatus;
    }
}

async function copyPublicUrl(token) {
    const url = buildPublicUrl(token);

    try {
        await navigator.clipboard.writeText(url);
    } catch (error) {
        console.warn('No se pudo copiar la URL', error);
    }
}
</script>

<style scoped>
.portfolio-admin {
    display: grid;
    gap: 0.9rem;
}

.portfolio-nav {
    display: flex;
    gap: 0.55rem;
    background: var(--bg-secondary);
    border: 1px solid var(--border-color);
    border-radius: 0.8rem;
    padding: 0.4rem;
    width: fit-content;
}

.nav-pill {
    border: 1px solid transparent;
    background: transparent;
    color: var(--text-secondary);
    border-radius: 0.6rem;
    padding: 0.45rem 0.75rem;
    font-weight: 600;
    cursor: pointer;
}

.nav-pill.active {
    background: rgba(var(--primary-rgb), 0.18);
    border-color: rgba(var(--primary-rgb), 0.35);
    color: var(--text-primary);
}

.header-actions-wrap {
    display: flex;
    align-items: center;
    gap: 0.55rem;
}

.header-counter {
    font-size: 0.8rem;
    color: var(--text-secondary);
}

.main-text {
    color: var(--text-primary);
    font-weight: 500;
}

.token-pill {
    display: inline-flex;
    background: var(--bg-secondary);
    border: 1px solid var(--border-color);
    border-radius: 999px;
    padding: 0.2rem 0.55rem;
    font-weight: 700;
}

.status-pill {
    border-radius: 999px;
    padding: 0.2rem 0.52rem;
    font-size: 0.78rem;
    font-weight: 700;
    border: 1px solid transparent;
}

.status-pill.published {
    color: #0b7f49;
    border-color: rgba(16, 185, 129, 0.35);
    background: rgba(16, 185, 129, 0.16);
}

.status-pill.draft {
    color: #a16207;
    border-color: rgba(245, 158, 11, 0.35);
    background: rgba(245, 158, 11, 0.16);
}

.public-link {
    color: var(--primary);
    text-decoration: none;
}

.basic-modal-overlay {
    position: fixed;
    inset: 0;
    z-index: 1250;
    background: rgba(0, 0, 0, 0.45);
    display: grid;
    place-items: center;
    padding: 0.55rem;
}

.basic-modal-card {
    width: min(1200px, calc(100vw - 1.1rem));
    max-height: calc(100vh - 1.1rem);
    border: 1px solid var(--border-color);
    border-radius: 1rem;
    background: var(--bg-primary);
    box-shadow: 0 24px 52px rgba(0, 0, 0, 0.28);
    overflow: hidden;
    display: flex;
    flex-direction: column;
}

.basic-system-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 0.8rem;
    padding: 0.95rem 1.15rem;
    background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
    color: #ffffff;
}

.basic-header-content {
    display: flex;
    align-items: center;
    gap: 0.7rem;
}

.basic-header-icon {
    width: 1.75rem;
    height: 1.75rem;
    border-radius: 999px;
    background: rgba(255, 255, 255, 0.22);
    border: 1px solid rgba(255, 255, 255, 0.28);
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-weight: 700;
}

.basic-header-title {
    margin: 0;
    font-size: 1.1rem;
    font-weight: 700;
}

.basic-header-subtitle {
    margin: 0.2rem 0 0;
    color: rgba(255, 255, 255, 0.92);
    font-size: 0.9rem;
}

.basic-close-btn {
    border: 1px solid rgba(255, 255, 255, 0.35);
    background: rgba(255, 255, 255, 0.12);
    color: #ffffff;
    width: 2rem;
    height: 2rem;
    border-radius: 999px;
    font-size: 1rem;
    font-weight: 700;
    line-height: 1;
    cursor: pointer;
}

.basic-modal-form {
    display: flex;
    flex-direction: column;
    min-height: 0;
    flex: 1;
}

.basic-modal-body {
    padding: 1rem 1.15rem;
    overflow: auto;
    min-height: 0;
}

.basic-form-grid {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 0.75rem;
}

.basic-form-grid label {
    display: grid;
    gap: 0.35rem;
    font-size: 0.88rem;
    color: var(--text-secondary);
}

input,
textarea,
select {
    width: 100%;
    border: 1px solid var(--border-color);
    border-radius: 0.65rem;
    background: var(--bg-primary);
    color: var(--text-primary);
    padding: 0.6rem 0.75rem;
}

.token-input-row {
    display: grid;
    grid-template-columns: 1fr auto;
    gap: 0.5rem;
}

.full-width {
    grid-column: span 2;
}

.form-error {
    margin: 0;
    color: #b91c1c;
    font-weight: 600;
}

.basic-system-footer {
    display: flex;
    justify-content: end;
    gap: 0.5rem;
    border-top: 1px solid var(--border-color);
    background: var(--bg-secondary);
    padding: 0.85rem 1.15rem;
}
.btn {
    border: 1px solid var(--border-color);
    background: var(--bg-primary);
    color: var(--text-primary);
    border-radius: 0.64rem;
    padding: 0.46rem 0.7rem;
    cursor: pointer;
    font-weight: 600;
}

.btn--primary {
    background: var(--primary);
    border-color: var(--primary);
    color: #ffffff;
}

@media (max-width: 760px) {
    .portfolio-nav {
        width: 100%;
        overflow-x: auto;
    }

    .basic-system-header {
        flex-direction: column;
        align-items: stretch;
    }

    .basic-header-content {
        align-items: flex-start;
    }

    .basic-form-grid {
        grid-template-columns: 1fr;
    }

    .full-width {
        grid-column: span 1;
    }

    .basic-system-footer {
        justify-content: stretch;
    }

    .basic-system-footer .btn {
        flex: 1;
    }
}
</style>
