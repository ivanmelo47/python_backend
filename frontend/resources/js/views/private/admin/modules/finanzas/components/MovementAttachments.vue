<template>
    <div class="movement-attachments-v3">
        <Table
            title="Recibos y Comprobantes"
            :rows="adjuntos"
            :columns="columns"
            :loading="isLoading"
            :search-query="searchQuery"
            module-id="finanzas-adjuntos"
            @update:searchQuery="searchQuery = $event"
            @request-data="fetchAdjuntos"
            :show-refresh="true"
            :items-per-page="100"
            :dropdown-z-index="1000000"
        >
            <!-- Custom Cell: File Name -->
            <template #cell-name="{ row }">
                <div class="flex items-center gap-4 cursor-pointer group py-2" @click="previewAttachment(row)">
                    <div class="file-icon-badge" :class="getFileClass(row.managed_file?.extension)">
                        <Icon :name="getIconName(row.managed_file?.extension)" :size="18" />
                    </div>
                    <span class="font-bold text-primary truncate group-hover:text-primary-light transition-colors" :title="row.managed_file?.original_name || 'Archivo sin nombre'">
                        {{ row.managed_file?.original_name || 'Archivo sin nombre' }}
                    </span>
                </div>
            </template>

            <!-- Custom Cell: Size -->
            <template #cell-size="{ row }">
                <span class="text-secondary font-medium">{{ formatSize(row.managed_file?.size_bytes || 0) }}</span>
            </template>

            <!-- Custom Cell: Date -->
            <template #cell-created_at="{ value }">
                <span class="text-tertiary">{{ formatDate(value) }}</span>
            </template>

            <!-- Actions -->
            <template #cell-botones="{ row }">
                <div class="flex items-center gap-1 justify-center">
                    <button class="btn-action-premium preview" @click.stop="previewAttachment(row)" title="Ver">
                        <Icon name="eye" :size="16" />
                    </button>
                    <button class="btn-action-premium download" @click.stop="downloadAttachment(row)" title="Descargar">
                        <Icon name="download" :size="16" />
                    </button>
                    <div class="divider-v"></div>
                    <button class="btn-action-premium delete" @click.stop="deleteAttachment(row)" title="Eliminar">
                        <Icon name="trash" :size="16" />
                    </button>
                </div>
            </template>

            <!-- Header Actions: Upload Button -->
            <template #header-actions>
                <label class="btn-upload-premium" :class="{ 'is-loading': isUploading }">
                    <Icon :name="isUploading ? 'refresh' : 'plus'" :size="18" :class="{ 'animate-spin': isUploading }" />
                    <span>{{ isUploading ? 'Subiendo...' : 'Subir Comprobante' }}</span>
                    <input type="file" class="hidden" @change="handleFileUpload" :disabled="isUploading" accept="image/*,.pdf">
                </label>
            </template>
        </Table>

        <!-- Preview Modal -->
        <ModalImagePreview
            v-if="showImagePreviewModal"
            :imageUrl="previewImageUrl"
            :title="previewImageTitle"
            :previewType="previewFileType"
            @close="closeImagePreview"
        />
    </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import Table from '@/views/private/admin/components/Table.vue';
import Icon from '@/components/Icon.vue';
import ModalImagePreview from '@/views/private/admin/modules/files/components/ModalImagePreview.vue';
import { finanzasApi } from '@/services/api/endpoints/finanzas';
import filesApi from '@/services/api/endpoints/files';
import { useAlert } from '@/composables/useAlert';
import { formatDate } from '@/utils/format-date';

const props = defineProps({
    movimientoUuid: {
        type: String,
        required: true
    }
});

const emit = defineEmits(['updated']);

const alert = useAlert();
const adjuntos = ref([]);
const isLoading = ref(false);
const isUploading = ref(false);
const searchQuery = ref('');

// Preview Modal State
const showImagePreviewModal = ref(false);
const previewImageUrl = ref('');
const previewImageTitle = ref('');
const previewFileType = ref('image');

const columns = [
    { key: 'name', label: 'NOMBRE DEL ARCHIVO' },
    { key: 'size', label: 'TAMAÑO', width: '180px', headerClass: 'text-center', cellClass: 'text-center' },
    { key: 'created_at', label: 'FECHA SUBIDA', width: '250px', headerClass: 'text-center', cellClass: 'text-center' },
    { key: 'botones', label: 'ACCIONES', width: '180px', headerClass: 'text-center', cellClass: 'text-center' }
];

const fetchAdjuntos = async () => {
    if (!props.movimientoUuid) return;
    isLoading.value = true;
    try {
        const response = await finanzasApi.getAdjuntos(props.movimientoUuid);
        adjuntos.value = response.data || response;
    } catch (error) {
        console.error('Error fetching adjuntos:', error);
    } finally {
        isLoading.value = false;
    }
};

