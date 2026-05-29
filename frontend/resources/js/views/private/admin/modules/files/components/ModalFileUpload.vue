<template>
    <component
        :is="embedded ? 'div' : ModalForm"
        v-bind="modalProps"
        class="upload-form-shell"
        :class="{ 'upload-form-embedded': embedded }"
        @close="handleClose"
        @submit="startUploadQueue"
    >
        <template v-if="!embedded" #header-icon>
            <Icon name="file" :size="20" />
        </template>

        <div class="upload-panel">
            <input
                ref="fileInputRef"
                type="file"
                class="hidden-file-input"
                multiple
                @change="handleFilesSelected"
            >

            <!-- Encryption Options -->
            <div class="encryption-section">
                <div class="encryption-header">
                    <input
                        type="checkbox"
                        id="enableEncryption"
                        v-model="encryptionEnabled"
                        class="encryption-checkbox"
                        :disabled="isUploading"
                    >
                    <label for="enableEncryption" class="encryption-label">
                        <Icon name="lock" :size="16" />
                        <span>Encriptar archivos con contraseña</span>
                    </label>
                </div>

                <div v-if="encryptionEnabled" class="encryption-password-field">
                    <input
                        v-model="encryptionPassword"
                        type="password"
                        placeholder="Contraseña de encriptación (mínimo 6 caracteres)"
                        class="password-input"
                        :disabled="isUploading"
                    >
                    <p class="encryption-note">
                        <Icon name="alert-triangle" :size="14" />
                        <span>Los archivos se encriptarán con AES-256. Solo podrán ser visualizados con esta contraseña. <strong>No olvides tu contraseña</strong>, no hay forma de recuperarla.</span>
                    </p>
                </div>
            </div>

            <div
                class="dropzone"
                :class="{ 'is-drag-over': isDragOver, 'is-disabled': isUploading }"
                @click="!isUploading && openPicker()"
                @dragenter.prevent="onDragEnter"
                @dragover.prevent="onDragOver"
                @dragleave.prevent="onDragLeave"
                @drop.prevent="onDrop"
            >
                <div class="dropzone-icon">
                    <Icon name="file" :size="26" />
                </div>
                <div class="dropzone-content">
                    <span class="dropzone-title">Arrastra archivos aquí o haz clic para seleccionar</span>
                    <span class="dropzone-subtitle">Puedes agregar uno o varios archivos a la cola</span>
                </div>
            </div>

            <div v-if="queue.length === 0" class="queue-empty">
                Aún no hay archivos en la cola.
            </div>

            <div v-else class="queue-list">
                <div v-for="item in queue" :key="item.id" class="queue-item">
                    <div class="queue-header">
                        <div class="queue-meta">
                            <span class="queue-name">{{ item.file.name }}</span>
                            <span class="queue-size">{{ formatBytes(item.file.size) }}</span>
                        </div>

                        <div class="queue-controls">
                            <span class="status-badge" :class="`is-${item.status}`">{{ statusLabel(item.status) }}</span>
                            <button
                                v-if="!isUploading && item.status !== 'uploading'"
                                class="btn-remove"
                                type="button"
                                @click="removeFromQueue(item.id)"
                            >
                                <Icon name="x" :size="14" />
                            </button>
                        </div>
                    </div>

                    <div class="progress-track">
                        <div
                            class="progress-fill"
                            :class="`is-${item.status}`"
                            :style="{ width: `${getProgressPercent(item)}%` }"
                        ></div>
                    </div>

                    <div v-if="item.status === 'error'" class="queue-error">
                        {{ item.errorMessage || 'Error al subir este archivo.' }}
                    </div>
                </div>
            </div>
        </div>

        <template v-if="!embedded" #footer>
            <button
                type="button"
                class="btn-ghost"
                @click="clearQueue"
                :disabled="isUploading || queue.length === 0"
            >
                Limpiar cola
            </button>
            <div class="footer-spacer"></div>
            <button type="button" class="btn-ghost" @click="handleClose" :disabled="isUploading">
                Cerrar
            </button>
            <button
                type="button"
                class="btn-solid"
                @click="startUploadQueue"
                :disabled="isUploading || !hasUploadableItems"
            >
                <span v-if="isUploading" class="spinner-sm mr-2"></span>
                {{ isUploading ? 'Subiendo...' : 'Subir Cola' }}
            </button>
        </template>
    </component>
