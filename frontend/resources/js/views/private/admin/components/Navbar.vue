<template>
    <header class="dashboard-header">
        <div class="header-left">
            <button class="toggle-sidebar-btn" @click="$emit('toggle-sidebar')">
                <Icon name="menu" :size="24" />
            </button>
            <h1 class="page-title">Dashboard</h1>
        </div>

        <!-- Center Search Bar -->
        <div class="header-center" :class="{ 'mobile-open': isMobileSearchOpen }">
            <div class="navbar-search-container" v-click-outside="closeSearch">
                <div class="navbar-search-wrapper" :class="{ 'focused': isSearchFocused }">
                    <button v-if="isMobileSearchOpen" @click.stop="closeMobileSearch" class="back-btn-mobile">
                        <Icon name="arrowLeft" :size="18" />
                    </button>
                    <Icon v-else name="search" :size="18" class="search-icon" />
                    <input ref="searchInput" type="text" v-model="searchQuery" placeholder="Buscar módulo..."
                        @focus="isSearchFocused = true" @keydown.down.prevent="navigateResults(1)"
                        @keydown.up.prevent="navigateResults(-1)" @keydown.enter="selectResult"
                        @keydown.esc="closeSearch" />
                    <button v-if="searchQuery" @click="clearSearch" class="clear-btn">
                        <Icon name="x" :size="14" />
                    </button>
                </div>

                <!-- Search Results Dropdown -->
                <Transition name="fade-slide">
                    <div v-if="showResults" class="search-results-dropdown">
                        <div v-if="filteredModules.length === 0" class="no-results">
                            <span>No se encontraron módulos</span>
                        </div>
                        <ul v-else>
                            <li v-for="(module, index) in filteredModules" :key="index"
                                :class="{ 'selected': index === selectedIndex }" @click="handleNavigate(module)"
                                @mouseover="selectedIndex = index">
                                <div class="result-icon">
                                    <DynamicIcon :name="module.icon || 'grid'" :databaseData="module.dbIcon" :size="18" />
                                </div>
                                <div class="result-info">
                                    <span class="result-name">
                                        <template v-if="module.parentName">
                                            <small class="breadcrumb-parent">{{ module.parentName }}</small>
                                            <Icon name="chevronRight" :size="10" class="breadcrumb-sep" />
                                        </template>
                                        {{ module.name }}
                                    </span>
                                    <span class="result-path">{{ module.description }}</span>
                                </div>
                                <Icon name="chevronRight" :size="14" class="result-arrow" />
                            </li>
                        </ul>
                    </div>
                </Transition>
            </div>
        </div>

        <div class="header-right">
            <!-- Mobile Search Toggle -->
            <button class="mobile-search-toggle" @click.stop="openMobileSearch">
                <Icon name="search" :size="20" />
            </button>

            <!-- User Dropdown Trigger -->
            <div class="user-profile-header" @click="toggleUserMenu" :class="{ 'active': isUserMenuOpen }">
                <div class="user-info">
                    <span class="name">{{ user?.name || 'Usuario' }}</span>
                    <span class="role">{{ user?.role?.name || 'Huesped' }}</span>
                </div>
                <div class="avatar" :class="{ 'has-image': !!user?.avatar_url }">
                    <img
                        v-if="user?.avatar_url"
                        :src="user.avatar_url"
                        :alt="`Avatar de ${user?.name || 'usuario'}`"
                    />
                    <Icon v-else name="user" :size="20" />
                </div>
                <Icon name="chevronDown" :size="16" class="chevron" :class="{ 'rotate': isUserMenuOpen }" />
            </div>

            <!-- Dropdown Menu -->
            <Transition name="dropdown">
                <div v-if="isUserMenuOpen" class="user-dropdown-menu">
                    <div class="menu-header">
                        <span class="label">Cuenta</span>
                    </div>

                    <button class="menu-item" @click="handleNavigate({ path: '/dashboard/perfil' })">
                        <Icon name="user" :size="18" />
                        <span>Mi Perfil</span>
                    </button>

                    <button class="menu-item" @click="toggleTheme">
                        <Icon :name="theme === 'dark' ? 'sun' : 'moon'" :size="18" />
                        <span>{{ theme === 'dark' ? 'Modo Claro' : 'Modo Oscuro' }}</span>
                    </button>

                    <div class="menu-divider"></div>

                    <!-- Scale Selector Group (Relative for flyout) -->
                    <div class="menu-item-wrapper">
                        <button class="menu-item" @click.stop="toggleScaleMenu" :class="{ 'active': isScaleMenuOpen }">
                            <Icon name="settings" :size="18" />
                            <span style="flex: 1">Escala: {{ scale }}%</span>
                            <Icon name="chevronDown" :size="16" class="chevron"
                                :class="{ 'rotate-minus-90': isScaleMenuOpen }" />
                        </button>

                        <Transition name="fade">
                            <div v-if="isScaleMenuOpen" class="submenu-options floating-menu">
                                <button v-for="option in ['60', '70', '80', '90', '100', '110', '120']" :key="option"
                                    class="submenu-item" :class="{ 'active': scale === option }"
                                    @click.stop="handleScaleChange(option)">
                                    <span>{{ option }}%</span>
                                    <Icon v-if="scale === option" name="check" :size="16" class="check-icon" />
                                </button>
                            </div>
                        </Transition>
                    </div>

                    <!-- Color Palette Selector Group -->
                    <div class="menu-item-wrapper">
                        <button class="menu-item" @click.stop="togglePaletteMenu"
                            :class="{ 'active': isPaletteMenuOpen }">
                            <Icon name="palette" :size="18" />
                            <span style="flex: 1">Color: {{ getPaletteLabel(palette) }}</span>
                            <Icon name="chevronDown" :size="16" class="chevron"
                                :class="{ 'rotate-minus-90': isPaletteMenuOpen }" />
                        </button>

                        <Transition name="fade">
                            <div v-if="isPaletteMenuOpen" class="submenu-options floating-menu">
                                <button v-for="p in allPalettes" :key="p.id" class="submenu-item"
                                    :class="{ 'active': palette === p.id }" @click.stop="handlePaletteChange(p.id)">
                                    <div style="display: flex; align-items: center; gap: 8px;">
                                        <div class="color-dot" :style="{ background: p.color }"></div>
                                        <span>{{ p.name }}</span>
                                    </div>
                                    <Icon v-if="palette === p.id" name="check" :size="16" class="check-icon" />
                                </button>
                            </div>
                        </Transition>
                    </div>

                    <div class="menu-divider"></div>

                    <button class="menu-item danger" @click="handleLogout">
                        <Icon name="logout" :size="18" />
                        <span>Cerrar Sesión</span>
                    </button>
                </div>
            </Transition>

            <!-- Backdrop to close menu -->
            <div v-if="isUserMenuOpen" class="menu-backdrop" @click="isUserMenuOpen = false"></div>
        </div>
    </header>
