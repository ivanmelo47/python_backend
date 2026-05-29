<template>
    <div class="share-viewer">
        <div v-if="loading" class="viewer-loading">
            <div class="loader"></div>
            <p>Cargando contenido...</p>
        </div>

        <div v-else-if="error" class="viewer-error">
            <Icon name="alert-triangle" :size="48" style="color: var(--danger);" />
            <h3>Oops, algo salió mal</h3>
            <p>{{ errorMessage }}</p>
        </div>

        <div v-else-if="contentData" class="viewer-content">
            
            <div class="content-header" v-if="contentData.type === 'folder'">
                <h1>{{ contentData.item.name }}</h1>
            </div>

            <!-- Breadcrumbs Navigation for Folders -->
            <div class="breadcrumbs-container" v-if="contentData.type === 'folder' && breadcrumbs.length > 0">
                <nav class="public-breadcrumbs">
                    <span 
                        v-for="(crumb, index) in breadcrumbs" 
                        :key="index"
                        class="crumb-item"
                        :class="{'active': index === breadcrumbs.length - 1}"
                        @click="index !== breadcrumbs.length - 1 && navigateToFolder(crumb.uuid)"
                    >
                        <Icon v-if="index === 0" name="home" :size="16" />
                        <span>{{ crumb.name }}</span>
                        <Icon v-if="index < breadcrumbs.length - 1" name="chevron-right" :size="14" class="separator"/>
                    </span>
                </nav>
                
                <div class="actions-right">
                    <button class="btn btn-primary btn-sm" @click="downloadFolderZip()">
                        <Icon name="download" :size="16" />
                        <span>Descargar todo (.zip)</span>
                    </button>
                </div>
            </div>

            <!-- Single File View -->
            <div v-if="contentData.type === 'file'" class="single-file-view">
                <div class="file-preview-card">
                    <div class="file-icon-large">
                        <div
                            v-if="hasCustomSvgIcon(contentData.item)"
                            class="custom-icon-wrapper large"
                            v-html="getCustomIconSvg(contentData.item)"
                        ></div>
                        <DynamicIcon
                            v-else
                            :name="getItemIconName(contentData.item)"
                            :databaseData="getItemIconData(contentData.item)"
                            :size="80"
                        />
                    </div>
                    <div class="file-details">
                        <h2>{{ contentData.item.original_name || contentData.item.name }}</h2>
                        <span class="file-meta">
                            {{ contentData.item.is_link ? 'Enlace externo' : `${contentData.item.size_human} • ${contentData.item.extension?.toUpperCase()}` }}
                        </span>
                        
                        <div class="file-actions">
                            <button class="btn btn-primary" @click="downloadFile(contentData.item)">
                                <Icon name="download" :size="20"/>
                                Descargar Archivo
                            </button>
                        </div>
                    </div>
                    
                    <div v-if="contentData.item.is_encrypted" class="encrypted-notice">
                        <Icon name="lock" :size="16"/>
                        <span>Este archivo está cifrado. Necesitarás la clave original para poder abrirlo tras la descarga.</span>
                    </div>
                </div>
            </div>

            <!-- Folder Contents Grid -->
            <div v-else-if="contentData.type === 'folder'" class="folder-view">
                
                <div v-if="folders.length === 0 && files.length === 0" class="empty-folder">
                    <Icon name="folder-open" :size="48" />
                    <p>Esta carpeta está vacía</p>
                </div>
                
                <div v-else class="folder-content-shell">
                    <div class="view-mode-switch">
                        <button
                            type="button"
                            class="view-btn"
                            :class="{ active: viewMode === 'list' }"
                            @click="viewMode = 'list'"
                        >
                            <Icon name="list" :size="16" />
                            <span>Lista</span>
                        </button>
                        <button
                            type="button"
                            class="view-btn"
                            :class="{ active: viewMode === 'grid' }"
                            @click="viewMode = 'grid'"
                        >
                            <Icon name="grid" :size="16" />
                            <span>Tarjetas</span>
                        </button>
                    </div>

                <div class="files-scroll-area">
                    <div v-if="viewMode === 'list'" class="public-list">
                        <div
                            v-for="folder in folders"
                            :key="`folder-${folder.uuid}`"
                            class="list-row folder-row"
                            @click="navigateToFolder(folder.uuid)"
                        >
                            <div class="row-main">
                                <div class="item-icon">
                                    <div
                                        v-if="hasCustomSvgIcon(folder)"
                                        class="custom-icon-wrapper"
                                        v-html="getCustomIconSvg(folder)"
                                    ></div>
                                    <DynamicIcon
                                        v-else
                                        :name="getItemIconName(folder)"
                                        :databaseData="getItemIconData(folder)"
                                        :size="28"
                                        :color="'var(--primary)'"
                                    />
                                </div>
                                <div class="item-info">
                                    <span class="item-name" :title="folder.name">{{ folder.name }}</span>
                                    <span class="item-size">Carpeta</span>
                                </div>
                            </div>
                            <div class="row-actions">
                                <button class="action-btn secondary labeled" @click.stop="downloadFolderZip(folder.uuid)" title="Descargar carpeta (.zip)">
                                    <Icon name="download" :size="14"/>
                                    <span>Descargar</span>
                                </button>
                                <button class="action-btn labeled" @click.stop="navigateToFolder(folder.uuid)" title="Abrir carpeta">
                                    <Icon name="folder-open" :size="14"/>
                                    <span>Abrir</span>
                                </button>
                            </div>
                        </div>

                        <div
                            v-for="file in files"
                            :key="`file-${file.uuid}`"
                            class="list-row file-row"
                            :class="{ 'link-clickable': file.is_link }"
                            @click="handlePublicFileClick(file)"
                        >
                            <div class="row-main">
                                <div class="item-icon">
                                    <div
                                        v-if="hasCustomSvgIcon(file)"
                                        class="custom-icon-wrapper"
                                        v-html="getCustomIconSvg(file)"
                                    ></div>
                                    <DynamicIcon
                                        v-else
                                        :name="getItemIconName(file)"
                                        :databaseData="getItemIconData(file)"
                                        :size="28"
                                    />
                                    <div v-if="file.is_encrypted" class="encrypted-badge">
                                        <Icon name="lock" :size="10" />
                                    </div>
                                    <div v-if="file.is_link" class="link-badge">
                                        <Icon name="link" :size="10" />
                                    </div>
                                </div>
                                <div class="item-info">
                                    <span class="item-name" :title="file.original_name || file.name">{{ file.original_name || file.name }}</span>
                                    <span class="item-size">{{ file.is_link ? 'Enlace externo' : file.size_human }}</span>
                                </div>
                            </div>
                            <div class="row-actions">
                                <button class="action-btn" @click.stop="downloadFile(file)" title="Descargar">
                                    <Icon name="download" :size="16"/>
                                </button>
                            </div>
                        </div>
                    </div>

                    <div v-else class="public-grid">
                        <!-- Folders -->
                        <div 
                            v-for="folder in folders" 
                            :key="folder.uuid"
                            class="grid-item folder-card"
                            @click="navigateToFolder(folder.uuid)"
                        >
                            <div class="item-icon">
                                <div
                                    v-if="hasCustomSvgIcon(folder)"
                                    class="custom-icon-wrapper"
                                    v-html="getCustomIconSvg(folder)"
                                ></div>
                                <DynamicIcon
                                    v-else
                                    :name="getItemIconName(folder)"
                                    :databaseData="getItemIconData(folder)"
                                    :size="40"
                                    :color="'var(--primary)'"
                                />
                            </div>
                            <div class="item-info">
                                <span class="item-name" :title="folder.name">{{ folder.name }}</span>
                            </div>
                            <div class="item-hover-actions">
                                <button class="action-btn secondary labeled" @click.stop="downloadFolderZip(folder.uuid)" title="Descargar carpeta (.zip)">
                                    <Icon name="download" :size="14"/>
                                    <span>Descargar</span>
                                </button>
                                <button class="action-btn labeled" @click.stop="navigateToFolder(folder.uuid)" title="Abrir carpeta">
                                    <Icon name="folder-open" :size="14"/>
                                    <span>Abrir</span>
                                </button>
                            </div>
                        </div>

                        <!-- Files -->
                        <div 
                            v-for="file in files" 
                            :key="file.uuid"
                            class="grid-item file-card"
                            :class="{ 'link-clickable': file.is_link }"
                            @click="handlePublicFileClick(file)"
                        >
                            <div class="item-icon">
                                <div
                                    v-if="hasCustomSvgIcon(file)"
                                    class="custom-icon-wrapper"
                                    v-html="getCustomIconSvg(file)"
                                ></div>
                                <DynamicIcon
                                    v-else
                                    :name="getItemIconName(file)"
                                    :databaseData="getItemIconData(file)"
                                    :size="40"
                                />
                                <div v-if="file.is_encrypted" class="encrypted-badge">
                                    <Icon name="lock" :size="12" />
                                </div>
                                <div v-if="file.is_link" class="link-badge">
                                    <Icon name="link" :size="12" />
                                </div>
                            </div>
                            <div class="item-info">
                                <span class="item-name" :title="file.original_name || file.name">{{ file.original_name || file.name }}</span>
                                <span class="item-size">{{ file.is_link ? 'Enlace externo' : file.size_human }}</span>
                            </div>
                            <div class="item-hover-actions">
                                <button class="action-btn" @click.stop="downloadFile(file)" title="Descargar">
                                    <Icon name="download" :size="18"/>
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
                </div>
            </div>
            
        </div>
    </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import Icon from '@/components/Icon.vue';
