<template>
    <div class="appearance-floater">
        <button
            class="appearance-button theme-button"
            @click="toggleTheme"
            :title="theme === 'dark' ? 'Cambiar a modo claro' : 'Cambiar a modo oscuro'"
            aria-label="Cambiar tema"
        >
            <Icon :name="theme === 'dark' ? 'sun' : 'moon'" :size="22" />
        </button>

        <div class="palette-group">
            <button
                class="appearance-button palette-button"
                @click="togglePaletteMenu"
                :class="{ active: isPaletteMenuOpen }"
                :title="`Paleta: ${getPaletteLabel(palette)}`"
                aria-label="Cambiar paleta de colores"
            >
                <Icon name="palette" :size="22" />
            </button>

            <Transition name="palette-menu">
                <div v-if="isPaletteMenuOpen" class="palette-menu" @click.stop>
                    <button
                        v-for="p in allPalettes"
                        :key="p.id"
                        class="palette-option"
                        :class="{ active: palette === p.id }"
                        @click="handlePaletteChange(p.id)"
                    >
                        <span class="palette-swatch" :style="{ backgroundColor: p.color }"></span>
                        <span class="palette-label">{{ p.name }}</span>
                        <Icon v-if="palette === p.id" name="check" :size="14" class="check-icon" />
                    </button>
                </div>
            </Transition>
        </div>
    </div>
</template>

<script setup>
import { onBeforeUnmount, onMounted, ref, computed } from 'vue';
import Icon from '../../../components/Icon.vue';
import { useTheme } from '../../../composables/useTheme';
import { useColorPalette } from '../../../composables/useColorPalette';

const { theme, toggleTheme } = useTheme();
const { palette, setPalette, staticPalettes, dynamicPalettes } = useColorPalette();

const isPaletteMenuOpen = ref(false);

const allPalettes = computed(() => {
    return [...Object.values(staticPalettes), ...dynamicPalettes.value];
});

const getPaletteLabel = (key) => {
    const p = allPalettes.value.find(x => x.id === key);
    return p ? p.name : 'Verde';
};

const togglePaletteMenu = () => {
    isPaletteMenuOpen.value = !isPaletteMenuOpen.value;
};

const handlePaletteChange = (newPalette) => {
    setPalette(newPalette);
    isPaletteMenuOpen.value = false;
};

const handleOutsideClick = (event) => {
    if (!event.target.closest('.palette-group')) {
        isPaletteMenuOpen.value = false;
    }
};

onMounted(() => {
    document.addEventListener('click', handleOutsideClick);
});

onBeforeUnmount(() => {
    document.removeEventListener('click', handleOutsideClick);
});
</script>

<style scoped>
.appearance-floater {
    position: fixed;
    right: 1.5rem;
    bottom: 1.5rem;
    z-index: 9999;
    display: flex;
    align-items: flex-end;
    gap: 0.75rem;
}

.appearance-button {
    width: 3.5rem;
    height: 3.5rem;
    border-radius: 99px;
    border: 1px solid rgba(255, 255, 255, 0.1);
    display: inline-flex;
    align-items: center;
    justify-content: center;
    color: #fff;
    cursor: pointer;
    background: rgba(17, 24, 39, 0.6);
    backdrop-filter: blur(12px);
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.appearance-button:hover {
    transform: translateY(-5px) scale(1.05);
    background: rgba(17, 24, 39, 0.8);
    border-color: rgba(92, 232, 191, 0.4);
    box-shadow: 0 15px 40px rgba(0, 0, 0, 0.4);
}

.appearance-button:active {
    transform: scale(0.95);
}

.theme-button {
    color: #fff;
}

.palette-button {
    background: linear-gradient(135deg, rgba(92, 232, 191, 0.4) 0%, rgba(59, 130, 246, 0.4) 100%);
}

.palette-button.active {
    border-color: #5ce8bf;
    background: rgba(92, 232, 191, 0.2);
}

.palette-group {
    position: relative;
}

.palette-menu {
    position: absolute;
    right: 0;
    bottom: calc(100% + 1rem);
    width: 14rem;
    padding: 8px;
    border-radius: 16px;
    background: rgba(15, 18, 24, 0.9);
    backdrop-filter: blur(24px);
    border: 1px solid rgba(255, 255, 255, 0.08);
    box-shadow: 0 20px 50px rgba(0, 0, 0, 0.5);
    display: grid;
    gap: 4px;
}

.palette-option {
    width: 100%;
    border: 1px solid transparent;
    background: transparent;
    color: #fff;
    border-radius: 10px;
    padding: 10px 12px;
    display: flex;
    align-items: center;
    gap: 12px;
    cursor: pointer;
    transition: all 0.2s;
}

.palette-option:hover {
    background: rgba(255, 255, 255, 0.05);
}

.palette-option.active {
    background: rgba(92, 232, 191, 0.1);
    border-color: rgba(92, 232, 191, 0.25);
}

.palette-swatch {
    width: 12px;
    height: 12px;
    border-radius: 50%;
    flex-shrink: 0;
    box-shadow: 0 0 10px rgba(0, 0, 0, 0.5);
}

.palette-label {
    flex: 1;
    font-size: 0.9rem;
    font-weight: 600;
}

.check-icon {
    color: #5ce8bf;
}

.palette-menu-enter-active,
.palette-menu-leave-active {
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.palette-menu-enter-from,
.palette-menu-leave-to {
    opacity: 0;
    transform: translateY(10px) scale(0.95);
    filter: blur(10px);
}

@media (max-width: 640px) {
    .appearance-floater {
        right: 1rem;
        bottom: 1rem;
    }
}
</style>
