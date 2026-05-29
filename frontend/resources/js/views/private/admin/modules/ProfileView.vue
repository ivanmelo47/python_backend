<template>
    <div class="profile-view">
        <div class="profile-header">
            <h1>Mi Perfil</h1>
            <p>Gestiona tu información personal, tu clave de acceso y tu imagen de cuenta.</p>
        </div>

        <div class="profile-grid">
            <section class="profile-card profile-summary-card">
                <div class="profile-avatar profile-avatar-large">
                    <img v-if="profileAvatarUrl" :src="profileAvatarUrl" alt="Avatar del usuario" />
                    <DynamicIcon v-else name="user" :size="60" />
                </div>
                <h2>{{ user?.name || 'Usuario' }}</h2>
                <div class="role-badge">{{ user?.role?.name || 'Sin Rol' }}</div>

                <div class="user-details">
                    <div class="detail-group">
                        <label>Correo electrónico</label>
                        <p>{{ user?.email || 'Sin correo' }}</p>
                    </div>
                    <div class="detail-group">
                        <label>Estado de cuenta</label>
                        <p>{{ user?.account_status || 'Sin estado' }}</p>
                    </div>
                </div>

                <button type="button" class="btn-solid-dark profile-action-btn" @click="openProfileModal">
                    <Icon name="edit" :size="16" />
                    Editar perfil
                </button>
            </section>

            <section class="profile-card profile-info-card">
                <h3 class="section-title">
                    <DynamicIcon name="settings" :size="20" />
                    Información de la cuenta
                </h3>

                <div class="info-grid">
                    <div class="info-row">
                        <span class="info-label">Nombre de usuario</span>
                        <span class="info-value">{{ user?.name || 'Usuario' }}</span>
                    </div>
                    <div class="info-row">
                        <span class="info-label">Correo</span>
                        <span class="info-value">{{ user?.email || 'Sin correo' }}</span>
                    </div>
                    <div class="info-row">
                        <span class="info-label">Rol</span>
                        <span class="info-value">{{ user?.role?.name || 'Sin rol' }}</span>
                    </div>
                    <div class="info-row">
                        <span class="info-label">Avatar</span>
                        <span class="info-value">{{ user?.avatar_url ? 'Personalizado' : 'Sin imagen' }}</span>
                    </div>
                </div>

                <div class="locked-notice profile-note">
                    <div class="notice-icon">
                        <DynamicIcon name="shield" :size="22" />
                    </div>
                    <p>
                        Los campos editables se limitan al nombre de usuario, la contraseña y la imagen de perfil.
                        El correo y el rol siguen protegidos por el sistema.
                    </p>
                </div>
            </section>
        </div>

        <ModalForm
            :isVisible="showProfileModal"
            title="Editar Perfil"
            :loading="isSaving"
            size="lg"
            :columns="2"
            :fields="profileFields"
            :modelValue="profileForm"
            :errors="profileErrors"
            @close="closeProfileModal"
            @submit="submitProfile"
        >
            <template #header-icon>
                <Icon name="user" :size="20" />
            </template>

            <template #default>
                <div class="profile-modal-extra full-width">
                    <div class="profile-modal-avatar">
                        <div class="profile-modal-avatar-preview">
                            <img v-if="modalAvatarPreviewUrl" :src="modalAvatarPreviewUrl" alt="Vista previa del avatar" />
                            <DynamicIcon v-else name="user" :size="34" />
                        </div>

                        <div class="profile-modal-avatar-copy">
                            <h4>Imagen de perfil</h4>
                            <p>La imagen se recorta antes de guardar. El resultado final se convierte a WebP y se ajusta a 512 × 512 píxeles.</p>
                        </div>

                        <div class="profile-modal-avatar-actions">
                            <button type="button" class="btn-ghost" @click="openAvatarPicker">
                                <Icon name="image" :size="16" />
                                Cambiar imagen
                            </button>
                            <button
                                v-if="profileForm.avatar_image"
                                type="button"
                                class="btn-ghost danger"
                                @click="removePendingAvatar"
                            >
                                <Icon name="trash" :size="16" />
                                Quitar pendiente
                            </button>
                        </div>

                        <input
                            ref="avatarInput"
                            type="file"
                            accept="image/jpeg,image/png,image/webp"
                            class="hidden-file-input"
                            @change="handleAvatarSelected"
                        />
                    </div>

                    <div class="profile-modal-hint">
                        <div class="hint-icon">
                            <DynamicIcon name="lock" :size="18" />
                        </div>
                        <p>
                            Si quieres cambiar tu contraseña, completa también tu contraseña actual.
                        </p>
                    </div>
                </div>
            </template>
        </ModalForm>

        <ModalForm
            :isVisible="showCropModal"
            title="Recortar imagen de perfil"
            size="xl"
            :columns="1"
            @close="closeCropModal"
        >
            <template #header-icon>
                <Icon name="crop" :size="20" />
            </template>

            <template #default>
                <div class="cropper-shell">
                    <div class="cropper-main">
                        <cropper
                            v-if="cropperSource"
                            ref="cropperRef"
                            class="avatar-cropper"
                            :src="cropperSource"
                            :stencil-props="{ aspectRatio: 1 }"
                        />
                    </div>

                    <aside class="cropper-side">
                        <div class="cropper-preview-title">Vista previa</div>
                        <div class="cropper-preview-circle">
                            <img v-if="modalAvatarPreviewUrl" :src="modalAvatarPreviewUrl" alt="Vista previa del avatar recortado" />
                            <DynamicIcon v-else name="user" :size="42" />
                        </div>
                        <p class="cropper-side-text">
                            Ajusta el encuadre como en una foto de perfil de WhatsApp. La imagen final se exportará en formato WebP.
                        </p>
                    </aside>
                </div>
            </template>

            <template #footer>
                <button type="button" class="btn-ghost" @click="closeCropModal">Cancelar</button>
                <button type="button" class="btn-solid" @click="applyCrop">Usar imagen</button>
            </template>
        </ModalForm>
    </div>
