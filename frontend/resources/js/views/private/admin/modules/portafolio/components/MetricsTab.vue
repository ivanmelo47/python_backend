<template>
    <article class="editor-card">
        <Table
            title="Métricas"
            :columns="columns"
            :rows="metrics"
            paginationMode="client"
            :showRefresh="false"
            searchPlaceholder="Buscar métricas..."
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
                        :name="`db:${row.icon_data.name || 'metric'}`"
                        :databaseData="row.icon_data"
                        :size="18"
                    />
                    <Icon v-else name="minus" :size="18" />
                </div>
            </template>

            <!-- Remove custom cell-isVisible slot as we'll use Table's built-in switch type -->

            <!-- Custom Cell for Actions -->
            <template #cell-actions="{ row }">
                <button class="dropdown-item" @click="openEditModal(row)">
                    <Icon name="pencil" :size="16" /> Editar
                </button>
                <button class="dropdown-item text-danger" @click="removeMetric(row)">
                    <Icon name="trash" :size="16" /> Eliminar
                </button>
            </template>
        </Table>

        <ModalForm
            :isVisible="showFormModal"
            :title="editingIndex > -1 ? 'Editar Métrica' : 'Nueva Métrica'"
            submitLabel="Guardar"
            :loading="false"
            @close="closeFormModal"
            @submit="submitForm"
        >
            <ModalField label="Valor" :required="true" :span="1">
                <input v-model.trim="formData.value" type="text" maxlength="20" placeholder="Ej: 6+" required />
            </ModalField>

            <ModalField label="Etiqueta" :required="true" :span="1">
                <input v-model.trim="formData.label" type="text" maxlength="80" placeholder="Ej: años de experiencia" required />
            </ModalField>

            <ModalField label="Icono asociado" :span="1">
                <IconSelect
                    category="portafolio"
                    v-model="formData.icon_uuid"
                    :selected-icon-data="formData.icon_data"
                    @change="handleMetricIconChange"
                />
            </ModalField>

            <ModalField label="¿Visible en portafolio?" :span="1">
                <div class="toggle-field">
                    <label class="toggle-switch">
                        <input type="checkbox" v-model="formData.is_active" />
                        <span class="toggle-slider"></span>
                    </label>
                    <span>{{ formData.is_active !== false ? 'Mostrar métrica' : 'Ocultar métrica' }}</span>
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
    metrics: { type: Array, required: true }
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
    { key: 'value', label: 'VALOR' },
    { key: 'label', label: 'ETIQUETA' }
];

const showFormModal = ref(false);
const editingIndex = ref(-1);

const initialForm = {
    value: '',
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
    const realIdx = props.metrics.indexOf(row);
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

function handleMetricIconChange(icon) {
    formData.value.icon_data = icon || null;
}

function submitForm() {
    if (editingIndex.value > -1) {
        props.metrics[editingIndex.value] = { ...formData.value };
        alert.toast.success('Editado', 'Métrica actualizada con éxito.');
    } else {
        props.metrics.push({ ...formData.value });
        alert.toast.success('Creado', 'Métrica registrada con éxito.');
    }
    closeFormModal();
}

function removeMetric(row) {
    const realIdx = props.metrics.indexOf(row);
    if (realIdx === -1) return;
    if (confirm('¿Estás seguro de eliminar esta métrica?')) {
        props.metrics.splice(realIdx, 1);
        alert.toast.success('Eliminado', 'Métrica eliminada con éxito.');
    }
}

function handleToggleStatus({ row }) {
    row.is_active = !row.is_active;
}
</script>

<style scoped>
.toggle-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 4px;
}

.status-text {
    font-size: 0.65rem;
    font-weight: 700;
    color: var(--text-muted);
}

.toggle-field {
    display: flex;
    align-items: center;
    gap: 12px;
    height: 42px;
    padding: 0 12px;
    background: var(--bg-secondary);
    border: 1px solid var(--border-color);
    border-radius: 8px;
    color: var(--text-secondary);
    font-size: 0.9rem;
}

/* Custom Toggle Switch */
.toggle-switch {
    position: relative;
    display: inline-block;
    width: 36px;
    height: 18px;
}

.toggle-switch input {
    opacity: 0;
    width: 0;
    height: 0;
}

.toggle-slider {
    position: absolute;
    cursor: pointer;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-color: rgba(255, 255, 255, 0.1);
    transition: .4s;
    border-radius: 18px;
    border: 1px solid var(--border-color);
}

.toggle-slider:before {
    position: absolute;
    content: "";
    height: 12px;
    width: 12px;
    left: 2px;
    bottom: 2px;
    background-color: white;
    transition: .4s;
    border-radius: 50%;
}

input:checked + .toggle-slider {
    background-color: var(--primary);
    border-color: var(--primary);
}

input:checked + .toggle-slider:before {
    transform: translateX(18px);
}
</style>
