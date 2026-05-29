<template>
    <ModalForm
        :is-visible="isOpen"
        :title="modalTitle"
        :loading="currentLoading"
        :close-on-backdrop="!currentLoading"
        size="lg"
        @close="emit('close')"
        @submit="submitActiveTab"
    >
        <template #header-icon>
            <Icon :name="headerIcon" :size="20" />
        </template>

        <div class="explorer-tabs">
            <button
                type="button"
                class="tab-btn"
                :class="{ active: activeTab === 'folder' }"
                @click="activeTab = 'folder'"
            >
                <Icon name="folder-plus" :size="16" />
                <span>Carpetas</span>
            </button>
            <button
                type="button"
                class="tab-btn"
                :class="{ active: activeTab === 'upload' }"
                @click="activeTab = 'upload'"
            >
                <Icon name="file" :size="16" />
                <span>Archivos</span>
            </button>
            <button
                type="button"
                class="tab-btn"
                :class="{ active: activeTab === 'link' }"
                @click="activeTab = 'link'"
            >
                <Icon name="link" :size="16" />
                <span>Enlaces</span>
            </button>
        </div>

        <div class="explorer-tab-content">
            <ModalFolderForm
                v-show="activeTab === 'folder'"
                ref="folderFormRef"
                :isOpen="isOpen"
                :embedded="true"
                :parentUuid="parentUuid"
                :parentPublic="parentPublic"
                :folder="null"
                @created="handleFolderCreated"
            />

            <ModalFileUpload
                v-show="activeTab === 'upload'"
                ref="uploadFormRef"
                :isOpen="isOpen"
                :embedded="true"
                :folderUuid="folderUuid"
                @uploaded="handleUploaded"
            />

            <ModalLinkForm
                v-show="activeTab === 'link'"
                ref="linkFormRef"
                :isOpen="isOpen"
                :embedded="true"
                :folderUuid="folderUuid"
                @created="handleLinkCreated"
            />
        </div>

        <template #footer>
            <button type="button" class="btn-ghost" @click="emit('close')" :disabled="currentLoading">
                Cancelar
            </button>
            <button
                type="button"
                class="btn-solid"
                @click="submitActiveTab"
                :disabled="submitDisabled"
            >
                <span v-if="currentLoading" class="spinner-sm mr-2"></span>
                {{ submitLabel }}
            </button>
        </template>
    </ModalForm>
</template>

<script setup>
import { computed, ref, watch } from 'vue';
import Icon from '@/components/Icon.vue';
import ModalForm from '@/views/private/admin/components/ModalForm.vue';
import ModalFolderForm from './ModalFolderForm.vue';
import ModalFileUpload from './ModalFileUpload.vue';
import ModalLinkForm from './ModalLinkForm.vue';

const props = defineProps({
    isOpen: {
        type: Boolean,
        default: false,
    },
    parentUuid: {
        type: String,
        default: null,
    },
    parentPublic: {
        type: Boolean,
        default: true,
    },
    folderUuid: {
        type: String,
        default: null,
    },
    initialTab: {
        type: String,
        default: 'folder',
    },
});

const emit = defineEmits(['close', 'folder-created', 'uploaded', 'link-created']);

const activeTab = ref('folder');
const folderFormRef = ref(null);
const uploadFormRef = ref(null);
const linkFormRef = ref(null);

const unwrapExposeValue = (value) => {
    if (value && typeof value === 'object' && 'value' in value) {
        return value.value;
    }

    return value;
};

watch(
    () => props.isOpen,
    (isOpen) => {
        if (isOpen) {
            activeTab.value = props.initialTab === 'upload' ? 'upload' : 'folder';
        }
    },
    { immediate: true }
);

const currentLoading = computed(() => {
    if (activeTab.value === 'folder') {
        return !!unwrapExposeValue(folderFormRef.value?.isSubmitting);
    }

    if (activeTab.value === 'link') {
        return !!unwrapExposeValue(linkFormRef.value?.isSubmitting);
    }

    return !!unwrapExposeValue(uploadFormRef.value?.isUploading);
});

const modalTitle = computed(() => {
    if (activeTab.value === 'folder') return 'Nueva Carpeta';
    if (activeTab.value === 'link') return 'Nuevo Enlace';
    return 'Subir Archivos';
});

const headerIcon = computed(() => {
    if (activeTab.value === 'folder') return 'folder-plus';
    if (activeTab.value === 'link') return 'link';
    return 'file';
});

const submitLabel = computed(() => {
    if (activeTab.value === 'folder') {
        return 'Crear Carpeta';
    }

    if (activeTab.value === 'link') {
        return 'Guardar Enlace';
    }

    return currentLoading.value ? 'Subiendo...' : 'Subir Cola';
});

const submitDisabled = computed(() => {
    if (currentLoading.value) return true;

    if (activeTab.value === 'upload') {
        return !unwrapExposeValue(uploadFormRef.value?.hasUploadableItems);
    }

    return false;
});

const submitActiveTab = async () => {
    if (submitDisabled.value) return;

    if (activeTab.value === 'folder') {
        await folderFormRef.value?.submitForm?.();
        return;
    }

    if (activeTab.value === 'link') {
        await linkFormRef.value?.submitForm?.();
        return;
    }

    await uploadFormRef.value?.submitForm?.();
};

const handleFolderCreated = () => {
    emit('folder-created');
    emit('close');
};

const handleUploaded = (payload) => {
    emit('uploaded', payload);
    emit('close');
};

const handleLinkCreated = () => {
    emit('link-created');
    emit('close');
};
</script>

<style lang="scss" scoped>
.explorer-tabs {
    grid-column: 1 / -1;
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    grid-auto-rows: 40px;
    gap: 0.5rem;
    align-items: start;

    .tab-btn {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        gap: 0.45rem;
        height: 40px;
        min-height: 40px;
        padding: 0.5rem 0.75rem;
        border-radius: 10px;
        border: 1px solid var(--border-color);
        background: var(--bg-primary);
        color: var(--text-secondary);
        font-weight: 600;
        cursor: pointer;
        transition: all 0.2s ease;

        &:hover {
            border-color: var(--primary);
            color: var(--primary);
        }

        &.active {
            background: rgba(var(--primary-rgb), 0.1);
            border-color: var(--primary);
            color: var(--primary);
        }
    }
}

.explorer-tab-content {
    grid-column: 1 / -1;
}

:deep(.modal-container.modal-lg) {
    height: 640px;
    max-height: 85vh;
}

:deep(.modal-body) {
    max-height: none;
    overflow-y: auto;
}
</style>
