<template>
    <article class="editor-card">
        <Table
            title="Proyectos"
            :columns="columns"
            :rows="projects"
            paginationMode="client"
            :showRefresh="false"
            searchPlaceholder="Buscar proyecto..."
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
                <div class="thumbnail-preview is-landscape is-clickable" @click.stop="openImagePreview(row, 0)" title="Clic para ampliar">
                    <img v-if="getPrimaryImage(row)" :src="getPrimaryImage(row)" alt="Preview" />
                    <Icon v-else name="folder" :size="16" />
                </div>
            </template>

            <template #cell-info="{ row }">
                <div class="project-info-cell">
                    <strong>{{ row.title }}</strong>
                    <span>{{ row.type || 'Proyecto' }}</span>
                </div>
            </template>

            <template #cell-actions="{ row }">
                <button class="dropdown-item" @click.stop="openEditModal(row)">
                    <Icon name="pencil" :size="16" /> Editar
                </button>
                <button class="dropdown-item text-danger" @click.stop="removeProject(row)">
                    <Icon name="trash" :size="16" /> Eliminar
                </button>
            </template>
        </Table>

        <ModalForm
            :isVisible="showFormModal"
            :title="editingIndex > -1 ? 'Editar Proyecto' : 'Nuevo Proyecto'"
            submitLabel="Guardar"
            :loading="false"
            @close="closeFormModal"
            @submit="submitForm"
            size="lg"
            :columns="2"
        >
            <template #header-icon>
                <Icon name="folder-git2" :size="20" />
            </template>

            <ModalField label="Título" :required="true" :span="1">
                <input v-model.trim="formData.title" type="text" maxlength="120" placeholder="Ej: Gestor inteligente de archivos" required />
            </ModalField>

            <ModalField label="Tipo" :span="1">
                <input v-model.trim="formData.type" type="text" maxlength="80" placeholder="Ej: Aplicacion Web" />
            </ModalField>

            <ModalField label="Descripción corta" :span="2">
                <textarea v-model.trim="formData.description" rows="3" maxlength="220" placeholder="Resumen breve para la tarjeta"></textarea>
            </ModalField>

            <ModalField label="Descripción detallada" :span="2">
                <textarea v-model.trim="formData.detailedDescription" rows="4" maxlength="2000" placeholder="Detalles visibles en la vista previa del proyecto"></textarea>
            </ModalField>

            <ModalField label="Etiquetas (separadas por coma)" :span="2">
                <input v-model.trim="formData.tagsText" type="text" maxlength="320" placeholder="Laravel, Vue 3, API, Docker" />
            </ModalField>

            <ModalField label="URL Repositorio" :span="1">
                <input v-model.trim="formData.repoUrl" type="url" maxlength="400" placeholder="https://github.com/..." />
            </ModalField>

            <ModalField label="URL App/Demo" :span="1">
                <input v-model.trim="formData.liveUrl" type="url" maxlength="400" placeholder="https://..." />
            </ModalField>

            <ModalField label="Imágenes del proyecto" :span="2">
                <div class="project-logo-uploader">
                    <div class="logo-preview-area is-clickable" @click="openImagePreview(formData, 0)" title="Clic para vista previa">
                        <img v-if="getPrimaryImage(formData)" :src="getPrimaryImage(formData)" alt="Imagen principal" />
                        <Icon v-else name="eye" :size="24" />
                    </div>

                    <div class="logo-uploader-actions">
                        <button type="button" class="btn" @click="openLogoPicker" :disabled="isUploading">
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
                            @click="openImagePreview(formData, index)"
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
                                <h3>Recortar Imagen</h3>
                                <p>Ajusta el encuadre final para el proyecto.</p>
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

        <teleport to="body">
            <div v-if="showPreviewModal" class="lightbox-overlay" @click="closeImagePreview">
                <div class="lightbox-content lightbox-fullscreen" @click.stop>
                    <button type="button" class="lightbox-close" @click="closeImagePreview">
                        <Icon name="x" :size="24" />
                    </button>

                    <div class="lightbox-topbar">
                        <div class="lightbox-title-block">
                            <span class="lightbox-kicker">Vista previa del proyecto</span>
                            <h3>{{ previewViewerTitle || selectedProject?.title || formData.title || 'Proyecto' }}</h3>
                        </div>
                        <div class="lightbox-counter">{{ previewViewerIndex + 1 }} / {{ previewViewerImages.length }}</div>
                    </div>

                    <div class="lightbox-stage">
                        <button
                            type="button"
                            class="lightbox-nav lightbox-nav-prev"
                            :disabled="previewViewerImages.length <= 1"
                            @click.stop="goToPreviewImage(previewViewerIndex - 1, true)"
                        >
                            <Icon name="chevron-left" :size="22" />
                        </button>

                        <div class="lightbox-image-frame">
                            <transition name="carousel-fade" mode="out-in">
                                <img
                                    v-if="currentViewerImage"
                                    :key="currentViewerImage"
                                    :src="currentViewerImage"
                                    alt="Vista previa"
                                    class="lightbox-img"
                                />
                                <div v-else key="empty" class="lightbox-empty">
                                    <Icon name="folder" :size="48" />
                                    <span>No hay imagenes</span>
                                </div>
                            </transition>
                        </div>

                        <button
                            type="button"
                            class="lightbox-nav lightbox-nav-next"
                            :disabled="previewViewerImages.length <= 1"
                            @click.stop="goToPreviewImage(previewViewerIndex + 1, true)"
                        >
                            <Icon name="chevron-right" :size="22" />
                        </button>
                    </div>

                    <div v-if="previewViewerImages.length > 1" class="lightbox-dots">
                        <button
                            v-for="(image, index) in previewViewerImages"
                            :key="`${image}-${index}`"
                            type="button"
                            class="carousel-dot"
                            :class="{ active: previewViewerIndex === index }"
                            :aria-label="`Ir a imagen ${index + 1}`"
                            @click.stop="goToPreviewImage(index, true)"
                        ></button>
                    </div>
                </div>
            </div>
        </teleport>

        <ModalForm
            :isVisible="showPreviewCard"
            title="Vista previa del proyecto"
            :loading="false"
            :hideFooter="true"
            size="xl"
            :columns="1"
            @close="closePreviewCard"
        >
            <div class="preview-modal-shell">
                <article class="project-preview-card">
                    <div class="card-content">
                        <section class="card-sidebar">
                            <div class="card-logo is-landscape is-clickable" title="Clic para abrir en pantalla completa" @click="openImagePreview(selectedProject, previewImageIndex)">
                                <transition name="carousel-fade" mode="out-in">
                                    <img v-if="currentPreviewImage" :key="currentPreviewImage" :src="currentPreviewImage" alt="Imagen del proyecto" />
                                    <div v-else key="empty" class="logo-placeholder">
                                        <Icon name="folder" :size="52" />
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
                                <div class="card-description-wrap" :class="{ 'is-collapsed': showProjectDescriptionToggle && !isProjectDescriptionExpanded, expanded: isProjectDescriptionExpanded }">
                                    <div class="card-description">{{ selectedProjectDescription }}</div>
                                </div>
                                <button
                                    v-if="showProjectDescriptionToggle"
                                    type="button"
                                    class="description-toggle"
                                    @click="isProjectDescriptionExpanded = !isProjectDescriptionExpanded"
                                >
                                    {{ isProjectDescriptionExpanded ? 'Ver menos' : 'Ver mas' }}
                                </button>
                            </section>

                            <section v-if="selectedProjectTags.length" class="info-panel">
                                <span class="panel-label">ETIQUETAS</span>
                                <div class="card-tags">
                                    <span v-for="(tag, index) in selectedProjectTags" :key="`${tag}-${index}`" class="card-tag">{{ tag }}</span>
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
    projects: { type: Array, required: true },
    portfolioItem: { type: Object, required: true },
    allBlocks: { type: Object, required: true }
});