</template>

<script setup>
import { computed, onBeforeUnmount, reactive, ref } from 'vue';
import { Cropper } from 'vue-advanced-cropper';
import 'vue-advanced-cropper/dist/style.css';
import DynamicIcon from '@/components/DynamicIcon.vue';
import Icon from '@/components/Icon.vue';
import ModalForm from '@/views/private/admin/components/ModalForm.vue';
import { useAlert } from '@/composables/useAlert';
import { useAuth } from '@/composables/useAuth';

const alert = useAlert();
const { user, updateProfile } = useAuth();

const showProfileModal = ref(false);
const showCropModal = ref(false);
const isSaving = ref(false);

const avatarInput = ref(null);
const cropperRef = ref(null);
const cropperSource = ref(null);
const modalAvatarPreviewUrl = ref(null);

const profileForm = reactive({
    name: '',
    current_password: '',
    password: '',
    password_confirmation: '',
    avatar_image: null,
});

const profileErrors = ref({});

const profileFields = computed(() => [
    {
        key: 'name',
        label: 'Nombre de usuario',
        type: 'text',
        placeholder: 'Ej. ivanmelo',
        required: true,
        span: 2,
    },
    {
        key: 'current_password',
        label: 'Contraseña actual',
        type: 'password',
        placeholder: 'Solo si vas a cambiar la contraseña',
        required: false,
        span: 1,
        autocomplete: 'current-password',
    },
    {
        key: 'password',
        label: 'Nueva contraseña',
        type: 'password',
        placeholder: 'Deja vacío si no cambiarás la clave',
        required: false,
        span: 1,
        autocomplete: 'new-password',
    },
    {
        key: 'password_confirmation',
        label: 'Confirmar nueva contraseña',
        type: 'password',
        placeholder: 'Repite la nueva contraseña',
        required: false,
        span: 2,
        autocomplete: 'new-password',
    },
]);

const profileAvatarUrl = computed(() => user.value?.avatar_url || null);

const resetProfileForm = () => {
    profileForm.name = user.value?.name || '';
    profileForm.current_password = '';
    profileForm.password = '';
    profileForm.password_confirmation = '';
    profileForm.avatar_image = null;
    profileErrors.value = {};
    modalAvatarPreviewUrl.value = profileAvatarUrl.value;
};

