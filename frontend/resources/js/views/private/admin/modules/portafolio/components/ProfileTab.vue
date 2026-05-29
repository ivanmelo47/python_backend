<template>
    <article class="editor-card">
        <h3>Perfil principal</h3>
        <div class="form-grid">
            <label>
                Nombre visible
                <input v-model.trim="localProfile.name" type="text" />
            </label>

            <label>
                Rol principal
                <input v-model.trim="localProfile.role" type="text" />
            </label>

            <label class="full-width">
                Resumen de perfil (Breve)
                <textarea v-model.trim="localProfile.summary" rows="2"></textarea>
            </label>

            <label class="full-width">
                Sobre mí (Extendido)
                <textarea v-model.trim="localProfile.aboutText" rows="6"></textarea>
            </label>

            <label class="full-width">
                URL de avatar
                <input :value="avatarUrl" @input="$emit('update:avatar-url', $event.target.value)" type="url" maxlength="400" />
            </label>

            <div class="full-width avatar-uploader">
                <div class="avatar-uploader-preview">
                    <img v-if="avatarUrl" :src="avatarUrl" alt="Vista previa avatar" class="avatar-preview" />
                    <div v-else class="avatar-fallback">AV</div>
                </div>

                <div class="avatar-uploader-content">
                    <h4>Avatar del portafolio</h4>
                    <p>Selecciona una imagen, recorta el encuadre en el modal flotante y se convertira a WebP optimizado.</p>

                    <div class="avatar-uploader-actions">
                        <button type="button" class="btn" @click="openAvatarPicker" :disabled="isAvatarUploading">
                            {{ avatarUrl ? 'Cambiar avatar' : 'Subir avatar' }}
                        </button>
                    </div>

                    <span v-if="isAvatarUploading" class="avatar-uploading">Subiendo avatar...</span>
                    <small class="field-help">PNG, JPG o WEBP (max 5 MB).</small>
                </div>

                <input
                    ref="avatarInputRef"
                    type="file"
                    accept="image/png,image/jpeg,image/webp"
                    class="avatar-input-hidden"
                    @change="handleAvatarUpload"
                />
            </div>
        </div>

        <!-- Crop Modal -->
        <teleport to="body">
            <div v-if="showAvatarCropModal" class="crop-modal-overlay" @click="closeAvatarCropModal">
                <article class="crop-modal premium-modal" @click.stop>
                    <header class="crop-modal-header">
                        <div class="header-info">
                            <Icon name="image" :size="20" class="header-icon" />
                            <div>
                                <h3>Recortar Avatar</h3>
                                <p>Ajusta tu foto de perfil para el portafolio.</p>
                            </div>
                        </div>
                        <button type="button" class="close-btn-ghost" @click="closeAvatarCropModal">
                            <Icon name="x" :size="20" />
                        </button>
                    </header>

                    <div class="crop-modal-content">
                        <div class="crop-main-area">
                            <cropper
                                v-if="cropperSource"
                                ref="cropperRef"
                                class="avatar-cropper-canvas"
                                :src="cropperSource"
                                :stencil-props="{ aspectRatio: 1 }"
                                @change="onCropperChange"
                            />
                        </div>

                        <aside class="crop-side-pane">
                            <div class="preview-section">
                                <span class="section-label">VISTA PREVIA</span>
                                <div class="live-preview-box">
                                    <div class="preview-container is-circle">
                                        <img v-if="previewUrl" :src="previewUrl" alt="Preview" />
                                        <div v-else class="preview-placeholder">AV</div>
                                    </div>
                                    <span class="preview-hint">Vista en círculo</span>
                                </div>
                            </div>

                            <div class="crop-instructions">
                                <Icon name="info" :size="14" />
                                <p>El resultado se optimizará automáticamente a formato WebP de alta calidad.</p>
                            </div>
                        </aside>
                    </div>

                    <footer class="crop-modal-footer">
                        <button type="button" class="btn btn-ghost" @click="closeAvatarCropModal">Cancelar</button>
                        <button type="button" class="btn btn-primary-gradient" @click="applyCropAndUploadAvatar" :disabled="isAvatarUploading">
                            <Icon v-if="isAvatarUploading" name="refresh" class="spin" :size="18" />
                            <span>{{ isAvatarUploading ? 'Guardando...' : 'Aplicar Foto' }}</span>
                        </button>
                    </footer>
                </article>
            </div>
        </teleport>
    </article>
