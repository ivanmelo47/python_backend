<template>
    <div class="explorer-grid">
        <template v-for="item in orderedItems" :key="item.key">
        <div
            v-if="item.type === 'folder'"
            class="explorer-item folder"
            :class="{ 'dropdown-active': activeDropdownUuid === `folder-${item.data.uuid}` }"
            @click="$emit('go-folder', item.data.uuid)"
        >
            <div class="item-icon">
                <div v-if="item.data.icon" class="custom-icon-wrapper main" v-html="item.data.icon.svg_content"></div>
                <Icon v-else name="folder-open" :size="48" />
                <div class="status-indicator" :title="item.data.is_public ? 'Pública' : item.data.shared_users?.length > 0 ? 'Compartida' : 'Privada'">
                    <Icon
                        :name="getFolderStatusIcon(item.data)"
                        :size="16"
                        :class="{
                            'is-public': item.data.is_public,
                            'is-shared': item.data.shared_users && item.data.shared_users.length > 0
                        }"
                    />
                </div>
            </div>
            <div class="item-info">
                <span class="item-name">{{ item.data.name }}</span>
                <span class="item-owner" v-if="item.data.is_public">Subido por: {{ item.data.owner.name }}</span>
            </div>

            <div class="item-actions">
                <div class="action-dropdown" :class="{ active: activeDropdownUuid === `folder-${item.data.uuid}` }">
                    <button
                        @click.stop="$emit('toggle-dropdown', `folder-${item.data.uuid}`)"
                        class="btn-icon dots"
                        title="Acciones"
                    >
                        <Icon name="moreVertical" :size="18" />
                    </button>

                    <transition name="dropdown-fade">
                        <div
                            v-if="activeDropdownUuid === `folder-${item.data.uuid}`"
                            class="dropdown-menu"
                            v-click-outside="handleClickOutside"
                        >
                            <button
                                v-if="!item.data.shared_link"
                                class="dropdown-item"
                                @click.stop="$emit('share-link', item.data, true)"
                            >
                                <Icon name="link" :size="16" />
                                <span>Compartir (Enlace)</span>
                            </button>
                            <button
                                v-else
                                class="dropdown-item"
                                @click.stop="$emit('view-link', item.data.shared_link)"
                            >
                                <Icon name="link" :size="16" />
                                <span style="color: var(--primary);">Ver Enlace</span>
                            </button>
                            <button
                                class="dropdown-item"
                                :class="{ disabled: !isOwner(item.data) }"
                                :style="!isOwner(item.data) ? { cursor: 'not-allowed' } : {}"
                                @click.stop="isOwner(item.data) && $emit('edit-folder', item.data)"
                                :title="!isOwner(item.data) ? 'Solo el propietario puede editar' : ''"
                            >
                                <Icon name="pencil" :size="16" />
                                <span>Editar</span>
                            </button>
                            <button
                                class="dropdown-item delete"
                                :class="{ disabled: !isOwner(item.data) }"
                                :style="!isOwner(item.data) ? { cursor: 'not-allowed' } : {}"
                                @click.stop="isOwner(item.data) && $emit('delete-folder', item.data)"
                                :title="!isOwner(item.data) ? 'Solo el propietario puede eliminar' : ''"
                            >
                                <Icon name="trash" :size="16" />
                                <span>Eliminar</span>
                            </button>
                        </div>
                    </transition>
                </div>
            </div>
        </div>

        <div
            v-else
            class="explorer-item file"
            :class="{
                'is-link-item': isLinkFile(item.data),
                'dropdown-active': activeDropdownUuid === `file-${item.data.uuid}`
            }"
            @click="handleFileItemClick(item.data)"
        >
            <div class="item-icon">
                <div v-if="item.data.icon" class="custom-icon-wrapper main" v-html="item.data.icon.svg_content"></div>
                <div v-else-if="item.data.configuration?.icon" class="custom-icon-wrapper main" v-html="item.data.configuration.icon.svg_content"></div>
                <Icon v-else name="file" :size="48" />
                <div v-if="isLinkFile(item.data)" class="status-indicator" title="Enlace externo">
                    <Icon name="link" :size="16" class="is-link" />
                </div>
                <div v-if="item.data.is_encrypted" class="status-indicator encrypt" title="Archivo encriptado">
                    <Icon name="lock" :size="16" class="is-encrypted" />
                </div>
            </div>
            <div class="item-info">
                <span class="item-name">{{ item.data.is_link ? item.data.name : item.data.original_name }}</span>
                <span class="item-owner">{{ item.data.is_link ? 'Enlace externo' : `${item.data.size_human} • .${item.data.extension}` }}</span>
            </div>

            <div class="item-actions">
                <div class="action-dropdown" :class="{ active: activeDropdownUuid === `file-${item.data.uuid}` }">
                    <button
                        @click.stop="$emit('toggle-dropdown', `file-${item.data.uuid}`)"
                        class="btn-icon dots"
                        title="Acciones"
                    >
                        <Icon name="moreVertical" :size="18" />
                    </button>

                    <transition name="dropdown-fade">
                        <div
                            v-if="activeDropdownUuid === `file-${item.data.uuid}`"
                            class="dropdown-menu"
                            v-click-outside="handleClickOutside"
                        >
                            <button
                                v-if="isPreviewableFile(item.data) && !item.data.is_encrypted"
                                class="dropdown-item"
                                @click.stop="$emit('preview-file', item.data)"
                            >
                                <Icon name="eye" :size="16" />
                                <span>Vista previa</span>
                            </button>
                            <button
                                class="dropdown-item"
                                :class="{ disabled: !isFileOwner(item.data) }"
                                :style="!isFileOwner(item.data) ? { cursor: 'not-allowed' } : {}"
                                @click.stop="isFileOwner(item.data) && $emit('edit-file', item.data)"
                                :title="!isFileOwner(item.data) ? 'Solo el propietario puede editar' : ''"
                            >
                                <Icon name="pencil" :size="16" />
                                <span>Editar</span>
                            </button>
                            <button
                                class="dropdown-item"
                                :class="{ disabled: !isFileOwner(item.data) }"
                                :style="!isFileOwner(item.data) ? { cursor: 'not-allowed' } : {}"
                                @click.stop="isFileOwner(item.data) && $emit('move-file', item.data)"
                                :title="!isFileOwner(item.data) ? 'Solo el propietario puede mover' : ''"
                            >
                                <Icon name="folder-open" :size="16" />
                                <span>Mover</span>
                            </button>
                            <button
                                v-if="!item.data.shared_link && !isLinkFile(item.data) && !item.data.is_encrypted"
                                class="dropdown-item"
                                @click.stop="$emit('share-link', item.data, false)"
                            >
                                <Icon name="link" :size="16" />
                                <span>Compartir (Enlace)</span>
                            </button>
                            <button
                                v-else-if="item.data.shared_link && !isLinkFile(item.data) && !item.data.is_encrypted"
                                class="dropdown-item"
                                @click.stop="$emit('view-link', item.data.shared_link)"
                            >
                                <Icon name="link" :size="16" />
                                <span style="color: var(--primary);">Ver Enlace</span>
                            </button>
                            <button
                                v-if="!item.data.is_encrypted && !isLinkFile(item.data)"
                                class="dropdown-item"
                                :class="{ disabled: !isFileOwner(item.data) }"
                                :style="!isFileOwner(item.data) ? { cursor: 'not-allowed' } : {}"
                                @click.stop="isFileOwner(item.data) && $emit('encrypt-file', item.data)"
                                :title="!isFileOwner(item.data) ? 'Solo el propietario puede encriptar' : ''"
                            >
                                <Icon name="lock" :size="16" />
                                <span>Encriptar</span>
                            </button>
                            <button
                                v-if="item.data.is_encrypted && !isLinkFile(item.data)"
                                class="dropdown-item"
                                :class="{ disabled: !isFileOwner(item.data) }"
                                :style="!isFileOwner(item.data) ? { cursor: 'not-allowed' } : {}"
                                @click.stop="isFileOwner(item.data) && $emit('decrypt-file', item.data)"
                                :title="!isFileOwner(item.data) ? 'Solo el propietario puede desencriptar' : ''"
                            >
                                <Icon name="unlock" :size="16" />
                                <span>Desencriptar</span>
                            </button>
                            <button
                                v-if="!isLinkFile(item.data)"
                                class="dropdown-item"
                                @click.stop="$emit('download-file', item.data)"
                            >
                                <Icon name="file-text" :size="16" />
                                <span>Descargar</span>
                            </button>
                            <button
                                class="dropdown-item delete"
                                :class="{ disabled: !isFileOwner(item.data) }"
                                :style="!isFileOwner(item.data) ? { cursor: 'not-allowed' } : {}"
                                @click.stop="isFileOwner(item.data) && $emit('delete-file', item.data)"
                                :title="!isFileOwner(item.data) ? 'Solo el propietario puede eliminar' : ''"
                            >
                                <Icon name="trash" :size="16" />
                                <span>Eliminar</span>
                            </button>
                        </div>
                    </transition>
                </div>
            </div>
        </div>
        </template>
    </div>
