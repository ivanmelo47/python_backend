<template>
    <div class="pagination-wrapper" :class="{ 'compact': compact }">
        <div class="pagination-left">
            <span class="pagination-info" v-if="pagination && !compact">
                {{ pagination.from || 0 }}-{{ pagination.to || 0 }} de {{ pagination.total || 0 }}
            </span>
            
            <div class="items-per-page" v-if="showItemsPerPage">
                <span class="label" v-if="!compact">Mostrar:</span>
                <select 
                    :value="itemsPerPage" 
                    @change="$emit('update:itemsPerPage', Number($event.target.value))"
                    class="per-page-select"
                >
                    <option v-for="opt in itemsPerPageOptions" :key="opt" :value="opt">
                        {{ opt }}
                    </option>
                </select>
            </div>
        </div>
        
        <div class="pagination-controls">
            <button 
                class="control-btn"
                :disabled="!pagination || pagination.current_page === 1"
                @click="changePage(pagination.current_page - 1)"
                title="Anterior"
            >
                <Icon name="chevronLeft" :size="20" />
            </button>
            
            <template v-if="!compact && pagination">
                <template v-for="(page, idx) in visiblePages" :key="idx">
                    <span v-if="page === '...'" class="pagination-dots">...</span>
                    <button 
                        v-else
                        class="page-btn"
                        :class="{ active: page === pagination.current_page }"
                        @click="changePage(page)"
                    >
                        {{ page }}
                    </button>
                </template>
            </template>

            <span v-else-if="compact && pagination" class="page-info">
                {{ pagination.current_page }} / {{ pagination.last_page }}
            </span>
            
            <button 
                class="control-btn"
                :disabled="!pagination || pagination.current_page === pagination.last_page"
                @click="changePage(pagination.current_page + 1)"
                title="Siguiente"
            >
                <Icon name="chevronRight" :size="20" />
            </button>
        </div>
    </div>
</template>

<script setup>
import { computed } from 'vue';
import Icon from '@/components/Icon.vue';

const props = defineProps({
    pagination: {
        type: Object,
        default: null
    },
    itemsPerPage: {
        type: Number,
        default: 10
    },
    itemsPerPageOptions: {
        type: Array,
        default: () => [5, 10, 20, 50, 100]
    },
    showItemsPerPage: {
        type: Boolean,
        default: true
    },
    compact: {
        type: Boolean,
        default: false
    }
});

const emit = defineEmits(['page-change', 'update:itemsPerPage']);

const changePage = (page) => {
    if (page >= 1 && page <= props.pagination.last_page) {
        emit('page-change', page);
    }
};

const visiblePages = computed(() => {
    if (!props.pagination) return [];
    
    const { current_page, last_page } = props.pagination;

    if (last_page < 8) {
        return Array.from({ length: last_page }, (_, i) => i + 1);
    }

    const pages = [];
    const windowSize = 1;

    if (current_page <= 4) {
        for (let i = 1; i <= 5; i++) pages.push(i);
        pages.push('...');
        pages.push(last_page);
    } else if (current_page >= last_page - 3) {
        pages.push(1);
        pages.push('...');
        for (let i = last_page - 4; i <= last_page; i++) pages.push(i);
    } else {
        pages.push(1);
        pages.push('...');
        for (let i = current_page - windowSize; i <= current_page + windowSize; i++) pages.push(i);
        pages.push('...');
        pages.push(last_page);
    }

    return pages;
});
</script>

<style lang="scss" scoped>
.pagination-wrapper {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 1.25rem 1.5rem;
    background: var(--bg-secondary);
    border-top: 1px solid var(--border-color);
    border-radius: 0 0 12px 12px;

    &.compact {
        padding: 0;
        background: transparent;
        border: none;
        justify-content: flex-end;
        gap: 1rem;
    }

    .pagination-left {
        display: flex;
        align-items: center;
        gap: 2rem;

        .pagination-info {
            font-size: 0.85rem;
            color: var(--text-tertiary);
            font-weight: 500;
        }

        .items-per-page {
            display: flex;
            align-items: center;
            gap: 0.75rem;

            .label {
                font-size: 0.85rem;
                color: var(--text-tertiary);
            }

            .per-page-select {
                background: var(--bg-tertiary);
                border: 1px solid var(--border-color);
                color: var(--text-primary);
                padding: 0.35rem 0.5rem;
                border-radius: 6px;
                font-size: 0.85rem;
                cursor: pointer;
                outline: none;
                transition: all 0.2s;

                &:focus {
                    border-color: var(--primary);
                }
            }
        }
    }

    .pagination-controls {
        display: flex;
        align-items: center;
        gap: 0.5rem;

        .page-info {
            font-size: 0.85rem;
            color: var(--text-primary);
            font-weight: 600;
            min-width: 40px;
            text-align: center;
        }

        .control-btn {
            display: flex;
            align-items: center;
            justify-content: center;
            width: 32px;
            height: 32px;
            border-radius: 8px;
            border: 1px solid var(--border-color);
            background: var(--bg-tertiary);
            color: var(--text-secondary);
            cursor: pointer;
            transition: all 0.2s;

            &:hover:not(:disabled) {
                background: var(--bg-hover);
                color: var(--primary);
                border-color: var(--primary);
            }

            &:disabled {
                opacity: 0.4;
                cursor: not-allowed;
            }
        }

        .page-btn {
            min-width: 32px;
            height: 32px;
            padding: 0 0.5rem;
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: 8px;
            border: 1px solid transparent;
            background: transparent;
            color: var(--text-secondary);
            font-size: 0.85rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s;

            &:hover {
                background: var(--bg-hover);
                color: var(--primary);
            }

            &.active {
                background: var(--primary);
                color: white;
            }
        }

        .pagination-dots {
            color: var(--text-muted);
            font-size: 0.85rem;
            padding: 0 0.25rem;
        }
    }
}
</style>
