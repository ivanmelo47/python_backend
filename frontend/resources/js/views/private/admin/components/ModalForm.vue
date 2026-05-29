<template>
    <transition name="modal-fade">
        <div v-if="isVisible" class="modal-overlay" @click.self="handleBackdropClick">
            <div
                class="modal-container"
                :class="[`modal-${size}`]"
                role="dialog"
                aria-modal="true"
            >
                <!-- Header -->
                <div class="modal-header">
                    <div class="header-content">
                        <div v-if="$slots['header-icon'] || icon" class="header-icon">
                            <slot name="header-icon">
                                <Icon v-if="icon" :name="icon" :size="20" />
                            </slot>
                        </div>
                        <slot name="header-title">
                            <h3 class="modal-title">{{ title }}</h3>
                        </slot>
                    </div>
                    <button class="close-btn" @click="close" aria-label="Cerrar">
                        <Icon name="x" :size="20" />
                    </button>
                </div>

                <!-- Body -->
                <div
                    class="modal-body"
                    :class="['grid-layout', `cols-${columns}`]"
                    :style="gridStyle"
                >
                    <template v-if="fields && fields.length">
                        <ModalField
                            v-for="field in fields.filter(f => !f.hidden)"
                            :key="field.key"
                            :label="field.label"
                            :error="errors[field.key]?.[0]"
                            :required="field.required"
                            :span="field.span"
                            :help="field.help"
                        >
                            <slot :name="`field-${field.key}`" :field="field" :modelValue="modelValue" :updateValue="(val) => modelValue[field.key] = val">
                                <select
                                    v-if="field.type === 'select'"
                                    v-model="modelValue[field.key]"
                                    :required="field.required"
                                    :disabled="field.disabled"
                                >
                                    <option value="" disabled>{{ field.placeholder }}</option>
                                    <option v-for="option in field.options" :key="option.id" :value="option.id">
                                        {{ option.name }}
                                    </option>
                                </select>
                                
                                <textarea
                                    v-else-if="field.type === 'textarea'"
                                    v-model="modelValue[field.key]"
                                    :placeholder="field.placeholder"
                                    :disabled="field.disabled"
                                    rows="3"
                                ></textarea>

                                <div v-else-if="field.type === 'percentage'" class="input-group">
                                    <input
                                        v-model="modelValue[field.key]"
                                        type="number"
                                        step="0.01"
                                        :placeholder="field.placeholder"
                                        :disabled="field.disabled"
                                    >
                                    <span class="input-group-text">%</span>
                                </div>

                                <IconSelect
                                    v-else-if="field.type === 'icon-select'"
                                    v-model="modelValue[field.key]"
                                    :selectedIconData="field.selectedData"
                                    :category="field.category"
                                    @change="field.onChange"
                                />

                                <div v-else-if="field.type === 'color'" class="custom-color-picker">
                                    <div class="picker-input-wrapper">
                                        <input
                                            v-model="modelValue[field.key]"
                                            type="color"
                                            class="absolute inset-0 opacity-0 cursor-pointer w-full h-full"
                                        >
                                        <div class="color-bar" :style="{ backgroundColor: modelValue[field.key] }"></div>
                                    </div>
                                    <input
                                        v-model="modelValue[field.key]"
                                        type="text"
                                        class="hex-input"
                                        placeholder="#000000"
                                    >
                                </div>

                                <!-- Switch / Toggle -->
                                <div v-else-if="field.type === 'switch'" class="flex items-center gap-3 py-1">
                                    <label class="premium-switch">
                                        <input 
                                            type="checkbox" 
                                            v-model="modelValue[field.key]"
                                            :disabled="field.disabled"
                                        >
                                        <span class="slider"></span>
                                    </label>
                                    <span v-if="field.options?.activeLabel || field.options?.inactiveLabel" class="text-xs font-semibold text-tertiary uppercase tracking-wider">
                                        {{ modelValue[field.key] ? (field.options.activeLabel || 'Activado') : (field.options.inactiveLabel || 'Desactivado') }}
                                    </span>
                                </div>

                                <input
                                    v-else
                                    v-model="modelValue[field.key]"
                                    :type="field.type"
                                    :placeholder="field.placeholder"
                                    :autocomplete="field.autocomplete || 'off'"
                                    :disabled="field.disabled"
                                >
                            </slot>
                        </ModalField>
                    </template>

                    <slot></slot>
                </div>

                <!-- Footer -->
                <div v-if="!hideFooter" class="modal-footer">
                    <slot name="footer">
                        <button
                            type="button"
                            class="btn-ghost"
                            @click="close"
                            :disabled="loading"
                        >
                            Cancelar
                        </button>
                        <button
                            type="button"
                            class="btn-solid"
                            @click="submit"
                            :disabled="loading"
                        >
                            <span v-if="loading" class="spinner-sm mr-2"></span>
                            {{ submitLabel }}
                        </button>
                    </slot>
                </div>
            </div>
        </div>
    </transition>
