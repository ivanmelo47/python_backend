<template>
    <article class="editor-card">
        <Table
            title="Experiencia laboral"
            :columns="columns"
            :rows="jobs"
            paginationMode="client"
            :showRefresh="false"
            searchPlaceholder="Buscar trabajo..."
            cardTitleTemplate="{role}"
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
                <div class="thumbnail-preview is-landscape is-clickable" @click="openImagePreview(getPrimaryImage(row))" title="Clic para ampliar">
                    <img v-if="getPrimaryImage(row)" :src="getPrimaryImage(row)" alt="Logo" />
                    <Icon v-else name="archiveFill" :size="16" />
                </div>
            </template>

            <template #cell-info="{ row }">
                <div class="job-info-cell">
                    <strong>{{ row.role }}</strong>
                    <span>{{ row.company }}</span>
                </div>
            </template>

            <template #cell-period_display="{ row }">
                <span class="period-tag">{{ formatPeriod(row) }}</span>
            </template>

            <template #cell-actions="{ row }">
                <button class="dropdown-item" @click.stop="openEditModal(row)">
                    <Icon name="pencil" :size="16" /> Editar
                </button>
                <button class="dropdown-item text-danger" @click.stop="removeJob(row)">
                    <Icon name="trash" :size="16" /> Eliminar
                </button>
            </template>
        </Table>

        <ModalForm
            :isVisible="showFormModal"
            :title="editingIndex > -1 ? 'Editar Trabajo' : 'Nuevo Trabajo'"
            submitLabel="Guardar"
            :loading="false"
            @close="closeFormModal"
            @submit="submitForm"
            size="lg"
            :columns="2"
        >
            <template #header-icon>
                <Icon name="briefcase" :size="20" />
            </template>

            <ModalField label="Rol / Puesto" :required="true" :span="1">
                <input v-model.trim="formData.role" type="text" maxlength="120" placeholder="Ej: Full Stack Developer" required />
            </ModalField>

            <ModalField label="Empresa" :required="true" :span="1">
                <input v-model.trim="formData.company" type="text" maxlength="120" placeholder="Ej: Tech Studio" required />
            </ModalField>

            <ModalField label="Enlace de la empresa" :span="2">
                <input v-model.trim="formData.companyUrl" type="url" maxlength="400" placeholder="https://www.empresa.com" />
            </ModalField>

            <ModalField label="Descripcion de responsabilidades o logros" :span="2">
                <textarea v-model="formData.description" rows="4" maxlength="1000" placeholder="Describe lo que hiciste en esta empresa, logros clave, etc."></textarea>
            </ModalField>

            <ModalField label="Etiquetas (separadas por coma)" :span="2">
                <input
                    v-model.trim="formData.tagsText"
                    type="text"
                    maxlength="320"
                    placeholder="Laravel, Vue 3, Liderazgo, Microservicios"
                />
            </ModalField>

            <ModalField label="Fecha Inicio" :required="true" :span="1">
                <input v-model="formData.startDate" type="month" required />
            </ModalField>

            <ModalField label="Fecha Fin" :span="1">
                <div class="date-input-group">
                    <input v-model="formData.endDate" type="month" :disabled="formData.isCurrent" />
                    <label class="current-check">
                        <input type="checkbox" v-model="formData.isCurrent" />
                        <span>Es mi trabajo actual</span>
                    </label>
                </div>
            </ModalField>

            <ModalField label="Imagenes del trabajo" :span="2">
                <div class="job-logo-uploader">
                    <div class="logo-preview-area is-landscape is-clickable" @click="openImagePreview(getPrimaryImage(formData))" title="Clic para vista previa">
                        <img v-if="getPrimaryImage(formData)" :src="getPrimaryImage(formData)" alt="Logo preview" />
                        <Icon v-else name="eye" :size="24" />
                    </div>
                    <div class="logo-uploader-actions">
                        <button type="button" class="btn" @click="openLogoPicker" :disabled="isUploading">
                            {{ getPrimaryImage(formData) ? 'Agregar imagen' : 'Subir imagen' }}
                        </button>
                        <button v-if="formData.imageUrls.length" type="button" class="btn btn-outline" @click="clearImages">Limpiar todas</button>
                        <small class="field-help">PNG, JPG o WEBP. Puedes subir varias imagenes para el carrusel.</small>
                    </div>

                    <div v-if="formData.imageUrls.length" class="uploaded-images-grid">
                        <button
                            v-for="(image, index) in formData.imageUrls"
                            :key="`${image}-${index}`"
                            type="button"
                            class="uploaded-image-item"
                            @click="openImagePreview(image)"
                            :title="`Imagen ${index + 1}`"
                        >
                            <img :src="image" :alt="`Imagen ${index + 1}`" />
                            <span class="uploaded-image-index">{{ index + 1 }}</span>
                            <span class="uploaded-image-remove" @click.stop="removeImageAt(index)">x</span>
                        </button>
                    </div>

                    <input ref="logoInputRef" type="file" accept="image/*" class="hidden-input" @change="handleLogoUpload" />
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
                                <h3>Recortar Logo</h3>
                                <p>Ajusta el encuadre final para la empresa.</p>
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
                                    <div class="preview-container">
                                        <img v-if="previewUrl" :src="previewUrl" alt="Preview" />
                                        <div v-else class="preview-placeholder">
                                            <Icon name="image" :size="32" />
                                        </div>
                                    </div>
                                    <span class="preview-hint">Asi se vera en la lista</span>
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

        <teleport to="body">
            <div v-if="showPreviewModal" class="lightbox-overlay" @click="closeImagePreview">
                <div class="lightbox-content" @click.stop>
                    <button type="button" class="lightbox-close" @click="closeImagePreview">
                        <Icon name="x" :size="24" />
                    </button>
                    <img :src="selectedPreviewUrl" alt="Full Preview" class="lightbox-img" />
                </div>
            </div>
        </teleport>

        <ModalForm
            :isVisible="showPreviewCard"
            title="Vista previa del trabajo"
            :loading="false"
            :hideFooter="true"
            size="xl"
            :columns="1"
            @close="closePreviewCard"
        >
            <div class="preview-modal-shell">
                <article class="job-preview-card">
                    <div class="card-content">
                        <section class="card-sidebar">
                            <div class="card-logo">
                                <transition name="carousel-fade" mode="out-in">
                                    <img v-if="currentPreviewImage" :key="currentPreviewImage" :src="currentPreviewImage" />
                                    <div v-else key="empty" class="logo-placeholder">
                                        <Icon name="archiveFill" :size="48" />
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
                                <span class="card-period">{{ formatPeriod(selectedJob) }}</span>
                                <div v-if="selectedJob?.isCurrent" class="current-badge">ACTUAL</div>
                            </header>

                            <div class="card-heading-block">
                                <h2 class="card-role">{{ selectedJob?.role }}</h2>
                                <h3 class="card-company">{{ selectedJob?.company }}</h3>
                            </div>

                            <a
                                v-if="selectedJob?.companyUrl"
                                class="card-link-btn"
                                :href="selectedJob.companyUrl"
                                target="_blank"
                                rel="noopener noreferrer"
                            >
                                <Icon name="link" :size="14" />
                                <span>Abrir sitio web</span>
                            </a>

                            <section v-if="selectedJob?.description" class="info-panel">
                                <span class="panel-label">DESCRIPCION</span>
                                <div class="card-description-wrap" :class="{ 'is-collapsed': showJobDescriptionToggle && !isJobDescriptionExpanded, expanded: isJobDescriptionExpanded }">
                                    <div class="card-description">{{ selectedJob.description }}</div>
                                </div>
                                <button
                                    v-if="showJobDescriptionToggle"
                                    type="button"
                                    class="description-toggle"
                                    @click="isJobDescriptionExpanded = !isJobDescriptionExpanded"
                                >
                                    {{ isJobDescriptionExpanded ? 'Ver menos' : 'Ver mas' }}
                                </button>
                            </section>

                            <section v-if="selectedJobTags.length" class="info-panel">
                                <span class="panel-label">ETIQUETAS</span>
                                <div class="card-tags">
                                    <span v-for="(tag, index) in selectedJobTags" :key="`${tag}-${index}`" class="card-tag">{{ tag }}</span>
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

