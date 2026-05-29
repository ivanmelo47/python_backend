<template>
    <ModalForm
        :is-visible="isOpen"
        :title="title"
        :icon="icon"
        :size="size"
        mode="info"
        :submit-label="submitLabel"
        :hide-footer="!showEditButton"
        @submit="$emit('edit')"
        @close="close"
    >
        <div class="modal-info-view">
            <!-- Optional Header Slot (Concept, Icon, etc) -->
            <slot name="top-header"></slot>

            <div class="info-rows-container">
                <div class="info-rows">
                    <!-- Standard data mapping -->
                    <template v-if="data && columns && columns.length">
                        <div 
                            v-for="col in columns" 
                            :key="col.key" 
                            class="info-row"
                            :class="{ 'full-width': col.fullWidth }"
                        >
                            <span class="row-label">{{ col.label.toUpperCase() }}:</span>
                            <div class="row-value" :class="[col.valueClass, { 'is-note': col.isNote }]">
                                <slot :name="`value-${col.key}`" :value="data[col.key]" :row="data">
                                    {{ data[col.key] }}
                                </slot>
                            </div>
                        </div>
                    </template>
                    
                    <!-- Generic content slot -->
                    <slot></slot>
                </div>
            </div>
        </div>
    </ModalForm>
</template>

<script setup>
import { computed } from 'vue';
import ModalForm from './ModalForm.vue';

const props = defineProps({
    isOpen: {
        type: Boolean,
        required: true
    },
    title: {
        type: String,
        default: 'Información Detallada'
    },
    icon: {
        type: String,
        default: 'info'
    },
    size: {
        type: String,
        default: 'md'
    },
    data: {
        type: Object,
        default: null
    },
    columns: {
        type: Array,
        default: () => []
    },
    showEditButton: {
        type: Boolean,
        default: false
    },
    submitLabel: {
        type: String,
        default: 'Editar Registro'
    }
});

const emit = defineEmits(['close', 'edit']);

const close = () => {
    emit('close');
};
</script>

<style lang="scss" scoped>
.modal-info-view {
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
}

.info-rows-container {
    padding-right: 8px;
}

.info-rows {
    display: flex;
    flex-direction: column;

    .info-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0.85rem 0;
        border-bottom: 1px dashed var(--border-color);
        gap: 1rem;

        &:last-child {
            border-bottom: none;
        }

        .row-label {
            font-size: 0.7rem;
            font-weight: 800;
            color: var(--text-tertiary);
            letter-spacing: 0.05em;
            white-space: nowrap;
        }

        .row-value {
            font-size: 0.95rem;
            font-weight: 600;
            color: var(--text-secondary);
            text-align: right;
            
            &.is-note {
                text-align: left;
                background: var(--bg-tertiary);
                padding: 0.75rem;
                border-radius: 8px;
                font-weight: 400;
                line-height: 1.5;
                font-size: 0.9rem;
                width: 100%;
                margin-top: 0.25rem;
            }
        }

        &.full-width {
            flex-direction: column;
            align-items: flex-start;
            gap: 0.5rem;
            
            .row-value {
                text-align: left;
            }
        }
    }
}

/* Header special row style */
:deep(.detail-header-row) {
    display: flex;
    align-items: center;
    gap: 1rem;
    padding-bottom: 1.25rem;
    border-bottom: 1px solid var(--border-color);

    .concept-badge {
        width: 42px;
        height: 42px;
        border-radius: 12px;
        background: var(--bg-tertiary);
        display: flex;
        align-items: center;
        justify-content: center;
        color: var(--primary);
        border: 1px solid var(--border-color);
    }

    .concept-title {
        font-size: 1.25rem;
        font-weight: 800;
        color: var(--text-primary);
        margin: 0;
    }
}
</style>