import DynamicIcon from '@/components/DynamicIcon.vue';
import axios from 'axios';
import { useAlert } from '@/composables/useAlert';
import { buildApiUrl } from '@/services/api/url';

const props = defineProps({
    token: {
        type: String,
        required: true
    }
});

const route = useRoute();
const router = useRouter();
const alert = useAlert();

const loading = ref(true);
const error = ref(false);
const errorMessage = ref('');
const contentData = ref(null);
const viewMode = ref('list');

const breadcrumbs = computed(() => contentData.value?.breadcrumbs || []);
const folders = computed(() => contentData.value?.contents?.folders || []);
const files = computed(() => contentData.value?.contents?.files || []);

// Query param for subfolder navigation
const currentPath = computed(() => route.query.path || null);

const fetchContent = async (pathObj = null) => {
    try {
        loading.value = true;
        error.value = false;
        
        let url = buildApiUrl(`s/${props.token}/content`);
        if (pathObj) {
            url += `?path=${pathObj}`;
        }
        
        const res = await axios.get(url, { withCredentials: true });
        contentData.value = res.data;
        
    } catch (e) {
        error.value = true;
        errorMessage.value = e.response?.data?.message || 'Error al cargar el contenido.';
    } finally {
        loading.value = false;
    }
};

onMounted(() => {
    fetchContent(currentPath.value);
});