</template>

<script setup>
import { computed } from 'vue';
import Icon from '@/components/Icon.vue';

const props = defineProps({
    folders: {
        type: Array,
        default: () => [],
    },
    files: {
        type: Array,
        default: () => [],
    },
    activeDropdownUuid: {
        type: String,
        default: null,
    },
    isOwner: {
        type: Function,
        required: true,
    },
    isFileOwner: {
        type: Function,
        required: true,
    },
    getFolderStatusIcon: {
        type: Function,
        required: true,
    },
    sortField: {
        type: String,
        default: 'created_at',
    },
    sortDirection: {
        type: String,
        default: 'desc',
    },
});

const emit = defineEmits([
    'go-folder',
    'toggle-dropdown',
    'close-dropdown',
    'edit-folder',
    'edit-file',
    'move-file',
    'delete-folder',
    'delete-file',
    'open-link',
    'download-file',
    'preview-file',
    'encrypt-file',
    'decrypt-file',
    'share-link',
    'view-link',
]);

const handleClickOutside = () => {
    emit('close-dropdown');
};

const isLinkFile = (file) => {
    return !!file?.is_link;
};

const isPreviewableFile = (file) => {
    if (!file || isLinkFile(file)) return false;
    const mimeType = String(file?.mime_type || '').toLowerCase();
    const extension = String(file?.extension || '').toLowerCase();
    const officeExtensions = ['doc', 'docx', 'odt', 'rtf', 'txt', 'xls', 'xlsx', 'ods', 'csv', 'ppt', 'pptx', 'odp'];
    return mimeType.startsWith('image/')
        || mimeType === 'application/pdf'
        || ['jpg', 'jpeg', 'png', 'gif', 'webp', 'bmp', 'svg', 'pdf'].includes(extension)
        || officeExtensions.includes(extension)
        || mimeType.includes('officedocument')
        || mimeType.includes('msword')
        || mimeType.includes('ms-excel')
        || mimeType.includes('ms-powerpoint')
        || mimeType.includes('spreadsheet')
        || mimeType.includes('presentation');
};