const revokeObjectUrl = (url) => {
    if (url && typeof url === 'string' && url.startsWith('blob:')) {
        URL.revokeObjectURL(url);
    }
};

const openProfileModal = () => {
    resetProfileForm();
    showProfileModal.value = true;
};

const closeProfileModal = () => {
    showProfileModal.value = false;
    profileErrors.value = {};
    profileForm.avatar_image = null;
    profileForm.password = '';
    profileForm.password_confirmation = '';
    profileForm.current_password = '';
    if (modalAvatarPreviewUrl.value !== profileAvatarUrl.value) {
        revokeObjectUrl(modalAvatarPreviewUrl.value);
    }
    modalAvatarPreviewUrl.value = profileAvatarUrl.value;
};

const openAvatarPicker = () => {
    avatarInput.value?.click();
};

const handleAvatarSelected = (event) => {
    const file = event.target.files?.[0];
    if (!file) {
        return;
    }

    if (cropperSource.value) {
        revokeObjectUrl(cropperSource.value);
    }

    cropperSource.value = URL.createObjectURL(file);
    showCropModal.value = true;
};

const closeCropModal = () => {
    showCropModal.value = false;

    if (cropperSource.value) {
        revokeObjectUrl(cropperSource.value);
        cropperSource.value = null;
    }

    if (!profileForm.avatar_image) {
        if (modalAvatarPreviewUrl.value !== profileAvatarUrl.value) {
            revokeObjectUrl(modalAvatarPreviewUrl.value);
        }
        modalAvatarPreviewUrl.value = profileAvatarUrl.value;
    }

    if (avatarInput.value) {
        avatarInput.value.value = '';
    }
};

const removePendingAvatar = () => {
    profileForm.avatar_image = null;
    if (modalAvatarPreviewUrl.value !== profileAvatarUrl.value) {
        revokeObjectUrl(modalAvatarPreviewUrl.value);
    }
    modalAvatarPreviewUrl.value = profileAvatarUrl.value;
    if (avatarInput.value) {
        avatarInput.value.value = '';
    }
};

const createWebpBlobFromCanvas = (sourceCanvas) => {
    const targetSize = 512;
    const targetCanvas = document.createElement('canvas');
    targetCanvas.width = targetSize;
    targetCanvas.height = targetSize;

    const context = targetCanvas.getContext('2d');
    if (!context) {
        return Promise.resolve(null);
    }

    context.drawImage(sourceCanvas, 0, 0, targetSize, targetSize);

    return new Promise((resolve) => {
        targetCanvas.toBlob((blob) => resolve(blob), 'image/webp', 0.92);
    });
};

const applyCrop = async () => {
    const cropper = cropperRef.value;
    if (!cropper) {
        alert.toast.error('Error', 'No se pudo cargar el recorte de imagen', 3000);
        return;
    }

    const result = cropper.getResult();
    if (!result?.canvas) {
        alert.toast.error('Error', 'Selecciona una imagen válida antes de continuar', 3000);
        return;
    }

    const blob = await createWebpBlobFromCanvas(result.canvas);
    if (!blob) {
        alert.toast.error('Error', 'No se pudo procesar la imagen recortada', 3000);
        return;
    }

    if (modalAvatarPreviewUrl.value && modalAvatarPreviewUrl.value !== profileAvatarUrl.value) {
        revokeObjectUrl(modalAvatarPreviewUrl.value);
    }

    profileForm.avatar_image = blob;
    modalAvatarPreviewUrl.value = URL.createObjectURL(blob);
    showCropModal.value = false;

    if (cropperSource.value) {
        revokeObjectUrl(cropperSource.value);
        cropperSource.value = null;
    }

    if (avatarInput.value) {
        avatarInput.value.value = '';
    }
};