// Watch route changes to navigate subfolders backwards/forwards
watch(currentPath, (newPath) => {
    fetchContent(newPath);
});

const navigateToFolder = (uuid) => {
    if(!uuid) {
        // Go to root
        router.push({ path: `/s/${props.token}` });
    } else {
        router.push({ path: `/s/${props.token}`, query: { path: uuid }});
    }
};

const getItemIconData = (item) => {
    return item.icon || item.configuration?.icon || null;
};

const hasCustomSvgIcon = (item) => {
    return !!getItemIconData(item)?.svg_content;
};

const getCustomIconSvg = (item) => {
    return getItemIconData(item)?.svg_content || '';
};

const getItemIconName = (item) => {
    const dbIcon = getItemIconData(item);
    if (dbIcon) return `db:${dbIcon.name || 'custom'}`;
    
    return getFileIcon(item);
};

const getFileIcon = (item) => {
    const ext = (item.extension || '').toLowerCase();
    
    const iconMap = {
        'pdf': 'file-pdf',
        'doc': 'file-text', 'docx': 'file-text',
        'xls': 'file-text', 'xlsx': 'file-text',
        'jpg': 'image', 'jpeg': 'image', 'png': 'image', 'gif': 'image', 'svg': 'image',
        'mp4': 'video', 'avi': 'video', 'mov': 'video', 'mkv': 'video',
        'zip': 'archive', 'rar': 'archive', '7z': 'archive'
    };
    
    return iconMap[ext] || 'file';
};

const downloadFile = async (file) => {
    try {
        // Trigger generic file download using window.location or a temporary a tag
        // Depending on backend implementation, this endpoint streams the file.
        const downloadUrl = buildApiUrl(`s/${props.token}/download?file_uuid=${file.uuid}`);
        window.open(downloadUrl, '_blank');
    } catch (error) {
         alert.toast.error('Error', 'No se pudo iniciar la descarga.');
    }
};

