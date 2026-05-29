<template>
    <div class="table-card">
        <!-- Header -->
        <div class="table-header">
            <h2 class="title">{{ title }}</h2>
            <div class="actions">
                <!-- Header Pagination (Visible only if fitToScreen is enabled) -->
                <div class="header-pagination" v-if="layoutConfig?.fitContentToScreen?.value && effectivePagination">
                    <div class="pagination-simple-controls">
                        <!-- Items Per Page (Compact) -->
                        <Pagination v-if="effectivePagination" :pagination="effectivePagination"
                            :itemsPerPage="localItemsPerPage" :itemsPerPageOptions="itemsPerPageOptions" compact
                            @page-change="changePage" @update:itemsPerPage="setItemsPerPage" />
                    </div>
                </div>

                <!-- Refresh Button -->
                <button v-if="showRefresh" class="toggle-btn refresh-btn" :class="{ spinning: loading }"
                    @click="triggerFetch" title="Recargar datos">
                    <Icon name="refresh" :size="18" />
                </button>

                <!-- Search Input -->
                <div class="search-input-wrapper">
                    <Icon name="search" :size="18" class="search-icon" />
                    <input type="text" :placeholder="searchPlaceholder" :value="searchQuery"
                        @input="$emit('update:searchQuery', $event.target.value)">
                </div>

                <!-- Sorting Controls -->
                <div class="sort-controls" v-if="sortOptions && sortOptions.length > 0">
                    <select :value="localSortBy" @change="handleSortByChange($event.target.value)" class="sort-select">
                        <option value="">Sin orden</option>
                        <option v-for="opt in sortOptions" :key="opt.key" :value="opt.key">
                            {{ opt.label }}
                        </option>
                    </select>

                    <button class="toggle-btn" @click="toggleSortOrder" :title="localSortOrder === 'asc' ? 'Ascendente' : 'Descendente'">
                        <Icon :name="localSortOrder === 'asc' ? 'arrowUp' : 'arrowDown'" :size="16" />
                    </button>
                </div>

                <!-- View Toggle (List/Grid) -->
                <div class="view-toggle">
                    <button class="toggle-btn" :class="{ active: localViewMode === 'list' }"
                        @click="setViewMode('list')" title="Vista de Lista">
                        <Icon name="list" :size="18" />
                    </button>
                    <button class="toggle-btn" :class="{ active: localViewMode === 'grid' }"
                        @click="setViewMode('grid')" title="Vista de Tarjetas">
                        <Icon name="grid" :size="18" />
                    </button>
                </div>

                <!-- Action Slots (e.g., New Button) -->
                <div v-if="showHeaderActions">
                    <slot name="header-actions"></slot>
                </div>
            </div>
        </div>

        <!-- Table View -->
        <div class="table-wrapper" v-if="localViewMode === 'list'">
            <!-- Loading Overlay -->
            <div class="loading-overlay" v-if="loading">
                <div class="spinner"></div>
                <span class="loading-text">Cargando registros...</span>
            </div>

            <table>
                <thead>
                    <tr>
                        <th v-for="col in displayedColumns" :key="col.key"
                            :class="col.headerClass" :style="{ width: col.width }">
                            {{ col.label }}
                        </th>
                    </tr>
                </thead>
                <tbody>
                    <tr v-for="(row, index) in processedRows" :key="row.uuid ?? row.id ?? index" @click="$emit('row-click', row)"
                        class="cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors">
                        <td v-for="col in displayedColumns" :key="col.key" :class="col.cellClass">
                            <template v-if="col.key === 'actions'">
                                <div class="actions-wrapper">
                                    <button v-if="!row.hideActions" class="action-btn dots"
                                        @click.stop="toggleDropdown(row.uuid ?? row.id ?? index, $event)">
                                        <Icon name="moreVertical" :size="20" />
                                    </button>
 
                                    <!-- Dropdown Menu (teleported to body to escape overflow clipping) -->
                                    <Teleport to="body">
                                        <div v-if="activeDropdownRow === (row.uuid ?? row.id ?? index)"
                                            class="actions-dropdown-menu teleported"
                                            :style="dropdownStyle"
                                            v-click-outside="closeDropdown"
                                            @click="closeDropdown">
                                            <slot :name="`cell-${col.key}`" :row="row" :value="row[col.key]" :index="index">
                                            </slot>
                                        </div>
                                    </Teleport>
                                </div>
                            </template>

                            <template v-else>
                                <!-- Dynamic Component Support -->
                                <component v-if="col.component" :is="resolveComponent(col.component)"
                                    v-bind="col.props ? col.props(row) : {}">
                                    {{ row[col.key] }}
                                </component>
                                <template v-else-if="col.type === 'switch'">
                                    <div class="status-toggle-container" @click.stop>
                                        <label class="switch-premium">
                                            <input 
                                                type="checkbox" 
                                                :checked="isStatusActive(row[col.key])" 
                                                @change="$emit('toggle-status', { row, column: col })"
                                            >
                                            <span class="slider-premium round">
                                                <span class="knob">
                                                    <Icon v-if="isStatusActive(row[col.key])" name="check" :size="10" />
                                                    <Icon v-else name="x" :size="10" />
                                                </span>
                                            </span>
                                        </label>
                                        <span :class="['status-text', isStatusActive(row[col.key]) ? 'active' : 'inactive']">
                                            {{ isStatusActive(row[col.key]) ? (col.activeLabel || 'Activa') : (col.inactiveLabel || 'Inactiva') }}
                                        </span>
                                    </div>
                                </template>

                                <!-- Default Slot / Text -->
                                <slot v-else :name="`cell-${col.key}`" :row="row" :value="row[col.key]" :index="index">
                                    {{ row[col.key] }}
                                </slot>
                            </template>
                        </td>
                    </tr>

                    <!-- Empty State -->
                    <tr v-if="processedRows.length === 0">
                        <td :colspan="columns.length" class="text-center py-6">
                            No hay registros para mostrar.
                        </td>
                    </tr>
                </tbody>
            </table>
        </div>

        <!-- Grid/Card View -->
        <div class="grid-view-wrapper" v-else>
            <!-- Loading Overlay -->
            <div class="loading-overlay" v-if="loading">
                <div class="spinner"></div>
                <span class="loading-text">Cargando registros...</span>
            </div>

            <div class="cards-grid" v-if="processedRows.length > 0">
                <div v-for="(row, index) in processedRows" :key="row.uuid ?? row.id ?? index" class="data-card"
                    @click="$emit('row-click', row)">
                    <!-- Card Header -->
                    <div class="card-header">
                        <!-- Identify Title Column (First non-action) OR Custom Template -->
                        <div class="card-title">
                            <template v-if="cardTitleTemplate">
                                {{ getCardTitle(row) }}
                            </template>
                            <template v-else>
                                <slot :name="`cell-${titleColumn.key}`" :row="row" :value="row[titleColumn.key]"
                                    :index="index">
                                    {{ row[titleColumn.key] }}
                                </slot>
                            </template>
                        </div>

                        <!-- Actions in Card (Dropdown only) -->
                        <div class="card-actions" v-if="hasActionsColumn">
                            <button class="action-btn dots" @click.stop="toggleDropdown(row.uuid ?? row.id ?? index, $event)">
                                <Icon name="moreVertical" :size="20" />
                            </button>

                            <!-- Dropdown Menu (teleported to body) -->
                            <Teleport to="body">
                                <div v-if="activeDropdownRow === (row.uuid ?? row.id ?? index)"
                                    class="actions-dropdown-menu teleported"
                                    :style="dropdownStyle"
                                    v-click-outside="closeDropdown"
                                    @click="closeDropdown">
                                    <slot name="cell-actions" :row="row" :value="row['actions']" :index="index"></slot>
                                </div>
                            </Teleport>
                        </div>
                    </div>

                    <!-- Card Body: Other Columns -->
                    <div class="card-body">
                        <div v-for="col in visibleCardColumns" :key="col.key" class="card-row">
                            <span class="card-label">{{ col.label }}:</span>
                            <span class="card-value">
                                <!-- Dynamic Component Support -->
                                <component v-if="col.component" :is="resolveComponent(col.component)"
                                    v-bind="col.props ? col.props(row) : {}">
                                    {{ row[col.key] }}
                                </component>

                                <template v-else-if="col.type === 'switch'">
                                    <div class="status-toggle-container compact" @click.stop>
                                        <label class="switch-premium">
                                            <input 
                                                type="checkbox" 
                                                :checked="isStatusActive(row[col.key])" 
                                                @change="$emit('toggle-status', { row, column: col })"
                                            >
                                            <span class="slider-premium round">
                                                <span class="knob">
                                                    <Icon v-if="isStatusActive(row[col.key])" name="check" :size="10" />
                                                    <Icon v-else name="x" :size="10" />
                                                </span>
                                            </span>
                                        </label>
                                        <span :class="['status-text', isStatusActive(row[col.key]) ? 'active' : 'inactive']">
                                            {{ isStatusActive(row[col.key]) ? (col.activeLabel || 'Activa') : (col.inactiveLabel || 'Inactiva') }}
                                        </span>
                                    </div>
                                </template>

                                <!-- Default Slot / Text -->
                                <slot v-else :name="`cell-${col.key}`" :row="row" :value="row[col.key]" :index="index">
                                    {{ row[col.key] }}
                                </slot>
                            </span>
                        </div>
                    </div>
                </div>
            </div>
            <!-- Empty State Grid -->
            <div v-if="processedRows.length === 0" class="empty-state-grid">
                No hay registros para mostrar.
            </div>
        </div>

        <!-- Footer / Pagination (Hidden if fitToScreen is enabled) -->
        <Pagination v-if="effectivePagination && !layoutConfig?.fitContentToScreen?.value"
            :pagination="effectivePagination" :itemsPerPage="localItemsPerPage"
            :itemsPerPageOptions="itemsPerPageOptions" @page-change="changePage"
            @update:itemsPerPage="setItemsPerPage" />
    </div>
