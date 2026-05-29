<template>
    <article class="editor-card">
        <Table
            title="Cursos"
            :columns="columns"
            :rows="courses"
            paginationMode="client"
            :showRefresh="false"
            searchPlaceholder="Buscar curso..."
            cardTitleTemplate="{title}"
            v-model:search-query="searchQuery"
            @row-click="openPreviewCard"
        >
            <template #header-actions>
                <button type="button" class="btn-solid" @click="openCreateModal" style="display: flex; align-items: center; gap: 6px;">
                    <Icon name="plus" :size="18" />
                    <span>NUEVO</span>
                </button>
            </template>

            <template #cell-logo="{ row }">
                <div class="thumbnail-preview is-landscape is-clickable" @click.stop="openLightboxViewer(row)" title="Clic para ampliar">
                    <img v-if="getPrimaryImage(row)" :src="getPrimaryImage(row)" alt="Imagen del curso" />
                    <Icon v-else name="collectionPlayFill" :size="16" />
                </div>
            </template>

            <template #cell-info="{ row }">
                <div class="course-info-cell">
                    <strong>{{ row.title }}</strong>
                    <span>{{ row.provider }}</span>
                </div>
            </template>

            <template #cell-year_display="{ row }">
                <span class="period-tag">{{ formatYear(row) }}</span>
            </template>

            <template #cell-certificates="{ row }">
                <span class="period-tag">{{ getCertificateCount(row) }} PDF</span>
            </template>

            <template #cell-actions="{ row }">
                <button class="dropdown-item" @click.stop="openEditModal(row)">
                    <Icon name="pencil" :size="16" /> Editar
                </button>
                <button class="dropdown-item text-danger" @click.stop="removeCourse(row)">
                    <Icon name="trash" :size="16" /> Eliminar
                </button>
            </template>
        </Table>

        <ModalForm
            :isVisible="showFormModal"
            :title="editingIndex > -1 ? 'Editar Curso' : 'Nuevo Curso'"
            submitLabel="Guardar"
            :loading="isPersisting || isUploading || isUploadingCertificate"
            @close="closeFormModal"
            @submit="submitForm"
            size="lg"
            :columns="2"
        >
            <template #header-icon>
                <Icon name="book-open" :size="20" />
            </template>

            <ModalField label="Título" :required="true" :span="1">
                <input v-model.trim="formData.title" type="text" maxlength="120" placeholder="Ej: Escalabilidad y performance web" required />
            </ModalField>

            <ModalField label="Proveedor" :required="true" :span="1">
                <input v-model.trim="formData.provider" type="text" maxlength="120" placeholder="Ej: Plataforma Online Pro" required />
            </ModalField>

            <ModalField label="Año" :required="true" :span="1">
                <input v-model.trim="formData.year" type="text" maxlength="16" placeholder="Ej: 2024" required />
            </ModalField>

            <ModalField label="URL del sitio del curso" :span="1">
                <input v-model.trim="formData.courseUrl" type="url" maxlength="400" placeholder="https://www.plataforma.com/curso" />
            </ModalField>

            <ModalField label="Descripción" :span="2">
                <textarea v-model.trim="formData.description" rows="4" maxlength="1500" placeholder="Resumen del curso, enfoque, resultados, etc."></textarea>
            </ModalField>

            <ModalField label="Etiquetas (separadas por coma)" :span="2">
                <input v-model.trim="formData.tagsText" type="text" maxlength="320" placeholder="Vue 3, Laravel, Backend, DevOps" />
            </ModalField>

            <ModalField label="Imágenes del curso" :span="2">
                <div class="course-logo-uploader">
                    <div class="logo-preview-area is-landscape is-clickable" @click="openLightboxViewer(formData)" title="Clic para vista previa">
                        <img v-if="getPrimaryImage(formData)" :src="getPrimaryImage(formData)" alt="Logo preview" />
                        <Icon v-else name="eye" :size="24" />
                    </div>

                    <div class="logo-uploader-actions">
                        <button type="button" class="btn" @click="openImagePicker" :disabled="isUploading">
                            {{ formData.images.length ? 'Agregar imagen' : 'Subir imagen' }}
                        </button>
                        <button v-if="formData.images.length" type="button" class="btn btn-outline" @click="clearImages">Limpiar todas</button>
                        <small class="field-help">PNG, JPG o WEBP. Puedes subir varias imágenes para el carrusel.</small>
                    </div>

                    <div v-if="formData.images.length" class="uploaded-images-grid">
                        <button
                            v-for="(image, index) in formData.images"
                            :key="`${image}-${index}`"
                            type="button"
                            class="uploaded-image-item"
                            @click="openLightboxViewer(formData, index)"
                            :title="`Imagen ${index + 1}`"
                        >
                            <img :src="image" :alt="`Imagen ${index + 1}`" />
                            <span class="uploaded-image-index">{{ index + 1 }}</span>
                            <span class="uploaded-image-remove" @click.stop="removeImageAt(index)">x</span>
                        </button>
                    </div>

                    <input ref="imageInputRef" type="file" accept="image/*" class="hidden-input" @change="handleImageUpload" />
                </div>
            </ModalField>

            <ModalField label="Certificados PDF" :span="2">
                <div class="media-uploader">
                    <div class="uploader-actions">
                        <button type="button" class="btn" @click="openCertificatePicker" :disabled="isUploadingCertificate">
                            {{ formData.certificateUrls.length ? 'Agregar PDF' : 'Subir PDF' }}
                        </button>
                        <button v-if="formData.certificateUrls.length" type="button" class="btn btn-outline" @click="clearCertificates">Limpiar todos</button>
                        <small class="field-help">Sube uno o varios certificados PDF para mostrarlos públicamente en la ficha del curso.</small>
                    </div>

                    <div v-if="formData.certificateUrls.length" class="certificate-list">
                        <button
                            v-for="(certificate, index) in formData.certificateUrls"
                            :key="`${certificate}-${index}`"
                            type="button"
                            class="certificate-item"
                            @click="openAsset(certificate)"
                        >
                            <span class="certificate-badge">PDF {{ index + 1 }}</span>
                            <span class="certificate-url">{{ shortUrlLabel(certificate) }}</span>
                            <span class="certificate-remove" @click.stop="removeCertificateAt(index)">x</span>
                        </button>
                    </div>

                    <input ref="certificateInputRef" type="file" accept="application/pdf" class="hidden-input" @change="handleCertificateUpload" />
                </div>
            </ModalField>
        </ModalForm>

        <teleport to="body">
            <div v-if="showCropModal" class="crop-modal-overlay" @click="closeCropModal">
                <article class="crop-modal premium-modal" @click.stop>
                    <header class="crop-modal-header">
                        <div class="header-info">
                            <Icon name="image" :size="20" class="header-icon" />
                            <div>
                                <h3>Recortar Portada</h3>
                                <p>Ajusta el encuadre final para el curso.</p>
                            </div>
                        </div>
                        <button type="button" class="close-btn-ghost" @click="closeCropModal">
                            <Icon name="x" :size="20" />
                        </button>
                    </header>

                    <div class="crop-modal-content">
                        <div class="crop-main-area">
                            <cropper
                                ref="cropperRef"
                                class="logo-cropper-canvas"
                                :src="cropperSource"
                                :stencil-props="{ aspectRatio: 16 / 10 }"
                                @change="onCropperChange"
                            />
                        </div>

                        <aside class="crop-side-pane">
                            <div class="preview-section">
                                <span class="section-label">VISTA PREVIA</span>
                                <div class="live-preview-box">
                                    <div class="preview-container is-landscape">
                                        <img v-if="previewUrl" :src="previewUrl" alt="Preview" />
                                        <div v-else class="preview-placeholder">
                                            <Icon name="image" :size="32" />
                                        </div>
                                    </div>
                                    <span class="preview-hint">Asi se vera en formato horizontal</span>
                                </div>
                            </div>
                        </aside>
                    </div>

                    <footer class="crop-modal-footer">
                        <button type="button" class="btn btn-ghost" @click="closeCropModal">Cancelar</button>
                        <button type="button" class="btn btn-primary-gradient" @click="applyCrop" :disabled="isUploading">
                            <Icon v-if="isUploading" name="refresh" class="spin" :size="18" />
                            <span>{{ isUploading ? 'Procesando...' : 'Guardar Cambios' }}</span>
                        </button>
                    </footer>
                </article>
            </div>
        </teleport>

        <ModalForm
            :isVisible="showPreviewCard"
            title="Vista previa del curso"
            :loading="false"
            :hideFooter="true"
            size="xl"
            :columns="1"
            @close="closePreviewCard"
        >
            <div class="preview-modal-shell">
                <article class="course-preview-card">
                    <div class="card-content">
                        <section class="card-sidebar">
                            <div class="card-logo is-landscape is-clickable" @click="openLightboxViewer()" title="Clic para pantalla completa">
                                <transition name="carousel-fade" mode="out-in">
                                    <img v-if="currentPreviewImage" :key="currentPreviewImage" :src="currentPreviewImage" alt="Imagen del curso" />
                                    <div v-else key="empty" class="logo-placeholder">
                                        <Icon name="collectionPlayFill" :size="48" />
                                    </div>
                                </transition>
                            </div>

                            <div v-if="previewCarouselImages.length > 1" class="card-carousel-controls">
                                <button
                                    v-for="(image, index) in previewCarouselImages"
                                    :key="`${image}-${index}`"
                                    type="button"
                                    class="carousel-dot"
                                    :class="{ active: previewImageIndex === index }"
                                    :aria-label="`Ir a imagen ${index + 1}`"
                                    @click="goToPreviewImage(index)"
                                ></button>
                            </div>
                        </section>

                        <div class="card-main">
                            <header class="card-header">
                                <span class="card-period">{{ formatYear(selectedCourse) }}</span>
                            </header>

                            <div class="card-heading-block">
                                <h2 class="card-title">{{ selectedCourse?.title }}</h2>
                                <h3 class="card-institution">{{ selectedCourse?.provider }}</h3>
                            </div>

                            <a
                                v-if="selectedCourse?.courseUrl"
                                class="card-link-btn"
                                :href="selectedCourse.courseUrl"
                                target="_blank"
                                rel="noopener noreferrer"
                            >
                                <Icon name="link" :size="14" />
                                <span>Abrir sitio web</span>
                            </a>

                            <section v-if="selectedCourseDescription" class="info-panel">
                                <span class="panel-label">DESCRIPCION</span>
                                <div class="card-description-wrap" :class="{ 'is-collapsed': showCourseDescriptionToggle && !isCourseDescriptionExpanded, expanded: isCourseDescriptionExpanded }">
                                    <div class="card-description">{{ selectedCourseDescription }}</div>
                                </div>
                                <button
                                    v-if="showCourseDescriptionToggle"
                                    type="button"
                                    class="description-toggle"
                                    @click="isCourseDescriptionExpanded = !isCourseDescriptionExpanded"
                                >
                                    {{ isCourseDescriptionExpanded ? 'Ver menos' : 'Ver mas' }}
                                </button>
                            </section>

                            <section v-if="selectedCourseTags.length" class="info-panel">
                                <span class="panel-label">ETIQUETAS</span>
                                <div class="card-tags">
                                    <span v-for="(tag, index) in selectedCourseTags" :key="`${tag}-${index}`" class="card-tag">{{ tag }}</span>
                                </div>
                            </section>

                            <section v-if="selectedCourseCertificates.length" class="info-panel">
                                <span class="panel-label">CERTIFICADOS PDF</span>
                                <div class="certificate-links">
                                    <a
                                        v-for="(certificate, index) in selectedCourseCertificates"
                                        :key="`${certificate}-${index}`"
                                        class="card-link-btn"
                                        :href="certificate"
                                        target="_blank"
                                        rel="noopener noreferrer"
                                    >
                                        <Icon name="fileEarmarkPdf" :size="14" />
                                        <span>Certificado {{ index + 1 }}</span>
                                    </a>
                                </div>
                            </section>

                            <div class="card-footer-meta">
                                <div class="card-id">EJEMPLO DE VISTA PUBLICA</div>
                            </div>
                        </div>
                    </div>
                </article>
            </div>
        </ModalForm>
    </article>

    <PortfolioLightbox
        :isVisible="showLightboxViewer"
        :images="lightboxImages"
        v-model:index="previewImageIndex"
        :title="lightboxTitle"
        kicker="Vista previa del curso"
        @close="showLightboxViewer = false"
    />
