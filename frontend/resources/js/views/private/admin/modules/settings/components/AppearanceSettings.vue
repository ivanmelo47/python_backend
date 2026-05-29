<template>
    <div class="settings-section">
        <div class="section-header">
            <h3><Icon name="palette" :size="18" /> Apariencia</h3>
            <p>Personaliza la escala visual de la aplicación para mayor comodidad.</p>
        </div>

        <div class="setting-item">
            <div class="setting-info">
                <label>Escala de la aplicación</label>
                <span>Ajusta el tamaño de la interfaz (fuentes, botones, márgenes)</span>
            </div>
            <div class="scale-options">
                <button
                    v-for="option in ['90', '100', '110', '120']"
                    :key="option"
                    class="scale-btn"
                    :class="{ active: scale === option }"
                    @click="setScale(option)"
                >
                    {{ option }}%
                </button>
            </div>
        </div>
    </div>
</template>

<script setup>
import Icon from '@/components/Icon.vue';
import { useScale } from '@/composables/useScale';

const { scale, setScale } = useScale();
</script>

<style lang="scss" scoped>
.settings-section {
    background: var(--bg-secondary);
    border-radius: 12px;
    padding: 1.5rem;
    border: 1px solid var(--border-color);

    .section-header {
        margin-bottom: 2rem;

        h3 {
            display: flex;
            align-items: center;
            gap: 0.75rem;
            color: var(--primary);
            margin: 0 0 0.5rem 0;
            font-size: 1.1rem;
        }

        p {
            color: var(--text-tertiary);
            font-size: 0.9rem;
            margin: 0;
        }
    }

    .setting-item {
        display: flex;
        justify-content: space-between;
        align-items: center;

        .setting-info {
            display: flex;
            flex-direction: column;
            gap: 0.25rem;

            label {
                font-weight: 600;
                color: var(--text-primary);
                font-size: 0.95rem;
            }

            span {
                font-size: 0.8rem;
                color: var(--text-tertiary);
            }
        }
    }

    .scale-options {
        display: flex;
        gap: 0.5rem;
        background: var(--bg-tertiary);
        padding: 4px;
        border-radius: 10px;
        border: 1px solid var(--border-color);

        .scale-btn {
            background: transparent;
            border: none;
            color: var(--text-tertiary);
            padding: 0.5rem 1rem;
            border-radius: 7px;
            font-size: 0.85rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s ease;

            &:hover {
                color: var(--text-secondary);
            }

            &.active {
                background: var(--bg-primary);
                color: var(--primary);
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            }
        }
    }
}
</style>