const props = defineProps({
    jobs: { type: Array, required: true },
    portfolioItem: { type: Object, required: true },
    allBlocks: { type: Object, required: true }
});

const emit = defineEmits(['request-save', 'portfolio-synced']);

const alert = useAlert();
const searchQuery = ref('');

const columns = [
    { key: 'actions', label: 'ACCIONES', headerClass: 'compact', cellClass: 'compact' },
    { key: 'logo', label: 'LOGO', cellClass: 'compact text-center' },
    { key: 'info', label: 'EXPERIENCIA' },
    { key: 'period_display', label: 'PERIODO' }
];

const showFormModal = ref(false);
const editingIndex = ref(-1);
const isPersisting = ref(false);

const isUploading = ref(false);
const showCropModal = ref(false);
const logoInputRef = ref(null);
const cropperRef = ref(null);
const cropperSource = ref(null);
const previewUrl = ref(null);

const showPreviewModal = ref(false);
const selectedPreviewUrl = ref('');

const showPreviewCard = ref(false);
const selectedJob = ref(null);
const previewImageIndex = ref(0);
const isJobDescriptionExpanded = ref(false);
let previewAutoplayTimer = null;

const initialForm = {
    role: '',
    company: '',
    startDate: '',
    endDate: '',
    isCurrent: false,
    companyUrl: '',
    imageUrl: '',
    imageUrls: [],
    description: '',
    tags: [],
    tagsText: ''
};