</template>

<script setup>
import { computed, onBeforeUnmount, ref, watch } from 'vue';
import { useAlert } from '@/composables/useAlert';
import { Cropper } from 'vue-advanced-cropper';
import 'vue-advanced-cropper/dist/style.css';
import { api } from '@/services/api';

import Table from '@/views/private/admin/components/Table.vue';
import ModalForm from '@/views/private/admin/components/ModalForm.vue';
import ModalField from '@/views/private/admin/components/ModalField.vue';
import Icon from '@/components/Icon.vue';
import PortfolioLightbox from '@/views/landing/portafolio_components/PortfolioLightbox.vue';

const props = defineProps({
    courses: { type: Array, required: true },
    portfolioItem: { type: Object, required: true },
    allBlocks: { type: Object, required: true }
});

const emit = defineEmits(['request-save', 'portfolio-synced']);

const alert = useAlert();
const searchQuery = ref('');
const isPersisting = ref(false);
const isUploadingCertificate = ref(false);
const certificateInputRef = ref(null);
const showPreviewCard = ref(false);

const columns = [
    { key: 'actions', label: 'ACCIONES', headerClass: 'compact', cellClass: 'compact' },
    { key: 'logo', label: 'LOGO', cellClass: 'compact text-center' },
    { key: 'info', label: 'CURSO' },
    { key: 'year_display', label: 'AÑO', cellClass: 'compact' },
    { key: 'certificates', label: 'PDF', cellClass: 'compact' }
];

