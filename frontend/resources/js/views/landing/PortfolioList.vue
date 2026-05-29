<template>
    <div id="app" ref="layoutRoot" class="directory-layout-container">
        <LandingNav class="directory-nav" />

        <!-- Immersive Premium Background -->
        <div class="premium-bg">
            <div class="mesh-gradient"></div>
            <div class="glow-orb orb-1"></div>
            <div class="glow-orb orb-2"></div>
        </div>

        <div class="landing-container">
            <div class="directory-wrapper animate-in">
                <!-- MAIN CONTENT AREA (Scrollable) -->
                <main class="directory-main">
                    <header class="main-header">
                        <div class="header-pretitle">
                            <div class="star-icon">
                                <Icon name="star" :size="14" />
                            </div>
                            <span>Comunidad de Profesionales</span>
                        </div>
                        <h1>Resultados del Directorio</h1>

                        <!-- Mini Stats Bar -->
                        <div class="stats-pills">
                            <div class="stat-pill">
                                <Icon name="users" :size="16" />
                                <span>{{ portfolios.length }} Miembros</span>
                            </div>
                            <div v-if="searchQuery" class="stat-pill active">
                                <Icon name="search" :size="16" />
                                <span>{{ filteredPortfolios.length }} Coincidencias</span>
                            </div>
                        </div>
                    </header>

                    <!-- Loading Experience -->
                    <div v-if="isLoading" class="loading-grid">
                        <div v-for="i in 4" :key="i" class="skeleton-card"></div>
                    </div>

                    <!-- No Results Interaction -->
                    <div v-else-if="filteredPortfolios.length === 0" class="not-found-view glass-panel">
                        <div class="not-found-icon">
                            <Icon name="search" :size="64" color="var(--text-tertiary)" />
                        </div>
                        <h2>Sin resultados</h2>
                        <p>No hay profesionales en "{{ searchQuery }}". Prueba otra categoría.</p>
                        <button @click="resetFilters" class="btn-refresh-glow">
                            <Icon name="refresh" :size="20" />
                            <span>Ver directorio completo</span>
                        </button>
                    </div>

                    <!-- Professional Grid -->
                    <div v-else class="portfolio-grid">
                        <article
                            v-for="item in filteredPortfolios"
                            :key="item.id"
                            class="pro-card"
                        >
                            <div class="pro-card-glow"></div>
                            <div class="pro-card-content">
                                <div class="pro-header">
                                    <div class="pro-avatar-box">
                                        <img v-if="item.avatarUrl" :src="item.avatarUrl" :alt="item.owner_name" />
                                        <div v-else class="avatar-placeholder">{{ item.owner_name.charAt(0) }}</div>
                                        <div class="online-indicator"></div>
                                    </div>
                                    <div class="pro-info">
                                        <div class="pro-tag">
                                            <Icon :name="getRoleIcon(item.role)" :size="12" />
                                            {{ item.role }}
                                        </div>
                                        <h3>{{ item.owner_name }}</h3>
                                    </div>
                                </div>

                                <div class="pro-bio">
                                    <p>{{ item.summary }}</p>
                                </div>

                                <div class="pro-tags-row">
                                    <span class="mini-tag"><Icon name="check" :size="10" /> Verificado</span>
                                    <span class="mini-tag"><Icon name="clock" :size="10" /> Portfolio</span>
                                </div>

                                <footer class="pro-footer-action">
                                    <router-link
                                        :to="{ name: 'PortfolioByToken', params: { token: item.token } }"
                                        class="pro-link"
                                    >
                                        <Icon name="eye" :size="18" />
                                        <span>Explorar Perfil</span>
                                        <Icon name="chevron-right" :size="14" class="arrow" />
                                    </router-link>
                                </footer>
                            </div>
                        </article>
                    </div>
                </main>

                <!-- SIDEBAR PANEL (Stationary/Fixed) -->
                <aside v-if="!isMobileViewport" class="directory-sidebar">
                    <div class="sidebar-fixed-content">
                        <!-- Search Widget -->
                        <div class="widget-glass search-widget">
                            <div class="widget-title">
                                <Icon name="search" :size="18" />
                                <h3>Búsqueda</h3>
                            </div>
                            <div class="input-container">
                                <input
                                    v-model="searchQuery"
                                    type="text"
                                    placeholder="Nombre, rol..."
                                    class="input-sidebar"
                                />
                            </div>
                        </div>

                        <!-- Categories Widget -->
                        <div class="widget-glass categories-widget">
                            <div class="widget-title">
                                <Icon name="list" :size="18" />
                                <h3>Filtros</h3>
                            </div>
                            <nav class="categories-nav">
                                <div
                                    v-for="(label, role) in roleIconsMap"
                                    :key="role"
                                    @click="toggleCategory(role)"
                                    :class="['nav-item', { active: searchQuery.toLowerCase() === role.toLowerCase() }]"
                                >
                                    <div class="nav-icon">
                                        <Icon :name="label.icon" :size="16" />
                                    </div>
                                    <span>{{ role }}</span>
                                    <span class="nav-count">{{ getCountByRole(role) }}</span>
                                </div>
                            </nav>
                        </div>

                        <!-- CTA Widget -->
                        <div class="widget-premium cta-widget">
                            <div class="premium-flare"></div>
                            <div class="cta-inner">
                                <!-- <Icon name="rocket" :size="32" class="mb-3" /> -->
                                <h4>¿Quieres destacar?</h4>
                                <p>Únete a nuestra comunidad hoy.</p>
                                <router-link to="/register" class="btn-join" @click="closeMobileSidebar">
                                    <span>Registrarme</span>
                                    <Icon name="plus" :size="18" />
                                </router-link>
                            </div>
                        </div>
                    </div>
                </aside>

                <button
                    v-if="isMobileViewport && !isMobileSidebarOpen"
                    class="sidebar-fab"
                    type="button"
                    aria-label="Abrir filtros"
                    @click="toggleMobileSidebar"
                >
                    <Icon name="list" :size="20" />
                </button>
            </div>
        </div>

        <ModalForm
            v-if="isMobileViewport"
            :is-visible="isMobileSidebarOpen"
            title="Filtros"
            size="md"
            :columns="1"
            :hide-footer="true"
            @close="closeMobileSidebar"
        >
            <div class="mobile-sidebar-content">
                <div class="widget-glass search-widget">
                    <div class="widget-title">
                        <Icon name="search" :size="18" />
                        <h3>Búsqueda</h3>
                    </div>
                    <div class="input-container">
                        <input
                            v-model="searchQuery"
                            type="text"
                            placeholder="Nombre, rol..."
                            class="input-sidebar"
                        />
                    </div>
                </div>

                <div class="widget-glass categories-widget">
                    <div class="widget-title">
                        <Icon name="list" :size="18" />
                        <h3>Filtros</h3>
                    </div>
                    <nav class="categories-nav">
                        <div
                            v-for="(label, role) in roleIconsMap"
                            :key="`mobile-${role}`"
                            @click="toggleCategory(role)"
                            :class="['nav-item', { active: searchQuery.toLowerCase() === role.toLowerCase() }]"
                        >
                            <div class="nav-icon">
                                <Icon :name="label.icon" :size="16" />
                            </div>
                            <span>{{ role }}</span>
                            <span class="nav-count">{{ getCountByRole(role) }}</span>
                        </div>
                    </nav>
                </div>

                <div class="widget-premium cta-widget mobile-cta-widget">
                    <div class="premium-flare"></div>
                    <div class="cta-inner">
                        <h4>¿Quieres destacar?</h4>
                        <p>Únete a nuestra comunidad hoy.</p>
                        <router-link to="/register" class="btn-join" @click="closeMobileSidebar">
                            <span>Registrarme</span>
                            <Icon name="plus" :size="18" />
                        </router-link>
                    </div>
                </div>
            </div>
        </ModalForm>

        <FloatingAppearanceControls />
    </div>