</template>

<script setup>
import { computed, ref, watch } from 'vue';
import Icon from '@/components/Icon.vue';
import ModalForm from '@/views/private/admin/components/ModalForm.vue';
import filesApi from '@/services/api/endpoints/files';
import { useAlert } from '@/composables/useAlert';

const props = defineProps({
    isOpen: {
        type: Boolean,
        default: false,
    },
    embedded: {
        type: Boolean,
        default: false,
    },
    folderUuid: {
        type: String,
        default: null,
    },
});

const emit = defineEmits(['close', 'uploaded']);
const alert = useAlert();

const fileInputRef = ref(null);
const queue = ref([]);
const isUploading = ref(false);
const isDragOver = ref(false);
const encryptionEnabled = ref(false);
const encryptionPassword = ref('');
let localQueueId = 0;

const hasUploadableItems = computed(() => queue.value.some(item => item.status !== 'success'));

const embedded = computed(() => props.embedded);

const modalProps = computed(() => {
    if (embedded.value) return {};

    return {
        isVisible: props.isOpen,
        title: 'Subir Archivos',
        loading: isUploading.value,
        closeOnBackdrop: !isUploading.value,
        submitLabel: 'Subir Cola',
        size: 'lg',
    };
});

watch(() => props.isOpen, (isOpen) => {
    if (isOpen) {
        queue.value = [];
        isUploading.value = false;
        if (fileInputRef.value) {
            fileInputRef.value.value = '';
        }
    }
});

const openPicker = () => {
    fileInputRef.value?.click();
};

const handleFilesSelected = (event) => {
    const selectedFiles = Array.from(event?.target?.files || []);
    addFilesToQueue(selectedFiles);

    if (fileInputRef.value) {
        fileInputRef.value.value = '';
    }
};

const addFilesToQueue = (selectedFiles) => {
    if (!selectedFiles?.length) return;

    selectedFiles.forEach((file) => {
        localQueueId += 1;
        queue.value.push({
            id: localQueueId,
            file,
            progress: 0,
            status: 'pending',
            errorMessage: '',
        });
    });
};

const onDragEnter = () => {
    if (isUploading.value) return;
    isDragOver.value = true;
};

const onDragOver = () => {
    if (isUploading.value) return;
    isDragOver.value = true;
};

const onDragLeave = (event) => {
    if (isUploading.value) return;
    if (event?.currentTarget && event.relatedTarget && event.currentTarget.contains(event.relatedTarget)) {
        return;
    }
    isDragOver.value = false;
};

const onDrop = (event) => {
    if (isUploading.value) return;

    isDragOver.value = false;
    const droppedFiles = Array.from(event?.dataTransfer?.files || []);
    addFilesToQueue(droppedFiles);
};

const removeFromQueue = (id) => {
    queue.value = queue.value.filter(item => item.id !== id);
};

const clearQueue = () => {
    queue.value = [];
};

const handleClose = () => {
    if (!isUploading.value) {
        emit('close');
    }
};

const uploadItem = async (item, conflictStrategy = 'ask') => {
    const password = encryptionEnabled.value && encryptionPassword.value
        ? encryptionPassword.value
        : null;

    return filesApi.uploadFile(item.file, props.folderUuid, {
        onUploadProgress: (progressEvent) => {
            const total = progressEvent.total || item.file.size;
            if (!total) return;
            item.progress = Math.min(100, Math.round((progressEvent.loaded * 100) / total));
        },
    }, conflictStrategy, password);
};

const resolveDuplicateNameConflict = async (fileName) => {
    const action = await alert.fire({
        title: 'Archivo duplicado',
        text: `Ya existe un archivo llamado "${fileName}" en esta carpeta. ¿Qué deseas hacer?`,
        type: 'warning',
        showCancel: true,
        showNeutral: true,
        confirmText: 'Reemplazar',
        cancelText: 'Cancelar',
        neutralText: 'Conservar ambos',
    });

    if (action === true) return 'replace';
    if (action === 'neutral') return 'rename';
    return 'cancel';
};