</template>

<script setup>
import { inject, ref, computed, watch, onMounted, onUnmounted, markRaw } from 'vue';
import Icon from '@/components/Icon.vue';
import Pagination from '@/components/Pagination.vue';
import SessionTimer from '@/views/private/admin/components/SessionTimer.vue';
import { useTableConfig } from '@/composables/useTableConfig';
const { 
    itemsPerPage: globalItemsPerPage, 
    viewMode: globalViewMode, 
    getModuleConfig,
    updateModuleConfig,
    setItemsPerPage: setGlobalItemsPerPage, 
    setViewMode: setGlobalViewMode,
} = useTableConfig();

// Map of available dynamic components
const componentMap = {
    'SessionTimer': markRaw(SessionTimer)
};

const isStatusActive = (val) => {
    return val === true || val === 'activa' || val === 'published' || val === 1 || val === 'active';
};

const resolveComponent = (comp) => {
    if (typeof comp === 'string') {
        return componentMap[comp] || comp;
    }
    return comp;
};

// Inject layout config (optional, default to null)
const layoutConfig = inject('layoutConfig', null);

// View Mode Logic removed: handled by useTableConfig

const props = defineProps({
    title: {
        type: String,
        default: 'Listado'
    },
    moduleId: {
        type: String,
        default: '' // If empty, uses global defaults
    },
    columns: {
        type: Array,
        required: true,
        // Expected format: { key: 'name', label: 'Nombre', headerClass?: '', cellClass?: '' }
    },
    rows: {
        type: Array,
        required: true
    },
    loading: {
        type: Boolean,
        default: false
    },
    pagination: {
        type: Object,
        default: null
        // Expected structure: { current_page, last_page, from, to, total }
    },
    sortOptions: {
        type: Array,
        default: () => []
        // Expected: { key: 'created_at', label: 'Fecha' }
    },
    searchQuery: {
        type: String,
        default: ''
    },
    searchPlaceholder: {
        type: String,
        default: 'Buscar...'
    },
    itemsPerPage: {
        type: Number,
        default: 10
    },
    itemsPerPageOptions: {
        type: Array,
        default: () => [2, 4, 5, 10, 20, 50, 100]
    },
    paginationMode: {
        type: String, // 'server' | 'client'
        default: 'server'
    },
    cardTitleTemplate: {
        type: String,
        default: ''
    },
    showHeaderActions: {
        type: Boolean,
        default: true
    },
    showRefresh: {
        type: Boolean,
        default: true
    },
    dropdownZIndex: {
        type: Number,
        default: 1000
    }
});