</template>

<script setup>
import { onMounted, onBeforeUnmount, nextTick, ref, computed } from 'vue';
import { api } from '@/services/api';
import Icon from '@/components/Icon.vue';
import ModalForm from '@/views/private/admin/components/ModalForm.vue';
import LandingNav from './components/LandingNav.vue';
import FloatingAppearanceControls from './components/FloatingAppearanceControls.vue';

const portfolios = ref([]);
const isLoading = ref(true);
const searchQuery = ref('');
const layoutRoot = ref(null);
const isMobileSidebarOpen = ref(false);
const isMobileViewport = ref(window.innerWidth <= 1100);

const roleIconsMap = {
    'Full Stack': { icon: 'code' },
    'Frontend': { icon: 'image' },
    'Backend': { icon: 'settings' },
    'UI/UX Design': { icon: 'palette' },
    'Mobile Engineer': { icon: 'bot' },
    'Data Scientist': { icon: 'users' }
};

function getRoleIcon(role) {
    const r = role?.toLowerCase() || '';
    if (r.includes('full')) return 'code';
    if (r.includes('front')) return 'image';
    if (r.includes('back')) return 'settings';
    if (r.includes('ui') || r.includes('ux')) return 'palette';
    return 'user';
}

function getCountByRole(role) {
    return portfolios.value.filter(p => p.role.toLowerCase().includes(role.toLowerCase())).length;
}