</template>

<script setup>
import { onMounted, onUnmounted, computed } from 'vue';
import Icon from '@/components/Icon.vue';
import IconSelect from '@/components/IconSelect.vue';
import ModalField from '@/views/private/admin/components/ModalField.vue';

const props = defineProps({
    isVisible: {
        type: Boolean,
        required: true
    },
    title: {
        type: String,
        default: 'Formulario'
    },
    loading: {
        type: Boolean,
        default: false
    },
    size: {
        type: String,
        default: 'md',
        validator: (value) => ['sm', 'md', 'lg', 'xl', 'full'].includes(value)
    },
    columns: {
        type: [Number, String],
        default: 1
    },
    submitLabel: {
        type: String,
        default: 'Guardar'
    },
    hideFooter: {
        type: Boolean,
        default: false
    },
    closeOnBackdrop: {
        type: Boolean,
        default: true
    },
    fields: {
        type: Array,
        default: () => []
    },
    mode: {
        type: String,
        default: 'form', // 'form' or 'info'
        validator: (value) => ['form', 'info'].includes(value)
    },
    icon: {
        type: String,
        default: ''
    },
    modelValue: {
        type: Object,
        default: () => ({})
    },
    errors: {
        type: Object,
        default: () => ({})
    }
});

const emit = defineEmits(['close', 'submit']);

// Computed Grid Style
const gridStyle = computed(() => {
    const cols = Number(props.columns);
    return {
        gridTemplateColumns: `repeat(${cols}, 1fr)`
    };
});

const close = () => {
    if (!props.loading) {
        emit('close');
    }
};

const submit = () => {
    if (!props.loading) {
        emit('submit');
    }
};

const handleBackdropClick = () => {
    if (props.closeOnBackdrop) {
        close();
    }
};

// Handle Escape key
const handleKeydown = (e) => {
    if (e.key === 'Escape' && props.isVisible) {
        close();
    }
};

onMounted(() => {
    document.addEventListener('keydown', handleKeydown);
});

onUnmounted(() => {
    document.removeEventListener('keydown', handleKeydown);
});
</script>

<style lang="scss" scoped>
.modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.5);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
    backdrop-filter: blur(4px);
}

.modal-container {
    background: var(--bg-secondary);
    border-radius: 1.25rem;
    box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
    width: 90%;
    max-width: 95vw;
    max-height: 92vh;
    display: flex;
    flex-direction: column;
    border: 1px solid var(--border-color);
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);

    @media (max-width: 640px) {
        width: 95%;
        border-radius: 1rem;
    }

    &.modal-sm { max-width: 400px; }
    &.modal-md { max-width: 600px; }
    &.modal-lg { max-width: 900px; }
    &.modal-xl { max-width: 1200px; }
    &.modal-full { max-width: 95%; width: 95%; }
}

