<template>
    <PortfolioBlock kicker="Proyectos" title="Trabajo reciente" id="proyectos" class="projects-block reveal reveal-delay-2">
        <div class="project-list">
            <div
                v-for="project in projects"
                :key="project.id"
                class="project-item"
                role="button"
                tabindex="0"
                @click="openProjectModal(project)"
                @keydown.enter.prevent="openProjectModal(project)"
                @keydown.space.prevent="openProjectModal(project)"
            >
                <strong>{{ project.title }}</strong>
                <p>{{ project.description }}</p>
                <span>{{ project.type }}</span>
                <small class="project-open-hint">Click para ver detalle</small>

                <div class="project-links" @click.stop>
                    <a
                        v-if="project.repoUrl"
                        :href="project.repoUrl"
                        target="_blank"
                        rel="noopener noreferrer"
                        class="project-link"
                    >
                        Repositorio
                    </a>
                    <a
                        v-if="project.liveUrl"
                        :href="project.liveUrl"
                        target="_blank"
                        rel="noopener noreferrer"
                        class="project-link"
                    >
                        App en linea
                    </a>
                    <small v-if="!project.repoUrl && !project.liveUrl" class="project-link-muted">
                        Enlaces aun no publicados
                    </small>
                </div>
            </div>
        </div>
    </PortfolioBlock>

    <ModalForm
        :isVisible="!!selectedProject"
        title="Vista previa del proyecto"
        :loading="false"
        :hideFooter="true"
        size="xl"
        :columns="1"
        @close="closeProjectModal"
    >
        <div class="preview-modal-shell">
            <article class="project-preview-card">
                <div class="card-content">
                    <section class="card-sidebar">
                        <div class="card-logo is-landscape is-clickable" title="Clic para pantalla completa" @click="openLightbox">
                            <transition name="carousel-fade" mode="out-in">
                                <img v-if="currentImage" :key="currentImage" :src="currentImage" alt="Imagen del proyecto" />
                                <div v-else key="empty" class="logo-placeholder">
                                    <Icon name="folder" :size="52" />
                                </div>
                            </transition>
                        </div>

                        <div v-if="carouselImages.length > 1" class="card-carousel-controls">
                            <button
                                v-for="(image, index) in carouselImages"
                                :key="`${image}-${index}`"
                                type="button"
                                class="carousel-dot"
                                :class="{ active: currentImageIndex === index }"
                                :aria-label="`Ir a imagen ${index + 1}`"
                                @click="goToImage(index)"
                            ></button>
                        </div>
                    </section>

                    <div class="card-main">
                        <header class="card-header">
                            <span class="card-type">{{ selectedProject?.type || 'Proyecto' }}</span>
                        </header>

                        <div class="card-heading-block">
                            <h2 class="card-title">{{ selectedProject?.title }}</h2>
                        </div>

                        <div class="card-links" v-if="selectedProject?.repoUrl || selectedProject?.liveUrl">
                            <a
                                v-if="selectedProject?.repoUrl"
                                class="card-link-btn"
                                :href="selectedProject.repoUrl"
                                target="_blank"
                                rel="noopener noreferrer"
                            >
                                <Icon name="link" :size="14" />
                                <span>Repositorio</span>
                            </a>
                            <a
                                v-if="selectedProject?.liveUrl"
                                class="card-link-btn"
                                :href="selectedProject.liveUrl"
                                target="_blank"
                                rel="noopener noreferrer"
                            >
                                <Icon name="external-link" :size="14" />
                                <span>Abrir demo</span>
                            </a>
                        </div>

                        <section v-if="selectedProjectDescription" class="info-panel">
                            <span class="panel-label">DESCRIPCION</span>
                            <div class="card-description-scroll">
                                <div class="card-description">{{ selectedProjectDescription }}</div>
                            </div>
                        </section>

                        <section v-if="selectedProjectTags.length" class="info-panel">
                            <span class="panel-label">ETIQUETAS</span>
                            <div class="card-tags">
                                <span v-for="(tag, index) in selectedProjectTags" :key="`${tag}-${index}`" class="card-tag">{{ tag }}</span>
                            </div>
                        </section>

                        <div class="card-footer-meta">
                            <div class="card-id">VISTA PÚBLICA DEL PROYECTO</div>
                        </div>
                    </div>
                </div>
            </article>
        </div>
    </ModalForm>

    <PortfolioLightbox
        :isVisible="showLightbox"
        :images="carouselImages"
        v-model:index="currentImageIndex"
        :title="selectedProject?.title"
        kicker="Vista previa del proyecto"
        @close="showLightbox = false; startAutoplay()"
    />
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue';
import PortfolioBlock from './PortfolioBlock.vue';
import ModalForm from '@/views/private/admin/components/ModalForm.vue';
import Icon from '@/components/Icon.vue';
import PortfolioLightbox from './PortfolioLightbox.vue';

const props = defineProps({
    projects: {
        type: Array,
        required: true
    }
});

const selectedProject = ref(null);
const currentImageIndex = ref(0);
const isDescriptionExpanded = ref(false);
const showLightbox = ref(false);
let autoplayTimer = null;

function splitLines(value) {
    return String(value || '')
        .split('\n')
        .map(line => line.trim())
        .filter(Boolean);
}

function normalizeTags(item = {}) {
    if (Array.isArray(item.tags)) return item.tags.map(tag => String(tag || '').trim()).filter(Boolean);
    if (typeof item.tagsText === 'string') return item.tagsText.split(',').map(tag => tag.trim()).filter(Boolean);
    if (typeof item.tags === 'string') return item.tags.split(',').map(tag => tag.trim()).filter(Boolean);
    return [];
}

