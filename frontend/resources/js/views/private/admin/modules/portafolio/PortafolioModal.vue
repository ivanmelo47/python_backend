<template>
    <div v-if="isOpen" class="portfolio-modal-overlay">
        <section class="portfolio-modal-screen">
            <header class="modal-system-header">
                <div class="modal-header-content">
                    <span class="modal-header-icon" aria-hidden="true">i</span>
                    <div>
                        <h2 class="modal-header-title">
                            {{ isEditing ? 'Editar bloques del portafolio' : 'Configurar bloques del portafolio' }}
                        </h2>
                        <p class="modal-header-subtitle">
                            Paso 2 de 2. Define la informacion de cada bloque que se mostrara en la vista publica.
                        </p>
                    </div>
                </div>
                <button type="button" class="modal-close-btn" @click="handleClose" aria-label="Cerrar modal">
                    x
                </button>
            </header>

            <form class="modal-form" @submit.prevent="handleSave">
                <div class="modal-body">
                    <div class="editor-layout">
                        <div class="editor-main">
                            <article class="editor-card">
                                <h3>Hero principal</h3>
                                <div class="form-grid">
                                    <label class="full-width">
                                        Titulo principal
                                        <input v-model.trim="localBlocks.heroTitle" type="text" maxlength="180" />
                                    </label>

                                    <label class="full-width">
                                        Subtitulo
                                        <textarea v-model.trim="localBlocks.heroSubtitle" rows="3" maxlength="240"></textarea>
                                    </label>
                                </div>
                            </article>

                            <article class="editor-card">
                                <h3>Sobre mi</h3>
                                <div class="form-grid">
                                    <label class="full-width">
                                        Descripcion general
                                        <textarea v-model.trim="localBlocks.aboutText" rows="5"></textarea>
                                    </label>
                                </div>
                            </article>

                            <article class="editor-card">
                                <h3>Habilidades y tecnologias</h3>
                                <div class="form-grid">
                                    <label>
                                        Habilidades (una por linea)
                                        <textarea v-model.trim="localBlocks.skillsText" rows="6"></textarea>
                                    </label>

                                    <label>
                                        Tecnologias (una por linea)
                                        <textarea v-model.trim="localBlocks.technologiesText" rows="6"></textarea>
                                    </label>
                                </div>
                            </article>

                            <article class="editor-card">
                                <h3>Trayectoria</h3>
                                <div class="form-grid">
                                    <label>
                                        Historial laboral (una experiencia por linea)
                                        <textarea v-model.trim="localBlocks.workHistoryText" rows="6"></textarea>
                                    </label>

                                    <label>
                                        Educacion y cursos (una entrada por linea)
                                        <textarea v-model.trim="localBlocks.educationText" rows="6"></textarea>
                                    </label>
                                </div>
                            </article>

                            <article class="editor-card">
                                <h3>Proyectos y contacto</h3>
                                <div class="form-grid">
                                    <label class="full-width">
                                        Proyectos (una entrada por linea)
                                        <textarea v-model.trim="localBlocks.projectsText" rows="6"></textarea>
                                    </label>

                                    <label>
                                        Cursos destacados (una entrada por linea)
                                        <textarea v-model.trim="localBlocks.coursesText" rows="5"></textarea>
                                    </label>

                                    <label>
                                        Correo de contacto
                                        <input v-model.trim="localBlocks.contactEmail" type="email" maxlength="120" />
                                    </label>
                                </div>
                            </article>

                            <p v-if="errorMessage" class="form-error">{{ errorMessage }}</p>
                        </div>

                        <aside class="editor-sidebar">
                            <article class="editor-card sticky">
                                <h3>Resumen base</h3>
                                <p><strong>Portafolio:</strong> {{ basicData.name || 'Sin nombre' }}</p>
                                <p><strong>Usuario:</strong> {{ basicData.ownerName || 'Sin usuario' }}</p>
                                <p><strong>Token:</strong> {{ basicData.token || '------' }}</p>
                                <p><strong>Estado:</strong> {{ basicData.status === 'published' ? 'Publicado' : 'Borrador' }}</p>

                                <hr />

                                <h4>Bloques configurados</h4>
                                <p><strong>Skills:</strong> {{ countLines(localBlocks.skillsText) }}</p>
                                <p><strong>Tecnologias:</strong> {{ countLines(localBlocks.technologiesText) }}</p>
                                <p><strong>Proyectos:</strong> {{ countLines(localBlocks.projectsText) }}</p>
                                <p v-if="isDirty" class="unsaved-warning">Tienes cambios sin guardar.</p>

                                <a
                                    class="public-link preview-link"
                                    :href="buildPublicUrl(basicData.token || '______')"
                                    target="_blank"
                                    rel="noopener noreferrer"
                                >
                                    Abrir vista publica
                                </a>
                            </article>
                        </aside>
                    </div>
                </div>

                <footer class="modal-system-footer">
                    <p v-if="isDirty" class="footer-note">Cambios pendientes por guardar</p>
                    <div class="footer-actions">
                        <button type="button" class="btn" @click="handleClose">Cancelar</button>
                        <button type="submit" class="btn btn--primary">
                            {{ isEditing ? 'Guardar cambios' : 'Crear portafolio' }}
                        </button>
                    </div>
                </footer>
            </form>
        </section>
    </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, reactive, ref, watch } from 'vue';
