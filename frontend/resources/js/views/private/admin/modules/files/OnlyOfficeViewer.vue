<template>
    <div ref="viewerRootRef" class="office-viewer-page" :class="{ 'is-fullscreen': isFullscreen }">
        <div class="viewer-topbar">
            <button
                class="exit-btn"
                type="button"
                :disabled="syncing || exiting"
                @click="exitAndSave"
            >
                {{ exiting ? 'Saliendo...' : 'Salir y guardar' }}
            </button>
            <button
                v-if="canSync"
                class="save-btn"
                type="button"
                :disabled="syncing"
                @click="syncChanges"
            >
                {{ syncing ? 'Sincronizando...' : 'Guardar y sincronizar' }}
            </button>
            <button class="fullscreen-btn" type="button" @click="toggleFullscreen">
                {{ isFullscreen ? 'Salir pantalla completa' : 'Pantalla completa' }}
            </button>
        </div>
        <div v-if="viewerNotice" class="viewer-notice">
            {{ viewerNotice }}
        </div>
        <div v-if="loading" class="viewer-state">Cargando visor de documento...</div>
        <div v-else-if="error" class="viewer-state error">{{ error }}</div>
        <div v-show="!loading && !error" id="onlyoffice-doc-editor" class="viewer-container"></div>
    </div>
</template>