const startUploadQueue = async () => {
    if (!hasUploadableItems.value || isUploading.value) return;

    // Validate encryption password if encryption is enabled
    if (encryptionEnabled.value) {
        if (!encryptionPassword.value || encryptionPassword.value.trim() === '') {
            alert.toast.error('Error', 'Debes proporcionar una contraseña de encriptación.');
            return;
        }

        if (encryptionPassword.value.length < 6) {
            alert.toast.error('Error', 'La contraseña de encriptación debe tener al menos 6 caracteres.');
            return;
        }
    }

    isUploading.value = true;

    queue.value.forEach((item) => {
        if (item.status !== 'success') {
            item.status = 'pending';
            item.progress = 0;
            item.errorMessage = '';
        }
    });

    let successCount = 0;
    let errorCount = 0;

    for (const item of queue.value) {
        if (item.status === 'success') {
            continue;
        }

        try {
            item.status = 'uploading';

            try {
                await uploadItem(item, 'ask');
            } catch (error) {
                if (error?.response?.status === 409) {
                    const strategy = await resolveDuplicateNameConflict(item.file.name);

                    if (strategy === 'cancel') {
                        item.status = 'error';
                        item.errorMessage = 'Subida cancelada por el usuario.';
                        alert.toast.info('Cancelado', `Se canceló la subida de "${item.file.name}".`);
                        errorCount += 1;
                        continue;
                    }

                    await uploadItem(item, strategy);
                } else {
                    throw error;
                }
            }

            item.progress = 100;
            item.status = 'success';
            successCount += 1;
        } catch (error) {
            item.status = 'error';
            item.errorMessage = extractErrorMessage(error);
            errorCount += 1;
        }
    }

    isUploading.value = false;

    if (successCount > 0) {
        emit('uploaded', {
            successCount,
            errorCount,
        });
    }

    if (errorCount === 0 && successCount > 0) {
        const message = successCount === 1
            ? 'Archivo subido correctamente.'
            : `Se subieron ${successCount} archivos correctamente.`;

        alert.toast.success('Éxito', message);
        if (!embedded.value) {
            emit('close');
        }
    }
};

const statusLabel = (status) => {
    if (status === 'uploading') return 'Subiendo';
    if (status === 'success') return 'Completado';
    if (status === 'error') return 'Error';
    return 'Pendiente';
};

const getProgressPercent = (item) => {
    if (item?.status === 'success') {
        return 100;
    }

    const percent = Number(item?.progress || 0);
    if (Number.isNaN(percent)) {
        return 0;
    }

    return Math.max(0, Math.min(100, percent));
};

const extractErrorMessage = (error) => {
    return error?.response?.data?.data?.message
        || error?.response?.data?.message
        || 'No se pudo subir el archivo.';
};

const formatBytes = (bytes) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
};

defineExpose({
    submitForm: startUploadQueue,
    isUploading,
    hasUploadableItems,
});
</script>

