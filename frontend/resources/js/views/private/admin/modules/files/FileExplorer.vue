<template>
    <div class="explorer-main-wrapper">
        <!-- Navigation Tabs -->
        <div class="view-navigation-tabs">
            <div class="tabs-inner">
                <button 
                    class="nav-tab" 
                    :class="{ active: activeTab === 'explorer' }"
                    @click="activeTab = 'explorer'"
                >
                    <Icon name="folder" :size="18" />
                    <span>Mi Unidad</span>
                    <div class="active-indicator"></div>
                </button>
                <button 
                    class="nav-tab" 
                    :class="{ active: activeTab === 'links' }"
                    @click="activeTab = 'links'"
                >
                    <Icon name="link" :size="18" />
                    <span>Enlaces Públicos</span>
                    <div class="active-indicator"></div>
                </button>
            </div>
        </div>

        <div v-if="activeTab === 'explorer'" class="explorer-view-content">
            <div class="file-explorer">
        <FileExplorerHeader
            :breadcrumbs="breadcrumbs"
            :currentFolderUuid="currentFolderUuid"
            :layoutConfig="layoutConfig"
            :pagination="explorerPagination"
            :foldersLength="explorerPagination?.total || 0"
            :itemsPerPage="itemsPerPage"
            :searchQuery="searchQuery"
            :sortField="sortField"
            :sortDirection="sortDirection"
            :viewMode="viewMode"
            @go-root="goToFolder(null)"
            @go-folder="goToFolder"
            @page-change="handlePageChange"
            @update:itemsPerPage="setItemsPerPage"
            @update:searchQuery="searchQuery = $event"
            @update:sortField="handleSortFieldChange"
            @update:sortDirection="handleSortDirectionChange"
            @set-view-mode="setViewMode"
            @open-actions-modal="openActionsModal('folder')"
        />

        <div v-if="loading || filesLoading" class="explorer-loading">
            <div class="loader"></div>
            <span>Cargando contenido...</span>
        </div>

        <div v-else-if="folders.length === 0 && files.length === 0" class="explorer-empty">
            <Icon name="folder" :size="64" />
            <h3>No se encontraron elementos</h3>
            <p>Comienza creando una carpeta, sube un archivo, guarda un enlace o ajusta tu búsqueda.</p>
        </div>

        <div v-else class="explorer-body">
            <FileExplorerGrid
                v-if="viewMode === 'grid'"
                :folders="folders"
                :files="files"
                :activeDropdownUuid="activeDropdownUuid"
                :isOwner="isOwner"
                :isFileOwner="isFileOwner"
                :getFolderStatusIcon="getFolderStatusIcon"
                :sortField="sortField"
                :sortDirection="sortDirection"
                @go-folder="goToFolder"
                @toggle-dropdown="toggleDropdown"
                @close-dropdown="closeDropdown"
                @edit-folder="editFolder"
                @edit-file="editFile"
                @delete-folder="confirmDelete"
                @delete-file="confirmDeleteFile"
                @open-link="openLinkItem"
                @download-file="downloadFile"
                @preview-file="openFilePreview"
                @move-file="openMoveFile"
                @encrypt-file="handleEncryptFile"
                @decrypt-file="handleDecryptFile"
                @share-link="handleShareLink"
                @view-link="handleViewLink"
            />

            <FileExplorerList
                v-else
                :folders="folders"
                :files="files"
                :activeDropdownUuid="activeDropdownUuid"
                :isOwner="isOwner"
                :isFileOwner="isFileOwner"
                :getFolderStatusIcon="getFolderStatusIcon"
                :formatDate="formatDate"
                :sortField="sortField"
                :sortDirection="sortDirection"
                @go-folder="goToFolder"
                @toggle-dropdown="toggleDropdown"
                @close-dropdown="closeDropdown"
                @edit-folder="editFolder"
                @edit-file="editFile"
                @delete-folder="confirmDelete"
                @delete-file="confirmDeleteFile"
                @open-link="openLinkItem"
                @download-file="downloadFile"
                @preview-file="openFilePreview"
                @move-file="openMoveFile"
                @encrypt-file="handleEncryptFile"
                @decrypt-file="handleDecryptFile"
                @share-link="handleShareLink"
                @view-link="handleViewLink"
            />
        </div>

        <!-- Footer Pagination -->
        <Pagination
            v-if="explorerPagination && explorerPagination.total > 0 && !layoutConfig?.fitContentToScreen?.value"
            :pagination="explorerPagination"
            :itemsPerPage="itemsPerPage"
            @page-change="handlePageChange"
            @update:itemsPerPage="setItemsPerPage"
        />

        <ModalExplorerActions
            v-if="showActionsModal"
            :isOpen="showActionsModal"
            :parentUuid="currentFolderUuid"
            :parentPublic="currentFolderPublic"
            :folderUuid="currentFolderUuid"
            :initialTab="actionsInitialTab"
            @close="showActionsModal = false"
            @folder-created="handleFolderCreatedFromActions"
            @uploaded="handleFilesUploadedFromActions"
            @link-created="handleLinkCreatedFromActions"
        />

        <!-- Edit Folder Modal -->
        <ModalFolderForm
            v-if="showCreateModal"
            :isOpen="showCreateModal"
            :parentUuid="currentFolderUuid"
            :parentPublic="currentFolderPublic"
            :folder="folderToEdit"
            @close="showCreateModal = false; folderToEdit = null"
            @created="handleFolderCreated"
            @updated="handleFolderUpdated"
        />

        <ModalFileEdit
            v-if="showFileEditModal && fileToEdit"
            :isOpen="showFileEditModal"
            :file="fileToEdit"
            :files="files"
            @close="showFileEditModal = false; fileToEdit = null"
            @updated="handleFileUpdated"
        />

        <ModalFileMove
            v-if="showFileMoveModal && fileToMove"
            :isOpen="showFileMoveModal"
            :file="fileToMove"
            @close="showFileMoveModal = false; fileToMove = null"
            @moved="handleFileMoved"
        />

        <ModalImagePreview
            v-if="showImagePreviewModal"
            :imageUrl="previewImageUrl"
            :title="previewImageTitle"
            :previewType="previewFileType"
            :showOpenInOffice="(previewFileType === 'pdf' || previewFileType === 'office' || previewFileType === 'excel' || previewFileType === 'word' || previewFileType === 'powerpoint') && !!previewFileUuid"
            :officeMeta="previewOfficeMeta"
            @open-onlyoffice="openPreviewInOnlyOffice"
            @close="closeImagePreview"
        />

        <ModalDecryptFile
            v-if="showDecryptModal"
            :isOpen="showDecryptModal"
            :file="fileToDecrypt"
            @close="showDecryptModal = false; fileToDecrypt = null"
            @success="handleDecryptSuccess"
        />

        <ModalDownloadEncrypted
            v-if="showDownloadEncryptedModal"
            :isOpen="showDownloadEncryptedModal"
            :file="fileToDownloadEncrypted"
            @close="showDownloadEncryptedModal = false; fileToDownloadEncrypted = null"
        />

        <ModalEncryptFile
            v-if="showEncryptModal"
            :isOpen="showEncryptModal"
            :file="fileToEncrypt"
            @close="showEncryptModal = false; fileToEncrypt = null"
            @success="handleEncryptSuccess"
        />

        <ModalShareLink
            v-if="showShareModal"
            :isOpen="showShareModal"
            :item="itemToShare"
            :isFolder="isSharedFolder"
            @close="showShareModal = false; itemToShare = null"
        />

        <ModalViewSharedLink
            v-if="showViewSharedLinkModal"
            :isOpen="showViewSharedLinkModal"
            :sharedLink="sharedLinkToView"
            @close="showViewSharedLinkModal = false; sharedLinkToView = null"
        />

            </div>
        </div>

        <div v-else class="links-view-content">
            <PublicLinksManager />
        </div>
    </div>
