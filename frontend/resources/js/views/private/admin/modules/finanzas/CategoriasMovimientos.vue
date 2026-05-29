<template>
    <div class="dashboard-module">
        <Table
            title="Categorías de Movimientos"
            :columns="columns"
            :rows="categorias"
            :loading="loading"
            @refresh="fetchCategorias"
            module-id="finanzas-categorias"
        >
            <template #cell-nombre="{ row, value }">
                <div class="flex items-center gap-3">
                    <div class="icon-circle" :style="{ backgroundColor: row.color + '20', color: row.color }">
                        <DynamicIcon 
                            v-if="row.icon_data"
                            :name="`db:${row.icon_data.name}`" 
                            :databaseData="row.icon_data" 
                            :size="18" 
                        />
                        <Icon v-else :name="row.icon || 'tag'" :size="18" />
                    </div>
                    <span class="font-bold text-primary">{{ value }}</span>
                </div>
            </template>

            <template #cell-tipo="{ value }">
                <span class="badge" :class="getTipoClass(value)">
                    {{ value.toUpperCase() }}
                </span>
            </template>

            <template #cell-status="{ row, value }">
                <div class="flex items-center">
                    <label class="switch" @click.stop>
                        <input
                            type="checkbox"
                            :checked="value"
                            @change="toggleStatus(row)"
                        >
                        <span class="slider"></span>
                    </label>
                </div>
            </template>

            <template #cell-actions="{ row }">
                <button class="dropdown-item" @click="openEditModal(row)">
                    <Icon name="edit" :size="16" /> Editar
                </button>
                <button class="dropdown-item text-danger" @click="confirmDelete(row)">
                    <Icon name="trash" :size="16" /> Eliminar
                </button>
            </template>

            <template #header-actions>
                <button class="btn btn-success btn-sm" @click="showCreateModal = true">
                    <Icon name="plus" :size="16" /> NUEVA
                </button>
            </template>
        </Table>

        <!-- Modal Form -->
        <ModalForm
            :is-visible="showCreateModal || showEditModal"
            :title="showEditModal ? 'Editar Categoría' : 'Nueva Categoría'"
            :loading="saving"
            :fields="formFields"
            v-model="formData"
            @submit="handleSubmit"
            @close="closeModals"
        />
    </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import Table from '@/views/private/admin/components/Table.vue';
import Icon from '@/components/Icon.vue';
import DynamicIcon from '@/components/DynamicIcon.vue';
import ModalForm from '@/views/private/admin/components/ModalForm.vue';
import IconSelect from '@/components/IconSelect.vue';
import api from '@/services/api';
import { useAlert } from '@/composables/useAlert';

const categorias = ref([]);
const loading = ref(false);
const saving = ref(false);
const showCreateModal = ref(false);
const showEditModal = ref(false);
const editingUuid = ref(null);
const alert = useAlert();

const formData = ref({
    nombre: '',
    tipo: 'gasto',
    icon: null,
    icon_data: null, // Guardamos el objeto completo para la previsualización
    color: '#3b82f6',
    status: true
});

const columns = [
    { key: 'nombre', label: 'CATEGORÍA' },
    { key: 'tipo', label: 'TIPO' },
    { key: 'status', label: 'ESTADO' },
    { key: 'actions', label: '' }
];

const formFields = computed(() => [
    { key: 'nombre', label: 'Nombre de la Categoría', type: 'text', placeholder: 'Ej. Servicios, Comida, etc.', required: true },
    { 
        key: 'tipo', 
        label: 'Tipo de Movimiento', 
        type: 'select', 
        options: [
            { id: 'ingreso', name: 'Ingreso' },
            { id: 'gasto', name: 'Gasto' },
            { id: 'mixto', name: 'Mixto (Ambos)' }
        ],
        placeholder: 'Seleccione un tipo',
        required: true 
    },
    { 
        key: 'icon', 
        label: 'Icono de la Categoría', 
        type: 'icon-select',
        selectedData: formData.value.icon_data, // Pasamos el objeto para que IconSelect lo muestre
        onChange: (icon) => { formData.value.icon_data = icon; } // Actualizamos el objeto al cambiar
    },
    { key: 'color', label: 'Color Distintivo', type: 'color' }
]);

const fetchCategorias = async () => {
    loading.value = true;
    try {
        const response = await api.finanzas.getCategorias();
        categorias.value = response.data;
    } catch (error) {
        alert.toast.error('Error', 'No se pudieron cargar las categorías.');
    } finally {
        loading.value = false;
    }
};

const handleSubmit = async () => {
    saving.value = true;
    try {
        if (showEditModal.value) {
            await api.finanzas.updateCategoria(editingUuid.value, formData.value);
            alert.toast.success('Actualizado', 'Categoría actualizada con éxito.');
        } else {
            await api.finanzas.storeCategoria(formData.value);
            alert.toast.success('Creado', 'Categoría creada con éxito.');
        }
        closeModals();
        fetchCategorias();
    } catch (error) {
        alert.toast.error('Error', 'No se pudo guardar la categoría.');
    } finally {
        saving.value = false;
    }
};

const openEditModal = (row) => {
    editingUuid.value = row.uuid;
    formData.value = { 
        nombre: row.nombre,
        tipo: row.tipo,
        icon: row.icon,
        icon_data: row.icon_data, // Cargamos el objeto del icono
        color: row.color || '#3b82f6',
        status: row.status
    };
    showEditModal.value = true;
};

const closeModals = () => {
    showCreateModal.value = false;
    showEditModal.value = false;
    editingUuid.value = null;
    formData.value = {
        nombre: '',
        tipo: 'gasto',
        icon: null,
        icon_data: null,
        color: '#3b82f6',
        status: true
    };
};

const toggleStatus = async (row) => {
    try {
        await api.finanzas.updateCategoria(row.uuid, { status: !row.status });
        fetchCategorias();
    } catch (error) {
        alert.toast.error('Error', 'No se pudo cambiar el estado.');
    }
};

const confirmDelete = async (row) => {
    const result = await alert.confirm('¿Eliminar categoría?', `Se eliminará "${row.nombre}". Esto no borrará los movimientos asociados.`);
    if (result) {
        try {
            await api.finanzas.deleteCategoria(row.uuid);
            alert.toast.success('Eliminado', 'Categoría eliminada.');
            fetchCategorias();
        } catch (error) {
            alert.toast.error('Error', 'No se pudo eliminar la categoría.');
        }
    }
};

const getTipoClass = (tipo) => {
    switch (tipo) {
        case 'ingreso': return 'badge-success';
        case 'gasto': return 'badge-danger';
        default: return 'badge-info';
    }
};

onMounted(fetchCategorias);
</script>

<style lang="scss" scoped>
.icon-circle {
    width: 36px;
    height: 36px;
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.3s ease;
}

.badge {
    padding: 4px 10px;
    border-radius: 6px;
    font-size: 10px;
    font-weight: 800;
    letter-spacing: 0.5px;

    &-success { background: rgba(16, 185, 129, 0.1); color: #10b981; }
    &-danger { background: rgba(239, 68, 68, 0.1); color: #ef4444; }
    &-info { background: rgba(59, 130, 246, 0.1); color: #3b82f6; }
}

.switch {
    position: relative;
    display: inline-block;
    width: 38px;
    height: 20px;
}
</style>