.modal-header {
    padding: 1.25rem 1.5rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
    border-bottom: 1px solid var(--border-color);

    @media (max-width: 640px) {
        padding: 1rem;
    }

    .header-content {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        
        .header-icon {
            color: var(--primary);
        }
        
        .modal-title {
            font-size: 1.1rem;
            font-weight: 700;
            color: var(--text-primary);
            margin: 0;
        }
    }

    .close-btn {
        background: transparent;
        border: none;
        color: var(--text-secondary);
        cursor: pointer;
        padding: 0.5rem;
        border-radius: 0.5rem;
        transition: all 0.2s;

        &:hover {
            background: var(--bg-tertiary);
            color: var(--text-primary);
        }
    }
}

.modal-body {
    padding: 1.5rem;
    overflow-y: auto;
    display: grid;
    gap: 1.25rem;

    @media (max-width: 768px) {
        padding: 1.25rem 1rem;
        gap: 1.25rem;
        grid-template-columns: 1fr !important; // Force 1 column on mobile and tablets
    }
}

.modal-footer {
    padding: 1.25rem 1.5rem;
    display: flex;
    justify-content: flex-end;
    gap: 0.75rem;
    border-top: 1px solid var(--border-color);

    @media (max-width: 640px) {
        padding: 1rem;
        
        .btn-ghost, .btn-solid {
            flex: 1;
            padding: 0.75rem;
        }
    }
}

/* Input Group Styles */
:deep(.input-group) {
    display: flex;
    align-items: stretch;
    width: 100%;
    
    input {
        flex: 1;
        border-top-right-radius: 0 !important;
        border-bottom-right-radius: 0 !important;
    }
    
    .input-group-text {
        display: flex;
        align-items: center;
        padding: 0 1rem;
        background: var(--bg-tertiary);
        border: 1px solid var(--border-color);
        border-left: none;
        border-top-right-radius: 0.85rem;
        border-bottom-right-radius: 0.85rem;
        color: var(--text-secondary);
        font-weight: 600;
        font-size: 0.9rem;
    }
}

/* Custom Color Picker */
.custom-color-picker {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
    width: 100%;

    .picker-input-wrapper {
        position: relative;
        height: 42px;
        width: 100%;
        border-radius: 0.85rem;
        overflow: hidden;
        border: 1px solid var(--border-color);
        cursor: pointer;
        transition: all 0.2s ease;

        &:hover {
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        }

        input[type="color"] {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            opacity: 0;
            cursor: pointer;
            z-index: 2;
        }

        .color-bar {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: 1;
            transition: background-color 0.3s ease;
            
            &::after {
                content: 'Seleccionar color';
                position: absolute;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                color: white;
                font-size: 0.75rem;
                font-weight: 700;
                text-transform: uppercase;
                letter-spacing: 0.05em;
                text-shadow: 0 1px 4px rgba(0,0,0,0.4);
                pointer-events: none;
                opacity: 0.8;
            }
        }
    }

    .hex-input {
        text-align: center;
        font-family: monospace;
        font-weight: 600;
        letter-spacing: 1px;
    }
}

.modal-fade-enter-active,
.modal-fade-leave-active {
    transition: opacity 0.3s ease, transform 0.3s ease;
}

.modal-fade-enter-from,
.modal-fade-leave-to {
    opacity: 0;
    transform: scale(0.95);
}
/* Premium Switch Toggle */
.premium-switch {
    position: relative;
    display: inline-block;
    width: 38px;
    height: 22px;
    
    input {
        opacity: 0;
        width: 0;
        height: 0;
        
        &:checked + .slider {
            background-color: var(--primary);
            box-shadow: 0 0 10px rgba(var(--primary-rgb), 0.3);
            
            &:before {
                transform: translateX(16px);
            }
        }
    }
    
    .slider {
        position: absolute;
        cursor: pointer;
        top: 0; left: 0; right: 0; bottom: 0;
        background-color: var(--bg-tertiary);
        transition: .3s;
        border-radius: 34px;
        border: 1px solid var(--border-color);
        
        &:before {
            position: absolute;
            content: "";
            height: 14px;
            width: 14px;
            left: 3px;
            bottom: 3px;
            background-color: white;
            transition: .3s;
            border-radius: 50%;
            box-shadow: 0 2px 4px rgba(0,0,0,0.2);
        }
    }
}
</style>
