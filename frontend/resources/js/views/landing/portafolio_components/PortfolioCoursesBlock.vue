<template>
    <PortfolioBlock kicker="Cursos" title="Actualizacion continua" class="courses-block reveal reveal-delay-4">
        <ul class="course-list">
            <li
                v-for="course in courses"
                :key="course.id"
                class="course-item"
                role="button"
                tabindex="0"
                @click="openCourseModal(course)"
                @keydown.enter.prevent="openCourseModal(course)"
                @keydown.space.prevent="openCourseModal(course)"
            >
                <strong>{{ course.title }}</strong>
                <p>{{ course.provider }}</p>
                <span>{{ formatYear(course) }}</span>
                <small class="course-open-hint">Click para ver detalle</small>
            </li>
        </ul>
    </PortfolioBlock>

    <ModalForm
        :isVisible="!!selectedCourse"
        title="Vista previa del curso"
        :loading="false"
        :hideFooter="true"
        size="xl"
        :columns="1"
        @close="closeCourseModal"
    >
        <div class="preview-modal-shell">
            <article class="course-preview-card">
                <div class="card-content">
                    <section class="card-sidebar">
                        <div class="card-logo is-landscape is-clickable" title="Clic para pantalla completa" @click="openLightbox">
                            <transition name="carousel-fade" mode="out-in">
                                <img v-if="currentImage" :key="currentImage" :src="currentImage" alt="Imagen del curso" />
                                <div v-else key="empty" class="logo-placeholder">
                                    <Icon name="book-open" :size="52" />
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
                            <span class="card-period">{{ formatYear(selectedCourse) }}</span>
                        </header>

                        <div class="card-heading-block">
                            <h2 class="card-title">{{ selectedCourse?.title }}</h2>
                            <h3 class="card-subtitle">{{ selectedCourse?.provider }}</h3>
                        </div>

                        <div class="card-links" v-if="selectedCourse?.courseUrl">
                            <a
                                class="card-link-btn"
                                :href="selectedCourse.courseUrl"
                                target="_blank"
                                rel="noopener noreferrer"
                            >
                                <Icon name="external-link" :size="14" />
                                <span>Página del curso</span>
                            </a>
                        </div>

                        <section v-if="selectedCourseDescription" class="info-panel">
                            <span class="panel-label">RESUMEN DEL CURSO</span>
                            <div class="card-description-scroll">
                                <div class="card-description">{{ selectedCourseDescription }}</div>
                            </div>
                        </section>

                        <section v-if="selectedCourseTags.length" class="info-panel">
                            <span class="panel-label">HABILIDADES / TEMAS</span>
                            <div class="card-tags">
                                <span v-for="(tag, index) in selectedCourseTags" :key="`${tag}-${index}`" class="card-tag">{{ tag }}</span>
                            </div>
                        </section>

                        <section v-if="selectedCourseCertificates.length" class="info-panel">
                            <span class="panel-label">CERTIFICACIONES Y LOGROS</span>
                            <div class="certificate-links">
                                <button
                                    v-for="(certificate, index) in selectedCourseCertificates"
                                    :key="`${certificate}-${index}`"
                                    type="button"
                                    class="certificate-chip"
                                    :class="{ active: currentCertificateIndex === index }"
                                    @click="selectCertificate(index)"
                                >
                                    <Icon name="file-text" :size="12" />
                                    <span>Certificado {{ index + 1 }}</span>
                                </button>
                            </div>

                            <a
                                v-if="currentCertificateUrl"
                                class="card-link-btn"
                                :href="currentCertificateUrl"
                                target="_blank"
                                rel="noopener noreferrer"
                                style="margin-bottom: 15px;"
                            >
                                <Icon name="download" :size="14" />
                                <span>Ver/Descargar PDF</span>
                            </a>

                        </section>

                        <div class="card-footer-meta">
                            <div class="card-id">REGISTRO DE FORMACIÓN CONTINUA</div>
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
        :title="selectedCourse?.title"
        kicker="Vista previa del curso"
        @close="showLightbox = false"
    />
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue';
import PortfolioBlock from './PortfolioBlock.vue';
import ModalForm from '@/views/private/admin/components/ModalForm.vue';
import Icon from '@/components/Icon.vue';
import PortfolioLightbox from './PortfolioLightbox.vue';

const props = defineProps({
    courses: {
        type: Array,
        required: true
    }
});

const selectedCourse = ref(null);
const currentImageIndex = ref(0);
const currentCertificateIndex = ref(0);
const isDescriptionExpanded = ref(false);
const showLightbox = ref(false);
let autoplayTimer = null;

function splitLines(value) {
    return String(value || '')
        .split('\n')
        .map(line => line.trim())
        .filter(Boolean);
}

function normalizeImages(item = {}) {
    if (Array.isArray(item.imageUrls)) return item.imageUrls.filter(Boolean);
    if (Array.isArray(item.images)) return item.images.filter(Boolean);
    if (typeof item.imagesText === 'string') return splitLines(item.imagesText);
    if (item.imageUrl || item.image_url) return [item.imageUrl || item.image_url];
    return [];
}