const showFormModal = ref(false);
const editingIndex = ref(-1);

const isUploading = ref(false);
const showCropModal = ref(false);
const imageInputRef = ref(null);
const cropperRef = ref(null);
const cropperSource = ref(null);
const previewUrl = ref(null);



const selectedCourse = ref(null);
const previewImageIndex = ref(0);
const isCourseDescriptionExpanded = ref(false);
const showLightboxViewer = ref(false);
const lightboxImages = ref([]);
const lightboxTitle = ref('');
let previewAutoplayTimer = null;

const initialForm = {
    title: '',
    provider: '',
    year: '',
    courseUrl: '',
    description: '',
    tags: [],
    tagsText: '',
    images: [],
    imagesText: '',
    certificateUrls: [],
    certificateUrl: ''
};

const formData = ref({ ...initialForm });

function splitLines(value) {
    return String(value || '')
        .split('\n')
        .map(line => line.trim())
        .filter(Boolean);
}

function normalizeImages(item = {}) {
    if (Array.isArray(item.imageUrls) && item.imageUrls.length > 0) return item.imageUrls.filter(Boolean);
    if (Array.isArray(item.images) && item.images.length > 0) return item.images.filter(Boolean);
    if (Array.isArray(item.image_urls) && item.image_urls.length > 0) return item.image_urls.filter(Boolean);
    if (typeof item.imagesText === 'string' && item.imagesText.trim()) return splitLines(item.imagesText);
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

function getPrimaryImage(item = {}) {
    const images = normalizeImages(item);
    return images[0] || '';
}

function getCertificateCount(item = {}) {
    return normalizeCertificates(item).length;
}

const previewCarouselImages = computed(() => {
    if (!selectedCourse.value) return [];
    const images = normalizeImages(selectedCourse.value);
    return images.length > 0 ? images : [`https://picsum.photos/seed/course-${selectedCourse.value.id}/960/620`];
});

const currentPreviewImage = computed(() => {
    if (!previewCarouselImages.value.length) return '';
    return previewCarouselImages.value[previewImageIndex.value] || previewCarouselImages.value[0];
});

const selectedCourseTags = computed(() => normalizeTags(selectedCourse.value || {}));
const selectedCourseCertificates = computed(() => normalizeCertificates(selectedCourse.value || {}));
const selectedCourseDescription = computed(() => String(selectedCourse.value?.description || '').trim());
const showCourseDescriptionToggle = computed(() => selectedCourseDescription.value.length > 260);

function formatYear(item) {
    if (!item) return '--';
    return item.year || item.period || '--';
}

function openCreateModal() {
    editingIndex.value = -1;
    formData.value = { ...initialForm };
    showFormModal.value = true;
}

function openEditModal(row) {
    const realIdx = props.courses.indexOf(row);
    if (realIdx === -1) return;

    const images = normalizeImages(row);
    const certificates = normalizeCertificates(row);
    const tags = normalizeTags(row);

    editingIndex.value = realIdx;
    formData.value = {
        ...initialForm,
        ...row,
        year: row.year || row.period || '',
        courseUrl: row.courseUrl || row.course_url || '',
        images,
        imagesText: images.join('\n'),
        certificateUrls: certificates,
        certificateUrl: certificates[0] || '',
        tags,
        tagsText: tags.join(', ')
    };

    showFormModal.value = true;
}

function closeFormModal() {
    showFormModal.value = false;
    editingIndex.value = -1;
    formData.value = { ...initialForm };
}

async function submitForm() {
    const images = normalizeImages(formData.value);
    const certificates = normalizeCertificates(formData.value);
    const tags = normalizeTags({ tags: formData.value.tagsText || formData.value.tags });

    const payload = {
        ...formData.value,
        year: formData.value.year || '',
        courseUrl: formData.value.courseUrl || '',
        images,
        imagesText: images.join('\n'),
        imageUrls: images,
        imageUrl: images[0] || '',
        certificateUrls: certificates,
        certificateUrl: certificates[0] || '',
        tags,
        tagsText: tags.join(', ')
    };

    if (editingIndex.value > -1) {
        const id = props.courses[editingIndex.value].id;
        props.courses.splice(editingIndex.value, 1, { ...payload, id });
        alert.toast.success('Editado', 'Curso actualizado con éxito.');
    } else {
        props.courses.push({ ...payload, id: Date.now() });
        alert.toast.success('Creado', 'Curso registrado con éxito.');
    }

    await persistPortfolioChanges();
    emit('request-save');
    closeFormModal();
}

async function removeCourse(row) {
    const realIdx = props.courses.indexOf(row);
    if (realIdx === -1) return;

    if (confirm('¿Estás seguro de eliminar este curso?')) {
        props.courses.splice(realIdx, 1);
        await persistPortfolioChanges();
        emit('request-save');
        alert.toast.success('Eliminado', 'Curso eliminado con éxito.');
    }
}

async function persistPortfolioChanges() {
    const portfolioId = props.portfolioItem?.id ?? props.portfolioItem?.value?.id;
    if (!portfolioId || isPersisting.value) return;

    isPersisting.value = true;
    try {
        const response = await api.portfolios.updatePortfolio(portfolioId, {
            blocks: JSON.parse(JSON.stringify(props.allBlocks || {})),
        });

        if (response?.data?.data) {
            emit('portfolio-synced', response.data.data);
        }
    } catch (error) {
        alert.toast.error('Error', error?.response?.data?.message || 'No se pudo sincronizar el curso.');
    } finally {
        isPersisting.value = false;
    }
}

function openImagePicker() {
    imageInputRef.value?.click();
}

function openCertificatePicker() {
    certificateInputRef.value?.click();
}

function openLightboxViewer(item = null, index = 0) {
    if (!item) {
        // Fallback to active preview if no item passed
        if (!selectedCourse.value) return;
        lightboxImages.value = normalizeImages(selectedCourse.value);
        lightboxTitle.value = selectedCourse.value.title;
    } else {
        lightboxImages.value = normalizeImages(item);
        lightboxTitle.value = item.title;
    }

    if (lightboxImages.value.length === 0) return;
    previewImageIndex.value = Math.max(0, Math.min(index, lightboxImages.value.length - 1));
    showLightboxViewer.value = true;
}

function shortUrlLabel(url) {
    if (!url) return '';
    return url.length > 42 ? `${url.slice(0, 20)}...${url.slice(-18)}` : url;
}

function clearImages() {
    formData.value.images = [];
    formData.value.imagesText = '';
}

function clearCertificates() {
    formData.value.certificateUrls = [];
    formData.value.certificateUrl = '';
}

function removeImageAt(index) {
    if (index < 0 || index >= formData.value.images.length) return;
    formData.value.images.splice(index, 1);
    formData.value.imagesText = formData.value.images.join('\n');
}

function removeCertificateAt(index) {
    if (index < 0 || index >= formData.value.certificateUrls.length) return;
    formData.value.certificateUrls.splice(index, 1);
    formData.value.certificateUrl = formData.value.certificateUrls[0] || '';
}

function closeCropModal() {
    showCropModal.value = false;
    revokeObjectUrl(cropperSource.value);
    cropperSource.value = null;
    previewUrl.value = null;
    if (imageInputRef.value) imageInputRef.value.value = '';
}

function revokeObjectUrl(url) {
    if (url && typeof url === 'string' && url.startsWith('blob:')) {
        URL.revokeObjectURL(url);
    }
}

function onCropperChange({ canvas }) {
    if (canvas) {
        previewUrl.value = canvas.toDataURL('image/webp', 0.95);
    }
}

function createWebpBlobFromCanvas(sourceCanvas) {
    const targetWidth = 960;
    const targetHeight = 600;

    const targetCanvas = document.createElement('canvas');
    targetCanvas.width = targetWidth;
    targetCanvas.height = targetHeight;

    const context = targetCanvas.getContext('2d');
    if (!context) return Promise.resolve(null);

    context.drawImage(sourceCanvas, 0, 0, targetWidth, targetHeight);

    return new Promise(resolve => {
        targetCanvas.toBlob(blob => resolve(blob), 'image/webp', 0.95);
    });
}

async function handleImageUpload(event) {
    const file = event?.target?.files?.[0];
    if (!file) return;

    // 5MB Limit check
    if (file.size > 5 * 1024 * 1024) {
        alert.toast.error('Archivo demasiado grande', 'El límite es de 5MB.');
        if (event.target) event.target.value = '';
        return;
    }

    revokeObjectUrl(cropperSource.value);
    cropperSource.value = URL.createObjectURL(file);
    showCropModal.value = true;
}

async function applyCrop() {
    if (!props.portfolioItem || isUploading.value) return;

    const cropper = cropperRef.value;
    if (!cropper) {
        alert.toast.error('Error', 'No se pudo inicializar el recorte de imagen.');
        return;
    }

    const result = cropper.getResult();
    if (!result?.canvas) {
        alert.toast.error('Error', 'Selecciona una imagen válida antes de continuar.');
        return;
    }

    isUploading.value = true;
    try {
        const blob = await createWebpBlobFromCanvas(result.canvas);
        if (!blob) throw new Error('Falló la generación del blob');

        const file = new File([blob], 'course_image.webp', { type: 'image/webp' });
        const response = await api.portfolios.uploadPortfolioImage(props.portfolioItem.id, file, 'course');
        const uploadedUrl = response?.data?.data?.url;

        if (!uploadedUrl) {
            throw new Error('No se recibió la URL de la imagen.');
        }

        const current = normalizeImages(formData.value);
        const nextImages = [...current, uploadedUrl];
        formData.value.images = nextImages;
        formData.value.imagesText = nextImages.join('\n');
        formData.value.imageUrls = nextImages;
        formData.value.imageUrl = nextImages[0] || '';

        if (editingIndex.value > -1 && props.courses[editingIndex.value]) {
            const row = props.courses[editingIndex.value];
            const normalizedRowImages = normalizeImages({
                ...row,
                images: [...normalizeImages(row), uploadedUrl],
            });

            props.courses.splice(editingIndex.value, 1, {
                ...row,
                images: normalizedRowImages,
                imagesText: normalizedRowImages.join('\n'),
                imageUrls: normalizedRowImages,
                imageUrl: normalizedRowImages[0] || ''
            });

            await persistPortfolioChanges();
            emit('request-save');
        }

        alert.toast.success('Imagen lista', 'La imagen del curso se ha guardado correctamente.');
        closeCropModal();
    } catch (error) {
        alert.toast.error('Error', error?.response?.data?.message || 'No se pudo subir la imagen.');
    } finally {
        isUploading.value = false;
        if (imageInputRef.value) imageInputRef.value.value = '';
    }
}

async function handleCertificateUpload(event) {
    const file = event?.target?.files?.[0];
    if (!file || !props.portfolioItem?.id || isUploadingCertificate.value) return;

    // 5MB Limit check
    if (file.size > 5 * 1024 * 1024) {
        alert.toast.error('Archivo demasiado grande', 'El límite es de 5MB.');
        if (event.target) event.target.value = '';
        return;
    }

    isUploadingCertificate.value = true;
    try {
        const response = await api.portfolios.uploadPortfolioCertificate(props.portfolioItem.id, file);
        const uploadedUrl = response?.data?.data?.url;
        if (!uploadedUrl) {
            throw new Error('No se recibió la URL del certificado.');
        }

        const current = normalizeCertificates(formData.value);
        const nextCertificates = [...current, uploadedUrl];
        formData.value.certificateUrls = nextCertificates;
        formData.value.certificateUrl = nextCertificates[0] || '';

        if (editingIndex.value > -1 && props.courses[editingIndex.value]) {
            const row = props.courses[editingIndex.value];
            const normalizedRowCertificates = [...normalizeCertificates(row), uploadedUrl];

            props.courses.splice(editingIndex.value, 1, {
                ...row,
                certificateUrls: normalizedRowCertificates,
                certificateUrl: normalizedRowCertificates[0] || ''
            });

            await persistPortfolioChanges();
            emit('request-save');
        }

        alert.toast.success('PDF listo', 'El certificado se ha guardado correctamente.');
    } catch (error) {
        alert.toast.error('Error', error?.response?.data?.message || 'No se pudo subir el PDF.');
    } finally {
        isUploadingCertificate.value = false;
        if (certificateInputRef.value) certificateInputRef.value.value = '';
    }
}

function openPreviewCard(row) {
    selectedCourse.value = row;
    previewImageIndex.value = 0;
    isCourseDescriptionExpanded.value = false;
    showPreviewCard.value = true;
    startPreviewAutoplay();
}

function closePreviewCard() {
    selectedCourse.value = null;
    previewImageIndex.value = 0;
    isCourseDescriptionExpanded.value = false;
    showPreviewCard.value = false;
    stopPreviewAutoplay();
}

function nextPreviewImage() {
    if (previewCarouselImages.value.length <= 1) return;
    previewImageIndex.value = (previewImageIndex.value + 1) % previewCarouselImages.value.length;
}

function goToPreviewImage(index) {
    if (index < 0 || index >= previewCarouselImages.value.length) return;
    previewImageIndex.value = index;
    restartPreviewAutoplay();
}

function startPreviewAutoplay() {
    stopPreviewAutoplay();
    if (!showPreviewCard.value || previewCarouselImages.value.length <= 1) return;

    previewAutoplayTimer = setInterval(() => {
        nextPreviewImage();
    }, 5000);
}

function stopPreviewAutoplay() {
    if (previewAutoplayTimer) {
        clearInterval(previewAutoplayTimer);
        previewAutoplayTimer = null;
    }
}

function restartPreviewAutoplay() {
    if (!showPreviewCard.value) return;
    startPreviewAutoplay();
}

watch(
    () => [showPreviewCard.value, previewCarouselImages.value.length],
    ([isOpen, imageCount]) => {
        if (isOpen && imageCount > 1) {
            startPreviewAutoplay();
            return;
        }

        stopPreviewAutoplay();
    }
);

onBeforeUnmount(() => {
    revokeObjectUrl(cropperSource.value);
    stopPreviewAutoplay();
});
</script>

<style lang="scss" scoped>
/* Redundant styles removed. Using shared portfolio-editor.scss */

.course-info-cell {
    display: flex;
    flex-direction: column;
    gap: 2px;
    text-align: left;

    strong {
        color: var(--text-primary);
        font-size: 0.95rem;
    }

    span {
        color: var(--text-muted);
        font-size: 0.85rem;
    }
}

.period-tag {
    background: var(--bg-tertiary);
    color: var(--text-secondary);
    padding: 4px 10px;
    border-radius: 20px;
    font-size: 0.8rem;
    font-weight: 500;
}

.course-logo-uploader {
    display: flex;
    align-items: flex-start;
    flex-wrap: wrap;
    gap: 20px;
    padding: 15px;
    background: var(--bg-overlay);
    border: 1px dashed var(--border-hover);
    border-radius: 12px;

    .logo-preview-area {
        width: 48px;
        height: 64px;
        background: var(--bg-tertiary);
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        overflow: hidden;
        border: 1px solid var(--border-color);
        cursor: zoom-in;

        img {
            width: 100%;
            height: 100%;
            object-fit: contain;
        }
    }

    .logo-uploader-actions {
        display: flex;
        flex-direction: column;
        gap: 8px;

        .btn-outline {
            background: transparent;
            border: 1px solid var(--border-color);
            color: var(--text-secondary);
        }
    }

    .uploaded-images-grid {
        width: 100%;
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(72px, 1fr));
        gap: 10px;
    }

    .uploaded-image-item {
        position: relative;
        width: 100%;
        height: 92px;
        border-radius: 10px;
        overflow: hidden;
        border: 1px solid var(--border-color);
        background: var(--bg-tertiary);
        padding: 0;
        cursor: zoom-in;

        img {
            width: 100%;
            height: 100%;
            object-fit: cover;
        }

        .uploaded-image-index {
            position: absolute;
            left: 6px;
            bottom: 6px;
            font-size: 0.7rem;
            color: #fff;
            background: rgba(0, 0, 0, 0.55);
            border-radius: 10px;
            padding: 2px 7px;
        }

        .uploaded-image-remove {
            position: absolute;
            top: 6px;
            right: 6px;
            width: 20px;
            height: 20px;
            display: grid;
            place-items: center;
            border-radius: 999px;
            background: rgba(0, 0, 0, 0.6);
            color: #fff;
            font-size: 0.78rem;
            font-weight: 700;
            line-height: 1;
        }
    }
}

.media-uploader {
    .certificate-list {
        display: flex;
        flex-direction: column;
        gap: 8px;
        margin-top: 12px;
    }

    .certificate-item {
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 8px 12px;
        background: var(--bg-tertiary);
        border: 1px solid var(--border-color);
        border-radius: 8px;
        width: 100%;
        text-align: left;
        cursor: pointer;
        transition: all 0.2s ease;

        &:hover {
            border-color: var(--primary);
            background: rgba(var(--primary-rgb), 0.05);
        }

        .certificate-badge {
            background: var(--primary);
            color: white;
            font-size: 0.65rem;
            font-weight: 700;
            padding: 2px 6px;
            border-radius: 4px;
            text-transform: uppercase;
        }

        .certificate-url {
            flex: 1;
            font-size: 0.85rem;
            color: var(--text-secondary);
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }

        .certificate-remove {
            color: var(--text-muted);
            font-weight: 700;
            padding: 0 4px;
            cursor: pointer;

            &:hover {
                color: #ef4444;
            }
        }
    }
}

.hidden-input { display: none; }
</style>