</template>

<script setup>
import { ref, watch, computed } from 'vue';
import { useRouter } from 'vue-router';
import { useTheme } from '@/composables/useTheme';
import { useScale } from '@/composables/useScale';
import { useColorPalette } from '@/composables/useColorPalette';
import { useAlert } from '@/composables/useAlert';
import { useAuth } from '@/composables/useAuth';
import Icon from '@/components/Icon.vue';
import DynamicIcon from '@/components/DynamicIcon.vue';
import { generateNavigation, flattenNavigation } from '@/utils/navigation-generator';
import adminDashboardRoutes from '@/routes/admin-dashboard';

import { useDynamicRoutes } from '@/composables/useDynamicRoutes';

const router = useRouter();
const { user, logout } = useAuth();
const { theme, toggleTheme } = useTheme();
const { scale, setScale } = useScale();
const { palette, setPalette, staticPalettes, dynamicPalettes } = useColorPalette();
const { mappedRoutes } = useDynamicRoutes();
const alert = useAlert();

const allPalettes = computed(() => {
    return [...Object.values(staticPalettes), ...dynamicPalettes.value];
});

const isUserMenuOpen = ref(false);
const isScaleMenuOpen = ref(false);
const isPaletteMenuOpen = ref(false);

// Search State
const isMobileSearchOpen = ref(false);
const searchQuery = ref('');
const isSearchFocused = ref(false);
const searchInput = ref(null); // Main search input ref
const selectedIndex = ref(0);