const emit = defineEmits(['update:searchQuery', 'page-change', 'update:itemsPerPage', 'request-data', 'row-click', 'toggle-status']);

// --- SCOPED CONFIGURATION LOGIC ---
const moduleConfig = computed(() => getModuleConfig(props.moduleId));

// Internal states synchronized with either scoped or global config
const localSortBy = ref(moduleConfig.value.sortBy);
const localSortOrder = ref(moduleConfig.value.sortOrder);
const localItemsPerPage = ref(moduleConfig.value.itemsPerPage);
const localViewMode = ref(moduleConfig.value.viewMode);

// Sync local states if moduleConfig changes (e.g. initial load)
watch(moduleConfig, (newConf) => {
    localSortBy.value = newConf.sortBy;
    localSortOrder.value = newConf.sortOrder;
    localItemsPerPage.value = newConf.itemsPerPage;
    localViewMode.value = newConf.viewMode;
}, { deep: true });

const handleSortByChange = (val) => {
    localSortBy.value = val;
    if (props.moduleId) {
        updateModuleConfig(props.moduleId, { sortBy: val });
    }
};

const toggleSortOrder = () => {
    const nextOrder = localSortOrder.value === 'asc' ? 'desc' : 'asc';
    localSortOrder.value = nextOrder;
    if (props.moduleId) {
        updateModuleConfig(props.moduleId, { sortOrder: nextOrder });
    }
};