const emit = defineEmits(['request-save', 'portfolio-synced']);

const alert = useAlert();
const searchQuery = ref('');
const isPersisting = ref(false);

const columns = [
    { key: 'actions', label: 'ACCIONES', headerClass: 'compact', cellClass: 'compact' },
    { key: 'logo', label: 'PREVIEW', cellClass: 'compact text-center' },
    { key: 'info', label: 'PROYECTO' }
];

const showFormModal = ref(false);
const editingIndex = ref(-1);

const isUploading = ref(false);
const showCropModal = ref(false);
const logoInputRef = ref(null);
const cropperRef = ref(null);
const cropperSource = ref(null);
const previewUrl = ref(null);

const showPreviewModal = ref(false);
const previewViewerImages = ref([]);
const previewViewerIndex = ref(0);
const previewViewerTitle = ref('');

const showPreviewCard = ref(false);
const selectedProject = ref(null);
const previewImageIndex = ref(0);
const isProjectDescriptionExpanded = ref(false);
let previewAutoplayTimer = null;

const initialForm = {
    title: '',
    type: 'Proyecto',
    description: '',
    detailedDescription: '',
    repoUrl: '',
    liveUrl: '',
    tags: [],
    tagsText: '',
    images: [],
    imagesText: ''
};

const formData = ref({ ...initialForm });