const handlePublicFileClick = async (file) => {
    if (!file?.is_link) {
        return;
    }

    const url = String(file.external_url || '').trim();
    if (!url) {
        alert.toast.error('Error', 'Este enlace no tiene una URL válida.');
        return;
    }

    const confirmed = await alert.fire({
        title: 'Abrir enlace externo',
        text: `¿Quieres abrir "${file.original_name || file.name || 'este enlace'}" en una nueva pestaña?`,
        type: 'warning',
        showCancel: true,
        confirmText: 'Abrir enlace',
        cancelText: 'Cancelar'
    });

    if (confirmed) {
        window.open(url, '_blank', 'noopener,noreferrer');
    }
};

const downloadFolderZip = async (targetFolderUuid = null) => {
    try {
        const normalizedTargetPath = typeof targetFolderUuid === 'string' && targetFolderUuid.trim() !== ''
            ? targetFolderUuid
            : null;
        const normalizedCurrentPath = typeof currentPath.value === 'string' && currentPath.value.trim() !== ''
            ? currentPath.value
            : null;

        const folderPath = normalizedTargetPath || normalizedCurrentPath;
        const pathParam = folderPath ? `&path=${folderPath}` : '';
        const downloadUrl = buildApiUrl(`s/${props.token}/download-zip?_=${Date.now()}${pathParam}`);
        
        // Show informative toast
        alert.toast.info('Preparando ZIP...', 'La descarga comenzará en un momento. Los archivos cifrados serán omitidos.', 5000);
        
        window.open(downloadUrl, '_blank');
    } catch (error) {
        alert.toast.error('Error', 'No se pudo crear el archivo ZIP.');
    }
};
</script>

<style lang="scss" scoped>
.share-viewer {
    width: 100%;
    height: 100%;
    min-height: 0;
    display: flex;
    flex-direction: column;
    animation: fadeIn 0.4s ease-out;
}

.viewer-content {
    flex: 1;
    min-height: 0;
    display: flex;
    flex-direction: column;
}

.content-header {
    margin-bottom: 1.5rem;
    
    h1 {
        font-size: 1.75rem;
        font-weight: 700;
        margin: 0;
        color: var(--text-primary);
        letter-spacing: -0.5px;
    }
}

.viewer-loading, .viewer-error {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 3rem;
    text-align: center;
    
    .loader {
        width: 30px; height: 30px;
        border: 3px solid var(--border-color);
        border-top-color: var(--primary);
        border-radius: 50%;
        animation: spin 1s linear infinite;
        margin-bottom: 1rem;
    }
    
    h3 { margin-top: 1rem; }
    p { color: var(--text-secondary); }
}

.breadcrumbs-container {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1.5rem;
    padding-bottom: 1rem;
    border-bottom: 1px solid var(--border-color);
    flex-wrap: wrap;
    gap: 1rem;

    .public-breadcrumbs {
        display: flex;
        align-items: center;
        flex-wrap: wrap;
        gap: 0.5rem;
        
        .crumb-item {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            color: var(--text-secondary);
            font-size: 0.95rem;
            cursor: pointer;
            transition: color 0.2s;
            
            &:hover:not(.active) {
                color: var(--primary);
            }
            
            &.active {
                color: var(--text-primary);
                font-weight: 600;
                cursor: default;
            }
            
            .separator {
                color: var(--text-muted);
            }
        }
    }
}

.view-mode-switch {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    margin-bottom: 1rem;
    padding: 0.35rem;
    background: var(--bg-secondary);
    border: 1px solid var(--border-color);
    border-radius: 10px;

    .view-btn {
        border: none;
        background: transparent;
        color: var(--text-secondary);
        padding: 0.5rem 0.75rem;
        border-radius: 8px;
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        cursor: pointer;
        font-size: 0.85rem;
        font-weight: 600;

        &.active {
            background: var(--primary);
            color: #fff;
        }
    }
}

.folder-view {
    flex: 1;
    min-height: 0;
    display: flex;
    flex-direction: column;
}

.folder-content-shell {
    flex: 1;
    min-height: 0;
    display: flex;
    flex-direction: column;
}

.files-scroll-area {
    flex: 1;
    min-height: 0;
    overflow-y: auto;
    overflow-x: hidden;
    padding-right: 0.25rem;
    scrollbar-width: thin;
    scrollbar-color: rgba(var(--primary-rgb), 0.55) rgba(255, 255, 255, 0.06);
}

.files-scroll-area::-webkit-scrollbar {
    width: 10px;
}

.files-scroll-area::-webkit-scrollbar-track {
    background: rgba(255, 255, 255, 0.05);
    border-radius: 999px;
}

