<template>
    <article class="editor-card">
        <Table
            title="Tecnologías"
            :columns="columns"
            :rows="technologies"
            paginationMode="client"
            :showRefresh="false"
            searchPlaceholder="Buscar tecnologías..."
            cardTitleTemplate="{label}"
            v-model:search-query="searchQuery"
            @toggle-status="handleToggleStatus"
        >
            <template #header-actions>
                <button type="button" class="btn-solid" @click="openCreateModal" style="display: flex; align-items: center; gap: 6px;">
                    <Icon name="plus" :size="18" />
                    <span>NUEVO</span>
                </button>
            </template>

            <!-- Custom Cell for Icon Preview -->
            <template #cell-icon="{ row }">
                <div style="display: flex; align-items: center; justify-content: center; width: 32px; height: 32px; background: var(--bg-secondary); border-radius: 6px; border: 1px solid var(--border-color);">
                    <DynamicIcon
                        v-if="row.icon_uuid && row.icon_data"
                        :name="`db:${row.icon_data.name || 'technology'}`"
                        :databaseData="row.icon_data"
                        :size="18"
                    />
                    <Icon v-else name="minus" :size="18" />
                </div>
            </template>

            <!-- Custom Cell for Actions -->
            <template #cell-actions="{ row }">
                <button class="dropdown-item" @click="openEditModal(row)">
                    <Icon name="pencil" :size="16" /> Editar
                </button>
                <button class="dropdown-item text-danger" @click="removeTechnology(row)">
                    <Icon name="trash" :size="16" /> Eliminar
                </button>
            </template>
        </Table>

        <ModalForm
            :isVisible="showFormModal"
            :title="editingIndex > -1 ? 'Editar Tecnología' : 'Nueva Tecnología'"
            submitLabel="Guardar"
            :loading="false"
            @close="closeFormModal"
            @submit="submitForm"
        >
            <ModalField label="Nombre" :required="true" :span="2">
                <input v-model.trim="formData.label" type="text" maxlength="100" placeholder="Ej: Vue 3" required />
            </ModalField>

            <ModalField label="Icono asociado" :span="2">
                <IconSelect
                    category="portafolio"
                    v-model="formData.icon_uuid"
                    :selected-icon-data="formData.icon_data"
                    @change="handleTechnologyIconChange"
                />
            </ModalField>
            <ModalField label="¿Visible en portafolio?" :span="1">
                <div class="toggle-field">
                    <label class="toggle-switch">
                        <input type="checkbox" v-model="formData.is_active" />
                        <span class="toggle-slider"></span>
                    </label>
                    <span>{{ formData.is_active !== false ? 'Mostrar tecnología' : 'Ocultar tecnología' }}</span>
                </div>
            </ModalField>
        </ModalForm>
    </article>
</template>

<script setup>
import { ref } from 'vue';
import { useAlert } from '@/composables/useAlert';
import Table from '@/views/private/admin/components/Table.vue';
import ModalForm from '@/views/private/admin/components/ModalForm.vue';
import ModalField from '@/views/private/admin/components/ModalField.vue';
import Icon from '@/components/Icon.vue';
import IconSelect from '@/components/IconSelect.vue';
import DynamicIcon from '@/components/DynamicIcon.vue';

const props = defineProps({
    technologies: { type: Array, required: true }
});

const alert = useAlert();
const searchQuery = ref('');

const columns = [
    { key: 'actions', label: 'ACCIONES', headerClass: 'compact', cellClass: 'compact' },
    { 
        key: 'is_active', 
        label: 'VISIBLE', 
        type: 'switch', 
        cellClass: 'text-center',
        activeLabel: 'SI',
        inactiveLabel: 'NO'
    },
    { key: 'icon', label: 'ICONO', cellClass: 'compact text-center' },
    { key: 'label', label: 'NOMBRE DE TECNOLOGÍA' }
];

const showFormModal = ref(false);
const editingIndex = ref(-1);

const initialForm = {
    label: '',
    icon_uuid: null,
    icon_data: null,
    is_active: true
};

const formData = ref({ ...initialForm });

function openCreateModal() {
    editingIndex.value = -1;
    formData.value = { ...initialForm };
    showFormModal.value = true;
}

function openEditModal(row) {
    const realIdx = props.technologies.indexOf(row);
    if (realIdx === -1) return;
    editingIndex.value = realIdx;
    formData.value = { ...row };
    showFormModal.value = true;
}

function closeFormModal() {
    showFormModal.value = false;
    editingIndex.value = -1;
    formData.value = { ...initialForm };
}

function handleTechnologyIconChange(icon) {
    formData.value.icon_data = icon || null;
}

function submitForm() {
    if (editingIndex.value > -1) {
        props.technologies[editingIndex.value] = { ...formData.value };
        alert.toast.success('Editado', 'Tecnología actualizada con éxito.');
    } else {
        props.technologies.push({ ...formData.value });
        alert.toast.success('Creado', 'Tecnología registrada con éxito.');
    }
    closeFormModal();
}

function removeTechnology(row) {
    const realIdx = props.technologies.indexOf(row);
    if (realIdx === -1) return;
    if (confirm('¿Estás seguro de eliminar esta tecnología?')) {
        props.technologies.splice(realIdx, 1);
        alert.toast.success('Eliminado', 'Tecnología eliminada con éxito.');
    }
}
function handleToggleStatus({ row }) {
    row.is_active = !row.is_active;
}
</script>