<style lang="scss" scoped>
.upload-panel {
    grid-column: 1 / -1;
    display: flex;
    flex-direction: column;
    gap: 0.75rem;

    .hidden-file-input {
        display: none;
    }

    .encryption-section {
        display: flex;
        flex-direction: column;
        gap: 0.75rem;
        padding: 1rem;
        border-radius: 10px;
        border: 1px solid var(--border-color);
        background: var(--bg-secondary);

        .encryption-header {
            display: flex;
            align-items: center;
            gap: 0.5rem;

            .encryption-checkbox {
                width: 18px;
                height: 18px;
                cursor: pointer;
                accent-color: var(--primary);
            }

            .encryption-label {
                display: flex;
                align-items: center;
                gap: 0.5rem;
                color: var(--text-primary);
                font-size: 0.95rem;
                font-weight: 600;
                cursor: pointer;
                user-select: none;

                span {
                    margin-top: 1px;
                }
            }
        }

        .encryption-password-field {
            display: flex;
            flex-direction: column;
            gap: 0.5rem;
            padding-left: 1.65rem;

            .password-input {
                width: 100%;
                padding: 0.65rem 0.85rem;
                border: 1px solid var(--border-color);
                border-radius: 8px;
                background: var(--bg-primary);
                color: var(--text-primary);
                font-size: 0.9rem;
                outline: none;
                transition: border-color 0.2s ease;

                &:focus {
                    border-color: var(--primary);
                }

                &::placeholder {
                    color: var(--text-tertiary);
                }

                &:disabled {
                    opacity: 0.6;
                    cursor: not-allowed;
                }
            }

            .encryption-note {
                display: flex;
                align-items: flex-start;
                gap: 0.5rem;
                padding: 0.65rem;
                border-radius: 6px;
                background: rgba(var(--warning-rgb, 255, 193, 7), 0.1);
                color: var(--text-secondary);
                font-size: 0.8rem;
                line-height: 1.4;

                svg {
                    color: var(--warning, #ffc107);
                    flex-shrink: 0;
                    margin-top: 2px;
                }

                strong {
                    color: var(--warning, #ffc107);
                    font-weight: 700;
                }
            }
        }
    }

    .dropzone {
        display: flex;
        align-items: center;
        gap: 0.85rem;
        min-height: 110px;
        padding: 1.25rem;
        border-radius: 12px;
        border: 1px dashed var(--border-color);
        background: var(--bg-primary);
        cursor: pointer;
        transition: border-color 0.2s ease, background 0.2s ease;

        &:hover {
            border-color: var(--primary);
            background: var(--bg-secondary);
        }

        &.is-drag-over {
            border-color: var(--primary);
            background: rgba(var(--primary-rgb), 0.08);
        }

        &.is-disabled {
            opacity: 0.6;
            cursor: not-allowed;
        }

        .dropzone-icon {
            width: 52px;
            height: 52px;
            border-radius: 10px;
            border: 1px solid var(--border-color);
            background: var(--bg-secondary);
            color: var(--primary);
            display: flex;
            align-items: center;
            justify-content: center;
            flex-shrink: 0;
        }

        .dropzone-content {
            display: flex;
            flex-direction: column;
            gap: 0.2rem;

            .dropzone-title {
                color: var(--text-primary);
                font-size: 1.05rem;
                font-weight: 600;
            }

            .dropzone-subtitle {
                color: var(--text-tertiary);
                font-size: 0.86rem;
            }
        }
    }

    .footer-spacer {
        flex: 1;
    }

    .queue-empty {
        padding: 1rem;
        border-radius: 10px;
        border: 1px dashed var(--border-color);
        color: var(--text-tertiary);
        font-size: 0.9rem;
    }

    .queue-list {
        display: flex;
        flex-direction: column;
        gap: 0.65rem;
        max-height: 330px;
        overflow-y: auto;
        padding-right: 0.25rem;
    }

    .queue-item {
        border: 1px solid var(--border-color);
        background: var(--bg-secondary);
        border-radius: 10px;
        padding: 0.75rem;
        display: flex;
        flex-direction: column;
        gap: 0.5rem;
    }

    .queue-header {
        display: flex;
        align-items: flex-start;
        justify-content: space-between;
        gap: 0.75rem;
    }

    .queue-meta {
        display: flex;
        flex-direction: column;
        min-width: 0;

        .queue-name {
            color: var(--text-primary);
            font-size: 0.9rem;
            font-weight: 600;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            max-width: 310px;
        }

        .queue-size {
            color: var(--text-tertiary);
            font-size: 0.75rem;
        }
    }

    .queue-controls {
        display: flex;
        align-items: center;
        gap: 0.4rem;
    }

    .status-badge {
        font-size: 0.7rem;
        font-weight: 700;
        border-radius: 999px;
        padding: 0.2rem 0.5rem;
        border: 1px solid var(--border-color);
        color: var(--text-tertiary);

        &.is-uploading {
            color: var(--primary);
            border-color: var(--primary);
        }

        &.is-success {
            color: var(--primary);
            border-color: var(--primary);
        }

        &.is-error {
            color: var(--error);
            border-color: var(--error);
        }
    }

    .btn-remove {
        width: 24px;
        height: 24px;
        border-radius: 50%;
        border: 1px solid var(--border-color);
        background: transparent;
        color: var(--text-tertiary);
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
    }

    .progress-track {
        width: 100%;
        height: 8px;
        border-radius: 999px;
        background: var(--bg-tertiary);
        overflow: hidden;
    }

    .progress-fill {
        height: 100%;
        width: 0;
        border-radius: inherit;
        background: var(--border-color);
        transition: width 0.2s ease;

        &.is-uploading {
            background: var(--primary);
        }

        &.is-success {
            background: var(--primary);
        }

        &.is-error {
            background: var(--error);
        }
    }

    .queue-error {
        color: var(--error);
        font-size: 0.78rem;
    }
}
</style>