function toggleCategory(role) {
    searchQuery.value = searchQuery.value.toLowerCase() === role.toLowerCase() ? '' : role;

    if (window.innerWidth <= 1100) {
        closeMobileSidebar();
    }
}

async function fetchPortfolios() {
    isLoading.value = true;
    try {
        const response = await api.portfolios.getPublicList();
        portfolios.value = response.data.data;
    } catch (error) {
        console.error('Error fetching portfolios:', error);
    } finally {
        isLoading.value = false;
    }
}

const filteredPortfolios = computed(() => {
    if (!searchQuery.value) return portfolios.value;
    const query = searchQuery.value.toLowerCase();
    return portfolios.value.filter(p =>
        p.owner_name.toLowerCase().includes(query) ||
        p.role.toLowerCase().includes(query) ||
        p.summary.toLowerCase().includes(query)
    );
});

function resetFilters() {
    searchQuery.value = '';
}

function syncLayoutFromNav() {
    const navEl = document.querySelector('.directory-nav');
    const measuredNavHeight = Math.round(navEl?.getBoundingClientRect().height || 64);

    if (layoutRoot.value) {
        layoutRoot.value.style.setProperty('--nav-height', `${measuredNavHeight}px`);
    }
}

function handleWindowResize() {
    isMobileViewport.value = window.innerWidth <= 1100;

    if (window.innerWidth > 1100 && isMobileSidebarOpen.value) {
        isMobileSidebarOpen.value = false;
    }

    syncLayoutFromNav();
    syncBodyScrollLock();
}

function handleKeydown(event) {
    if (event.key === 'Escape' && isMobileSidebarOpen.value) {
        closeMobileSidebar();
    }
}

function syncBodyScrollLock() {
    if (window.innerWidth <= 1100) {
        document.body.style.overflow = isMobileSidebarOpen.value ? 'hidden' : '';
        return;
    }

    document.body.style.overflow = '';
}

function toggleMobileSidebar() {
    if (!isMobileViewport.value) {
        return;
    }

    isMobileSidebarOpen.value = !isMobileSidebarOpen.value;
    syncBodyScrollLock();
}

function closeMobileSidebar() {
    if (!isMobileSidebarOpen.value) {
        return;
    }

    isMobileSidebarOpen.value = false;
    syncBodyScrollLock();
}

onMounted(async () => {
    await nextTick();
    syncLayoutFromNav();
    syncBodyScrollLock();
    window.addEventListener('resize', handleWindowResize);
    window.addEventListener('keydown', handleKeydown);
    fetchPortfolios();
});

onBeforeUnmount(() => {
    window.removeEventListener('resize', handleWindowResize);
    window.removeEventListener('keydown', handleKeydown);
    document.body.style.overflow = '';
});
</script>

<style scoped>
.directory-layout-container {
    --nav-height: 64px;
    --viewport-gap: 16px;
    --layout-top: calc(var(--nav-height) + var(--viewport-gap));
    --column-height: calc(100vh - var(--nav-height) - (var(--viewport-gap) * 2));
    min-height: 100vh;
    height: 100vh;
    display: flex;
    flex-direction: column;
    overflow: hidden;
}

.landing-container {
    flex: 1;
    min-height: 0;
}

.directory-nav {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    z-index: 100;
    background: var(--bg-primary);
}