const submitProfile = async () => {
    profileErrors.value = {};

    if (profileForm.password && !profileForm.current_password) {
        alert.toast.error('Error', 'Debes ingresar tu contraseña actual para cambiar la clave.', 3000);
        return;
    }

    isSaving.value = true;
    try {
        await updateProfile(profileForm);
        alert.toast.success('Perfil actualizado', 'Los cambios se guardaron correctamente.', 3000);
        closeProfileModal();
    } catch (error) {
        profileErrors.value = error.response?.data?.errors || {};
        const message = error.response?.data?.message || 'No se pudo actualizar el perfil';
        alert.toast.error('Error', message, 3000);
    } finally {
        isSaving.value = false;
    }
};

onBeforeUnmount(() => {
    if (cropperSource.value) {
        revokeObjectUrl(cropperSource.value);
    }
    if (modalAvatarPreviewUrl.value && modalAvatarPreviewUrl.value !== profileAvatarUrl.value) {
        revokeObjectUrl(modalAvatarPreviewUrl.value);
    }
});
</script>

<style scoped>
.profile-view {
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
}

.profile-header h1 {
    font-size: 1.9rem;
    font-weight: 800;
    color: var(--text-primary);
    margin-bottom: 0.35rem;
}

.profile-header p {
    color: var(--text-secondary);
}

.profile-grid {
    display: grid;
    grid-template-columns: minmax(280px, 360px) 1fr;
    gap: 1.25rem;
}

.profile-card {
    background: var(--bg-primary);
    border: 1px solid var(--border-color);
    border-radius: 20px;
    padding: 1.25rem;
    box-shadow: 0 14px 34px rgba(15, 23, 42, 0.08);
}

.profile-summary-card {
    display: flex;
    flex-direction: column;
    align-items: center;
    text-align: center;
    gap: 0.9rem;
}

.profile-avatar {
    width: 84px;
    height: 84px;
    border-radius: 50%;
    display: grid;
    place-items: center;
    overflow: hidden;
    background: var(--bg-secondary);
    border: 2px solid var(--border-color);
    color: var(--primary);
}

.profile-avatar-large {
    width: 124px;
    height: 124px;
    border: 2px solid rgba(var(--primary-rgb), 0.22);
    background: radial-gradient(circle at top, rgba(var(--primary-rgb), 0.18), rgba(255, 255, 255, 0.04));
}

.profile-avatar img {
    width: 100%;
    height: 100%;
    object-fit: cover;
}

.profile-summary-card h2 {
    font-size: 1.35rem;
    font-weight: 800;
    color: var(--text-primary);
}

.role-badge {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    padding: 0.3rem 0.7rem;
    border-radius: 999px;
    background: rgba(var(--primary-rgb), 0.14);
    color: var(--primary);
    font-size: 0.78rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.06em;
}

.user-details {
    width: 100%;
    display: grid;
    gap: 0.85rem;
    margin-top: 0.25rem;
}

.detail-group {
    padding: 0.8rem 0.9rem;
    border-radius: 14px;
    background: var(--bg-secondary);
    border: 1px solid var(--border-color);
    text-align: left;
}

.detail-group label,
.info-label {
    display: block;
    font-size: 0.72rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: var(--text-secondary);
    margin-bottom: 0.35rem;
}

.detail-group p,
.info-value {
    color: var(--text-primary);
    font-weight: 700;
}

.profile-action-btn {
    width: 100%;
    justify-content: center;
    display: inline-flex;
    gap: 0.5rem;
}

.profile-info-card {
    display: flex;
    flex-direction: column;
    gap: 1rem;
}

.section-title {
    display: flex;
    align-items: center;
    gap: 0.55rem;
    font-size: 1rem;
    color: var(--text-primary);
}

.info-grid {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 0.8rem;
}

.info-row {
    padding: 0.95rem 1rem;
    border-radius: 16px;
    background: var(--bg-secondary);
    border: 1px solid var(--border-color);
}

.locked-notice {
    display: flex;
    gap: 0.9rem;
    align-items: flex-start;
    padding: 1rem;
    border-radius: 16px;
    background: var(--bg-secondary);
    border: 1px solid var(--border-color);
    color: var(--text-secondary);
}

.notice-icon,
.hint-icon {
    display: grid;
    place-items: center;
    width: 36px;
    height: 36px;
    border-radius: 12px;
    background: rgba(var(--primary-rgb), 0.12);
    color: var(--primary);
    flex: 0 0 auto;
}