.files-scroll-area::-webkit-scrollbar-thumb {
    background: linear-gradient(
        180deg,
        rgba(var(--primary-rgb), 0.85),
        rgba(var(--primary-rgb), 0.55)
    );
    border-radius: 999px;
    border: 2px solid rgba(255, 255, 255, 0.05);
}

.files-scroll-area::-webkit-scrollbar-thumb:hover {
    background: linear-gradient(
        180deg,
        rgba(var(--primary-rgb), 0.95),
        rgba(var(--primary-rgb), 0.7)
    );
}

.public-list {
    display: flex;
    flex-direction: column;
    gap: 0.65rem;
}

.list-row {
    background: var(--bg-secondary);
    border: 1px solid var(--border-color);
    border-radius: 12px;
    padding: 0.75rem 1rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 1rem;
    transition: all 0.2s;

    &:hover {
        border-color: var(--primary);
        box-shadow: 0 6px 18px rgba(0, 0, 0, 0.08);
    }

    &.file-row.link-clickable {
        cursor: pointer;
    }

    &.folder-row {
        cursor: pointer;
    }

    .row-main {
        min-width: 0;
        display: flex;
        align-items: center;
        gap: 0.8rem;
        flex: 1;

        .item-icon {
            position: relative;
            width: 30px;
            height: 30px;
            flex-shrink: 0;
            display: inline-flex;
            align-items: center;
            justify-content: center;

            .custom-icon-wrapper {
                width: 28px;
                height: 28px;
                display: inline-flex;
                align-items: center;
                justify-content: center;
                line-height: 0;

                :deep(svg),
                :deep(img) {
                    width: 100%;
                    height: 100%;
                    display: block;
                    object-fit: contain;
                }
            }

            .encrypted-badge,
            .link-badge {
                position: absolute;
                width: 15px;
                height: 15px;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                color: #fff;
            }

            .encrypted-badge {
                right: -6px;
                bottom: -6px;
                background: var(--warning);
            }

            .link-badge {
                right: -6px;
                top: -6px;
                background: var(--primary);
            }
        }

        .item-info {
            min-width: 0;
            display: flex;
            flex-direction: column;

            .item-name {
                font-weight: 600;
                color: var(--text-primary);
                white-space: nowrap;
                overflow: hidden;
                text-overflow: ellipsis;
            }

            .item-size {
                font-size: 0.82rem;
                color: var(--text-muted);
                margin-top: 0.15rem;
            }
        }
    }

    .row-actions {
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;

        .action-btn {
            width: 34px;
            height: 34px;
            border: none;
            border-radius: 50%;
            background: var(--primary);
            color: #fff;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            font-size: 0.78rem;
            font-weight: 600;
            transition: all 0.2s ease;

            &.labeled {
                width: auto;
                height: 34px;
                border-radius: 999px;
                padding: 0 0.7rem;
                gap: 0.35rem;
            }

            &.secondary {
                background: transparent;
                border: 2px solid var(--primary);
                color: var(--primary);
                box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.08);
            }

            &:hover {
                transform: translateY(-1px);
                filter: brightness(1.06);
            }

            &.secondary:hover {
                background: rgba(var(--primary-rgb), 0.1);
                border-color: var(--primary);
                color: #fff;
            }
        }
    }
}

// Grid Layout
.public-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 1.5rem;
}