import { FRONTEND_BASE_URL } from '@/services/api/url';

const props = defineProps({
    isOpen: {
        type: Boolean,
        default: false
    },
    isEditing: {
        type: Boolean,
        default: false
    },
    basicData: {
        type: Object,
        required: true
    },
    initialBlocks: {
        type: Object,
        required: true
    },
    errorMessage: {
        type: String,
        default: ''
    }
});

const emit = defineEmits(['close', 'save']);

const localBlocks = reactive({
    heroTitle: '',
    heroSubtitle: '',
    aboutText: '',
    skillsText: '',
    technologiesText: '',
    projectsText: '',
    workHistoryText: '',
    educationText: '',
    coursesText: '',
    contactEmail: ''
});

const initialSnapshot = ref('');

const isDirty = computed(() => JSON.stringify(localBlocks) !== initialSnapshot.value);

watch(
    () => [props.isOpen, props.initialBlocks],
    () => {
        if (!props.isOpen) {
            return;
        }

        localBlocks.heroTitle = props.initialBlocks.heroTitle || '';
        localBlocks.heroSubtitle = props.initialBlocks.heroSubtitle || '';
        localBlocks.aboutText = props.initialBlocks.aboutText || '';
        localBlocks.skillsText = props.initialBlocks.skillsText || '';
        localBlocks.technologiesText = props.initialBlocks.technologiesText || '';
        localBlocks.projectsText = props.initialBlocks.projectsText || '';
        localBlocks.workHistoryText = props.initialBlocks.workHistoryText || '';
        localBlocks.educationText = props.initialBlocks.educationText || '';
        localBlocks.coursesText = props.initialBlocks.coursesText || '';
        localBlocks.contactEmail = props.initialBlocks.contactEmail || '';

        initialSnapshot.value = JSON.stringify(localBlocks);
    },
    { immediate: true, deep: true }
);

function buildPublicUrl(token) {
    const origin = FRONTEND_BASE_URL || (typeof window !== 'undefined' ? window.location.origin : 'https://tu-dominio.com');
    return `${origin}/portafolio-usuario/${String(token || '______').toUpperCase()}`;
}

function handleSave() {
    emit('save', { ...localBlocks });
}

function handleClose() {
    emit('close');
}

function handleBeforeUnload(event) {
    if (!props.isOpen || !isDirty.value) {
        return;
    }

    event.preventDefault();
    event.returnValue = '';
}

function countLines(text) {
    if (!text) {
        return 0;
    }

    return text
        .split('\n')
        .map(line => line.trim())
        .filter(Boolean).length;
}

onMounted(() => {
    window.addEventListener('beforeunload', handleBeforeUnload);
});

onBeforeUnmount(() => {
    window.removeEventListener('beforeunload', handleBeforeUnload);
});
</script>

<style scoped>
.portfolio-modal-overlay {
    position: fixed;
    inset: 0;
    z-index: 1300;
    background: rgba(0, 0, 0, 0.66);
    backdrop-filter: blur(3px);
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 0.55rem;
    animation: modalOverlayFade 0.26s ease-out;
}

.portfolio-modal-screen {
    width: min(1640px, calc(100vw - 1.1rem));
    max-height: calc(100vh - 1.1rem);
    background: var(--bg-primary);
    color: var(--text-primary);
    border-radius: 1rem;
    border: 1px solid var(--border-color);
    box-shadow: 0 28px 60px rgba(0, 0, 0, 0.35);
    transform-origin: top center;
    animation: modalFloatIn 0.32s cubic-bezier(0.2, 0.8, 0.2, 1);
    overflow: hidden;
    display: flex;
    flex-direction: column;
}

@keyframes modalOverlayFade {
    from {
        opacity: 0;
    }

    to {
        opacity: 1;
    }
}

@keyframes modalFloatIn {
    from {
        opacity: 0;
        transform: translateY(14px) scale(0.985);
    }

    to {
        opacity: 1;
        transform: translateY(0) scale(1);
    }
}