const formData = ref({ ...initialForm });

function normalizeJobImages(job = {}) {
    if (Array.isArray(job.imageUrls) && job.imageUrls.length > 0) return job.imageUrls.filter(Boolean);
    if (Array.isArray(job.image_urls) && job.image_urls.length > 0) return job.image_urls.filter(Boolean);
    if (Array.isArray(job.images) && job.images.length > 0) return job.images.filter(Boolean);
    if (job.imageUrl || job.image_url) return [job.imageUrl || job.image_url];
    return [];
}

function normalizeTags(job = {}) {
    if (Array.isArray(job.tags)) return job.tags.map(tag => String(tag || '').trim()).filter(Boolean);
    if (Array.isArray(job.labels)) return job.labels.map(tag => String(tag || '').trim()).filter(Boolean);
    if (typeof job.tags === 'string') return job.tags.split(',').map(tag => tag.trim()).filter(Boolean);
    return [];
}

function getPrimaryImage(job = {}) {
    const images = normalizeJobImages(job);
    return images[0] || '';
}

const previewCarouselImages = computed(() => {
    if (!selectedJob.value) return [];
    return normalizeJobImages(selectedJob.value);
});

const currentPreviewImage = computed(() => {
    if (!previewCarouselImages.value.length) return '';
    return previewCarouselImages.value[previewImageIndex.value] || previewCarouselImages.value[0];
});

const selectedJobTags = computed(() => normalizeTags(selectedJob.value || {}));
const showJobDescriptionToggle = computed(() => {
    const description = String(selectedJob.value?.description || '');
    return description.trim().length > 260;
});

function openCreateModal() {
    editingIndex.value = -1;
    formData.value = { ...initialForm };
    showFormModal.value = true;
}