.grid-item {
    background: var(--bg-secondary);
    border: 1px solid var(--border-color);
    border-radius: 12px;
    padding: 1.5rem 1rem;
    display: flex;
    flex-direction: column;
    align-items: center;
    text-align: center;
    cursor: pointer;
    transition: all 0.2s;
    position: relative;
    overflow: hidden;

    &:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 24px rgba(0,0,0,0.06);
        border-color: var(--primary);
        
        .item-hover-actions {
            opacity: 1;
        }
    }
    
    .item-icon {
        position: relative;
        margin-bottom: 1rem;
        color: var(--text-secondary);

        .custom-icon-wrapper {
            width: 40px;
            height: 40px;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            line-height: 0;

            :deep(svg),
            :deep(img) {
                width: 100%;
                height: 100%;
                display: block;
                object-fit: contain;
            }
        }
        
        .encrypted-badge {
            position: absolute;
            bottom: -5px;
            right: -5px;
            background: var(--warning);
            color: white;
            border-radius: 50%;
            width: 20px;
            height: 20px;
            display: flex;
            align-items: center;
            justify-content: center;
        }

        .link-badge {
            position: absolute;
            top: -5px;
            right: -5px;
            background: var(--primary);
            color: white;
            border-radius: 50%;
            width: 20px;
            height: 20px;
            display: flex;
            align-items: center;
            justify-content: center;
        }
    }

    .item-info {
        display: flex;
        flex-direction: column;
        width: 100%;
        
        .item-name {
            font-weight: 500;
            color: var(--text-primary);
            font-size: 0.95rem;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            margin-bottom: 0.25rem;
        }
        
        .item-size {
            font-size: 0.8rem;
            color: var(--text-muted);
        }
    }
    
    .item-hover-actions {
        opacity: 0;
        position: absolute;
        top: 0; left: 0; right: 0; bottom: 0;
        background: rgba(var(--bg-secondary-rgb), 0.85);
        backdrop-filter: blur(2px);
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 0.5rem;
        transition: opacity 0.2s;
        
        .action-btn {
            background: var(--primary);
            color: white;
            border: none;
            border-radius: 50%;
            width: 45px; height: 45px;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            transition: all 0.2s ease;
            font-size: 0.82rem;
            font-weight: 600;

            &.labeled {
                width: auto;
                height: 40px;
                border-radius: 999px;
                padding: 0 0.8rem;
                gap: 0.35rem;
            }
            
            &:hover {
                transform: scale(1.06);
                filter: brightness(1.08);
                box-shadow: 0 8px 18px rgba(var(--primary-rgb), 0.28);
            }

            &.secondary {
                background: transparent;
                border: 2px solid var(--primary);
                color: var(--primary);
                box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.08);
            }

            &.secondary:hover {
                background: rgba(var(--primary-rgb), 0.1);
                border-color: var(--primary);
                color: #fff;
                box-shadow: 0 8px 18px rgba(var(--primary-rgb), 0.2);
            }
        }
    }
}

.grid-item.file-card.link-clickable {
    cursor: pointer;
}

.empty-folder {
    text-align: center;
    padding: 4rem 2rem;
    color: var(--text-muted);
    
    p { margin-top: 1rem; }
}

// Single File View
.single-file-view {
    display: flex;
    justify-content: center;
    padding: 2rem 0;
}

.file-preview-card {
    background: var(--bg-secondary);
    border: 1px solid var(--border-color);
    border-radius: 16px;
    padding: 3rem;
    text-align: center;
    max-width: 500px;
    width: 100%;
    
    .file-icon-large {
        color: var(--primary);
        margin-bottom: 1.5rem;

        .custom-icon-wrapper.large {
            width: 80px;
            height: 80px;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            line-height: 0;

            :deep(svg),
            :deep(img) {
                width: 100%;
                height: 100%;
                display: block;
                object-fit: contain;
            }
        }
    }
    
    .file-details {
        h2 {
            margin: 0 0 0.5rem 0;
            font-size: 1.5rem;
            word-break: break-all;
            color: var(--text-primary);
        }
        
        .file-meta {
            color: var(--text-secondary);
            font-size: 0.95rem;
            display: block;
            margin-bottom: 2rem;
        }
        
        .file-actions {
            display: flex;
            justify-content: center;
            
            button {
                display: flex;
                align-items: center;
                gap: 0.75rem;
                padding: 0.75rem 2rem;
                font-size: 1.1rem;
                border-radius: 8px;
            }
        }
    }
    
    .encrypted-notice {
        margin-top: 2rem;
        padding: 1rem;
        background: rgba(var(--warning-rgb), 0.1);
        border: 1px solid rgba(var(--warning-rgb), 0.2);
        border-radius: 8px;
        color: var(--text-primary);
        font-size: 0.85rem;
        display: flex;
        align-items: flex-start;
        gap: 0.75rem;
        text-align: left;
        
        :deep(svg) {
            color: var(--warning);
            margin-top: 2px;
            flex-shrink: 0;
        }
    }
}

@keyframes spin { to { transform: rotate(360deg); } }
@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }

@media (max-width: 600px) {
    .public-grid {
        grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
        gap: 1rem;
    }

    .list-row {
        padding: 0.7rem 0.8rem;

        .row-actions {
            .action-btn.labeled {
                height: 32px;
                padding: 0 0.6rem;
                font-size: 0.74rem;
            }
        }
    }

    .grid-item {
        .item-hover-actions {
            opacity: 1;
            position: static;
            background: transparent;
            backdrop-filter: none;
            margin-top: 0.7rem;
        }
    }
    
    .file-preview-card {
        padding: 2rem 1.5rem;
    }
}
</style>