.animate-in {
    animation: slideUpFade 0.8s cubic-bezier(0.16, 1, 0.3, 1) both;
}

@keyframes slideUpFade {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
}

/* Premium Background */
.premium-bg {
    position: fixed;
    inset: 0;
    z-index: -1;
    overflow: hidden;
}

.mesh-gradient {
    position: absolute;
    inset: 0;
    background: radial-gradient(circle at 70% 30%, var(--bg-tertiary) 0%, var(--bg-primary) 100%);
}

.glow-orb {
    position: absolute;
    border-radius: 50%;
    filter: blur(140px);
}

.orb-1 { width: 500px; height: 500px; top: -100px; right: -100px; background: color-mix(in srgb, var(--primary), transparent 80%); }
.orb-2 { width: 400px; height: 400px; bottom: -100px; left: -100px; background: color-mix(in srgb, var(--primary), transparent 90%); }

/* Main Wrapper with spacing for stationary sidebar */
.directory-wrapper {
    display: flex;
    align-items: flex-start;
    gap: 40px;
    padding: var(--layout-top) 20px var(--viewport-gap);
    box-sizing: border-box;
    max-width: 1400px;
    margin: 0 auto;
    height: 100%;
}

/* MAIN CONTENT */
.directory-main {
    flex: 1;
    min-width: 0;
    height: var(--column-height);
    overflow-y: auto;
    padding-right: 8px;
}

.directory-main::-webkit-scrollbar { width: 6px; }
.directory-main::-webkit-scrollbar-thumb { background: var(--border-color); border-radius: 10px; }

.main-header h1 {
    font-size: 3rem;
    font-weight: 900;
    margin-bottom: 20px;
    letter-spacing: -0.05em;
}

.header-pretitle {
    display: flex;
    align-items: center;
    gap: 8px;
    font-weight: 800;
    text-transform: uppercase;
    color: var(--primary);
    letter-spacing: 0.1em;
    font-size: 0.75rem;
    margin-bottom: 12px;
}

.star-icon {
    width: 24px;
    height: 24px;
    background: color-mix(in srgb, var(--primary), transparent 90%);
    border-radius: 6px;
    display: flex;
    align-items: center;
    justify-content: center;
}

.stats-pills {
    display: flex;
    gap: 12px;
    margin-bottom: 40px;
}

.stat-pill {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 8px 16px;
    background: var(--bg-secondary);
    border: 1px solid var(--border-color);
    border-radius: 12px;
    font-size: 0.9rem;
    font-weight: 700;
}

.stat-pill.active {
    background: var(--primary);
    color: white;
    border-color: var(--primary);
}

/* Portfolio Grid */
.portfolio-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
    gap: 24px;
}

.pro-card {
    position: relative;
    background: var(--bg-secondary);
    border: 1px solid var(--border-color);
    border-radius: 28px;
    overflow: hidden;
    transition: all 0.4s ease;
}

.pro-card:hover {
    transform: translateY(-8px);
    border-color: var(--primary);
    box-shadow: 0 20px 40px rgba(0,0,0,0.2);
}

.pro-card-glow {
    position: absolute;
    inset: 0;
    background: radial-gradient(circle at 50% 0%, color-mix(in srgb, var(--primary), transparent 94%), transparent 70%);
    opacity: 0;
    transition: opacity 0.4s;
}

.pro-card:hover .pro-card-glow { opacity: 1; }

.pro-card-content {
    padding: 28px;
    position: relative;
    z-index: 2;
}

.pro-header {
    display: flex;
    gap: 16px;
    align-items: center;
    margin-bottom: 20px;
}

.pro-avatar-box {
    position: relative;
    flex-shrink: 0;
}

.pro-avatar-box img, .avatar-placeholder {
    width: 64px;
    height: 64px;
    border-radius: 16px;
    object-fit: cover;
    background: var(--bg-tertiary);
}

.avatar-placeholder {
    display: flex;
    align-items: center;
    justify-content: center;
    background: var(--primary);
    color: white;
    font-size: 1.8rem;
    font-weight: 900;
}

.online-indicator {
    position: absolute;
    bottom: -4px;
    right: -4px;
    width: 16px;
    height: 16px;
    background: #10b981;
    border: 3px solid var(--bg-secondary);
    border-radius: 50%;
}

