<template>
    <div class="login-layout">
        <LandingNav />

        <div class="login-container">
            <div class="login-card" :class="[`width-${width}`, `align-${align}`]">
                <div class="login-header">
                    <slot name="header">
                        <h1>
                            <slot name="header-icon"></slot>
                            <span v-if="title">{{ title }}</span>
                        </h1>
                    </slot>
                    <p v-if="subtitle">{{ subtitle }}</p>
                </div>

                <slot name="form"></slot>

                <div class="login-footer">
                    <slot name="footer"></slot>
                </div>
            </div>
        </div>

        <button class="theme-toggle" @click="toggleTheme" :title="theme === 'dark' ? 'Modo claro' : 'Modo oscuro'">
            <Icon :name="theme === 'dark' ? 'sun' : 'moon'" :size="24" />
        </button>
    </div>
</template>

<script setup>
import { useTheme } from '@/composables/useTheme';
import Icon from '@/components/Icon.vue';
import LandingNav from './LandingNav.vue';

defineProps({
    title: {
        type: String,
        required: true
    },
    subtitle: {
        type: String,
        default: ''
    },
    width: {
        type: Number,
        default: 1
    },
    align: {
        type: String,
        default: 'center'
    }
});

const { theme, toggleTheme } = useTheme();
</script>
