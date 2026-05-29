<template>
    <div class="table-header">
        <div class="header-content">
            <div class="breadcrumb-container">
                <button
                    class="breadcrumb-item home"
                    @click="$emit('go-root')"
                    :class="{ active: !currentFolderUuid }"
                >
                    <Icon name="folder-open" :size="18" />
                    <span>Raíz</span>
                </button>

                <template v-for="crumb in breadcrumbs" :key="crumb.uuid">
                    <span class="separator">/</span>
                    <button
                        class="breadcrumb-item"
                        @click="$emit('go-folder', crumb.uuid)"
                        :class="{ active: currentFolderUuid === crumb.uuid }"
                    >
                        {{ crumb.name }}
                    </button>
                </template>
            </div>
        </div>

        <div class="actions">
            <div class="header-pagination" v-if="layoutConfig?.fitContentToScreen?.value && pagination && foldersLength > 0">
                <Pagination
                    :pagination="pagination"
                    :itemsPerPage="itemsPerPage"
                    compact
                    @page-change="$emit('page-change', $event)"
                    @update:itemsPerPage="$emit('update:itemsPerPage', $event)"
                />
            </div>

            <div class="sort-controls" title="Ordenar elementos">
                <select
                    :value="sortField"
                    class="sort-select"
                    @change="$emit('update:sortField', $event.target.value)"
                >
                    <option value="created_at">Fecha de creación</option>
                    <option value="updated_at">Fecha de modificación</option>
                    <option value="name">Nombre</option>
                    <option value="type">Tipo (carpeta/archivo)</option>
                </select>

                <button
                    type="button"
                    class="sort-direction-btn"
                    @click="$emit('update:sortDirection', sortDirection === 'asc' ? 'desc' : 'asc')"
                    :title="sortDirection === 'asc' ? 'Orden ascendente' : 'Orden descendente'"
                >
                    {{ sortDirection === 'asc' ? '↑' : '↓' }}
                </button>
            </div>

            <div class="search-input-wrapper">
                <Icon name="search" :size="18" class="search-icon" />
                <input
                    :value="searchQuery"
                    @input="$emit('update:searchQuery', $event.target.value)"
                    type="text"
                    placeholder="Buscar carpeta o archivo..."
                >
            </div>

            <div class="view-toggle">
                <button
                    class="toggle-btn"
                    :class="{ active: viewMode === 'list' }"
                    @click="$emit('set-view-mode', 'list')"
                    title="Vista de Lista"
                >
                    <Icon name="list" :size="18" />
                </button>
                <button
                    class="toggle-btn"
                    :class="{ active: viewMode === 'grid' }"
                    @click="$emit('set-view-mode', 'grid')"
                    title="Vista de Tarjetas"
                >
                    <Icon name="grid" :size="18" />
                </button>
            </div>

            <div class="explorer-actions">
                <button class="upload-fab" @click="$emit('open-actions-modal')" title="Nueva carpeta / Subir archivo">
                    <Icon name="plus" :size="22" />
                </button>
            </div>
        </div>
    </div>
</template>

<script setup>
import Icon from '@/components/Icon.vue';
import Pagination from '@/components/Pagination.vue';

defineProps({
    breadcrumbs: {
        type: Array,
        default: () => [],
    },
    currentFolderUuid: {
        type: String,
        default: null,
    },
    layoutConfig: {
        type: Object,
        default: null,
    },
    pagination: {
        type: Object,
        default: null,
    },
    foldersLength: {
        type: Number,
        default: 0,
    },
    itemsPerPage: {
        type: Number,
        default: 10,
    },
    searchQuery: {
        type: String,
        default: '',
    },
    sortField: {
        type: String,
        default: 'created_at',
    },
    sortDirection: {
        type: String,
        default: 'desc',
    },
    viewMode: {
        type: String,
        default: 'grid',
    },
});

defineEmits([
    'go-root',
    'go-folder',
    'page-change',
    'update:itemsPerPage',
    'update:searchQuery',
    'update:sortField',
    'update:sortDirection',
    'set-view-mode',
    'open-actions-modal',
]);
</script>

<style scoped>
.sort-controls {
    display: inline-flex;
    align-items: center;
    gap: 0.45rem;
}

.sort-select {
    height: 36px;
    min-width: 170px;
    padding: 0 0.7rem;
    border-radius: 10px;
    border: 1px solid var(--border-color);
    background: var(--bg-tertiary);
    color: var(--text-primary);
    font-size: 0.9rem;
    outline: none;
    transition: border-color 0.2s ease, box-shadow 0.2s ease;

    &:focus {
        border-color: var(--primary);
        box-shadow: 0 0 0 2px rgba(var(--primary-rgb), 0.2);
    }
}

.sort-direction-btn {
    width: 36px;
    height: 36px;
    border-radius: 10px;
    border: 1px solid var(--border-color);
    background: var(--bg-tertiary);
    color: var(--text-primary);
    font-size: 1rem;
    font-weight: 700;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    transition: all 0.2s ease;

    &:hover {
        border-color: var(--primary);
        color: var(--primary);
    }
}
</style>