function openEditModal(row) {
    const realIdx = props.jobs.indexOf(row);
    if (realIdx === -1) return;
    editingIndex.value = realIdx;
    const imageUrls = normalizeJobImages(row);
    const tags = normalizeTags(row);

    formData.value = {
        ...row,
        imageUrls,
        imageUrl: imageUrls[0] || '',
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
    const imageUrls = normalizeJobImages(formData.value);
    const tags = normalizeTags({ tags: formData.value.tagsText || formData.value.tags });

    const payload = {
        ...formData.value,
        imageUrls,
        imageUrl: imageUrls[0] || '',
        tags,
        tagsText: tags.join(', ')
    };

    if (editingIndex.value > -1) {
        const id = props.jobs[editingIndex.value].id;
        props.jobs.splice(editingIndex.value, 1, { ...payload, id });
        alert.toast.success('Editado', 'Experiencia laboral actualizada.');
    } else {
        props.jobs.push({ ...payload, id: Date.now() });
        alert.toast.success('Creado', 'Experiencia laboral registrada.');
    }

    await persistPortfolioChanges();
    emit('request-save');
    closeFormModal();
}

async function removeJob(row) {
    const realIdx = props.jobs.indexOf(row);
    if (realIdx === -1) return;

    if (confirm('¿Estas seguro de eliminar esta experiencia laboral?')) {
        props.jobs.splice(realIdx, 1);
        await persistPortfolioChanges();
        emit('request-save');
        alert.toast.success('Eliminado', 'Experiencia laboral eliminada con exito.');
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
        alert.toast.error('Error', error?.response?.data?.message || 'No se pudo sincronizar el trabajo.');
    } finally {
        isPersisting.value = false;
    }
}

function formatPeriod(job) {
    const start = job?.startDate || '?';
    const end = job?.isCurrent ? 'Actual' : (job?.endDate || '?');
    return `${start} — ${end}`;
}

function revokeObjectUrl(url) {
    if (url && typeof url === 'string' && url.startsWith('blob:')) {
        URL.revokeObjectURL(url);
    }
}

function openLogoPicker() {
    logoInputRef.value?.click();
}

function openImagePreview(url) {
    if (!url) return;
    selectedPreviewUrl.value = url;
    showPreviewModal.value = true;
}

function closeImagePreview() {
    showPreviewModal.value = false;
    selectedPreviewUrl.value = '';
}

function openPreviewCard(row) {
    selectedJob.value = row;
    previewImageIndex.value = 0;
    isJobDescriptionExpanded.value = false;
    showPreviewCard.value = true;
    startPreviewAutoplay();
}

function closePreviewCard() {
    showPreviewCard.value = false;
    selectedJob.value = null;
    previewImageIndex.value = 0;
    isJobDescriptionExpanded.value = false;
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

function clearImages() {
    formData.value.imageUrls = [];
    formData.value.imageUrl = '';
}

function removeImageAt(index) {
    if (index < 0 || index >= formData.value.imageUrls.length) return;
    formData.value.imageUrls.splice(index, 1);
    formData.value.imageUrl = formData.value.imageUrls[0] || '';
}

function closeCropModal() {
    showCropModal.value = false;
    revokeObjectUrl(cropperSource.value);
    cropperSource.value = null;
    previewUrl.value = null;
    if (logoInputRef.value) logoInputRef.value.value = '';
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

function handleLogoUpload(event) {
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
        alert.toast.error('Error', 'Selecciona una imagen valida antes de continuar.');
        return;
    }

    isUploading.value = true;
    try {
        const blob = await createWebpBlobFromCanvas(result.canvas);
        if (!blob) throw new Error('Fallo la generacion del blob');

        const file = new File([blob], 'job_logo.webp', { type: 'image/webp' });
        const response = await api.portfolios.uploadPortfolioImage(props.portfolioItem.id, file, 'job');

        const uploadedUrl = response?.data?.data?.url;
        if (uploadedUrl) {
            const current = normalizeJobImages(formData.value);
            formData.value.imageUrls = [...current, uploadedUrl];
            formData.value.imageUrl = formData.value.imageUrls[0] || '';

            if (editingIndex.value > -1 && props.jobs[editingIndex.value]) {
                const row = props.jobs[editingIndex.value];
                const normalizedRowUrls = normalizeJobImages({
                    ...row,
                    imageUrls: [...normalizeJobImages(row), uploadedUrl],
                });

                props.jobs.splice(editingIndex.value, 1, {
                    ...row,
                    imageUrls: normalizedRowUrls,
                    imageUrl: normalizedRowUrls[0] || '',
                });

                await persistPortfolioChanges();
                emit('request-save');
            }
        }

        alert.toast.success('Imagen lista', 'El logo se ha guardado y optimizado correctamente.');
        closeCropModal();
    } catch (error) {
        alert.toast.error('Error', error?.response?.data?.message || 'No se pudo subir la imagen.');
    } finally {
        isUploading.value = false;
    }
}

onBeforeUnmount(() => {
    revokeObjectUrl(cropperSource.value);
    stopPreviewAutoplay();
});
</script>

<style lang="scss" scoped>
/* Redundant styles removed. Using shared portfolio-editor.scss */

.job-info-cell {
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

.date-input-group {
    display: flex;
    flex-direction: column;
    gap: 8px;

    .current-check {
        display: flex;
        align-items: center;
        gap: 8px;
        cursor: pointer;
        font-size: 0.85rem;
        color: var(--text-secondary);

        input { width: auto; }
    }
}

.job-logo-uploader {
    display: flex;
    align-items: flex-start;
    flex-wrap: wrap;
    gap: 20px;
    padding: 15px;
    background: var(--bg-overlay);
    border: 1px dashed var(--border-hover);
    border-radius: 12px;

    .logo-preview-area {
        width: 64px;
        height: 40px;
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

.hidden-input { display: none; }
</style>