@media (prefers-reduced-motion: reduce) {
    .portfolio-modal-overlay,
    .portfolio-modal-screen {
        animation: none;
    }
}

.modal-system-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 0.8rem;
    padding: 0.95rem 1.2rem;
    background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
    color: #ffffff;
}

.modal-header-content {
    display: flex;
    align-items: center;
    gap: 0.75rem;
}

.modal-header-icon {
    width: 1.85rem;
    height: 1.85rem;
    border-radius: 999px;
    border: 1px solid rgba(255, 255, 255, 0.3);
    background: rgba(255, 255, 255, 0.2);
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-weight: 700;
}

.modal-header-title {
    margin: 0;
    font-size: 1.3rem;
}

.modal-header-subtitle {
    margin: 0.22rem 0 0;
    color: rgba(255, 255, 255, 0.92);
    font-size: 0.93rem;
}

.modal-close-btn {
    border: 1px solid rgba(255, 255, 255, 0.35);
    background: rgba(255, 255, 255, 0.12);
    color: #ffffff;
    width: 2rem;
    height: 2rem;
    border-radius: 999px;
    font-size: 1rem;
    font-weight: 700;
    line-height: 1;
    cursor: pointer;
}

.modal-form {
    display: flex;
    flex-direction: column;
    min-height: 0;
    flex: 1;
}

.modal-body {
    padding: 1rem 1.2rem;
    overflow: auto;
    min-height: 0;
}

.editor-layout {
    display: grid;
    grid-template-columns: minmax(0, 1.95fr) minmax(340px, 1fr);
    gap: 1rem;
    align-items: start;
}

.editor-main {
    display: grid;
    gap: 0.9rem;
}

.editor-card {
    border: 1px solid var(--border-color);
    border-radius: 0.9rem;
    background: var(--bg-secondary);
    padding: 0.9rem;
}

.editor-card h3 {
    margin: 0 0 0.7rem;
}

.form-grid {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 0.75rem;
}

.form-grid label {
    display: grid;
    gap: 0.35rem;
    font-size: 0.88rem;
    color: var(--text-secondary);
}

input,
textarea,
select {
    width: 100%;
    border: 1px solid var(--border-color);
    border-radius: 0.65rem;
    background: var(--bg-primary);
    color: var(--text-primary);
    padding: 0.6rem 0.75rem;
}

.full-width {
    grid-column: span 2;
}

.form-error {
    margin: 0;
    color: #b91c1c;
    font-weight: 600;
}

.editor-sidebar .sticky {
    position: sticky;
    top: 0.8rem;
}

.editor-sidebar p {
    margin: 0.45rem 0;
    color: var(--text-secondary);
}

.editor-sidebar hr {
    margin: 0.85rem 0;
    border: 0;
    border-top: 1px solid var(--border-color);
}

.editor-sidebar h4 {
    margin: 0;
}

.unsaved-warning {
    color: #b45309;
    font-weight: 600;
}

.public-link {
    color: var(--primary);
    text-decoration: none;
}

.preview-link {
    display: inline-flex;
    margin-top: 0.3rem;
}

.modal-system-footer {
    border-top: 1px solid var(--border-color);
    background: var(--bg-secondary);
    padding: 0.85rem 1.2rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 0.8rem;
}

.footer-note {
    margin: 0;
    font-size: 0.88rem;
    color: #a16207;
    font-weight: 600;
}

.footer-actions {
    display: flex;
    gap: 0.5rem;
}

.btn {
    border: 1px solid var(--border-color);
    background: var(--bg-primary);
    color: var(--text-primary);
    border-radius: 0.64rem;
    padding: 0.46rem 0.7rem;
    cursor: pointer;
    font-weight: 600;
}

.btn--primary {
    background: var(--primary);
    border-color: var(--primary);
    color: #ffffff;
}

@media (max-width: 860px) {
    .portfolio-modal-overlay {
        padding: 0.45rem;
    }

    .portfolio-modal-screen {
        width: min(1640px, calc(100vw - 0.9rem));
        max-height: calc(100vh - 0.9rem);
        border-radius: 0.85rem;
    }

    .modal-system-header {
        flex-direction: column;
        align-items: stretch;
    }

    .editor-layout {
        grid-template-columns: 1fr;
    }

    .form-grid {
        grid-template-columns: 1fr;
    }

    .full-width {
        grid-column: span 1;
    }

    .modal-system-footer {
        flex-direction: column;
        align-items: stretch;
    }

    .footer-actions {
        width: 100%;
    }

    .footer-actions .btn {
        flex: 1;
    }
}
</style>