.pro-tag {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    font-size: 0.65rem;
    font-weight: 800;
    color: var(--primary);
    background: color-mix(in srgb, var(--primary), transparent 94%);
    padding: 3px 8px;
    border-radius: 6px;
    text-transform: uppercase;
    margin-bottom: 4px;
}

.pro-info h3 { font-size: 1.4rem; font-weight: 850; margin: 0; color: var(--text-primary); }

.pro-bio {
    margin-bottom: 20px;
    color: var(--text-secondary);
    font-size: 0.95rem;
    line-height: 1.6;
    display: -webkit-box;
    line-clamp: 2;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
}

.pro-tags-row {
    display: flex;
    gap: 8px;
    margin-bottom: 30px;
}

.mini-tag {
    font-size: 0.75rem;
    font-weight: 700;
    color: var(--text-tertiary);
    background: var(--bg-tertiary);
    padding: 4px 10px;
    border-radius: 8px;
}

.pro-footer-action {
    padding-top: 20px;
    border-top: 1px solid var(--border-color);
}

.pro-link {
    display: flex;
    align-items: center;
    gap: 12px;
    text-decoration: none;
    color: var(--text-primary);
    font-weight: 800;
    transition: color 0.3s;
}

.pro-link:hover { color: var(--primary); }
.pro-link .arrow { margin-left: auto; transition: transform 0.3s; }
.pro-link:hover .arrow { transform: translateX(5px); }

/* SIDEBAR (STATIONARY) */
.directory-sidebar {
    width: 360px;
    flex-shrink: 0;
    height: var(--column-height);
    position: sticky;
    top: var(--layout-top);
}

.sidebar-fixed-content {
    position: relative;
    width: 360px;
    height: 100%;
    display: flex;
    flex-direction: column;
    gap: 16px;
    overflow-y: auto;
    padding-right: 5px;
    padding-bottom: var(--viewport-gap);
    box-sizing: border-box;
}

/* Scrollbar Sidebar */
.sidebar-fixed-content::-webkit-scrollbar { width: 4px; }
.sidebar-fixed-content::-webkit-scrollbar-thumb { background: var(--border-color); border-radius: 10px; }

.widget-glass {
    background: var(--bg-secondary);
    border: 1px solid var(--border-color);
    border-radius: 20px;
    padding: 20px;
    backdrop-filter: blur(10px);
}

.widget-title {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 15px;
}

.widget-title h3 {
    font-size: 0.85rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    font-weight: 800;
    color: var(--text-primary);
}

.input-sidebar {
    width: 100%;
    background: var(--bg-tertiary);
    border: 1px solid var(--border-color);
    border-radius: 12px;
    padding: 12px;
    color: var(--text-primary);
    font-size: 0.9rem;
    outline: none;
}

.input-sidebar:focus { border-color: var(--primary); }

.categories-nav { display: flex; flex-direction: column; gap: 6px; }

.nav-item {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 10px;
    border-radius: 10px;
    cursor: pointer;
    transition: all 0.2s;
    color: var(--text-secondary);
}

.nav-icon {
    width: 32px;
    height: 32px;
    background: var(--bg-tertiary);
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
}

.nav-item span { font-weight: 700; font-size: 0.9rem; flex: 1; }
.nav-count { font-size: 0.7rem; opacity: 0.5; }

.nav-item:hover, .nav-item.active {
    background: color-mix(in srgb, var(--primary), transparent 92%);
    color: var(--primary);
}

.nav-item.active .nav-icon { background: var(--primary); color: white; }

.widget-premium {
    background: var(--bg-tertiary);
    border-radius: 20px;
    padding: 30px;
    position: relative;
    overflow: hidden;
    color: white;
}

.cta-widget {
    position: sticky;
    bottom: 0;
    margin-top: 4px;
    flex-shrink: 0;
}

.mobile-sidebar-content {
    display: flex;
    flex-direction: column;
    gap: 16px;
}

.mobile-cta-widget {
    margin-top: 0;
    position: relative;
}

.sidebar-fab {
    display: none;
}

.premium-flare {
    position: absolute;
    inset: 0;
    background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
    opacity: 0.95;
}