const handleFileItemClick = (file) => {
    if (isLinkFile(file)) {
        emit('open-link', file);
        return;
    }

    if (file.is_encrypted) {
        emit('download-file', file);
        return;
    }

    if (isPreviewableFile(file)) {
        emit('preview-file', file);
    }
};

const getCreatedTimestamp = (entry) => {
    const raw = entry?.created_at || entry?.uploaded_at || null;
    const time = raw ? new Date(raw).getTime() : 0;
    return Number.isNaN(time) ? 0 : time;
};

const getUpdatedTimestamp = (entry) => {
    const raw = entry?.updated_at || entry?.uploaded_at || entry?.created_at || null;
    const time = raw ? new Date(raw).getTime() : 0;
    return Number.isNaN(time) ? 0 : time;
};

const getSortableName = (item) => {
    if (item.type === 'folder') return String(item.data?.name || '').toLowerCase();
    return String(item.data?.is_link ? item.data?.name : item.data?.original_name || '').toLowerCase();
};

const getTypeRank = (item) => (item.type === 'folder' ? 0 : 1);

const orderedItems = computed(() => {
    const folderItems = (props.folders || []).map((folder) => ({
        type: 'folder',
        key: `folder-${folder.uuid}`,
        data: folder,
        createdAt: getCreatedTimestamp(folder),
    }));

    const fileItems = (props.files || []).map((file) => ({
        type: 'file',
        key: `file-${file.uuid}`,
        data: file,
        createdAt: getCreatedTimestamp(file),
    }));

    const direction = props.sortDirection === 'asc' ? 1 : -1;
    const field = props.sortField;

    return [...folderItems, ...fileItems].sort((a, b) => {
        if (field === 'name') {
            const result = getSortableName(a).localeCompare(getSortableName(b), 'es', { sensitivity: 'base' });
            if (result !== 0) return result * direction;
        } else if (field === 'updated_at') {
            const result = getUpdatedTimestamp(a.data) - getUpdatedTimestamp(b.data);
            if (result !== 0) return result * direction;
        } else if (field === 'type') {
            const result = getTypeRank(a) - getTypeRank(b);
            if (result !== 0) return result * direction;
        } else {
            const result = a.createdAt - b.createdAt;
            if (result !== 0) return result * direction;
        }

        return (b.createdAt - a.createdAt);
    });
});
</script>
