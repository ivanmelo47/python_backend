<template>
    <div id="app">
        <LandingNav />

        <div class="landing-container">
            <div class="card mt-4">
                <h1 class="text-center mb-3">
                    <Icon name="home" :size="48" color="var(--primary)" />
                    Bienvenido a Laravel 12 + Vue 3
                </h1>

                <div class="landing-features">
                    <div class="feature-card">
                        <div class="icon">⚡</div>
                        <h3>Vite</h3>
                        <p>Build tool rápido con HMR instantáneo</p>
                    </div>

                    <div class="feature-card">
                        <div class="icon">🎨</div>
                        <h3>Sass</h3>
                        <p>Preprocesador CSS con variables y mixins</p>
                    </div>

                    <div class="feature-card">
                        <div class="icon">🧭</div>
                        <h3>Vue Router</h3>
                        <p>Navegación SPA fluida y moderna</p>
                    </div>

                    <div class="feature-card">
                        <div class="icon">🚀</div>
                        <h3>Laravel 12</h3>
                        <p>Backend potente y elegante</p>
                    </div>
                </div>

                <div class="text-center mt-4">
                    <p>Edita <code>resources/js/views/landing/Home.vue</code> y guarda para ver los cambios en vivo</p>
                    <router-link to="/login" class="landing-cta mt-4">
                        <Icon name="login" :size="20" />
                        Iniciar Sesión
                    </router-link>
                </div>
            </div>
        </div>

        <FloatingAppearanceControls />
    </div>
</template>

<script setup>
import { ref } from 'vue';
import Icon from '../../components/Icon.vue';
import LandingNav from './components/LandingNav.vue';
import FloatingAppearanceControls from './components/FloatingAppearanceControls.vue';

const message = ref('¡El stack funciona correctamente!');
</script>

<style scoped>
/* Component uses global landing styles from sass/landing/_landing.scss */

h1 {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 1rem;
    flex-wrap: wrap;
}

.landing-cta {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
}

code {
    background: var(--bg-tertiary);
    color: var(--primary);
    padding: 0.25rem 0.5rem;
    border-radius: 0.25rem;
    font-family: 'Courier New', monospace;
}
</style>

<style scoped>
/* Component uses global landing styles from sass/landing/_landing.scss */
code {
    background: var(--bg-tertiary);
    color: var(--primary);
    padding: 0.25rem 0.5rem;
    border-radius: 0.25rem;
    font-family: 'Courier New', monospace;
}
</style>
