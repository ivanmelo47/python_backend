<template>
    <ModalForm
        :is-visible="isOpen"
        title="Mover Elemento"
        :loading="isSubmitting"
        submit-label="Mover aquí"
        size="lg"
        @close="$emit('close')"
        @submit="handleSubmit"
    >
        <template #header-icon>
            <Icon name="folder-open" :size="20" />
        </template>

        <div class="move-context">
            <p class="move-file-name" :title="file?.original_name || file?.name">
                {{ file?.original_name || file?.name || 'Archivo' }}
            </p>
            <p class="move-location">
                Destino actual: <strong>{{ currentLocationLabel }}</strong>
            </p>
        </div>

        <div class="breadcrumbs">
            <button
                v-for="crumb in breadcrumbs"
                :key="crumb.uuid || 'root'"
                type="button"
                class="crumb"
                :class="{ active: (crumb.uuid || null) === currentParentUuid }"
                @click="navigateTo(crumb.uuid || null)"
            >
                {{ crumb.name }}
            </button>
        </div>

        <div class="folders-panel">
            <div v-if="isLoadingFolders" class="state">Cargando carpetas...</div>
            <div v-else-if="folders.length === 0" class="state">No hay subcarpetas en esta ubicación.</div>
            <ul v-else class="folder-list">
                <li v-for="folder in folders" :key="folder.uuid" class="folder-row">
                    <div class="folder-main">
                        <Icon name="folder" :size="16" />
                        <span class="folder-name">{{ folder.name }}</span>
                    </div>
                    <button type="button" class="open-btn" @click="navigateTo(folder.uuid)">
                        Abrir
                    </button>
                </li>
            </ul>
        </div>

        <div v-if="!canMove" class="hint-warning">
            El elemento ya está en esta ubicación.
        </div>
    </ModalForm>
</template>

<script setup>
import { computed, ref, watch } from 'vue';
import Icon from '@/components/Icon.vue';
import ModalForm from '@/views/private/admin/components/ModalForm.vue';
import folderApi from '@/services/api/endpoints/folders';
import filesApi from '@/services/api/endpoints/files';
import { useAlert } from '@/composables/useAlert';

const props = defineProps({
    isOpen: {
        type: Boolean,
        default: false,
    },
    file: {
        type: Object,
        default: null,
    },
});

const emit = defineEmits(['close', 'moved']);
const alert = useAlert();

const isLoadingFolders = ref(false);
const isSubmitting = ref(false);
const currentParentUuid = ref(null);
const folders = ref([]);
const breadcrumbs = ref([{ uuid: null, name: 'Raíz' }]);

const sourceFolderUuid = computed(() => props.file?.folder?.uuid || null);
const currentLocationLabel = computed(() => breadcrumbs.value.map((item) => item.name).join(' / '));
const canMove = computed(() => {
    if (!props.file) return false;
    return (sourceFolderUuid.value || null) !== (currentParentUuid.value || null);
});

const normalizeCollection = (value) => {
    if (Array.isArray(value)) return value;
    if (Array.isArray(value?.data)) return value.data;
    return [];
};

const setBreadcrumbsFromResponse = (payload) => {
    const nextBreadcrumbs = [{ uuid: null, name: 'Raíz' }];

    const ancestors = normalizeCollection(payload?.ancestors);
    ancestors.forEach((ancestor) => {
        if (!ancestor?.uuid) return;
        if (!nextBreadcrumbs.some((item) => item.uuid === ancestor.uuid)) {
            nextBreadcrumbs.push({ uuid: ancestor.uuid, name: ancestor.name || 'Carpeta' });
        }
    });

    const parentRaw = payload?.parent;
    const parent = parentRaw?.data ? parentRaw.data : parentRaw;
    if (parent?.uuid && !nextBreadcrumbs.some((item) => item.uuid === parent.uuid)) {
        nextBreadcrumbs.push({ uuid: parent.uuid, name: parent.name || 'Carpeta' });
    }

    breadcrumbs.value = nextBreadcrumbs;
    currentParentUuid.value = parent?.uuid || null;
};

const loadFolders = async (parentUuid = null) => {
    isLoadingFolders.value = true;
    try {
        const response = await folderApi.getFolders({
            parent: parentUuid || null,
            per_page: 200,
            page: 1,
        });

        const payload = response?.data || {};
        folders.value = normalizeCollection(payload?.data);
        setBreadcrumbsFromResponse(payload);
    } catch (error) {
        alert.toast.error('Error', error?.response?.data?.message || 'No se pudieron cargar las carpetas.');
    } finally {
        isLoadingFolders.value = false;
    }
};

const navigateTo = async (folderUuid) => {
    await loadFolders(folderUuid || null);
};

const handleSubmit = async () => {
    if (!props.file || isSubmitting.value) return;

    if (!canMove.value) {
        alert.toast.warning('Mover elemento', 'El elemento ya está en esta ubicación.');
        return;
    }

    isSubmitting.value = true;
    try {
        await filesApi.moveFile(props.file.uuid, {
            folder_uuid: currentParentUuid.value || null,
        });

        alert.toast.success('Éxito', 'Elemento movido correctamente.');
        emit('moved');
    } catch (error) {
        alert.toast.error('Error', error?.response?.data?.message || 'No se pudo mover el elemento.');
    } finally {
        isSubmitting.value = false;
    }
};

watch(
    () => props.isOpen,
    async (isOpen) => {
        if (!isOpen) return;
        await loadFolders(null);
    },
    { immediate: true }
);
</script>

<style scoped lang="scss">
.move-context {
    margin-bottom: 0.75rem;
}

.move-file-name {
    margin: 0;
    font-size: 0.9rem;
    color: var(--text-primary);
    font-weight: 600;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.move-location {
    margin: 0.25rem 0 0;
    font-size: 0.82rem;
    color: var(--text-secondary);
}

.breadcrumbs {
    display: flex;
    flex-wrap: wrap;
    gap: 0.4rem;
    margin-bottom: 0.75rem;
}

.crumb {
    border: 1px solid var(--border-color);
    background: var(--bg-tertiary);
    color: var(--text-primary);
    border-radius: 8px;
    padding: 0.3rem 0.6rem;
    font-size: 0.78rem;
    cursor: pointer;
}

.crumb.active {
    border-color: var(--primary);
    color: var(--primary);
}

.folders-panel {
    border: 1px solid var(--border-color);
    border-radius: 10px;
    background: var(--bg-primary);
    min-height: 210px;
    max-height: 320px;
    overflow: auto;
}

.state {
    padding: 1rem;
    color: var(--text-secondary);
    font-size: 0.85rem;
}

.folder-list {
    list-style: none;
    margin: 0;
    padding: 0;
}

.folder-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0.7rem 0.9rem;
    border-bottom: 1px solid var(--border-color);
}

.folder-row:last-child {
    border-bottom: none;
}

.folder-main {
    display: flex;
    align-items: center;
    gap: 0.55rem;
    min-width: 0;
}

.folder-name {
    color: var(--text-primary);
    font-size: 0.86rem;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.open-btn {
    border: 1px solid var(--border-color);
    background: var(--bg-tertiary);
    color: var(--text-primary);
    border-radius: 8px;
    padding: 0.25rem 0.7rem;
    font-size: 0.78rem;
    cursor: pointer;
}

.hint-warning {
    margin-top: 0.7rem;
    color: var(--text-secondary);
    font-size: 0.8rem;
}
</style>
