<template>
    <div class="stat-card settings-card">
        <div class="stat-header">
            <div class="icon">
                <Icon name="settings" :size="24" />
            </div>
            <span class="card-label">Apariencia</span>
        </div>
        
        <div class="settings-content">
            <!-- Theme Toggle -->
            <div class="setting-group">
                <label>Tema</label>
                <div class="toggle-options">
                    <button 
                        class="toggle-btn" 
                        :class="{ active: theme === 'light' }"
                        @click="setTheme('light')"
                    >
                        <Icon name="sun" :size="16" />
                        <span>Claro</span>
                    </button>
                    <button 
                        class="toggle-btn" 
                        :class="{ active: theme === 'dark' }"
                        @click="setTheme('dark')"
                    >
                        <Icon name="moon" :size="16" />
                        <span>Oscuro</span>
                    </button>
                </div>
            </div>

            <!-- Scale Selector -->
            <div class="setting-group">
                <label>Escala: {{ scale }}%</label>
                <div class="scale-buttons">
                    <button 
                        v-for="option in ['90', '100', '110', '120']" 
                        :key="option"
                        class="scale-dot"
                        :class="{ active: scale === option }"
                        @click="setScale(option)"
                        :title="`${option}%`"
                    >
                        {{ option }}
                    </button>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import Icon from '@/components/Icon.vue';
import { useTheme } from '@/composables/useTheme';
import { useScale } from '@/composables/useScale';

const { theme, toggleTheme } = useTheme();
const { scale, setScale } = useScale();

const setTheme = (mode) => {
    if (theme.value !== mode) {
        toggleTheme();
    }
};
</script>

<style lang="scss" scoped>
.settings-card {
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
}

.settings-content {
    display: flex;
    flex-direction: column;
    gap: 1.25rem;
}

.setting-group {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;

    label {
        font-size: 0.875rem;
        font-weight: 600;
        color: var(--text-secondary);
    }
}

.toggle-options {
    display: flex;
    background: var(--bg-tertiary);
    padding: 4px;
    border-radius: 8px;
    gap: 4px;

    .toggle-btn {
        flex: 1;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 8px;
        padding: 8px;
        border: none;
        background: transparent;
        color: var(--text-tertiary);
        border-radius: 6px;
        cursor: pointer;
        font-size: 0.875rem;
        transition: all 0.2s;

        &:hover {
            color: var(--text-primary);
        }

        &.active {
            background: var(--bg-primary);
            color: var(--primary);
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
    }
}

.scale-buttons {
    display: flex;
    gap: 8px;
    justify-content: space-between;

    .scale-dot {
        flex: 1;
        padding: 8px 4px;
        border: 1px solid var(--border-color);
        background: var(--bg-primary);
        color: var(--text-secondary);
        border-radius: 6px;
        cursor: pointer;
        font-size: 0.75rem;
        font-weight: 600;
        transition: all 0.2s;

        &:hover {
            border-color: var(--primary);
            color: var(--primary);
        }

        &.active {
            background: var(--primary);
            border-color: var(--primary);
            color: white;
        }
    }
}
</style>