const setItemsPerPage = (val) => {
    localItemsPerPage.value = parseInt(val);
    if (props.moduleId) {
        updateModuleConfig(props.moduleId, { itemsPerPage: parseInt(val) });
    } else {
        setGlobalItemsPerPage(val);
    }
};

const setViewMode = (mode) => {
    localViewMode.value = mode;
    if (props.moduleId) {
        updateModuleConfig(props.moduleId, { viewMode: mode });
    } else {
        setGlobalViewMode(mode);
    }
};

// Card View Computeds
const titleColumn = computed(() => {
    // Find first column identifying that is NOT actions
    return props.columns.find(c => c.key !== 'actions') || props.columns[0];
});

const displayedColumns = computed(() => {
    if (!props.showHeaderActions) {
        return props.columns.filter(c => c.key !== 'actions');
    }
    return props.columns;
});

const hasActionsColumn = computed(() => {
    return props.showHeaderActions && props.columns.some(col => col.key === 'actions');
});

const getCardTitle = (row) => {
    if (props.cardTitleTemplate) {
        // Interpolate {key} with row[key]
        return props.cardTitleTemplate.replace(/{(\w+)}/g, (_, key) => {
            return row[key] !== undefined ? row[key] : '';
        });
    }
    return '';
};

const visibleCardColumns = computed(() => {
    const cols = props.columns.filter(c => c.key !== 'actions');

    // If using custom template, show ALL columns (don't hide title column)
    if (props.cardTitleTemplate) {
        return cols;
    }

    // Default: Hide the column used as title
    return cols.filter(c => c.key !== titleColumn.value.key);
});


// Dropdown Logic
const activeDropdownRow = ref(null);
const dropdownStyle = ref({});

const DROPDOWN_WIDTH = 190; // px — must match CSS min-width

const toggleDropdown = (rowId, event) => {
    if (activeDropdownRow.value === rowId) {
        activeDropdownRow.value = null;
        return;
    }
    // Calculate position from the trigger button
    const btn = event?.currentTarget ?? event?.target;
    if (btn) {
        const rect = btn.getBoundingClientRect();
        const spaceBelow = window.innerHeight - rect.bottom;
        const spaceRight = window.innerWidth - rect.left;

        // Prefer opening below; flip up if not enough space
        const top = spaceBelow >= 160
            ? rect.bottom + 6
            : rect.top - 6; // will use transform to anchor bottom

        // Prefer opening to the right of button; flip left if near edge
        const left = spaceRight >= DROPDOWN_WIDTH
            ? rect.left
            : rect.right - DROPDOWN_WIDTH;

        dropdownStyle.value = {
            position: 'fixed',
            top: `${top}px`,
            left: `${Math.max(8, left)}px`,
            zIndex: props.dropdownZIndex,
            minWidth: `${DROPDOWN_WIDTH}px`,
            // Flip anchor when opening upward
            ...(spaceBelow < 160 ? { transform: 'translateY(-100%)' } : {}),
        };
    }
    activeDropdownRow.value = rowId;
};