<script setup>
import { computed, onMounted, onUnmounted, ref, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import filesApi from '@/services/api/endpoints/files';
import { useTheme } from '@/composables/useTheme';
import { useAlert } from '@/composables/useAlert';

const route = useRoute();
const router = useRouter();
const loading = ref(true);
const error = ref('');
const docEditorInstance = ref(null);
const viewerRootRef = ref(null);
const isFullscreen = ref(false);
const onlyOfficePayload = ref(null);
const syncing = ref(false);
const activeFileUuid = ref('');
const viewerNotice = ref('');
const fallbackInProgress = ref(false);
const fallbackAttempted = ref(false);
const hasPendingChanges = ref(false);
const autoSyncPendingByEdit = ref(false);
const lastEditAtMs = ref(0);
const exiting = ref(false);
const { theme } = useTheme();
const alert = useAlert();
const autoSyncEnabled = String(import.meta.env.VITE_ENABLE_ONLYOFFICE_AUTO_SYNC ?? 'false').toLowerCase() === 'true';
const parsedAutoSyncIdleMs = Number.parseInt(String(import.meta.env.VITE_ONLYOFFICE_AUTO_SYNC_IDLE_MS ?? '5000'), 10);
const autoSyncIdleMs = Number.isFinite(parsedAutoSyncIdleMs) && parsedAutoSyncIdleMs >= 1000 ? parsedAutoSyncIdleMs : 5000;
let autoSyncTimer = null;

const canSync = computed(() => {
    return !!onlyOfficePayload.value?.config?.document?.permissions?.edit;
});

const handleFullscreenChange = () => {
    isFullscreen.value = document.fullscreenElement === viewerRootRef.value;
};

const toggleFullscreen = async () => {
    if (!viewerRootRef.value) return;

    try {
        if (document.fullscreenElement === viewerRootRef.value) {
            await document.exitFullscreen();
        } else {
            await viewerRootRef.value.requestFullscreen();
        }
    } catch (_) {
        // noop
    }
};

const getOnlyOfficeUiTheme = () => (theme.value === 'dark' ? 'theme-dark' : 'theme-light');

const isPdfPayload = (payload) => {
    const sourceExtension = String(payload?.meta?.source_extension || payload?.config?.document?.fileType || '').toLowerCase();
    return sourceExtension === 'pdf';
};

const applyPayloadMeta = (payload) => {
    activeFileUuid.value = String(payload?.meta?.managed_file_uuid || route.params.uuid || '').trim();
    viewerNotice.value = String(payload?.meta?.fallback_notice || '').trim();
    hasPendingChanges.value = false;
};

const clearAutoSyncTimer = () => {
    if (autoSyncTimer) {
        clearTimeout(autoSyncTimer);
        autoSyncTimer = null;
    }
};

const scheduleAutoSync = () => {
    if (!autoSyncEnabled || !canSync.value || !autoSyncPendingByEdit.value || syncing.value) {
        return;
    }

    clearAutoSyncTimer();
    autoSyncTimer = setTimeout(async () => {
        autoSyncTimer = null;

        if (!autoSyncEnabled || !autoSyncPendingByEdit.value || syncing.value) {
            return;
        }

        const elapsed = Date.now() - Number(lastEditAtMs.value || 0);
        if (elapsed < autoSyncIdleMs) {
            scheduleAutoSync();
            return;
        }

        await syncChanges({ silent: true, source: 'auto' });
    }, autoSyncIdleMs);
};

const handlePdfFallback = async () => {
    if (fallbackInProgress.value || fallbackAttempted.value) {
        return;
    }

    const uuid = String(route.params.uuid || '').trim();
    if (!uuid) {
        return;
    }

    fallbackInProgress.value = true;
    fallbackAttempted.value = true;

    try {
        const response = await filesApi.requestOnlyOfficePdfFallback(uuid);
        const fallbackPayload = response?.data?.data;

        if (!fallbackPayload?.script_url || !fallbackPayload?.config) {
            throw new Error('No se pudo preparar el fallback PDF→Word.');
        }

        applyPayloadMeta(fallbackPayload);
        onlyOfficePayload.value = fallbackPayload;
        renderEditor(fallbackPayload);

        const message = fallbackPayload?.meta?.fallback_notice || 'Se convirtió el documento de PDF a Word para continuar la edición en línea.';
        alert.toast.info('Fallback aplicado', message, 5000);
    } catch (err) {
        const message = err?.response?.data?.data?.message || err?.response?.data?.message || err?.message || 'No se pudo aplicar fallback PDF→Word.';
        alert.toast.error('Error', message);
    } finally {
        fallbackInProgress.value = false;
    }
};

const handleOnlyOfficeError = (event) => {
    if (!onlyOfficePayload.value || !isPdfPayload(onlyOfficePayload.value)) {
        return;
    }

    handlePdfFallback();

    const errorCode = event?.data?.errorCode;
    if (typeof errorCode !== 'undefined') {
        console.warn('OnlyOffice PDF edit error code:', errorCode);
    }
};

const handleDocumentStateChange = (event) => {
    const raw = typeof event?.data === 'boolean' ? event.data : event;
    const state = !!raw;
    hasPendingChanges.value = state;

    if (!autoSyncEnabled || !canSync.value) {
        return;
    }

    if (state) {
        autoSyncPendingByEdit.value = true;
        lastEditAtMs.value = Date.now();
        scheduleAutoSync();
    }
};

const renderEditor = (payload) => {
    if (!window.DocsAPI?.DocEditor || !payload?.config) {
        return;
    }

    if (docEditorInstance.value && typeof docEditorInstance.value.destroyEditor === 'function') {
        docEditorInstance.value.destroyEditor();
    }

    const nextConfig = JSON.parse(JSON.stringify(payload.config));
    nextConfig.editorConfig = nextConfig.editorConfig || {};
    nextConfig.editorConfig.customization = nextConfig.editorConfig.customization || {};
    nextConfig.editorConfig.customization.uiTheme = getOnlyOfficeUiTheme();
    const previousEvents = nextConfig.events || {};
    nextConfig.events = {
        ...previousEvents,
        onError: (event) => {
            if (typeof previousEvents.onError === 'function') {
                previousEvents.onError(event);
            }
            handleOnlyOfficeError(event);
        },
        onDocumentStateChange: (event) => {
            if (typeof previousEvents.onDocumentStateChange === 'function') {
                previousEvents.onDocumentStateChange(event);
            }
            handleDocumentStateChange(event);
        },
    };

    docEditorInstance.value = new window.DocsAPI.DocEditor('onlyoffice-doc-editor', nextConfig);
};

const loadScript = (scriptUrl) => {
    if (window.DocsAPI?.DocEditor) {
        return Promise.resolve();
    }

    return new Promise((resolve, reject) => {
        const existing = document.querySelector(`script[data-onlyoffice="${scriptUrl}"]`);
        if (existing) {
            existing.addEventListener('load', () => resolve(), { once: true });
            existing.addEventListener('error', () => reject(new Error('No se pudo cargar el script de OnlyOffice.')), { once: true });
            return;
        }

        const script = document.createElement('script');
        script.src = scriptUrl;
        script.async = true;
        script.dataset.onlyoffice = scriptUrl;
        script.onload = () => resolve();
        script.onerror = () => reject(new Error('No se pudo cargar el script de OnlyOffice.'));
        document.head.appendChild(script);
    });
};

const initViewer = async () => {
    loading.value = true;
    error.value = '';

    try {
        const uuid = String(route.params.uuid || '').trim();
        if (!uuid) {
            throw new Error('No se encontró el identificador del archivo.');
        }

        const response = await filesApi.getOnlyOfficeConfig(uuid);
        const payload = response?.data?.data;

        if (!payload?.script_url || !payload?.config) {
            throw new Error('La configuración de OnlyOffice es inválida.');
        }

        await loadScript(payload.script_url);

        if (!window.DocsAPI?.DocEditor) {
            throw new Error('OnlyOffice no está disponible en este momento.');
        }

        onlyOfficePayload.value = payload;
        fallbackAttempted.value = false;
        autoSyncPendingByEdit.value = false;
        lastEditAtMs.value = 0;
        clearAutoSyncTimer();
        applyPayloadMeta(payload);
        renderEditor(payload);
    } catch (err) {
        error.value = err?.response?.data?.message || err?.message || 'No se pudo abrir el visor del documento.';
    } finally {
        loading.value = false;
    }
};

const syncChanges = async ({ silent = false, source = 'manual' } = {}) => {
    if (syncing.value || !canSync.value) {
        return;
    }

    const uuid = String(activeFileUuid.value || route.params.uuid || '').trim();
    if (!uuid) {
        alert.toast.error('Error', 'No se encontró el identificador del archivo.');
        return;
    }

    syncing.value = true;
    try {
        const documentKey = onlyOfficePayload.value?.config?.document?.key || null;
        const response = await filesApi.syncOnlyOfficeFile(uuid, {
            document_key: documentKey,
        });

        hasPendingChanges.value = false;
        autoSyncPendingByEdit.value = false;
        lastEditAtMs.value = 0;

        if (!silent) {
            alert.toast.success('Sincronización', response?.data?.data?.message || 'Se solicitó la sincronización del archivo.');
        }

        return true;
    } catch (err) {
        const message = err?.response?.data?.data?.message || err?.response?.data?.message || 'No se pudo sincronizar el documento.';
        const isNoPendingChanges = String(message).toLowerCase().includes('no hay cambios pendientes');

        if (isNoPendingChanges) {
            hasPendingChanges.value = false;
            autoSyncPendingByEdit.value = false;
            lastEditAtMs.value = 0;
            clearAutoSyncTimer();
        }

        if (!silent || !isNoPendingChanges) {
            alert.toast.error(source === 'auto' ? 'Auto-sincronización' : 'Error', message);
        }

        return false;
    } finally {
        syncing.value = false;

        if (autoSyncEnabled && hasPendingChanges.value) {
            scheduleAutoSync();
        }
    }
};

const buildReturnLocation = () => {
    const folderUuid = String(route.query.origin_folder_uuid || '').trim();
    const query = {
        page: String(route.query.origin_page || '1'),
        sort_by: String(route.query.origin_sort_by || 'created_at'),
        sort_dir: String(route.query.origin_sort_dir || 'desc'),
    };

    if (folderUuid) {
        return {
            name: 'FilesFolder',
            params: { uuid: folderUuid },
            query,
        };
    }

    return {
        name: 'Files',
        query,
    };
};

const exitAndSave = async () => {
    if (exiting.value || syncing.value) {
        return;
    }

    exiting.value = true;
    try {
        const shouldSync = canSync.value && (hasPendingChanges.value || autoSyncPendingByEdit.value);
        if (shouldSync) {
            const synced = await syncChanges({ silent: false, source: 'exit' });
            if (!synced) {
                return;
            }
        }

        await router.push(buildReturnLocation());
    } finally {
        exiting.value = false;
    }
};

watch(
    () => theme.value,
    () => {
        if (loading.value || error.value || !onlyOfficePayload.value) {
            return;
        }

        renderEditor(onlyOfficePayload.value);
    }
);

onMounted(() => {
    document.addEventListener('fullscreenchange', handleFullscreenChange);
    initViewer();
});

onUnmounted(() => {
    document.removeEventListener('fullscreenchange', handleFullscreenChange);
    clearAutoSyncTimer();

    if (document.fullscreenElement === viewerRootRef.value) {
        document.exitFullscreen();
    }

    if (docEditorInstance.value && typeof docEditorInstance.value.destroyEditor === 'function') {
        docEditorInstance.value.destroyEditor();
    }
});
</script>

<style scoped lang="scss">
.office-viewer-page {
    width: 100%;
    height: calc(100vh - 120px);
    min-height: 620px;
    border: 1px solid var(--border-color);
    border-radius: 12px;
    overflow: hidden;
    background: var(--bg-primary);
    display: flex;
    flex-direction: column;
}

.office-viewer-page.is-fullscreen {
    width: 100vw;
    height: 100vh;
    min-height: 100vh;
    border-radius: 0;
    border: none;
}

.viewer-topbar {
    height: 44px;
    min-height: 44px;
    padding: 0 0.75rem;
    display: flex;
    align-items: center;
    justify-content: flex-end;
    gap: 0.5rem;
    border-bottom: 1px solid var(--border-color);
    background: var(--bg-secondary);
}

.exit-btn {
    height: 32px;
    padding: 0 0.85rem;
    border-radius: 8px;
    border: 1px solid var(--border-color);
    background: var(--bg-tertiary);
    color: var(--text-primary);
    font-size: 0.85rem;
    cursor: pointer;
}

.exit-btn:disabled {
    opacity: 0.75;
    cursor: not-allowed;
}

.viewer-notice {
    min-height: 38px;
    display: flex;
    align-items: center;
    padding: 0 0.75rem;
    border-bottom: 1px solid var(--border-color);
    background: var(--bg-tertiary);
    color: var(--text-secondary);
    font-size: 0.83rem;
}

.save-btn {
    height: 32px;
    padding: 0 0.85rem;
    border-radius: 8px;
    border: 1px solid var(--border-color);
    background: var(--bg-tertiary);
    color: var(--text-primary);
    font-size: 0.85rem;
    cursor: pointer;
}

.save-btn:disabled {
    opacity: 0.75;
    cursor: not-allowed;
}

.fullscreen-btn {
    height: 32px;
    padding: 0 0.75rem;
    border-radius: 8px;
    border: 1px solid var(--border-color);
    background: var(--bg-tertiary);
    color: var(--text-primary);
    font-size: 0.85rem;
    cursor: pointer;
}

.viewer-state {
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: center;
    color: var(--text-secondary);
    font-size: 1rem;
}

.viewer-state.error {
    color: #ff6b6b;
}

.viewer-container {
    width: 100%;
    flex: 1;
    min-height: 0;
}
</style>