.profile-note {
    margin-top: auto;
}

.profile-modal-extra,
.cropper-shell {
    display: flex;
    flex-direction: column;
    gap: 1rem;
}

.profile-modal-avatar {
    display: grid;
    grid-template-columns: auto 1fr auto;
    gap: 1rem;
    align-items: center;
    padding: 1rem;
    border-radius: 18px;
    background: var(--bg-secondary);
    border: 1px solid var(--border-color);
}

.profile-modal-avatar-preview {
    width: 84px;
    height: 84px;
    border-radius: 50%;
    overflow: hidden;
    display: grid;
    place-items: center;
    background: var(--bg-primary);
    border: 2px solid rgba(var(--primary-rgb), 0.18);
    color: var(--primary);
}

.profile-modal-avatar-preview img,
.cropper-preview-circle img {
    width: 100%;
    height: 100%;
    object-fit: cover;
}

.profile-modal-avatar-copy h4 {
    font-size: 1rem;
    color: var(--text-primary);
    margin-bottom: 0.25rem;
}

.profile-modal-avatar-copy p,
.profile-modal-hint p,
.cropper-side-text {
    color: var(--text-secondary);
    font-size: 0.92rem;
    line-height: 1.5;
}

.profile-modal-avatar-actions {
    display: flex;
    flex-direction: column;
    gap: 0.6rem;
    align-items: stretch;
}

.hidden-file-input {
    display: none;
}

.profile-modal-hint {
    grid-column: 1 / -1;
    display: flex;
    gap: 0.75rem;
    align-items: flex-start;
    padding: 0.95rem 1rem;
    border-radius: 14px;
    background: rgba(var(--primary-rgb), 0.08);
    border: 1px solid rgba(var(--primary-rgb), 0.12);
}

.cropper-shell {
    display: grid;
    grid-template-columns: minmax(0, 1fr) 260px;
    gap: 1rem;
    min-height: 460px;
}

.cropper-main {
    min-height: 460px;
    border-radius: 18px;
    overflow: hidden;
    background: var(--bg-secondary);
    border: 1px solid var(--border-color);
}

.avatar-cropper {
    width: 100%;
    height: 100%;
    min-height: 460px;
}

.cropper-side {
    display: flex;
    flex-direction: column;
    gap: 0.9rem;
    padding: 1rem;
    border-radius: 18px;
    background: var(--bg-secondary);
    border: 1px solid var(--border-color);
}

:global([data-theme='dark']) .profile-card {
    background: linear-gradient(180deg, rgba(18, 24, 38, 0.98), rgba(13, 18, 29, 0.98));
    border-color: rgba(255, 255, 255, 0.08);
    box-shadow: 0 22px 60px rgba(0, 0, 0, 0.25);
}

:global([data-theme='dark']) .detail-group,
:global([data-theme='dark']) .info-row,
:global([data-theme='dark']) .locked-notice,
:global([data-theme='dark']) .profile-modal-avatar,
:global([data-theme='dark']) .cropper-main,
:global([data-theme='dark']) .cropper-side {
    border-color: rgba(255, 255, 255, 0.08);
    background: rgba(255, 255, 255, 0.04);
}

.cropper-preview-title {
    color: var(--text-primary);
    font-weight: 700;
}

.cropper-preview-circle {
    width: 170px;
    height: 170px;
    border-radius: 50%;
    overflow: hidden;
    display: grid;
    place-items: center;
    margin: 0 auto;
    background: radial-gradient(circle at top, rgba(var(--primary-rgb), 0.2), rgba(255, 255, 255, 0.04));
    border: 2px solid rgba(var(--primary-rgb), 0.2);
    color: var(--primary);
}

.full-width {
    grid-column: 1 / -1;
}

@media (max-width: 1100px) {
    .profile-grid,
    .cropper-shell {
        grid-template-columns: 1fr;
    }
}

@media (max-width: 720px) {
    .info-grid {
        grid-template-columns: 1fr;
    }

    .profile-modal-avatar {
        grid-template-columns: 1fr;
        justify-items: start;
    }

    .profile-modal-avatar-actions {
        width: 100%;
    }
}
</style>