const closeDropdown = () => {
    activeDropdownRow.value = null;
};

// Close dropdown if user scrolls (prevents it from drifting away from trigger)
const handleScroll = () => { if (activeDropdownRow.value !== null) closeDropdown(); };
onMounted(() => window.addEventListener('scroll', handleScroll, true));
onUnmounted(() => window.removeEventListener('scroll', handleScroll, true));

// Client-Side Pagination Logic
const clientCurrentPage = ref(1);

// Computed: Filtered & Paginated Rows
const processedRows = computed(() => {
    if (props.paginationMode === 'server') {
        return props.rows;
    }

    // CLIENT MODE
    let filtered = props.rows;

    // 1. Filter by Search Query
    if (props.searchQuery) {
        const query = props.searchQuery.toLowerCase();
        filtered = filtered.filter(row => {
            // Simple check: does any column value contain the query?
            return Object.values(row).some(val =>
                String(val).toLowerCase().includes(query)
            );
        });
    }

    // 2. Paginate
    const start = (clientCurrentPage.value - 1) * localItemsPerPage.value;
    const end = start + localItemsPerPage.value;

    return filtered.slice(start, end);
});

// Computed: Effective Pagination Metadata
const effectivePagination = computed(() => {
    if (props.paginationMode === 'server') {
        return props.pagination;
    }

    // CLIENT MODE
    let total = props.rows.length;

    // Recalculate total based on filter to be accurate
    if (props.searchQuery) {
        const query = props.searchQuery.toLowerCase();
        total = props.rows.filter(row =>
            Object.values(row).some(val => String(val).toLowerCase().includes(query))
        ).length;
    }

    const lastPage = Math.ceil(total / localItemsPerPage.value) || 1;
    const currentPage = clientCurrentPage.value;
    const from = total === 0 ? 0 : ((currentPage - 1) * localItemsPerPage.value) + 1;
    const to = Math.min(from + localItemsPerPage.value - 1, total);

    return {
        current_page: currentPage,
        last_page: lastPage,
        from: from,
        to: to,
        total: total
    };
});

// Computed: Pages to display (e.g. 1 ... 4 5 6 ... 10)
// Computed: Pages to display (e.g. 1 ... 4 5 6 ... 10)
// Computed: Pages to display (e.g. 1 ... 4 5 6 ... 10)
// Computed: Pages to display (e.g. 1 ... 4 5 6 ... 10)
const visiblePages = computed(() => {
    const { current_page, last_page } = effectivePagination.value;

    // Standard Compact Logic (Max 7 items)
    // 1. Less than 8 pages -> Show all
    if (last_page < 8) {
        return Array.from({ length: last_page }, (_, i) => i + 1);
    }

    // 2. Complex Logic with Ellipses
    // Always show First and Last
    // Show Current +/- 1 (Neighbors)
    // Use Ellipsis for gaps

    const pages = [];
    const windowSize = 1; // 1 neighbor on each side

    // Start Mode: If current is near start (<= 4)
    // Show 1, 2, 3, 4, 5, ..., Last
    if (current_page <= 4) {
        for (let i = 1; i <= 5; i++) {
            pages.push(i);
        }
        pages.push('...');
        pages.push(last_page);
    }
    // End Mode: If current is near end (>= Last - 3)
    // Show 1, ..., Last-4, Last-3, Last-2, Last-1, Last
    else if (current_page >= last_page - 3) {
        pages.push(1);
        pages.push('...');
        for (let i = last_page - 4; i <= last_page; i++) {
            pages.push(i);
        }
    }
    // Middle Mode: Double Ellipsis
    // Show 1, ..., Current-1, Current, Current+1, ..., Last
    else {
        pages.push(1);
        pages.push('...');

        for (let i = current_page - windowSize; i <= current_page + windowSize; i++) {
            pages.push(i);
        }

        pages.push('...');
        pages.push(last_page);
    }

    return pages;
});

// Watchers for Client Mode reset
watch(() => props.searchQuery, () => {
    if (props.paginationMode === 'client') {
        clientCurrentPage.value = 1;
    }
});

watch(() => props.itemsPerPage, () => {
    if (props.paginationMode === 'client') {
        clientCurrentPage.value = 1;
    }
});


