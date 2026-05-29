<template>
    <div id="app">
        <LandingNav />

        <div class="landing-container">
            <div class="card mt-4">
                <h1 class="text-center mb-3">ℹ️ Acerca de Este Proyecto</h1>

                <div class="about-content">
                    <section class="about-section mb-4">
                        <h2>🎯 Stack Tecnológico</h2>
                        <ul class="tech-list">
                            <li><strong>Backend:</strong> Laravel 12 (PHP 8.4)</li>
                            <li><strong>Frontend:</strong> Vue 3 (Composition API)</li>
                            <li><strong>Routing:</strong> Vue Router 4</li>
                            <li><strong>Build Tool:</strong> Vite 7</li>
                            <li><strong>Estilos:</strong> Sass modular (SCSS)</li>
                            <li><strong>Gestión:</strong> manager.js personalizado</li>
                        </ul>
                    </section>

                    <section class="about-section mb-4">
                        <h2>📦 Características</h2>
                        <ul>
                            <li>✅ PHP 8.4 Portable</li>
                            <li>✅ Composer Portable</li>
                            <li>✅ Hot Module Replacement (HMR)</li>
                            <li>✅ Single Page Application (SPA)</li>
                            <li>✅ Sass modular con modo oscuro</li>
                            <li>✅ Escalabilidad de UI con rem</li>
                            <li>✅ Script de gestión integrado</li>
                        </ul>
                    </section>

                    <section class="about-section">
                        <h2>🚀 Gestión del Proyecto</h2>
                        <p>Utiliza <code>npm run manager</code> para acceder a todas las herramientas de gestión:</p>
                        <ul>
                            <li>Iniciar servidores (PHP + Vite)</li>
                            <li>Instalar dependencias</li>
                            <li>Ejecutar migraciones</li>
                            <li>Gestionar Git</li>
                            <li>Y mucho más...</li>
                        </ul>
                    </section>
                </div>
            </div>
        </div>

        <FloatingAppearanceControls />
    </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import LandingNav from './components/LandingNav.vue';
import FloatingAppearanceControls from './components/FloatingAppearanceControls.vue';

const projectInfo = ref({
    name: 'Laravel 12 + Vue 3 Base Project',
    version: '1.0.0',
    created: new Date().toLocaleDateString('es-ES')
});

onMounted(() => {
    console.log('About page mounted!', projectInfo.value);
});
</script>

<style scoped>
/* Component uses global landing styles from sass/landing/_landing.scss */

.about-content {
    max-width: 800px;
    margin: 0 auto;
}

.about-section {
    background: var(--bg-secondary);
    padding: 1.5rem;
    border-left: 4px solid var(--primary);
    border-radius: 0.5rem;

    h2 {
        color: var(--primary);
        margin-bottom: 1rem;
        font-size: 1.5rem;
    }

    ul {
        list-style: none;
        padding-left: 0;

        li {
            padding: 0.5rem 0;
            padding-left: 1.5rem;
            position: relative;
            color: var(--text-secondary);

            &::before {
                content: '▸';
                position: absolute;
                left: 0;
                color: var(--primary);
                font-weight: bold;
            }

            strong {
                color: var(--text-primary);
            }
        }
    }

    p {
        color: var(--text-secondary);
        margin-bottom: 1rem;
    }
}

code {
    background: var(--bg-tertiary);
    color: var(--primary);
    padding: 0.25rem 0.5rem;
    border-radius: 0.25rem;
    font-family: 'Courier New', monospace;
}
</style>
