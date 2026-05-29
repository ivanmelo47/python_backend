<template>
    <PortfolioBlock kicker="Trabajos" title="Historial laboral" class="jobs-block reveal reveal-delay-3">
        <ul class="timeline-list">
            <li
                v-for="job in jobs"
                :key="job.id"
                class="timeline-item"
                role="button"
                tabindex="0"
                @click="openJobModal(job)"
                @keydown.enter.prevent="openJobModal(job)"
                @keydown.space.prevent="openJobModal(job)"
            >
                <div>
                    <strong>{{ job.role }}</strong>
                    <p>{{ job.company }}</p>
                </div>
                <span>{{ formatPeriod(job) }}</span>
            </li>
        </ul>
    </PortfolioBlock>

    <ModalForm
        :isVisible="!!selectedJob"
        title="Vista previa del trabajo"
        :loading="false"
        :hideFooter="true"
        size="xl"
        :columns="1"
        @close="closeJobModal"
    >
        <div class="preview-modal-shell">
            <article class="job-preview-card">
                <div class="card-content">
                    <section class="card-sidebar">
                        <div class="card-logo is-landscape is-clickable" title="Clic para pantalla completa" @click="openLightbox">
                            <transition name="carousel-fade" mode="out-in">
                                <img v-if="currentImage" :key="currentImage" :src="currentImage" alt="Logo de la empresa" />
                                <div v-else key="empty" class="logo-placeholder">
                                    <Icon name="briefcase" :size="52" />
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
                            <span class="card-period">{{ formatPeriod(selectedJob) }}</span>
                            <span v-if="selectedJob?.isCurrent" class="current-badge">ACTUAL</span>
                        </header>

                        <div class="card-heading-block">
                            <h2 class="card-title">{{ selectedJob?.role }}</h2>
                            <h3 class="card-company">{{ selectedJob?.company }}</h3>
                        </div>

                        <div class="card-links" v-if="selectedJob?.companyUrl">
                            <a
                                class="card-link-btn"
                                :href="selectedJob.companyUrl"
                                target="_blank"
                                rel="noopener noreferrer"
                            >
                                <Icon name="external-link" :size="14" />
                                <span>Sitio web de la empresa</span>
                            </a>
                        </div>

                        <section v-if="selectedJobDescription" class="info-panel">
                            <span class="panel-label">RESEÑA Y FUNCIONES</span>
                            <div class="card-description-scroll">
                                <div class="card-description">{{ selectedJobDescription }}</div>
                            </div>
                        </section>

                        <section v-if="selectedJobTags.length" class="info-panel">
                            <span class="panel-label">TECNOLOGÍAS / COMPETENCIAS</span>
                            <div class="card-tags">
                                <span v-for="(tag, index) in selectedJobTags" :key="`${tag}-${index}`" class="card-tag">{{ tag }}</span>
                            </div>
                        </section>

                        <div class="card-footer-meta">
                            <div class="card-id">REGISTRO PROFESIONAL</div>
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
        :title="selectedJob?.role"
        kicker="Vista previa del trabajo"
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
    jobs: {
        type: Array,
        required: true
    }
});

const selectedJob = ref(null);
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
    if (!selectedJob.value) return [];
    const images = normalizeImages(selectedJob.value);
    return images.length > 0 ? images : [`https://picsum.photos/seed/job-${selectedJob.value.id}/960/620`];
});

const currentImage = computed(() => {
    if (carouselImages.value.length === 0) return '';
    return carouselImages.value[currentImageIndex.value] || carouselImages.value[0];
});

const selectedJobTags = computed(() => normalizeTags(selectedJob.value || {}));
const selectedJobDescription = computed(() => String(selectedJob.value?.description || '').trim());

function formatPeriod(job) {
    if (!job) return '--';
    const start = job.startDate || '';
    const end = job.isCurrent ? 'Actual' : (job.endDate || '');

    if (!start && !end) return job.period || '--';
    if (!start) return end || '--';
    if (!end) return start;
    return `${start} — ${end}`;
}

function openJobModal(job) {
    selectedJob.value = job;
    currentImageIndex.value = 0;
    isDescriptionExpanded.value = false;
    startAutoplay();
}

function closeJobModal() {
    selectedJob.value = null;
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
    if (carouselImages.value.length <= 1) return;
    currentImageIndex.value = (currentImageIndex.value + 1) % carouselImages.value.length;
}

function prevImage() {
    if (carouselImages.value.length <= 1) return;
    currentImageIndex.value = (currentImageIndex.value - 1 + carouselImages.value.length) % carouselImages.value.length;
}

function goToImage(index) {
    if (index < 0 || index >= carouselImages.value.length) return;
    currentImageIndex.value = index;
    restartAutoplay();
}

function startAutoplay() {
    stopAutoplay();
    if (!selectedJob.value || carouselImages.value.length <= 1) return;

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
    if (!selectedJob.value) return;
    startAutoplay();
}

function onKeyDown(event) {
    if (!selectedJob.value) return;
    if (event.key === 'Escape') closeJobModal();
    if (event.key === 'ArrowRight') nextImage();
    if (event.key === 'ArrowLeft') prevImage();
}

watch(selectedJob, (value) => {
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
.timeline-list {
    margin-top: 1.25rem;
    display: grid;
    gap: 0.75rem;
}

.timeline-item {
    position: relative;
    padding: 16px 20px;
    border-radius: 14px;
    background: var(--bg-primary);
    border: 1px solid var(--border-color);
    cursor: pointer;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 12px;
}

.timeline-item:hover {
    background: var(--bg-secondary);
    border-color: var(--primary);
    transform: translateX(4px);
}

.timeline-item strong {
    display: block;
    font-size: 1.05rem;
    color: var(--text-primary);
    font-weight: 700;
}

.timeline-item p {
    margin: 2px 0 0;
    font-size: 0.88rem;
    color: var(--text-secondary);
}

.timeline-item span {
    font-size: 0.75rem;
    font-weight: 700;
    color: var(--primary);
    background: color-mix(in srgb, var(--primary), transparent 90%);
    padding: 4px 10px;
    border-radius: 6px;
    white-space: nowrap;
}

.carousel-fade-enter-active,
.carousel-fade-leave-active {
    transition: all 0.5s ease;
}

.carousel-fade-enter-from,
.carousel-fade-leave-to {
    opacity: 0;
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
        width: 20px;
        background: var(--primary);
        border-radius: 4px;
    }
}

@media (max-width: 640px) {
    .timeline-item {
        flex-direction: column;
        align-items: flex-start;
        gap: 8px;
    }
}
</style>