</template>

<script setup>
import { computed, ref, onBeforeUnmount } from 'vue';
import { Cropper } from 'vue-advanced-cropper';
import 'vue-advanced-cropper/dist/style.css';
import { api } from '@/services/api';
import { useAlert } from '@/composables/useAlert';
import Icon from '@/components/Icon.vue';

const props = defineProps({
    profile: Object,
    avatarUrl: String,
    portfolioItem: Object
});

const emit = defineEmits(['update:avatar-url', 'avatar-updated']);

const localProfile = computed({
    get: () => props.profile,
    set: (value) => {
        // Vue objects are passed by reference, mutating properties directly works,
        // but it's cleaner to bind directly via `props.profile`.
    }
});

const alert = useAlert();
const isAvatarUploading = ref(false);
const showAvatarCropModal = ref(false);
const avatarInputRef = ref(null);
const cropperRef = ref(null);
const cropperSource = ref(null);
const previewUrl = ref(null);

function revokeObjectUrl(url) {
    if (url && typeof url === 'string' && url.startsWith('blob:')) {
        URL.revokeObjectURL(url);
    }
}

async function handleAvatarUpload(event) {
    const file = event?.target?.files?.[0];
    event.target.value = '';

    if (!file || !props.portfolioItem) {
        return;
    }

    revokeObjectUrl(cropperSource.value);
    cropperSource.value = URL.createObjectURL(file);
    showAvatarCropModal.value = true;
}

function openAvatarPicker() {
    avatarInputRef.value?.click();
}

function closeAvatarCropModal() {
    showAvatarCropModal.value = false;
    revokeObjectUrl(cropperSource.value);
    cropperSource.value = null;
    previewUrl.value = null;

    if (avatarInputRef.value) {
        avatarInputRef.value.value = '';
    }
}

function onCropperChange({ canvas }) {
    if (canvas) {
        previewUrl.value = canvas.toDataURL('image/webp');
    }
}

function createWebpBlobFromCanvas(sourceCanvas) {
    const targetSize = 512;
    const targetCanvas = document.createElement('canvas');
    targetCanvas.width = targetSize;
    targetCanvas.height = targetSize;

    const context = targetCanvas.getContext('2d');
    if (!context) {
        return Promise.resolve(null);
    }

    context.drawImage(sourceCanvas, 0, 0, targetSize, targetSize);

    return new Promise(resolve => {
        targetCanvas.toBlob(blob => resolve(blob), 'image/webp', 0.9);
    });
}

async function applyCropAndUploadAvatar() {
    if (!props.portfolioItem || isAvatarUploading.value) {
        return;
    }

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

    const blob = await createWebpBlobFromCanvas(result.canvas);
    if (!blob) {
        alert.toast.error('Error', 'No se pudo procesar la imagen recortada.');
        return;
    }

    const file = new File([blob], 'avatar.webp', { type: 'image/webp' });

    isAvatarUploading.value = true;

    try {
        const response = await api.portfolios.uploadAvatar(props.portfolioItem.id, file);
        emit('avatar-updated', response.data.data);
        alert.toast.success('Avatar actualizado', 'La imagen se guardo correctamente.');
        closeAvatarCropModal();
    } catch (error) {
        alert.toast.error('Error', error?.response?.data?.message || 'No se pudo subir el avatar.');
    } finally {
        isAvatarUploading.value = false;
    }
}

onBeforeUnmount(() => {
    revokeObjectUrl(cropperSource.value);
});
</script>
