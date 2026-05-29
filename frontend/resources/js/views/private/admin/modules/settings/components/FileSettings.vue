<template>
    <div class="file-settings-module">
        <Table
            title="Tipos de Archivos Permitidos"
            :columns="columns"
            :rows="rows"
            :pagination="pagination"
            :search-query="searchQuery"
            v-model:items-per-page="itemsPerPage"
            @update:searchQuery="searchQuery = $event"
            @request-data="fetchData"
            :pagination-mode="'server'"
            :loading="isLoading"
            search-placeholder="Buscar extensión o nombre..."
            :show-header-actions="true"
        >
            <template #header-actions>
                <button class="btn-solid-dark" @click="openCreateModal">
                    <Icon name="plus" :size="16" />
                    NUEVO TIPO
                </button>
            </template>

            <!-- Icon Column -->
            <template #cell-icon="{ row }">
                <div class="file-type-icon" v-if="row.icon" v-html="row.icon.svg_content"></div>
                <Icon v-else name="file-text" :size="24" class="text-tertiary" />
            </template>

            <!-- Extension Column -->
            <template #cell-extension="{ value }">
                <span class="extension-badge">{{ value }}</span>
            </template>

            <!-- Max Size Column -->
            <template #cell-max_file_size="{ value }">
                <span class="size-text">{{ value }} MB</span>
            </template>

            <!-- Status Column -->
            <template #cell-is_active="{ row }">
                <label class="switch" @click.stop>
                    <input
                        type="checkbox"
                        :checked="row.is_active"
                        @change="handleToggleStatus(row)"
                    >
                    <span class="slider round"></span>
                </label>
            </template>

            <!-- Actions Column -->
            <template #cell-actions="{ row }">
                <button class="dropdown-item" @click.stop="openEditModal(row)" title="Editar">
                    <Icon name="pencil" :size="16" />
                    <span>Editar</span>
                </button>
                <button class="dropdown-item delete" @click.stop="handleDelete(row)" title="Eliminar">
                    <Icon name="trash" :size="16" />
                    <span>Eliminar</span>
                </button>
            </template>
        </Table>

        <!-- Create/Edit Modal -->
        <ModalForm
            :is-visible="showModal"
            :title="isEditing ? 'Editar Tipo de Archivo' : 'Nuevo Tipo de Archivo'"
            :loading="isSaving"
            size="md"
            :columns="4"
            @close="showModal = false"
            @submit="handleSave"
        >
            <template #header-icon>
                <Icon :name="isEditing ? 'pencil' : 'plus'" :size="20" />
            </template>

            <ModalField label="Extensión" required :span="2" :error="formErrors.extension?.[0]">
                <input
                    v-model="formData.extension"
                    type="text"
                    placeholder="Ej. pdf"
                    :disabled="isEditing"
                />
            </ModalField>

            <ModalField label="Nombre Descriptivo" required :span="2" :error="formErrors.name?.[0]">
                <input
                    v-model="formData.name"
                    type="text"
                    placeholder="Ej. Documento PDF"
                />
            </ModalField>

            <ModalField label="MIME Type" :span="4" :error="formErrors.mime_type?.[0]">
                <input
                    v-model="formData.mime_type"
                    type="text"
                    placeholder="Ej. application/pdf"
                />
            </ModalField>

            <ModalField label="Tamaño Máximo (MB)" required :span="2" :error="formErrors.max_file_size?.[0]">
                <input
                    v-model="formData.max_file_size"
                    type="number"
                />
            </ModalField>

            <ModalField label="Habilitado" :span="2">
                <div class="checkbox-wrapper">
                    <label class="switch-inline">
                        <input type="checkbox" v-model="formData.is_active">
                        <span class="slider round"></span>
                    </label>
                    <span class="ml-2">{{ formData.is_active ? 'Activo' : 'Inactivo' }}</span>
                </div>
            </ModalField>

            <ModalField label="Icono del Tipo de Archivo" :span="4" :error="formErrors.icon_uuid?.[0]">
                <IconSelect
                    v-model="formData.icon_uuid"
                    :selected-icon-data="initialIconData"
                />
            </ModalField>
        </ModalForm>
    </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue';
import Table from '../../../components/Table.vue';
import Icon from '../../../../../../components/Icon.vue';
import ModalForm from '../../../components/ModalForm.vue';
import ModalField from '../../../components/ModalField.vue';
import IconSelect from '../../../../../../components/IconSelect.vue';
import { settingsApi } from '../../../../../../services/api/endpoints/settings';
import { useTableData } from '../../../../../../composables/useTableData';
import { useTableConfig } from '../../../../../../composables/useTableConfig';
import { useAlert } from '../../../../../../composables/useAlert';

const alert = useAlert();
const { itemsPerPage } = useTableConfig();
const searchQuery = ref('');

// Table Columns
const columns = [
    { key: 'actions', label: 'ACCIONES', headerClass: 'compact', cellClass: 'compact' },
    { key: 'icon', label: 'ICONO', headerClass: 'compact', cellClass: 'compact' },
    { key: 'extension', label: 'EXTENSIÓN' },
    { key: 'name', label: 'NOMBRE' },
    { key: 'mime_type', label: 'MIME TYPE' },
    { key: 'max_file_size', label: 'TAMAÑO MÁX' },
    { key: 'is_active', label: 'ESTADO' }
];