</template>

<script setup>
import { ref, computed, watch, inject, onUnmounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import Icon from '@/components/Icon.vue';
import Pagination from '@/components/Pagination.vue';
import ModalFolderForm from './components/ModalFolderForm.vue';
import ModalExplorerActions from './components/ModalExplorerActions.vue';
import FileExplorerHeader from './components/FileExplorerHeader.vue';
import FileExplorerGrid from './components/FileExplorerGrid.vue';
import FileExplorerList from './components/FileExplorerList.vue';
import ModalFileEdit from './components/ModalFileEdit.vue';
import ModalFileMove from './components/ModalFileMove.vue';
import ModalImagePreview from './components/ModalImagePreview.vue';
import ModalDecryptFile from './components/ModalDecryptFile.vue';
import ModalDownloadEncrypted from './components/ModalDownloadEncrypted.vue';
import ModalEncryptFile from './components/ModalEncryptFile.vue';
import ModalShareLink from './components/ModalShareLink.vue';
import ModalViewSharedLink from './components/ModalViewSharedLink.vue';
import PublicLinksManager from './components/PublicLinksManager.vue';

// ... existing code
import folderApi from '@/services/api/endpoints/folders';
import filesApi from '@/services/api/endpoints/files';
import { useAlert } from '@/composables/useAlert';
import { useAuth } from '@/composables/useAuth';
import { useTableConfig } from '@/composables/useTableConfig';

const alert = useAlert();
const route = useRoute();
const router = useRouter();
const { user } = useAuth();
const { viewMode, setViewMode, itemsPerPage, setItemsPerPage } = useTableConfig();
const layoutConfig = inject('layoutConfig', null);

// Tabs
const activeTabStorageKey = 'fileExplorer_activeTab';
const activeTab = ref(localStorage.getItem(activeTabStorageKey) || 'explorer');

watch(activeTab, (newVal) => {
    localStorage.setItem(activeTabStorageKey, newVal);
});

// Refs
const currentFolderUuid = ref(null);
const breadcrumbs = ref([]);
const showActionsModal = ref(false);
const actionsInitialTab = ref('folder');
const showCreateModal = ref(false);
const searchQuery = ref('');
const activeDropdownUuid = ref(null);
const folderToEdit = ref(null);
const fileToEdit = ref(null);
const showFileEditModal = ref(false);
const fileToMove = ref(null);
const showFileMoveModal = ref(false);
const showImagePreviewModal = ref(false);
const showDecryptModal = ref(false);
const fileToDecrypt = ref(null);
const showDownloadEncryptedModal = ref(false);
const fileToDownloadEncrypted = ref(null);
const showEncryptModal = ref(false);
const fileToEncrypt = ref(null);
const showShareModal = ref(false);
const itemToShare = ref(null);
const isSharedFolder = ref(false);
const showViewSharedLinkModal = ref(false);
const sharedLinkToView = ref(null);
const previewImageUrl = ref('');
const previewImageTitle = ref('');
const previewFileType = ref('image');
const previewFileUuid = ref(null);
const previewOfficeMeta = ref(null);
const previewImageLoading = ref(false);
const folders = ref([]);
const files = ref([]);
const loading = ref(false);
const filesLoading = ref(false);
const explorerPagination = ref(null);
const usingLegacyFallback = ref(false);
const legacyNoticeShown = ref(false);
const sortField = ref('created_at');
const sortDirection = ref('desc');
const parsedOfficePreviewEnabled = String(import.meta.env.VITE_ENABLE_PARSED_OFFICE_PREVIEW ?? 'true').toLowerCase() === 'true';

const allowedSortFields = ['created_at', 'updated_at', 'name', 'type'];
const parseSortField = (value) =>
    allowedSortFields.includes(String(value || '')) ? String(value) : 'created_at';
const parseSortDirection = (value) =>
    String(value || '').toLowerCase() === 'asc' ? 'asc' : 'desc';

const parsePage = (value) => {
    const p = Number.parseInt(value, 10);
    return Number.isFinite(p) && p > 0 ? p : 1;
};

const setPageInUrl = async (page, { replace = false } = {}) => {
    const targetPage = String(parsePage(page));
    const currentPage = String(route.query.page || '1');

    if (currentPage === targetPage) {
        return false;
    }

    const query = {
        ...route.query,
        page: targetPage,
    };

    if (replace) {
        await router.replace({ name: route.name, params: route.params, query });
    } else {
        await router.push({ name: route.name, params: route.params, query });
    }

    return true;
};

const setSortInUrl = async ({ field, direction }, { replace = false } = {}) => {
    const nextField = parseSortField(field);
    const nextDirection = parseSortDirection(direction);

    const currentField = parseSortField(route.query.sort_by);
    const currentDirection = parseSortDirection(route.query.sort_dir);

    if (currentField === nextField && currentDirection === nextDirection) {
        return false;
    }

    const query = {
        ...route.query,
        sort_by: nextField,
        sort_dir: nextDirection,
        page: '1',
    };

    if (replace) {
        await router.replace({ name: route.name, params: route.params, query });
    } else {
        await router.push({ name: route.name, params: route.params, query });
    }

    return true;
};

// Source of truth for current folder privacy
const currentFolderPublicState = ref(true);
const currentFolderPublic = computed(() => currentFolderPublicState.value);

// Helper to check if current user owns the folder
const isOwner = (folder) => {
    if (!folder || !user.value) return false;
    if (folder.owner?.uuid && user.value.uuid) return folder.owner.uuid === user.value.uuid;
    if (folder.user_id && user.value.id) return folder.user_id == user.value.id;
    if (folder.owner?.name && user.value.name) return folder.owner.name === user.value.name;
    return false;
};

const isFileOwner = (file) => {
    if (!file || !user.value) return false;
    if (file.owner?.uuid && user.value.uuid) return file.owner.uuid === user.value.uuid;
    if (file.user_id && user.value.id) return file.user_id == user.value.id;
    return false;
};

// Helper to get folder status icon
const getFolderStatusIcon = (folder) => {
    if (folder.shared_users && folder.shared_users.length > 0) return 'userShare';
    if (folder.is_public) return 'unlock';
    return 'lock';
};

const getCreatedTimestamp = (entry) => {
    const raw = entry?.created_at || entry?.uploaded_at || null;
    const time = raw ? new Date(raw).getTime() : 0;
    return Number.isNaN(time) ? 0 : time;
};

const buildLegacyCombined = (folderItems, fileItems) => {
    const merged = [
        ...(folderItems || []).map((folder) => ({ type: 'folder', data: folder, createdAt: getCreatedTimestamp(folder) })),
        ...(fileItems || []).map((file) => ({ type: 'file', data: file, createdAt: getCreatedTimestamp(file) })),
    ];

    const direction = sortDirection.value === 'asc' ? 1 : -1;
    const getUpdatedTimestamp = (entry) => {
        const raw = entry?.updated_at || entry?.uploaded_at || entry?.created_at || null;
        const time = raw ? new Date(raw).getTime() : 0;
        return Number.isNaN(time) ? 0 : time;
    };

    const getSortableName = (item) => {
        if (item.type === 'folder') return String(item.data?.name || '').toLowerCase();
        return String(item.data?.is_link ? item.data?.name : item.data?.original_name || '').toLowerCase();
    };

    merged.sort((a, b) => {
        if (sortField.value === 'name') {
            const result = getSortableName(a).localeCompare(getSortableName(b), 'es', { sensitivity: 'base' });
            if (result !== 0) return result * direction;
        } else if (sortField.value === 'updated_at') {
            const result = getUpdatedTimestamp(a.data) - getUpdatedTimestamp(b.data);
            if (result !== 0) return result * direction;
        } else if (sortField.value === 'type') {
            const typeResult = (a.type === 'folder' ? 0 : 1) - (b.type === 'folder' ? 0 : 1);
            if (typeResult !== 0) return typeResult * direction;
        } else {
            const result = a.createdAt - b.createdAt;
            if (result !== 0) return result * direction;
        }

        return b.createdAt - a.createdAt;
    });

    return merged;
};

const applyLegacyPagination = (allItems, page = 1) => {
    const perPage = Number(itemsPerPage.value) || 10;
    const total = allItems.length;
    const lastPage = Math.max(1, Math.ceil(total / perPage));
    const safePage = Math.min(Math.max(1, page), lastPage);
    const start = (safePage - 1) * perPage;
    const chunk = allItems.slice(start, start + perPage);

    folders.value = chunk.filter((item) => item.type === 'folder').map((item) => item.data);
    files.value = chunk.filter((item) => item.type === 'file').map((item) => item.data);

    explorerPagination.value = {
        current_page: safePage,
        last_page: lastPage,
        per_page: perPage,
        total,
        from: total === 0 ? 0 : start + 1,
        to: total === 0 ? 0 : Math.min(start + perPage, total),
    };
};

const fetchLegacyExplorerData = async (page = 1) => {
    const [foldersResponse, filesResponse] = await Promise.all([
        folderApi.getFolders({
            parent: currentFolderUuid.value,
            page: 1,
            per_page: 300,
            search: searchQuery.value,
        }),
        filesApi.getFiles({
            folder_uuid: currentFolderUuid.value,
            search: searchQuery.value,
            per_page: 300,
            page: 1,
        }),
    ]);

    const folderData = foldersResponse?.data || {};
    const folderItems = folderData.data || [];
    const fileItems = filesResponse?.data?.data || [];

    const merged = buildLegacyCombined(folderItems, fileItems);
    applyLegacyPagination(merged, page);

    if (folderData.parent) {
        currentFolderPublicState.value = !!folderData.parent.is_public;
    } else if (currentFolderUuid.value === null) {
        currentFolderPublicState.value = true;
    }

    if (folderData.ancestors) {
        const ancestors = folderData.ancestors.map((f) => ({
            uuid: f.uuid,
            name: f.name,
            is_public: !!f.is_public,
        }));

        if (folderData.parent) {
            ancestors.push({
                uuid: folderData.parent.uuid,
                name: folderData.parent.name,
                is_public: !!folderData.parent.is_public,
            });
        }

        breadcrumbs.value = ancestors;
    } else {
        breadcrumbs.value = [];
    }
};

const fetchExplorerData = async (page = 1) => {
    loading.value = true;
    filesLoading.value = true;
    try {
        const response = await folderApi.getExplorerItems({
            parent: currentFolderUuid.value,
            page,
            per_page: itemsPerPage.value,
            search: searchQuery.value,
            sort_by: sortField.value,
            sort_dir: sortDirection.value,
        });

        if (response?.data) {
            const payload = response.data;
            const items = payload.data || [];

            folders.value = items
                .filter((item) => item.type === 'folder')
                .map((item) => item.data);

            files.value = items
                .filter((item) => item.type === 'file')
                .map((item) => item.data);

            explorerPagination.value = payload.meta || null;

            if (explorerPagination.value?.current_page) {
                await setPageInUrl(explorerPagination.value.current_page, { replace: true });
            }

            // Sync privacy from API if available
            if (payload.parent) {
                currentFolderPublicState.value = !!payload.parent.is_public;
            } else if (currentFolderUuid.value === null) {
                currentFolderPublicState.value = true;
            }

            // Sync Breadcrumbs
            if (payload.ancestors) {
                const ancestors = payload.ancestors.map(f => ({
                    uuid: f.uuid,
                    name: f.name,
                    is_public: !!f.is_public
                }));

                // Add current folder (parent) to breadcrumbs if it exists
                if (payload.parent) {
                    ancestors.push({
                        uuid: payload.parent.uuid,
                        name: payload.parent.name,
                        is_public: !!payload.parent.is_public
                    });
                }

                breadcrumbs.value = ancestors;
            } else {
                breadcrumbs.value = [];
            }
        }
        usingLegacyFallback.value = false;
    } catch (error) {
        console.error('Fetch error:', error);

        try {
            await fetchLegacyExplorerData(page);
            usingLegacyFallback.value = true;

            if (!legacyNoticeShown.value) {
                alert.toast.warning(
                    'Modo compatibilidad',
                    'Se activó el listado clásico temporalmente por un error en la carga optimizada.',
                );
                legacyNoticeShown.value = true;
            }
        } catch (legacyError) {
            console.error('Legacy fetch error:', legacyError);
            folders.value = [];
            files.value = [];
            explorerPagination.value = {
                current_page: 1,
                last_page: 1,
                per_page: itemsPerPage.value,
                total: 0,
                from: 0,
                to: 0,
            };
            await setPageInUrl(1, { replace: true });
        }
    } finally {
        loading.value = false;
        filesLoading.value = false;
    }
};

const goToFolder = (uuid) => {
    const query = {
        ...route.query,
        page: '1',
        sort_by: sortField.value,
        sort_dir: sortDirection.value,
    };
    if (uuid) {
        router.push({ name: 'FilesFolder', params: { uuid }, query });
    } else {
        router.push({ name: 'Files', query });
    }
};

const handleSortFieldChange = async (field) => {
    const nextField = parseSortField(field);
    sortField.value = nextField;

    const changed = await setSortInUrl({ field: nextField, direction: sortDirection.value });
    if (!changed) {
        await fetchExplorerData(1);
    }
};

const handleSortDirectionChange = async (direction) => {
    const nextDirection = parseSortDirection(direction);
    sortDirection.value = nextDirection;

    const changed = await setSortInUrl({ field: sortField.value, direction: nextDirection });
    if (!changed) {
        await fetchExplorerData(1);
    }
};

const handlePageChange = async (page) => {
    const nextPage = parsePage(page);
    const changed = await setPageInUrl(nextPage);

    if (!changed) {
        await fetchExplorerData(nextPage);
    }
};

// Watch route params/query to sync folder and page state
watch(
    [() => route.params.uuid, () => route.query.page, () => route.query.sort_by, () => route.query.sort_dir],
    ([newUuid, pageQuery, sortByQuery, sortDirQuery]) => {
        const rawUuid = String(newUuid || "").trim();
        const isMalformed = rawUuid && (rawUuid.startsWith(":") || rawUuid === "undefined" || rawUuid === "null");

        if (isMalformed) {
             router.replace({ name: 'Files', query: route.query });
             return;
        }

        currentFolderUuid.value = newUuid || null;
        sortField.value = parseSortField(sortByQuery);
        sortDirection.value = parseSortDirection(sortDirQuery);
        fetchExplorerData(parsePage(pageQuery));
    },
    { immediate: true },
);

const handleFolderCreated = () => {
    showCreateModal.value = false;
    fetchExplorerData(explorerPagination.value?.current_page || 1);
};

const handleFolderUpdated = () => {
    showCreateModal.value = false;
    folderToEdit.value = null;
    fetchExplorerData(explorerPagination.value?.current_page || 1);
};

const handleFolderCreatedFromActions = () => {
    showActionsModal.value = false;
    fetchExplorerData(1);
};

const handleFilesUploadedFromActions = () => {
    showActionsModal.value = false;
    fetchExplorerData(1);
};

const handleLinkCreatedFromActions = () => {
    showActionsModal.value = false;
    fetchExplorerData(1);
};

const openActionsModal = (tab = 'folder') => {
    actionsInitialTab.value = tab;
    showActionsModal.value = true;
};

const editFolder = (folder) => {
    if (!isOwner(folder)) return;
    folderToEdit.value = folder;
    showCreateModal.value = true;
    closeDropdown();
};

const editFile = (file) => {
    if (!isFileOwner(file)) return;
    fileToEdit.value = file;
    showFileEditModal.value = true;
    closeDropdown();
};

const handleFileUpdated = () => {
    showFileEditModal.value = false;
    fileToEdit.value = null;
    fetchExplorerData(explorerPagination.value?.current_page || 1);
};

const openMoveFile = (file) => {
    if (!isFileOwner(file)) return;
    fileToMove.value = file;
    showFileMoveModal.value = true;
    closeDropdown();
};

const handleFileMoved = () => {
    showFileMoveModal.value = false;
    fileToMove.value = null;
    fetchExplorerData(explorerPagination.value?.current_page || 1);
};

const toggleDropdown = (uuid) => {
    activeDropdownUuid.value = activeDropdownUuid.value === uuid ? null : uuid;
};

const closeDropdown = () => {
    activeDropdownUuid.value = null;
};

const openLinkItem = (file) => {
    if (!file?.is_link || !file?.external_url) return;
    window.open(file.external_url, '_blank', 'noopener,noreferrer');
};

const isImageFile = (file) => {
    if (!file || file?.is_link) return false;
    const mimeType = String(file?.mime_type || '').toLowerCase();
    const extension = String(file?.extension || '').toLowerCase();
    return mimeType.startsWith('image/') || ['jpg', 'jpeg', 'png', 'gif', 'webp', 'bmp', 'svg'].includes(extension);
};

const isPdfFile = (file) => {
    if (!file || file?.is_link) return false;
    const mimeType = String(file?.mime_type || '').toLowerCase();
    const extension = String(file?.extension || '').toLowerCase();
    return mimeType === 'application/pdf' || extension === 'pdf';
};

const isOfficeFile = (file) => {
    if (!file || file?.is_link) return false;
    const extension = String(file?.extension || '').toLowerCase();
    const mimeType = String(file?.mime_type || '').toLowerCase();
    const officeExtensions = ['doc', 'docx', 'odt', 'rtf', 'txt', 'xls', 'xlsx', 'ods', 'csv', 'ppt', 'pptx', 'odp'];

    if (officeExtensions.includes(extension)) {
        return true;
    }

    return mimeType.includes('officedocument')
        || mimeType.includes('msword')
        || mimeType.includes('ms-excel')
        || mimeType.includes('ms-powerpoint')
        || mimeType.includes('spreadsheet')
        || mimeType.includes('presentation');
};

const isExcelFile = (file) => {
    if (!file || file?.is_link) return false;
    const extension = String(file?.extension || '').toLowerCase();
    const mimeType = String(file?.mime_type || '').toLowerCase();
    return ['xls', 'xlsx', 'ods', 'csv'].includes(extension)
        || mimeType.includes('spreadsheet')
        || mimeType.includes('ms-excel');
};

const isWordFile = (file) => {
    if (!file || file?.is_link) return false;
    const extension = String(file?.extension || '').toLowerCase();
    const mimeType = String(file?.mime_type || '').toLowerCase();
    return extension === 'docx'
        || mimeType.includes('wordprocessingml');
};

const isPowerPointFile = (file) => {
    if (!file || file?.is_link) return false;
    const extension = String(file?.extension || '').toLowerCase();
    const mimeType = String(file?.mime_type || '').toLowerCase();
    return extension === 'pptx'
        || mimeType.includes('presentationml')
        || mimeType.includes('ms-powerpoint');
};

const isPreviewableFile = (file) => isImageFile(file) || isPdfFile(file) || isOfficeFile(file);

const closeImagePreview = () => {
    showImagePreviewModal.value = false;
    previewImageTitle.value = '';
    previewFileType.value = 'image';
    previewFileUuid.value = null;
    previewOfficeMeta.value = null;
    if (previewImageUrl.value) {
        URL.revokeObjectURL(previewImageUrl.value);
        previewImageUrl.value = '';
    }
};

const openPreviewInOnlyOffice = async () => {
    if (!previewFileUuid.value) {
        return;
    }

    const uuid = previewFileUuid.value;
    const originFolderUuid = currentFolderUuid.value ? String(currentFolderUuid.value) : '';
    const originQuery = {
        page: String(route.query.page || '1'),
        sort_by: String(route.query.sort_by || sortField.value || 'created_at'),
        sort_dir: String(route.query.sort_dir || sortDirection.value || 'desc'),
    };
    closeImagePreview();
    await router.push({
        name: 'FilesOfficeViewer',
        params: { uuid },
        query: {
            origin_folder_uuid: originFolderUuid,
            origin_page: originQuery.page,
            origin_sort_by: originQuery.sort_by,
            origin_sort_dir: originQuery.sort_dir,
        },
    });
};

const openFilePreview = async (file) => {
    if (!isPreviewableFile(file) || previewImageLoading.value || file.is_encrypted) return;

    if (parsedOfficePreviewEnabled && (isExcelFile(file) || isWordFile(file) || isPowerPointFile(file))) {
        previewImageLoading.value = true;
        try {
            if (previewImageUrl.value) {
                URL.revokeObjectURL(previewImageUrl.value);
                previewImageUrl.value = '';
            }

            const response = await filesApi.downloadFile(file.uuid);
            const blob = new Blob([response.data], {
                type: response.headers?.['content-type'] || file.mime_type || 'application/octet-stream'
            });

            previewFileType.value = isExcelFile(file)
                ? 'excel'
                : (isWordFile(file) ? 'word' : 'powerpoint');
            previewFileUuid.value = file.uuid;
            previewImageTitle.value = file.original_name || file.name || 'Vista previa';
            previewOfficeMeta.value = {
                extension: String(file.extension || '').toUpperCase(),
                size: file.size_human || '-',
                mime: file.mime_type || '-',
                name: file.original_name || file.name || 'Documento Office',
                note: 'Vista rápida estática avanzada activa.',
            };
            previewImageUrl.value = URL.createObjectURL(blob);
            showImagePreviewModal.value = true;
            closeDropdown();
        } catch (error) {
            alert.toast.error('Error', error.response?.data?.message || 'No se pudo cargar la vista previa.');
        } finally {
            previewImageLoading.value = false;
        }
        return;
    }

    if (isOfficeFile(file)) {
        previewFileType.value = 'office';
        previewFileUuid.value = file.uuid;
        previewImageTitle.value = file.original_name || file.name || 'Vista previa';
        const isLightweightFallbackFile = isExcelFile(file) || isWordFile(file) || isPowerPointFile(file);
        previewOfficeMeta.value = {
            extension: String(file.extension || '').toUpperCase(),
            size: file.size_human || '-',
            mime: file.mime_type || '-',
            name: file.original_name || file.name || 'Documento Office',
            note: (!parsedOfficePreviewEnabled && isLightweightFallbackFile)
                ? 'Vista previa sencilla habilitada por configuración del servidor. Para edición o visualización completa, usa “Abrir en OnlyOffice”.'
                : 'Vista rápida estática. Para edición o visualización completa, usa “Abrir en OnlyOffice”.',
        };
        showImagePreviewModal.value = true;
        closeDropdown();
        return;
    }

    previewImageLoading.value = true;
    try {
        if (previewImageUrl.value) {
            URL.revokeObjectURL(previewImageUrl.value);
            previewImageUrl.value = '';
        }

        const response = isImageFile(file)
            ? await filesApi.previewFile(file.uuid)
            : await filesApi.downloadFile(file.uuid);
        const blob = new Blob([response.data], {
            type: response.headers?.['content-type'] || file.mime_type || 'application/octet-stream'
        });

        previewFileType.value = isPdfFile(file) ? 'pdf' : 'image';
        previewFileUuid.value = file.uuid;
        previewImageUrl.value = URL.createObjectURL(blob);
        previewImageTitle.value = file.original_name || file.name || 'Vista previa';
        showImagePreviewModal.value = true;
        closeDropdown();
    } catch (error) {
        alert.toast.error('Error', error.response?.data?.message || 'No se pudo cargar la vista previa.');
    } finally {
        previewImageLoading.value = false;
    }
};

const downloadFile = async (file) => {
    if (!file || file?.is_link) return;

    // Check if file is encrypted
    // Check if file is encrypted
    if (file.is_encrypted) {
        fileToDownloadEncrypted.value = file;
        showDownloadEncryptedModal.value = true;
        closeDropdown();
        return;
    }

    try {
        const response = await filesApi.downloadFile(file.uuid);
        const blob = new Blob([response.data], {
            type: response.headers?.['content-type'] || file.mime_type || 'application/octet-stream'
        });

        const link = document.createElement('a');
        const objectUrl = URL.createObjectURL(blob);
        link.href = objectUrl;
        link.download = file.original_name || file.name || 'archivo';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(objectUrl);
        closeDropdown();
    } catch (error) {
        if (error?.response?.status === 403 && error?.response?.data?.data?.message?.includes('encriptado')) {
            // File is encrypted, show download encrypted modal (fallback)
            fileToDownloadEncrypted.value = file;
            showDownloadEncryptedModal.value = true;
            closeDropdown();
        } else {
            alert.toast.error('Error', error.response?.data?.message || 'No se pudo descargar el archivo.');
        }
    }
};

const handleDecryptSuccess = () => {
    showDecryptModal.value = false;
    fileToDecrypt.value = null;
    fetchExplorerData(explorerPagination.value?.current_page || 1);
};

const handleDecryptFile = (file) => {
    if (!file.is_encrypted) return;
    fileToDecrypt.value = file;
    showDecryptModal.value = true;
    closeDropdown();
};

const handleEncryptFile = (file) => {
    if (file.is_encrypted || file.is_link) return;
    fileToEncrypt.value = file;
    showEncryptModal.value = true;
    closeDropdown();
};

const handleEncryptSuccess = () => {
    showEncryptModal.value = false;
    fileToEncrypt.value = null;
    fetchExplorerData(explorerPagination.value?.current_page || 1);
};

const handleShareLink = (item, isFolder) => {
    itemToShare.value = item;
    isSharedFolder.value = isFolder;
    showShareModal.value = true;
    closeDropdown();
};

const handleViewLink = (sharedLink) => {
    sharedLinkToView.value = sharedLink;
    showViewSharedLinkModal.value = true;
    closeDropdown();
};

const formatDate = (dateString) => {
    if (!dateString) return '-';
    const date = new Date(dateString);
    return date.toLocaleDateString('es-ES', {
        day: '2-digit', month: '2-digit', year: 'numeric',
        hour: '2-digit', minute: '2-digit'
    });
};

const confirmDelete = async (folder) => {
    if (!isOwner(folder)) return;
    const confirmed = await alert.fire({
        title: '¿Eliminar carpeta?',
        text: `¿Estás seguro de que deseas eliminar la carpeta "${folder.name}"? Esta acción no se puede deshacer.`,
        type: 'warning',
        showCancel: true,
        confirmText: 'Sí, eliminar',
        cancelText: 'Cancelar'
    });

    if (confirmed) {
        try {
            await folderApi.deleteFolder(folder.uuid);
            alert.toast.success('Eliminado', 'Carpeta eliminada correctamente.');
            fetchExplorerData(explorerPagination.value?.current_page || 1);
        } catch (error) {
            alert.toast.error('Error', error.response?.data?.message || 'No se pudo eliminar la carpeta.');
        }
    }
};

const confirmDeleteFile = async (file) => {
    if (!isFileOwner(file)) return;

    const confirmed = await alert.fire({
        title: file?.is_link ? '¿Eliminar enlace?' : '¿Eliminar archivo?',
        text: file?.is_link
            ? `¿Estás seguro de que deseas eliminar el enlace "${file.name}"? Esta acción no se puede deshacer.`
            : `¿Estás seguro de que deseas eliminar el archivo "${file.original_name}"? Esta acción no se puede deshacer.`,
        type: 'warning',
        showCancel: true,
        confirmText: 'Sí, eliminar',
        cancelText: 'Cancelar'
    });

    if (confirmed) {
        try {
            await filesApi.deleteFile(file.uuid);
            alert.toast.success('Eliminado', 'Archivo eliminado correctamente.');
            fetchExplorerData(explorerPagination.value?.current_page || 1);
        } catch (error) {
            alert.toast.error('Error', error.response?.data?.message || 'No se pudo eliminar el archivo.');
        }
    }
};

// Search Watcher (Reset to page 1)
watch(searchQuery, async () => {
    const changed = await setPageInUrl(1, { replace: true });
    if (!changed) {
        await fetchExplorerData(1);
    }
});

// Items Per Page Watcher (Reset to page 1)
watch(itemsPerPage, async () => {
    const changed = await setPageInUrl(1, { replace: true });
    if (!changed) {
        await fetchExplorerData(1);
    }
});

onUnmounted(() => {
    localStorage.removeItem(activeTabStorageKey);
    if (previewImageUrl.value) {
        URL.revokeObjectURL(previewImageUrl.value);
    }
});
</script>

<style scoped>
.explorer-main-wrapper {
    display: flex;
    flex-direction: column;
    min-height: 100%;
    width: 100%;
    flex: 1;
}

/* Tab Navigation */
.view-navigation-tabs {
    padding: 1.25rem 2rem 0;
    background: var(--bg-secondary);
    border-bottom: 1px solid var(--border-color);
    border-top-left-radius: 12px;
    border-top-right-radius: 12px;
}

.tabs-inner {
    display: flex;
    gap: 2rem;
}

.nav-tab {
    background: transparent;
    border: none;
    color: var(--text-tertiary);
    padding: 0.75rem 0.25rem;
    font-size: 0.95rem;
    font-weight: 600;
    cursor: pointer;
    display: flex;
    align-items: center;
    gap: 10px;
    position: relative;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.nav-tab :deep(svg) {
    transition: transform 0.3s ease;
}

.nav-tab:hover {
    color: var(--text-primary);
}

.nav-tab:hover :deep(svg) {
    transform: scale(1.1);
}

.nav-tab.active {
    color: var(--primary);
}

.active-indicator {
    position: absolute;
    bottom: 0;
    left: 0;
    width: 100%;
    height: 3px;
    background: var(--primary);
    border-radius: 4px 4px 0 0;
    transform: scaleX(0);
    transition: transform 0.3s ease;
    box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.1);
}

.nav-tab.active .active-indicator {
    transform: scaleX(1);
}

/* Transition Views */
.explorer-view-content,
.links-view-content {
    flex: 1;
    overflow-y: auto;
    overflow-x: hidden;
}

/* Existing File Explorer Styles */
.file-explorer {
    padding: 1rem;
    position: relative;
    max-width: 100%;
}

.explorer-loading {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 5rem;
    gap: 1.5rem;
    color: #10b981;
}

.explorer-empty {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 8rem 2rem;
    text-align: center;
    color: rgba(255, 255, 255, 0.5);
}

.explorer-empty h3 {
    margin: 1.5rem 0 0.5rem;
    color: white;
}

.explorer-empty p {
    max-width: 400px;
}

.explorer-body {
    animation: slideUp 0.4s ease;
}

@keyframes slideUp {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
}

.loader {
    width: 48px;
    height: 48px;
    border: 3px solid rgba(16, 185, 129, 0.1);
    border-radius: 50%;
    border-top-color: #10b981;
    animation: spin 1s linear infinite;
}

@keyframes spin {
    to { transform: rotate(360deg); }
}

/* Adjustments for Fit to Screen */
:deep(.fit-screen-active) .explorer-view-content,
:deep(.fit-screen-active) .links-view-content {
    overflow: hidden;
    display: flex;
    flex-direction: column;
}
</style>