// Helper for Page Change
const changePage = (newPage) => {
    if (props.paginationMode === 'server') {
        const params = {
            page: newPage,
            per_page: localItemsPerPage.value,
            search: props.searchQuery,
            sort_by: localSortBy.value,
            sort_order: localSortOrder.value
        };
        emit('request-data', params);
        emit('page-change', newPage);
    } else {
        clientCurrentPage.value = newPage;
    }
};

// --- DATA FETCHING ORCHESTRATION ---

// Trigger Fetch based on current state and mode
const triggerFetch = () => {
    let params = {};
    if (props.paginationMode === 'server') {
        params = {
            page: props.pagination?.current_page || 1,
            per_page: localItemsPerPage.value,
            search: props.searchQuery,
            sort_by: localSortBy.value,
            sort_order: localSortOrder.value
        };
    } else {
        // Client/All Mode
        params = { per_page: -1 };
    }
    emit('request-data', params);
};

// Watchers for Server Mode
watch(localItemsPerPage, () => {
    if (props.paginationMode === 'server') {
        const params = {
            page: 1,
            per_page: localItemsPerPage.value,
            search: props.searchQuery,
            sort_by: localSortBy.value,
            sort_order: localSortOrder.value
        };
        emit('request-data', params);
        emit('page-change', 1);
    }
});

// Sorting Watchers
watch([localSortBy, localSortOrder], () => {
    if (props.paginationMode === 'server') {
        const params = {
            page: 1, // Reset to page 1 on sort change
            per_page: localItemsPerPage.value,
            search: props.searchQuery,
            sort_by: localSortBy.value,
            sort_order: localSortOrder.value
        };
        emit('request-data', params);
        emit('page-change', 1);
    }
});

// Debounce helper
const debounce = (fn, delay) => {
    let timeoutId;
    return (...args) => {
        clearTimeout(timeoutId);
        timeoutId = setTimeout(() => fn(...args), delay);
    };
};

// Search Debounce for Server Mode
const debouncedFetch = debounce(() => {
    if (props.paginationMode === 'server') {
        const params = {
            page: 1, // Reset to page 1 on search
            per_page: localItemsPerPage.value,
            search: props.searchQuery,
            sort_by: localSortBy.value,
            sort_order: localSortOrder.value
        };
        emit('request-data', params);
        emit('page-change', 1);
    }
}, 300);

watch(() => props.searchQuery, () => {
    // Always update client page to 1
    if (props.paginationMode === 'client') {
        clientCurrentPage.value = 1;
    } else {
        // Server fetch
        debouncedFetch();
    }
});

// Initial Load
onMounted(() => {
    triggerFetch();
});

</script>
<style scoped>
.status-toggle-container { display: flex; flex-direction: column; align-items: center; gap: 4px; user-select: none; }
.status-toggle-container.compact { flex-direction: row; gap: 8px; }
.status-toggle-container .status-text { font-size: 10px; font-weight: 800; text-transform: uppercase; letter-spacing: 0.5px; }
.status-toggle-container .status-text.active { color: #10b981; }
.status-toggle-container .status-text.inactive { color: #ef4444; }
.switch-premium { position: relative; display: inline-block; width: 38px; height: 20px; }
.switch-premium input { opacity: 0; width: 0; height: 0; }
.switch-premium input:checked + .slider-premium { background-color: rgba(16, 185, 129, 0.2); border-color: rgba(16, 185, 129, 0.4); }
.switch-premium input:checked + .slider-premium .knob { transform: translateX(18px); background: #10b981; color: white; box-shadow: 0 2px 8px rgba(16, 185, 129, 0.4); }
.slider-premium { position: absolute; cursor: pointer; top: 0; left: 0; right: 0; bottom: 0; background-color: rgba(75, 85, 99, 0.2); border: 1px solid rgba(255, 255, 255, 0.1); transition: .3s; }
.slider-premium.round { border-radius: 20px; }
.slider-premium .knob { position: absolute; height: 16px; width: 16px; left: 1px; bottom: 1px; background-color: #4b5563; color: rgba(255, 255, 255, 0.5); transition: .3s cubic-bezier(0.4, 0, 0.2, 1); border-radius: 50%; display: flex; align-items: center; justify-content: center; box-shadow: 0 2px 4px rgba(0,0,0,0.2); }
</style>