function splitLines(value) {
    return String(value || '')
        .split('\n')
        .map(line => line.trim())
        .filter(Boolean);
}

function normalizeProjectImages(project = {}) {
    if (Array.isArray(project.images) && project.images.length > 0) return project.images.filter(Boolean);
    if (Array.isArray(project.imageUrls) && project.imageUrls.length > 0) return project.imageUrls.filter(Boolean);
    if (typeof project.imagesText === 'string' && project.imagesText.trim()) return splitLines(project.imagesText);
    if (project.imageUrl || project.image_url) return [project.imageUrl || project.image_url];
    return [];
}

function normalizeTags(item = {}) {
    if (Array.isArray(item.tags)) return item.tags.map(tag => String(tag || '').trim()).filter(Boolean);
    if (typeof item.tagsText === 'string') return item.tagsText.split(',').map(tag => tag.trim()).filter(Boolean);
    if (typeof item.tags === 'string') return item.tags.split(',').map(tag => tag.trim()).filter(Boolean);
    return [];
}

function getPrimaryImage(project = {}) {
    const images = normalizeProjectImages(project);
    return images[0] || '';
}

const previewCarouselImages = computed(() => {
    if (!selectedProject.value) return [];
    return normalizeProjectImages(selectedProject.value);
});

const currentPreviewImage = computed(() => {
    if (!previewCarouselImages.value.length) return '';
    return previewCarouselImages.value[previewImageIndex.value] || previewCarouselImages.value[0];
});

const currentViewerImage = computed(() => {
    if (!previewViewerImages.value.length) return '';
    return previewViewerImages.value[previewViewerIndex.value] || previewViewerImages.value[0];
});

const selectedProjectTags = computed(() => normalizeTags(selectedProject.value || {}));
const selectedProjectDescription = computed(() => {
    return String(selectedProject.value?.detailedDescription || selectedProject.value?.description || '').trim();
});
const showProjectDescriptionToggle = computed(() => selectedProjectDescription.value.length > 260);

function openCreateModal() {
    editingIndex.value = -1;
    formData.value = { ...initialForm };
    showFormModal.value = true;
}