function normalizeImages(item = {}) {
    if (Array.isArray(item.imageUrls)) return item.imageUrls.filter(Boolean);
    if (Array.isArray(item.images)) return item.images.filter(Boolean);
    if (typeof item.imagesText === 'string') return splitLines(item.imagesText);
    if (item.imageUrl || item.image_url) return [item.imageUrl || item.image_url];
    return [];
}

const carouselImages = computed(() => {
    if (!selectedProject.value) return [];
    const images = normalizeImages(selectedProject.value);
    return images.length > 0 ? images : [`https://picsum.photos/seed/project-${selectedProject.value.id}/960/620`];
});

const currentImage = computed(() => {
    if (carouselImages.value.length === 0) return '';
    return carouselImages.value[currentImageIndex.value] || carouselImages.value[0];
});

const selectedProjectTags = computed(() => normalizeTags(selectedProject.value || {}));
const selectedProjectDescription = computed(() => {
    const project = selectedProject.value;
    if (!project) return '';
    return String(project.detailedDescription || project.description || project.detailedDescriptionText || project.descriptionText || '').trim();
});

function openProjectModal(project) {
    selectedProject.value = project;
    currentImageIndex.value = 0;
    isDescriptionExpanded.value = false;
    startAutoplay();
}

function closeProjectModal() {
    selectedProject.value = null;
    currentImageIndex.value = 0;
    isDescriptionExpanded.value = false;
    stopAutoplay();
}

function openLightbox() {
    if (carouselImages.value.length > 0) {
        showLightbox.value = true;
        stopAutoplay();
    }
}

function nextImage() {
    if (carouselImages.value.length <= 1) {
        return;
    }

    currentImageIndex.value = (currentImageIndex.value + 1) % carouselImages.value.length;
}

function goToImage(index) {
    if (index < 0 || index >= carouselImages.value.length) {
        return;
    }

    currentImageIndex.value = index;
    restartAutoplay();
}

function prevImage() {
    if (carouselImages.value.length <= 1) {
        return;
    }

    currentImageIndex.value = (currentImageIndex.value - 1 + carouselImages.value.length) % carouselImages.value.length;
}

function startAutoplay() {
    stopAutoplay();

    if (!selectedProject.value || carouselImages.value.length <= 1) {
        return;
    }

    autoplayTimer = setInterval(() => {
        nextImage();
    }, 5000);
}

function stopAutoplay() {
    if (autoplayTimer) {
        clearInterval(autoplayTimer);
        autoplayTimer = null;
    }
}

function restartAutoplay() {
    if (!selectedProject.value) return;
    startAutoplay();
}

function onKeyDown(event) {
    if (!selectedProject.value) {
        return;
    }

    if (event.key === 'Escape') {
        closeProjectModal();
    }

    if (event.key === 'ArrowRight') {
        nextImage();
    }

    if (event.key === 'ArrowLeft') {
        prevImage();
    }
}

watch(selectedProject, (value) => {
    document.body.style.overflow = value ? 'hidden' : '';
});

onMounted(() => {
    window.addEventListener('keydown', onKeyDown);
});

onBeforeUnmount(() => {
    window.removeEventListener('keydown', onKeyDown);
    document.body.style.overflow = '';
    stopAutoplay();
});
</script>

<style scoped>
.project-list {
    margin-top: 1.25rem;
    display: grid;
    gap: 0.75rem;
}

.project-item {
    position: relative;
    padding: 16px 20px;
    border-radius: 14px;
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(255, 255, 255, 0.06);
    cursor: pointer;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    display: flex;
    flex-direction: column;
    gap: 4px;
}

.project-item:hover {
    background: rgba(255, 255, 255, 0.07);
    border-color: var(--primary);
    transform: translateX(4px);
    box-shadow: 
        -10px 0 30px color-mix(in srgb, var(--primary), transparent 95%),
        inset 0 0 10px rgba(255, 255, 255, 0.03);
}

.project-item strong {
    font-size: 1.1rem;
    color: var(--text-primary);
    font-weight: 700;
}

.project-item p {
    margin: 0;
    font-size: 0.9rem;
    color: var(--text-secondary);
    line-height: 1.5;
    white-space: pre-wrap;
}

.project-type-chip {
    display: inline-flex;
    margin-top: 8px;
    font-size: 0.65rem;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: var(--primary);
    opacity: 0.8;
}

.project-open-hint {
    font-size: 0.72rem;
    color: var(--text-tertiary);
    margin-top: 8px;
    font-weight: 500;
}

.project-links {
    margin-top: 12px;
    display: flex;
    gap: 10px;
}

.project-link {
    font-size: 0.72rem;
    font-weight: 700;
    color: var(--text-secondary);
    text-decoration: none;
    padding: 4px 12px;
    border-radius: 8px;
    background: var(--bg-secondary);
    border: 1px solid var(--border-color);
    transition: all 0.2s;

    &:hover {
        background: var(--primary);
        color: var(--bg-primary);
        border-color: var(--primary);
    }
}

.carousel-fade-enter-active,
.carousel-fade-leave-active {
    transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
}

.carousel-fade-enter-from,
.carousel-fade-leave-to {
    opacity: 0;
    transform: scale(1.05);
    filter: blur(10px);
}

.carousel-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: rgba(255, 255, 255, 0.2);
    border: none;
    padding: 0;
    cursor: pointer;
    transition: all 0.3s;

    &.active {
        width: 24px;
        background: var(--primary);
        border-radius: 4px;
    }
}


.preview-modal-shell {
    padding: 0;
    overflow: hidden;
}
</style>