// Modal & Form State
const showModal = ref(false);
const isEditing = ref(false);
const isSaving = ref(false);
const editingId = ref(null);
const formErrors = ref({});
const initialIconData = ref(null);

const formData = reactive({
    extension: '',
    name: '',
    mime_type: '',
    max_file_size: 10,
    is_active: true,
    icon_uuid: null
});

// Data fetching via composable
const transformer = (item) => ({
    ...item
});

const {
    data: rows,
    loading: isLoading,
    pagination,
    fetchData
} = useTableData(settingsApi.getFileConfigurations, {
    transformer,
    mode: 'server',
    itemsPerPage,
    searchQuery
});

// Actions
const openCreateModal = () => {
    isEditing.value = false;
    editingId.value = null;
    formData.extension = '';
    formData.name = '';
    formData.mime_type = '';
    formData.max_file_size = 10;
    formData.is_active = true;
    formData.icon_uuid = null;
    initialIconData.value = null;
    formErrors.value = {};
    showModal.value = true;
};

const openEditModal = (row) => {
    isEditing.value = true;
    editingId.value = row.id;
    formData.extension = row.extension;
    formData.name = row.name;
    formData.mime_type = row.mime_type;
    formData.max_file_size = row.max_file_size;
    formData.is_active = row.is_active;
    formData.icon_uuid = row.icon?.uuid || null;
    initialIconData.value = row.icon || null;
    formErrors.value = {};
    showModal.value = true;
};

const handleSave = async () => {
    isSaving.value = true;
    formErrors.value = {};

    try {
        if (isEditing.value) {
            await settingsApi.updateFileConfiguration(editingId.value, formData);
            alert.toast.success('Actualizado', 'Configuración actualizada correctamente');
        } else {
            await settingsApi.createFileConfiguration(formData);
            alert.toast.success('Creado', 'Nuevo tipo de archivo agregado');
        }
        showModal.value = false;
        fetchData();
    } catch (error) {
        if (error.response?.data?.errors) {
            formErrors.value = error.response.data.errors;
        } else {
            alert.toast.error('Error', error.response?.data?.message || 'Error al guardar');
        }
    } finally {
        isSaving.value = false;
    }
};

const handleToggleStatus = async (row) => {
    try {
        await settingsApi.toggleFileConfigurationStatus(row.id);
        row.is_active = !row.is_active;
        alert.toast.success('Estado actualizado', `Tipo .${row.extension} ${row.is_active ? 'activado' : 'desactivado'}`);
    } catch (error) {
        alert.toast.error('Error', 'No se pudo cambiar el estado');
    }
};

const handleDelete = async (row) => {
    const confirmed = await alert.fire({
        title: '¿Eliminar tipo de archivo?',
        text: `¿Estás seguro de eliminar el soporte para archivos .${row.extension}?`,
        type: 'warning',
        showCancel: true,
        confirmText: 'Sí, eliminar',
        cancelText: 'Cancelar'
    });

    if (confirmed) {
        try {
            await settingsApi.deleteFileConfiguration(row.id);
            alert.toast.success('Eliminado', 'El tipo de archivo ha sido removido');
            fetchData();
        } catch (error) {
            alert.toast.error('Error', 'No se pudo eliminar el registro');
        }
    }
};
</script>

<style lang="scss" scoped>
.file-settings-module {
    .file-type-icon {
        width: 32px;
        height: 32px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: var(--primary);

        :deep(svg) {
            width: 100%;
            height: 100%;
        }
    }

    .extension-badge {
        position: static;
        display: inline-flex;
        align-items: center;
        background: var(--bg-tertiary);
        color: var(--primary);
        padding: 0.2rem 0.6rem;
        border-radius: 6px;
        font-weight: 700;
        font-size: 0.85rem;
        text-transform: uppercase;
        border: 1px solid var(--border-color);
    }

    .size-text {
        font-weight: 600;
        color: var(--text-primary);
    }

    .checkbox-wrapper {
        display: flex;
        align-items: center;
        height: 100%;
    }
}

/* Switch Styles */
.switch, .switch-inline {
    position: relative;
    display: inline-block;
    width: 44px;
    height: 22px;
}

.switch input, .switch-inline input {
    opacity: 0;
    width: 0;
    height: 0;
}

.slider {
    position: absolute;
    cursor: pointer;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-color: var(--bg-tertiary);
    transition: .4s;
    border: 1px solid var(--border-color);
}

.slider:before {
    position: absolute;
    content: "";
    height: 14px;
    width: 14px;
    left: 4px;
    bottom: 3px;
    background-color: white;
    transition: .4s;
}

input:checked + .slider {
    background-color: var(--primary);
}

input:checked + .slider:before {
    transform: translateX(20px);
}

.slider.round {
    border-radius: 24px;
}

.slider.round:before {
    border-radius: 50%;
}
</style>