// Generate flat list of modules for search
const modules = computed(() => {
    const userHierarchy = user.value?.role?.hierarchy || 99;

    const layoutRoute = adminDashboardRoutes[0];
    if (!layoutRoute || !layoutRoute.children) return [];

    // Merge static and dynamic routes
    const allRoutes = [...layoutRoute.children, ...mappedRoutes.value];

    const tree = generateNavigation(allRoutes, userHierarchy, layoutRoute.path, {
        ignoreSidebarVisibility: true
    });
    // Filter out paths with parameters (e.g., :uuid) to avoid duplicated entries in search
    return flattenNavigation(tree).filter(m => !m.path.includes(':'));
});

const filteredModules = computed(() => {
    if (!searchQuery.value) return [];

    const query = searchQuery.value.toLowerCase();

    return modules.value.filter(module => {
        // Exclude parents that have children to favor leaf actions
        if (module.children && module.children.length > 0) return false;

        // Search by name, keywords or parent name
        const nameMatch = module.name.toLowerCase().includes(query);
        const keywordsMatch = module.keywords && module.keywords.includes(query);
        const descriptionMatch = module.description && module.description.toLowerCase().includes(query);
        const parentMatch = module.parentName && module.parentName.toLowerCase().includes(query);

        return nameMatch || keywordsMatch || descriptionMatch || parentMatch;
    });
});

const showResults = computed(() => {
    return searchQuery.value.length > 0 && isSearchFocused.value;
});

const closeSearch = () => {
    isSearchFocused.value = false;
    if (isMobileSearchOpen.value) {
        closeMobileSearch();
    }
};

const clearSearch = () => {
    searchQuery.value = '';
    selectedIndex.value = 0;
    searchInput.value?.focus();
};

const navigateResults = (direction) => {
    if (!filteredModules.value.length) return;

    const newIndex = selectedIndex.value + direction;
    if (newIndex >= 0 && newIndex < filteredModules.value.length) {
        selectedIndex.value = newIndex;
    }
};

const selectResult = () => {
    if (filteredModules.value.length > 0 && filteredModules.value[selectedIndex.value]) {
        handleNavigate(filteredModules.value[selectedIndex.value]);
    }
};

const handleNavigate = (module) => {
    closeMobileSearch();
    router.push(module.path); // Changed from module.route to module.path
};


const getPaletteLabel = (key) => {
    const p = allPalettes.value.find(x => x.id === key);
    return p ? p.name : 'Verde';
};

const getColorValue = (key) => {
    const p = allPalettes.value.find(x => x.id === key);
    return p ? p.color : '#42b983';
};

// Reset menus when user menu closes
watch(isUserMenuOpen, (isOpen) => {
    if (!isOpen) {
        setTimeout(() => {
            isScaleMenuOpen.value = false;
            isPaletteMenuOpen.value = false;
        }, 200);
    }
});

// Close one submenu when the other opens
watch(isScaleMenuOpen, (isOpen) => {
    if (isOpen) isPaletteMenuOpen.value = false;
});
watch(isPaletteMenuOpen, (isOpen) => {
    if (isOpen) isScaleMenuOpen.value = false;
});

const toggleUserMenu = () => {
    isUserMenuOpen.value = !isUserMenuOpen.value;
};

const toggleScaleMenu = () => {
    isScaleMenuOpen.value = !isScaleMenuOpen.value;
};

const togglePaletteMenu = () => {
    isPaletteMenuOpen.value = !isPaletteMenuOpen.value;
};

const openMobileSearch = () => {
    isMobileSearchOpen.value = true;
    setTimeout(() => {
        searchInput.value?.focus();
    }, 100);
};

const closeMobileSearch = () => {
    isMobileSearchOpen.value = false;
    searchQuery.value = ''; // Optional: clear search on close
    isSearchFocused.value = false;
};

const handleScaleChange = (newScale) => {
    setScale(newScale);
};

const handlePaletteChange = (newPalette) => {
    setPalette(newPalette);
};

const handleLogout = async () => {
    // Close menus first
    isUserMenuOpen.value = false;

    const confirmed = await alert.fire({
        title: '¿Cerrar sesión?',
        text: 'Tendrás que iniciar sesión nuevamente para acceder.',
        type: 'warning',
        showCancel: true,
        confirmText: 'Sí, salir',
        cancelText: 'Cancelar'
    });

    if (confirmed) {
        alert.toast.info('Cerrando sesión', 'Hasta pronto');
        await logout();
        router.push('/login');
    }
};
</script>