.cta-inner { position: relative; z-index: 2; text-align: center; }
.cta-inner h4 { font-size: 1.2rem; font-weight: 900; margin-bottom: 8px; }
.cta-inner p { font-size: 0.85rem; opacity: 0.8; margin-bottom: 20px; }

.btn-join {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: white;
    color: var(--primary);
    padding: 10px 20px;
    border-radius: 10px;
    font-weight: 800;
    text-decoration: none;
    transition: transform 0.3s;
}

.btn-join:hover { transform: scale(1.05); }

/* States */
.glass-panel { background: var(--bg-secondary); border: 1px solid var(--border-color); padding: 60px; border-radius: 30px; text-align: center; }

.not-found-view h2 {
    margin: 10px 0 12px;
    font-size: 2rem;
    font-weight: 900;
    letter-spacing: -0.02em;
}

.not-found-view p {
    margin: 0 0 22px;
    color: var(--text-secondary);
    font-size: 1.05rem;
    line-height: 1.6;
}

.btn-refresh-glow {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    border: 1px solid color-mix(in srgb, var(--primary), transparent 65%);
    background: color-mix(in srgb, var(--bg-tertiary), var(--primary) 12%);
    color: var(--text-primary);
    padding: 11px 16px;
    border-radius: 12px;
    font-size: 0.95rem;
    font-weight: 800;
    line-height: 1;
    cursor: pointer;
    box-shadow: 0 8px 18px rgba(0, 0, 0, 0.2);
    transition: transform 0.18s ease, border-color 0.18s ease, background 0.18s ease, box-shadow 0.18s ease;
}

.btn-refresh-glow:hover {
    transform: translateY(-1px);
    border-color: color-mix(in srgb, var(--primary), transparent 40%);
    background: color-mix(in srgb, var(--bg-tertiary), var(--primary) 20%);
    box-shadow: 0 12px 24px rgba(0, 0, 0, 0.28);
}

.btn-refresh-glow:active {
    transform: translateY(0);
}

.btn-refresh-glow:focus-visible {
    outline: 2px solid color-mix(in srgb, var(--primary), white 25%);
    outline-offset: 2px;
}

/* Responsive */
@media (max-width: 1100px) {
    .directory-layout-container {
        height: auto;
        overflow: visible;
    }

    .landing-container {
        min-height: auto;
    }

    .directory-wrapper {
        flex-direction: column;
        padding-top: 100px;
        height: auto;
        position: relative;
    }

    .directory-main {
        height: auto;
        overflow: visible;
        padding-right: 0;
    }

    .sidebar-fab {
        display: inline-flex;
        position: fixed;
        top: calc(var(--nav-height) + 18px);
        right: 14px;
        width: 52px;
        height: 52px;
        border: 1px solid color-mix(in srgb, var(--primary), transparent 65%);
        border-radius: 50%;
        background: color-mix(in srgb, var(--bg-secondary), var(--primary) 16%);
        color: var(--text-primary);
        box-shadow: 0 10px 28px rgba(0, 0, 0, 0.32);
        align-items: center;
        justify-content: center;
        z-index: 281;
        transition: transform 0.2s ease, background 0.2s ease, border-color 0.2s ease;
    }

    :deep(.modal-overlay) {
        z-index: 270;
        padding: calc(var(--nav-height) + 18px) 12px 12px;
        align-items: flex-start;
        justify-content: center;
    }

    :deep(.modal-container.modal-md) {
        width: min(430px, calc(100vw - 24px));
        max-width: min(430px, calc(100vw - 24px));
        max-height: calc(100vh - var(--nav-height) - 30px);
        border-radius: 1.5rem;
    }

    :deep(.modal-header) {
        padding: 0.95rem 1.1rem;
    }

    :deep(.modal-header .modal-title) {
        font-size: 1rem;
    }

    :deep(.modal-body) {
        padding: 1rem;
        max-height: calc(100vh - var(--nav-height) - 106px);
    }

    .sidebar-fab:hover {
        border-color: color-mix(in srgb, var(--primary), transparent 45%);
        background: color-mix(in srgb, var(--bg-secondary), var(--primary) 22%);
    }

    .sidebar-fab:active {
        transform: scale(0.96);
    }
}
</style>
