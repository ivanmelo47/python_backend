<template>
    <div class="modal-field" :class="[`col-span-${span}`, { 'has-error': error }]" :style="fieldStyle">
        <label v-if="label" class="field-label">
            {{ label }}
            <span v-if="required" class="required-mark">*</span>
        </label>

        <div class="field-input-wrapper">
            <slot></slot>
            <p v-if="help" class="field-help">{{ help }}</p>
            <p v-if="error" class="field-error">{{ error }}</p>
        </div>
    </div>
</template>

<script setup>
import { computed } from 'vue';

const props = defineProps({
    label: String,
    help: String,
    error: String,
    required: Boolean,
    span: {
        type: [Number, String],
        default: 1
    }
});

const fieldStyle = computed(() => {
    const span = props.span;
    if (span === 'full') return { gridColumn: '1 / -1' };
    return { gridColumn: `span ${span}` };
});
</script>

<style lang="scss" scoped>
@use 'sass:map';
@use '../../../../../sass/shared/variables' as *;

.modal-field {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;

    @media (max-width: 768px) {
        grid-column: span 1 !important;
    }

    .field-label {
        font-size: 0.82rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        color: var(--text-secondary);
        display: flex;
        align-items: center;
        gap: 0.35rem;

        .required-mark {
            color: map.get($colors, error);
        }
    }

    .field-input-wrapper {
        position: relative;

        :deep(input),
        :deep(select),
        :deep(textarea) {
            width: 100%;
            padding: 0.8rem 1.1rem;
            background-color: var(--bg-primary);
            border: 1px solid var(--border-color);
            border-radius: 0.85rem;
            color: var(--text-primary);
            font-size: 0.95rem;
            font-weight: 500;
            transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
            box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.05);

            &:focus {
                outline: none;
                border-color: var(--primary);
                background-color: var(--bg-secondary);
                box-shadow: 0 0 0 4px rgba(var(--primary-rgb), 0.12), 
                            inset 0 2px 4px rgba(0, 0, 0, 0.05);
                transform: translateY(-1px);
            }

            &::placeholder {
                color: var(--text-tertiary);
                font-weight: 400;
            }

            &:disabled {
                opacity: 0.7;
                cursor: not-allowed;
            }
        }

        :deep(select) {
            appearance: none;
            background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 24 24' stroke='rgba(255,255,255,0.4)'%3E%3Cpath stroke-linecap='round' stroke-linejoin='round' stroke-width='2' d='M19 9l-7 7-7-7'%3E%3C/path%3E%3C/svg%3E");
            background-repeat: no-repeat;
            background-position: right 1rem center;
            background-size: 1.1rem;
            padding-right: 2.8rem;
            cursor: pointer;

            &:focus {
                background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 24 24' stroke='rgba(255,255,255,0.8)'%3E%3Cpath stroke-linecap='round' stroke-linejoin='round' stroke-width='2' d='M19 9l-7 7-7-7'%3E%3C/path%3E%3C/svg%3E");
            }
        }

        :deep(input[type="date"]),
        :deep(input[type="time"]) {
            position: relative;
            cursor: pointer;

            &::-webkit-calendar-picker-indicator {
                cursor: pointer;
                opacity: 0.6;
                filter: invert(1);
                transition: opacity 0.2s;
                
                &:hover {
                    opacity: 1;
                }
            }
        }
    }

    &.has-error {
        .field-label {
            color: map.get($colors, error);
        }

        :deep(input),
        :deep(select),
        :deep(textarea) {
            border-color: map.get($colors, error);
            background-color: rgba(map.get($colors, error), 0.05);

            &:focus {
                box-shadow: 0 0 0 3px rgba(map.get($colors, error), 0.1);
            }
        }
    }

    .field-help {
        font-size: 0.75rem;
        color: var(--text-tertiary);
        margin-top: 0.4rem;
        font-style: italic;
    }

    .field-error {
        font-size: 0.75rem;
        color: map.get($colors, error);
        font-weight: 600;
        margin-top: 0.4rem;
    }
}
</style>