const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    if (file.size > 10 * 1024 * 1024) {
        alert.toast.error('Archivo demasiado grande', 'El tamaño máximo es 10MB');
        return;
    }

    isUploading.value = true;
    try {
        await finanzasApi.uploadAdjunto(props.movimientoUuid, file);
        alert.toast.success('Éxito', 'Comprobante añadido correctamente');
        fetchAdjuntos();
        emit('updated');
    } catch (error) {
        alert.toast.error('Error', 'No se pudo subir el archivo');
    } finally {
        isUploading.value = false;
        event.target.value = '';
    }
};

const deleteAttachment = async (adj) => {
    const confirmed = await alert.confirm(
        '¿Eliminar comprobante?',
        'Este archivo se eliminará permanentemente del servidor y del gestor de archivos.',
        'trash'
    );

    if (confirmed) {
        try {
            await finanzasApi.deleteAdjunto(adj.uuid);
            alert.toast.success('Eliminado', 'El archivo ha sido removido');
            fetchAdjuntos();
            emit('updated');
        } catch (error) {
            alert.toast.error('Error', 'No se pudo eliminar el archivo');
        }
    }
};

const previewAttachment = async (adj) => {
    if (!adj.managed_file) {
        alert.toast.error('Error', 'No se encontró la información del archivo');
        return;
    }
    try {
        const response = await filesApi.previewFile(adj.managed_file.uuid);
        const blob = new Blob([response.data], { 
            type: response.headers?.['content-type'] || adj.managed_file.mime_type || 'application/octet-stream' 
        });
        
        const ext = (adj.managed_file.extension || '').toLowerCase();
        previewFileType.value = ext === 'pdf' ? 'pdf' : 'image';
        previewImageUrl.value = URL.createObjectURL(blob);
        previewImageTitle.value = adj.managed_file.original_name;
        showImagePreviewModal.value = true;
    } catch (error) {
        alert.toast.error('Error', 'No se pudo generar la vista previa');
    }
};

const closeImagePreview = () => {
    showImagePreviewModal.value = false;
    previewImageTitle.value = '';
    previewFileType.value = 'image';
    if (previewImageUrl.value) {
        URL.revokeObjectURL(previewImageUrl.value);
        previewImageUrl.value = '';
    }
};

const downloadAttachment = async (adj) => {
    if (!adj.managed_file) {
        alert.toast.error('Error', 'No se encontró la información del archivo');
        return;
    }
    try {
        const response = await filesApi.downloadFile(adj.managed_file.uuid);
        const blob = new Blob([response.data], { 
            type: response.headers?.['content-type'] || adj.managed_file.mime_type || 'application/octet-stream' 
        });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = adj.managed_file.original_name || adj.managed_file.name;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
    } catch (error) {
        alert.toast.error('Error', 'No se pudo descargar el archivo');
    }
};

const getIconName = (ext) => {
    const e = (ext || '').toLowerCase();
    if (['jpg', 'jpeg', 'png', 'gif', 'webp'].includes(e)) return 'image';
    if (e === 'pdf') return 'filePdf';
    return 'file';
};

const getFileClass = (ext) => {
    const e = (ext || '').toLowerCase();
    if (['jpg', 'jpeg', 'png', 'gif', 'webp'].includes(e)) return 'is-image';
    if (e === 'pdf') return 'is-pdf';
    return 'is-generic';
};

const formatSize = (bytes) => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};

onMounted(fetchAdjuntos);
</script>

<style lang="scss" scoped>
.movement-attachments-v3 {
    :deep(.table-header) {
        background: transparent;
        padding: 1.5rem 2rem;
        border-bottom: 1px solid rgba(255, 255, 255, 0.05);
    }
}

.file-icon-badge {
    width: 38px;
    height: 38px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
    
    &.is-image { background: rgba(16, 185, 129, 0.1); color: #10b981; }
    &.is-pdf { background: rgba(239, 68, 68, 0.1); color: #ef4444; }
    &.is-generic { background: rgba(59, 130, 246, 0.1); color: #3b82f6; }
}

.btn-upload-premium {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 0.7rem 1.25rem;
    background: linear-gradient(135deg, #06b6d4 0%, #0891b2 100%);
    color: white;
    border: none;
    border-radius: 12px;
    font-weight: 700;
    font-size: 0.9rem;
    cursor: pointer;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    box-shadow: 0 4px 12px rgba(6, 182, 212, 0.3);

    &:hover:not(.is-loading) {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(6, 182, 212, 0.4);
        filter: brightness(1.1);
    }

    &.is-loading {
        opacity: 0.7;
        cursor: not-allowed;
    }
}

.btn-action-premium {
    width: 32px;
    height: 32px;
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(255, 255, 255, 0.05);
    color: var(--text-tertiary);
    transition: all 0.2s ease;

    &:hover {
        background: rgba(255, 255, 255, 0.08);
        color: var(--text-primary);
        
        &.preview { color: #3b82f6; border-color: rgba(59, 130, 246, 0.3); }
        &.download { color: #10b981; border-color: rgba(16, 185, 129, 0.3); }
        &.delete { color: #ef4444; border-color: rgba(239, 68, 68, 0.3); }
    }
}

.divider-v {
    width: 1px;
    height: 20px;
    background: rgba(255, 255, 255, 0.08);
    margin: 0 4px;
}
</style>