function openEditModal(row) {
    const realIdx = props.projects.indexOf(row);
    if (realIdx === -1) return;

    const images = normalizeProjectImages(row);
    const tags = normalizeTags(row);

    editingIndex.value = realIdx;
    formData.value = {
        ...initialForm,
        ...row,
        images,
        imagesText: images.join('\n'),
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
    const images = normalizeProjectImages(formData.value);
    const tags = normalizeTags({ tags: formData.value.tagsText || formData.value.tags });

    const payload = {
        ...formData.value,
        images,
        imagesText: images.join('\n'),
        tags,
        tagsText: tags.join(', ')
    };

    if (editingIndex.value > -1) {
        const id = props.projects[editingIndex.value].id;
        props.projects.splice(editingIndex.value, 1, { ...payload, id });
        alert.toast.success('Editado', 'Proyecto actualizado con exito.');
    } else {
        props.projects.push({ ...payload, id: Date.now() });
        alert.toast.success('Creado', 'Proyecto registrado con exito.');
    }

    await persistPortfolioChanges();
    emit('request-save');
    closeFormModal();
}

async function removeProject(row) {
    const realIdx = props.projects.indexOf(row);
    if (realIdx === -1) return;

    if (confirm('¿Estas seguro de eliminar este proyecto?')) {
        props.projects.splice(realIdx, 1);
        await persistPortfolioChanges();
        emit('request-save');
        alert.toast.success('Eliminado', 'Proyecto eliminado con exito.');
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
        alert.toast.error('Error', error?.response?.data?.message || 'No se pudo sincronizar el proyecto.');
    } finally {
        isPersisting.value = false;
    }
}

function revokeObjectUrl(url) {
    if (url && typeof url === 'string' && url.startsWith('blob:')) {
        URL.revokeObjectURL(url);
    }
}

function openLogoPicker() {
    logoInputRef.value?.click();
}

function openImagePreview(source, index = 0) {
    const images = Array.isArray(source)
        ? source.filter(Boolean)
        : normalizeProjectImages(source || {});

    if (!images.length) return;

    previewViewerImages.value = images;
    previewViewerIndex.value = Math.min(Math.max(index, 0), images.length - 1);
    previewViewerTitle.value = source?.title || source?.type || '';
    showPreviewModal.value = true;
}

function closeImagePreview() {
    showPreviewModal.value = false;
    previewViewerImages.value = [];
    previewViewerIndex.value = 0;
    previewViewerTitle.value = '';
}

function openPreviewCard(row) {
    selectedProject.value = row;
    previewImageIndex.value = 0;
    isProjectDescriptionExpanded.value = false;
    showPreviewCard.value = true;
    startPreviewAutoplay();
}

function closePreviewCard() {
    selectedProject.value = null;
    previewImageIndex.value = 0;
    isProjectDescriptionExpanded.value = false;
    showPreviewCard.value = false;
    stopPreviewAutoplay();
}

function nextPreviewImage() {
    if (previewCarouselImages.value.length <= 1) return;
    previewImageIndex.value = (previewImageIndex.value + 1) % previewCarouselImages.value.length;
}

function goToPreviewImage(index, isViewer = false) {
    const images = isViewer ? previewViewerImages.value : previewCarouselImages.value;
    if (!images.length) return;

    const nextIndex = index < 0
        ? images.length - 1
        : index >= images.length
            ? 0
            : index;

    if (isViewer) {
        previewViewerIndex.value = nextIndex;
        return;
    }

    previewImageIndex.value = nextIndex;
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
    formData.value.images = [];
    formData.value.imagesText = '';
}

function removeImageAt(index) {
    if (index < 0 || index >= formData.value.images.length) return;
    formData.value.images.splice(index, 1);
    formData.value.imagesText = formData.value.images.join('\n');
}

function closeCropModal() {
    showCropModal.value = false;
    revokeObjectUrl(cropperSource.value);
    cropperSource.value = null;
    previewUrl.value = null;
    if (logoInputRef.value) logoInputRef.value.value = '';
}

function onCropperChange({ canvas }) {
    previewUrl.value = canvas.toDataURL('image/webp', 0.95);
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
    const file = event.target.files[0];
    if (!file) return;

    // 5MB Limit check
    if (file.size > 5 * 1024 * 1024) {
        alert.toast.error('Archivo demasiado grande', 'El límite es de 5MB.');
        event.target.value = '';
        return;
    }

    // Reset input
    event.target.value = '';

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

        const file = new File([blob], 'project_image.webp', { type: 'image/webp' });
        const response = await api.portfolios.uploadPortfolioImage(props.portfolioItem.id, file, 'project');

        const uploadedUrl = response?.data?.data?.url;
        if (uploadedUrl) {
            const current = normalizeProjectImages(formData.value);
            formData.value.images = [...current, uploadedUrl];
            formData.value.imagesText = formData.value.images.join('\n');

            if (editingIndex.value > -1 && props.projects[editingIndex.value]) {
                const row = props.projects[editingIndex.value];
                const normalizedRowImages = normalizeProjectImages({
                    ...row,
                    images: [...normalizeProjectImages(row), uploadedUrl],
                });

                props.projects.splice(editingIndex.value, 1, {
                    ...row,
                    images: normalizedRowImages,
                    imagesText: normalizedRowImages.join('\n'),
                });

                await persistPortfolioChanges();
                emit('request-save');
            }
        }

        alert.toast.success('Imagen lista', 'La imagen se ha guardado y optimizado correctamente.');
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

.project-info-cell {
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

.project-logo-uploader {
    display: flex;
    align-items: flex-start;
    flex-wrap: wrap;
    gap: 20px;
    padding: 15px;
    background: var(--bg-overlay);
    border: 1px dashed var(--border-hover);
    border-radius: 12px;

    .logo-preview-area {
        width: 80px;
        height: 50px;
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
            object-fit: cover;
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
        grid-template-columns: repeat(auto-fill, minmax(92px, 1fr));
        gap: 10px;
    }

    .uploaded-image-item {
        position: relative;
        width: 100%;
        height: 74px;
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

:deep(.modal-container.modal-xl) {
    width: min(1260px, calc(100vw - 36px));
}

:deep(.modal-container.modal-xl .modal-body) {
    max-height: 84vh;
    overflow-x: hidden;
}

.preview-container {
    width: 100%;
    border-radius: 12px;
    overflow: hidden;
    background: var(--bg-tertiary);
    border: 1px solid var(--border-color);

    &.is-landscape {
        aspect-ratio: 16 / 10;
        max-width: 240px;
    }

    img {
        width: 100%;
        height: 100%;
        object-fit: cover;
        display: block;
    }
}

.lightbox-fullscreen {
    width: min(96vw, 1560px);
    height: min(94vh, 960px);
    display: flex;
    flex-direction: column;
    gap: 16px;
    padding: 22px;
}

.lightbox-topbar {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    gap: 16px;
    padding-right: 40px;
}

.lightbox-title-block {
    display: flex;
    flex-direction: column;
    gap: 4px;

    .lightbox-kicker {
        color: var(--text-muted);
        font-size: 0.78rem;
        letter-spacing: 0.08em;
        text-transform: uppercase;
    }

    h3 {
        margin: 0;
        color: var(--text-primary);
        font-size: 1.1rem;
        font-weight: 700;
    }
}

.lightbox-counter {
    color: var(--text-secondary);
    font-size: 0.9rem;
    font-weight: 600;
    align-self: center;
}

.lightbox-stage {
    flex: 1;
    display: grid;
    grid-template-columns: auto minmax(0, 1fr) auto;
    align-items: center;
    gap: 14px;
    min-height: 0;
}

.lightbox-image-frame {
    height: 100%;
    min-height: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    overflow: hidden;
    width: min(100%, 1120px);
    margin: 0 auto;
    aspect-ratio: 16 / 10;
    border-radius: 20px;
    background: rgba(255, 255, 255, 0.02);
    border: 1px solid rgba(255, 255, 255, 0.08);
}

.lightbox-img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    border-radius: 20px;
    box-shadow: 0 24px 60px rgba(0, 0, 0, 0.35);
}

.lightbox-empty {
    width: 100%;
    height: 100%;
    border-radius: 18px;
    border: 1px dashed rgba(255, 255, 255, 0.16);
    background: rgba(255, 255, 255, 0.03);
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 10px;
    color: var(--text-muted);
}

.lightbox-nav {
    width: 48px;
    height: 48px;
    border: none;
    border-radius: 999px;
    background: rgba(255, 255, 255, 0.08);
    color: var(--text-primary);
    display: inline-flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    transition: all 0.2s ease;

    &:hover:not(:disabled) {
        background: rgba(255, 255, 255, 0.16);
        transform: translateY(-1px);
    }

    &:disabled {
        opacity: 0.35;
        cursor: default;
    }
}

.lightbox-dots {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
}

.carousel-dot {
    width: 10px;
    height: 10px;
    border: none;
    border-radius: 999px;
    padding: 0;
    cursor: pointer;
    background: rgba(255, 255, 255, 0.28);
    transition: all 0.25s ease;

    &.active {
        width: 28px;
        background: #5ce8bf;
    }
}

@media (max-width: 900px) {
    .lightbox-fullscreen {
        width: calc(100vw - 18px);
        height: calc(100vh - 18px);
        padding: 16px;
    }

    .lightbox-stage {
        grid-template-columns: 1fr;
    }

    .lightbox-nav {
        display: none;
    }

    .lightbox-image-frame {
        width: 100%;
        aspect-ratio: 16 / 10;
    }

    .lightbox-topbar {
        padding-right: 34px;
    }

    .lightbox-empty {
        width: 100%;
        height: 100%;
    }

    .preview-container.is-landscape {
        max-width: 100%;
    }
}

.carousel-fade-enter-active,
.carousel-fade-leave-active {
    transition: opacity 0.45s ease;
}

.carousel-fade-enter-from,
.carousel-fade-leave-to {
    opacity: 0;
}
</style>