function normalizeCertificates(item = {}) {
    if (Array.isArray(item.certificateUrls)) return item.certificateUrls.filter(Boolean);
    if (Array.isArray(item.certificate_urls)) return item.certificate_urls.filter(Boolean);
    if (typeof item.certificateUrl === 'string' && item.certificateUrl.trim()) return [item.certificateUrl.trim()];
    if (typeof item.certificate_url === 'string' && item.certificate_url.trim()) return [item.certificate_url.trim()];
    return [];
}

function normalizeTags(item = {}) {
    if (Array.isArray(item.tags)) return item.tags.map(tag => String(tag || '').trim()).filter(Boolean);
    if (typeof item.tagsText === 'string') return item.tagsText.split(',').map(tag => tag.trim()).filter(Boolean);
    if (typeof item.tags === 'string') return item.tags.split(',').map(tag => tag.trim()).filter(Boolean);
    return [];
}

const carouselImages = computed(() => {
    if (!selectedCourse.value) return [];
    const images = normalizeImages(selectedCourse.value);
    return images.length > 0 ? images : [`https://picsum.photos/seed/course-${selectedCourse.value.id}/960/620`];
});

const currentImage = computed(() => {
    if (!carouselImages.value.length) return '';
    return carouselImages.value[currentImageIndex.value] || carouselImages.value[0];
});
const selectedCourseCertificates = computed(() => normalizeCertificates(selectedCourse.value || {}));
const selectedCourseTags = computed(() => normalizeTags(selectedCourse.value || {}));

const selectedCourseDescription = computed(() => {
    const course = selectedCourse.value;
    if (!course) return '';
    return String(course.description || course.descriptionText || '').trim();
});
const currentCertificateUrl = computed(() => selectedCourseCertificates.value[currentCertificateIndex.value] || selectedCourseCertificates.value[0] || '');

function formatYear(item) {
    if (!item) return '--';
    return item.year || item.period || '--';
}

function openCourseModal(course) {
    selectedCourse.value = course;
    currentImageIndex.value = 0;
    currentCertificateIndex.value = 0;
    isDescriptionExpanded.value = false;
    startAutoplay();
}

function openLightbox() {
    showLightbox.value = true;
}

function closeCourseModal() {
    selectedCourse.value = null;
    currentImageIndex.value = 0;
    currentCertificateIndex.value = 0;
    isDescriptionExpanded.value = false;
    stopAutoplay();
}

function nextImage() {
    if (carouselImages.value.length <= 1) return;
    currentImageIndex.value = (currentImageIndex.value + 1) % carouselImages.value.length;
}

function goToImage(index) {
    if (index < 0 || index >= carouselImages.value.length) return;
    currentImageIndex.value = index;
    restartAutoplay();
}

function selectCertificate(index) {
    if (index < 0 || index >= selectedCourseCertificates.value.length) return;
    currentCertificateIndex.value = index;
}

function startAutoplay() {
    stopAutoplay();
    if (!selectedCourse.value || carouselImages.value.length <= 1) return;

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
    if (!selectedCourse.value) return;
    startAutoplay();
}

function onKeyDown(event) {
    if (!selectedCourse.value) return;
    if (event.key === 'Escape') closeCourseModal();
    if (event.key === 'ArrowRight') nextImage();
    if (event.key === 'ArrowLeft') {
        if (carouselImages.value.length <= 1) return;
        currentImageIndex.value = (currentImageIndex.value - 1 + carouselImages.value.length) % carouselImages.value.length;
    }
}

watch(selectedCourse, (value) => {
    document.body.style.overflow = value ? 'hidden' : '';
});

watch(selectedCourseCertificates, (items) => {
    if (currentCertificateIndex.value >= items.length) {
        currentCertificateIndex.value = 0;
    }
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
.course-list {
    margin: 0.9rem 0 0;
    list-style: none;
    padding: 0;
    display: grid;
    gap: 0.6rem;
}

.course-item {
    padding: 0.72rem 0.8rem;
    border-radius: 0.72rem;
    border: 1px solid var(--border-color);
    background: var(--bg-primary);
    cursor: pointer;
    transition: border-color 0.2s ease, transform 0.2s ease;
}

.course-item:hover,
.course-item:focus-visible {
    transform: translateY(-2px);
    border-color: var(--primary);
    outline: none;
}

.course-item strong {
    display: block;
    margin-bottom: 0.25rem;
}

.course-item p {
    margin: 0;
}

.course-item span {
    display: inline-flex;
    margin-top: 0.45rem;
    font-size: 0.76rem;
    color: var(--text-tertiary);
}

.course-open-hint {
    display: block;
    margin-top: 0.5rem;
    font-size: 0.75rem;
    color: var(--text-tertiary);
}


.certificate-links {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin-bottom: 12px;
}

.certificate-chip {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 6px 12px;
    border-radius: 999px;
    background: var(--bg-primary);
    border: 1px solid var(--border-color);
    color: var(--text-secondary);
    font-size: 0.75rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s;

    &:hover {
        background: var(--bg-secondary);
        border-color: var(--primary);
    }

    &.active {
        background: color-mix(in srgb, var(--primary), transparent 85%);
        border-color: var(--primary);
        color: var(--primary);
    }
}


.preview-modal-shell {
    padding: 0;
    overflow: hidden;
}
</style>
