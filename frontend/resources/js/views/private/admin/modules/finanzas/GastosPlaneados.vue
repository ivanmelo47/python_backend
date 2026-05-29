<template>
    <div class="dashboard-module">
        <Table 
            title="Movimientos Programados y Gastos Planeados"
            :rows="scheduledMovements"
            :columns="columns"
            :loading="loading"
            show-refresh
            @refresh="fetchData"
            module-id="finanzas-programados"
            @row-click="handleRowClick"
        >
            <template #cell-status="{ row, value }">
                <div class="flex items-center">
                    <label class="switch" @click.stop>
                        <input
                            type="checkbox"
                            :checked="value === 'activo'"
                            @change="toggleStatus(row)"
                        >
                        <span class="slider"></span>
                    </label>
                </div>
            </template>

            <template #cell-monto="{ row, value }">
                <span class="font-bold" :class="row.tipo === 'ingreso' ? 'text-success' : 'text-danger'">
                    {{ row.tipo === 'ingreso' ? '+' : '-' }} {{ formatCurrency(value) }}
                </span>
            </template>

            <template #cell-proxima_ejecucion="{ value }">
                <div class="date-display">
                    <Icon name="calendar" :size="14" class="text-primary" />
                    <span class="date-text">{{ formatDate(value) }}</span>
                </div>
            </template>

            <template #cell-hora="{ value }">
                <div class="flex items-center gap-2">
                    <Icon name="clock" :size="14" class="text-tertiary" />
                    <span class="text-sm font-medium">{{ value ? value.substring(0, 5) : '23:00' }}</span>
                </div>
            </template>

            <template #cell-frecuencia="{ value }">
                <span class="frequency-tag">{{ value }}</span>
            </template>

            <template #cell-cuenta="{ value }">
                <div v-if="value" class="flex items-center gap-2">
                    <DynamicIcon 
                        v-if="value.icon_data"
                        :name="`db:${value.icon_data.name}`" 
                        :databaseData="value.icon_data" 
                        :size="16" 
                    />
                    <Icon v-else :name="value.icon || 'wallet'" :size="16" class="text-tertiary" />
                    <span class="text-sm">{{ value.nombre }}</span>
                </div>
            </template>

            <template #header-actions>
                <div class="header-actions-wrapper">
                    <button class="header-dropdown-trigger" :class="{ 'active': showFabMenu }" @click="showFabMenu = !showFabMenu">
                        <Icon :name="showFabMenu ? 'x' : 'plus'" :size="16" /> NUEVO / REGISTRAR
                    </button>
                    <div v-if="showFabMenu" class="header-actions-menu">
                        <button class="dropdown-item item-income" @click="openCreateModal('ingreso'); showFabMenu = false">
                            <Icon name="arrowDown" :size="16" class="text-success" /> 
                            <span>Ingreso a futuro</span>
                        </button>
                        <button class="dropdown-item item-expense" @click="openCreateModal('gasto'); showFabMenu = false">
                            <Icon name="arrowUp" :size="16" class="text-danger" /> 
                            <span>Gasto a futuro</span>
                        </button>
                    </div>
                    <div v-if="showFabMenu" class="menu-overlay-transparent" @click="showFabMenu = false"></div>
                </div>
            </template>

            <!-- Card View Customizations -->
            <template #cell-descripcion="{ row, value }">
                <div class="flex items-center gap-2">
                    <div 
                        v-if="row.categoria_rel?.icon_data" 
                        class="category-icon-main"
                        :style="{ color: row.categoria_rel.color || 'var(--color-tertiary)' }"
                        :title="row.categoria_rel.nombre"
                    >
                        <DynamicIcon 
                            :name="`db:${row.categoria_rel.icon_data.name}`" 
                            :databaseData="row.categoria_rel.icon_data" 
                            :size="20" 
                        />
                    </div>
                    <span class="text-lg font-bold text-primary">{{ value }}</span>
                </div>
            </template>
            
            <!-- Cell actions for Table.vue -->
            <template #cell-actions="{ row }">
                <button class="dropdown-item" @click="openEditModal(row)">
                    <Icon name="edit" :size="16" /> Editar
                </button>
                <button class="dropdown-item text-danger" @click="confirmDelete(row)">
                    <Icon name="trash" :size="16" /> Eliminar
                </button>
            </template>
        </Table>

        <!-- Create Modal -->
        <ModalForm
            :is-visible="showCreateModal"
            :title="createTitle"
            v-model="createForm"
            :fields="formFields"
            :loading="saving"
            columns="2"
            @submit="handleCreate"
            @close="showCreateModal = false"
        >
            <template #field-categoria_uuid="{ field, modelValue }">
                <div class="flex items-center gap-2">
                    <select
                        v-model="modelValue.categoria_uuid"
                        class="flex-1"
                        :disabled="field.options.length === 0"
                    >
                        <option value="" disabled>
                            {{ field.options.length === 0 ? 'Sin categorías disponibles' : 'Selecciona una categoría' }}
                        </option>
                        <option v-for="option in field.options" :key="option.id" :value="option.id">
                            {{ option.name }}
                        </option>
                    </select>
                    <button 
                        type="button" 
                        class="btn-icon-square" 
                        title="Nueva Categoría"
                        @click="openQuickCategoryModal(createForm)"
                    >
                        <Icon name="plus" :size="18" />
                    </button>
                </div>
            </template>
        </ModalForm>

        <!-- Edit Modal -->
        <ModalForm
            :is-visible="showEditModal"
            title="Editar Programación"
            v-model="editForm"
            :fields="formFields"
            :loading="saving"
            columns="2"
            @submit="handleUpdate"
            @close="showEditModal = false"
        >
            <template #field-categoria_uuid="{ field, modelValue }">
                <div class="flex items-center gap-2">
                    <select
                        v-model="modelValue.categoria_uuid"
                        class="flex-1"
                        :disabled="field.options.length === 0"
                    >
                        <option value="" disabled>
                            {{ field.options.length === 0 ? 'Sin categorías disponibles' : 'Selecciona una categoría' }}
                        </option>
                        <option v-for="option in field.options" :key="option.id" :value="option.id">
                            {{ option.name }}
                        </option>
                    </select>
                    <button 
                        type="button" 
                        class="btn-icon-square" 
                        title="Nueva Categoría"
                        @click="openQuickCategoryModal(editForm)"
                    >
                        <Icon name="plus" :size="18" />
                    </button>
                </div>
            </template>
        </ModalForm>

        <!-- Quick Create Category Modal -->
        <ModalForm
            :is-visible="showQuickCategoryModal"
            title="Nueva Categoría Rápida"
            :loading="isCreatingQuickCategory"
            :fields="quickCategoryFields"
            v-model="quickCategoryForm"
            @submit="handleQuickCategoryCreate"
            @close="showQuickCategoryModal = false"
        >
            <template #header-icon>
                <Icon name="tag" :size="20" />
            </template>
        </ModalForm>

        <!-- Details Modal -->
        <ModalInformation
            v-if="selectedMovement"
            :is-open="showDetailsModal"
            title="Detalles de Programación"
            icon="info"
            size="md"
            :data="selectedMovement"
            :columns="detailColumns"
            show-edit-button
            submit-label="Editar Programación"
            @edit="showDetailsModal = false; openEditModal(selectedMovement)"
            @close="showDetailsModal = false"
        >
            <!-- Custom Header Slot -->
            <template #top-header>
                <div class="detail-header-row">
                    <div class="concept-badge">
                        <Icon :name="selectedMovement.tipo === 'ingreso' ? 'arrowUp' : 'arrowDown'" :size="20" />
                    </div>
                    <h4 class="concept-title">{{ selectedMovement.descripcion }}</h4>
                </div>
            </template>

            <!-- Custom Value Slots for Icons -->
            <template #value-cuenta_uuid>
                <div class="flex items-center gap-2">
                    <DynamicIcon 
                        v-if="selectedMovement.cuenta?.icon_data"
                        :name="`db:${selectedMovement.cuenta.icon_data.name}`" 
                        :databaseData="selectedMovement.cuenta.icon_data" 
                        :size="16" 
                    />
                    {{ selectedMovement.cuenta?.nombre }}
                </div>
            </template>

            <template #value-categoria_uuid>
                <div class="flex items-center gap-2">
                    <DynamicIcon 
                        v-if="selectedMovement.categoria?.icon_data"
                        :name="`db:${selectedMovement.categoria.icon_data.name}`" 
                        :databaseData="selectedMovement.categoria.icon_data" 
                        :size="16" 
                    />
                    {{ selectedMovement.categoria?.nombre || 'Sin categoría' }}
                </div>
            </template>

            <template #value-proxima_ejecucion>
                <div class="flex items-center gap-1">
                    <Icon name="calendar" :size="14" class="text-primary" />
                    {{ formatDate(selectedMovement.proxima_ejecucion) }}
                </div>
            </template>

            <template #value-hora>
                <div class="flex items-center gap-1">
                    <Icon name="clock" :size="14" class="text-tertiary" />
                    {{ selectedMovement.hora ? selectedMovement.hora.substring(0, 5) : '23:00' }}
                </div>
            </template>

            <template #value-monto>
                <span class="font-bold" :class="selectedMovement.tipo === 'ingreso' ? 'text-success' : 'text-danger'">
                    {{ selectedMovement.tipo === 'ingreso' ? '+' : '-' }} {{ formatCurrency(selectedMovement.monto) }}
                </span>
            </template>

            <template #value-status>
                <span class="status-pill" :class="selectedMovement.status">
                    {{ selectedMovement.status }}
                </span>
            </template>

            <template #value-cuenta_cargo_uuid>
                <div v-if="selectedMovement.cuenta_cargo_id" class="flex items-center gap-2">
                    <Icon name="arrowRight" :size="12" class="text-tertiary" />
                    {{ accounts.find(a => a.id === selectedMovement.cuenta_cargo_id)?.nombre || 'Cuenta de origen' }}
                </div>
                <span v-else class="text-tertiary">Externo / Terceros</span>
            </template>
        </ModalInformation>
    </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue';
import Icon from '@/components/Icon.vue';
import DynamicIcon from '@/components/DynamicIcon.vue';
import Table from '@/views/private/admin/components/Table.vue';
import ModalForm from '@/views/private/admin/components/ModalForm.vue';
import ModalInformation from '@/views/private/admin/components/ModalInformation.vue';
import api from '@/services/api';
import { useAlert } from '@/composables/useAlert';
import { useCurrency } from '@/composables/useCurrency';
import { useDate } from '@/composables/useDate';

const alert = useAlert();
const { formatCurrency } = useCurrency();
const { formatDate } = useDate();

const loading = ref(false);
const saving = ref(false);
const scheduledMovements = ref([]);
const accounts = ref([]);
const categorias = ref([]);
const showCreateModal = ref(false);
const showFabMenu = ref(false);
const showEditModal = ref(false);
const editingUuid = ref(null);
const createTitle = ref('Programar Nuevo Movimiento');
const showDetailsModal = ref(false);
const selectedMovement = ref(null);

const detailColumns = [
    { key: 'cuenta_uuid', label: 'CUENTA DESTINO' },
    { key: 'cuenta_cargo_uuid', label: 'ORIGEN' },
    { key: 'categoria_uuid', label: 'CATEGORÍA' },
    { key: 'proxima_ejecucion', label: 'PRÓXIMA FECHA' },
    { key: 'hora', label: 'HORA' },
    { key: 'frecuencia', label: 'FRECUENCIA' },
    { key: 'monto', label: 'MONTO' },
    { key: 'status', label: 'ESTADO' },
    { key: 'notas', label: 'NOTAS', fullWidth: true, isNote: true }
];

// Categorías Rápida Logic
const showQuickCategoryModal = ref(false);
const isCreatingQuickCategory = ref(false);
const activeParentForm = ref(null);
const quickCategoryForm = reactive({
    nombre: '',
    tipo: 'gasto',
    icon: null,
    color: '#3b82f6',
    status: true
});

const quickCategoryFields = computed(() => [
    { key: 'nombre', label: 'Nombre de la Categoría', type: 'text', placeholder: 'Ej. Vivienda, Suscripciones...', required: true },
    { key: 'icon', label: 'Icono representativo', type: 'icon-select' },
    { key: 'color', label: 'Color distintivo', type: 'color' }
]);

const openQuickCategoryModal = (parentForm) => {
    activeParentForm.value = parentForm;
    quickCategoryForm.nombre = '';
    quickCategoryForm.tipo = parentForm.tipo; // Heredar tipo (ingreso/gasto)
    quickCategoryForm.icon = null;
    quickCategoryForm.color = parentForm.tipo === 'ingreso' ? '#10b981' : '#3b82f6';
    showQuickCategoryModal.value = true;
};

const handleQuickCategoryCreate = async () => {
    isCreatingQuickCategory.value = true;
    try {
        const response = await api.finanzas.storeCategoria(quickCategoryForm);
        const newCategory = response.data;
        
        // Recargar categorías y seleccionar la nueva en el formulario padre
        await fetchData();
        if (activeParentForm.value) {
            activeParentForm.value.categoria_uuid = newCategory.uuid;
        }
        
        alert.toast.success('¡Listo!', 'Categoría añadida y seleccionada.');
        showQuickCategoryModal.value = false;
    } catch (e) {
        alert.toast.error('Error', 'No se pudo crear la categoría.');
    } finally {
        isCreatingQuickCategory.value = false;
    }
};

const createForm = ref({
    cuenta_uuid: '',
    tipo: 'gasto',
    monto: '',
    descripcion: '',
    categoria_uuid: '',
    frecuencia: 'mensual',
    fecha_inicio: new Date().toISOString().substr(0, 10),
    hora: '',
    fecha_fin: null,
    notas: ''
});

const openCreateModal = (tipo = 'gasto') => {
    resetCreateForm();
    createForm.value.tipo = tipo;
    createTitle.value = tipo === 'ingreso' ? 'Programar Nuevo Ingreso' : 'Programar Nuevo Gasto';
    showCreateModal.value = true;
};

const editForm = ref({});

const columns = [
    { key: 'descripcion', label: 'CONCEPTO' },
    { key: 'cuenta', label: 'CUENTA' },
    { key: 'proxima_ejecucion', label: 'PRÓXIMA FECHA' },
    { key: 'hora', label: 'HORA' },
    { key: 'frecuencia', label: 'FRECUENCIA' },
    { key: 'monto', label: 'MONTO' },
    { key: 'status', label: 'ESTADO' },
    { key: 'actions', label: '', width: '50px' }
];

const formFields = computed(() => {
    const isEdit = showEditModal.value;
    const currentType = isEdit ? editForm.value.tipo : createForm.value.tipo;
    
    const baseFields = [
        { key: 'descripcion', label: 'Descripción / Concepto', type: 'text', placeholder: 'Ej. Pago de Renta', required: true, span: 2 },
        { 
            key: 'cuenta_uuid', 
            label: 'Cuenta Destino', 
            type: 'select', 
            placeholder: 'Seleccione cuenta',
            options: accounts.value.map(a => ({ id: a.uuid, name: a.nombre + ' (' + a.banco + ')' })),
            required: true 
        }
    ];

    // Only show "Tipo" selector if we are NOT creating via the specialized dropdown
    if (isEdit) {
        baseFields.push({ 
            key: 'tipo', 
            label: 'Tipo de Movimiento', 
            type: 'select', 
            placeholder: 'Seleccione tipo',
            options: [
                { id: 'ingreso', name: 'Ingreso (+)' },
                { id: 'gasto', name: 'Gasto (-)' }
            ],
            required: true 
        });
    }

    baseFields.push(
        { key: 'monto', label: 'Monto', type: 'number', placeholder: '0.00', required: true },
        { 
            key: 'categoria_uuid', 
            label: 'Categoría', 
            type: 'select', 
            placeholder: 'Selecciona una categoría',
            options: categorias.value
                .filter(c => c.tipo === currentType || c.tipo === 'mixto')
                .map(c => ({ id: c.uuid, name: c.nombre })),
            required: true 
        },
        { 
            key: 'frecuencia', 
            label: 'Frecuencia', 
            type: 'select', 
            placeholder: 'Seleccione frecuencia',
            options: [
                { id: 'diario', name: 'Diario' },
                { id: 'semanal', name: 'Semanal' },
                { id: 'quincenal', name: 'Quincenal' },
                { id: 'mensual', name: 'Mensual' },
                { id: 'anual', name: 'Anual' }
            ],
            required: true 
        },
        { key: 'fecha_inicio', label: 'Fecha de Inicio', type: 'date', required: true },
        { key: 'hora', label: 'Hora (Opcional)', type: 'time', help: 'Por defecto: 11:00 PM' },
        { key: 'fecha_fin', label: 'Fecha de Fin (Opcional)', type: 'date' }
    );

    if (isEdit) {
        baseFields.push({ 
            key: 'status', 
            label: 'Estado', 
            type: 'select', 
            placeholder: 'Seleccione estado', 
            options: [
                { id: 'activo', name: 'Activo' },
                { id: 'pausado', name: 'Pausado' }
            ] 
        });
    }

    baseFields.push({ key: 'notas', label: 'Notas adicionales', type: 'textarea', span: 2 });
    
    // --- TRANSFER LOGIC: Add source account if it's an income ---
    if (currentType === 'ingreso') {
        // Insert after 'cuenta_uuid' (index 2)
        baseFields.splice(2, 0, {
            key: 'cuenta_cargo_uuid',
            label: '🏦 Cuenta de Origen (Opcional)',
            type: 'select',
            placeholder: '¿De dónde sale el dinero?',
            help: 'Si seleccionas una cuenta, se descontará de ella automáticamente.',
            options: accounts.value.map(a => ({ id: a.uuid, name: a.nombre + ' (' + a.banco + ')' })),
            span: 2
        });
    }

    return baseFields;
});

const fetchData = async () => {
    loading.value = true;
    try {
        const [progRes, accRes, catRes] = await Promise.all([
            api.finanzas.getProgramados(),
            api.finanzas.getCuentasAhorro({ per_page: -1 }),
            api.finanzas.getCategorias()
        ]);
        scheduledMovements.value = progRes.data;
        accounts.value = accRes.data.data;
        categorias.value = catRes.data;
    } catch (error) {
        alert.toast.error('Error', 'No se pudieron cargar los datos.');
    } finally {
        loading.value = false;
    }
};

const handleCreate = async () => {
    saving.value = true;
    try {
        const payload = { ...createForm.value };
        if (!payload.hora) payload.hora = '23:00';
        
        await api.finanzas.storeProgramado(payload);
        alert.toast.success('Creado', 'Programación guardada exitosamente.');
        showCreateModal.value = false;
        fetchData();
        resetCreateForm();
    } catch (error) {
        alert.toast.error('Error', 'No se pudo guardar la programación.');
    } finally {
        saving.value = false;
    }
};

const openEditModal = (row) => {
    editingUuid.value = row.uuid;
    
    // Truncamos las fechas para que el input type="date" del navegador no dé error
    const fecha_inicio = row.fecha_inicio ? row.fecha_inicio.split('T')[0] : '';
    const fecha_fin = row.fecha_fin ? row.fecha_fin.split('T')[0] : null;

    editForm.value = { 
        ...row, 
        cuenta_uuid: row.cuenta?.uuid,
        categoria_uuid: row.categoria_rel?.uuid,
        fecha_inicio,
        fecha_fin,
        hora: row.hora ? row.hora.substring(0, 5) : '',
        cuenta_cargo_uuid: row.cuenta_cargo_id ? accounts.value.find(a => a.id === row.cuenta_cargo_id)?.uuid : ''
    };
    showDetailsModal.value = false;
    showEditModal.value = true;
};

const handleRowClick = (row) => {
    selectedMovement.value = row;
    showDetailsModal.value = true;
};

const handleUpdate = async () => {
    saving.value = true;
    try {
        const payload = { ...editForm.value };
        if (!payload.hora) payload.hora = '23:00';

        await api.finanzas.updateProgramado(editingUuid.value, payload);
        alert.toast.success('Actualizado', 'Programación actualizada.');
        showEditModal.value = false;
        fetchData();
    } catch (error) {
        alert.toast.error('Error', 'No se pudo actualizar.');
    } finally {
        saving.value = false;
    }
};

const toggleStatus = async (row) => {
    const newStatus = row.status === 'activo' ? 'pausado' : 'activo';
    try {
        await api.finanzas.updateProgramado(row.uuid, { status: newStatus });
        row.status = newStatus;
        alert.toast.success('Estado actualizado', `Ahora está ${newStatus}`);
    } catch (error) {
        alert.toast.error('Error', 'No se pudo cambiar el estado.');
    }
};

const confirmDelete = async (row) => {
    const confirmed = await alert.confirm('¿Eliminar programación?', `Se dejarán de registrar estos movimientos automáticos.`);
    if (confirmed) {
        try {
            await api.finanzas.deleteProgramado(row.uuid);
            alert.toast.success('Eliminado');
            fetchData();
        } catch (error) {
            alert.toast.error('Error');
        }
    }
};

const getStatusClass = (status) => {
    switch (status) {
        case 'activo': return 'badge-success';
        case 'pausado': return 'badge-warning';
        case 'completado': return 'badge-info';
        default: return '';
    }
};

const resetCreateForm = () => {
    createForm.value = {
        cuenta_uuid: '',
        tipo: 'gasto',
        monto: '',
        descripcion: '',
        categoria_uuid: '',
        frecuencia: 'mensual',
        fecha_inicio: new Date().toISOString().substr(0, 10),
        hora: '',
        fecha_fin: null,
        notas: '',
        cuenta_cargo_uuid: ''
    };
};

onMounted(fetchData);
</script>

<style lang="scss" scoped>
.date-display {
    display: flex;
    align-items: center;
    gap: 8px;
    background: rgba(var(--primary-rgb), 0.08);
    padding: 4px 10px;
    border-radius: 8px;
    border: 1px solid rgba(var(--primary-rgb), 0.15);
    
    .date-text {
        font-size: 0.85rem;
        font-weight: 600;
        color: var(--text-primary);
    }
}

.frequency-tag {
    font-size: 10px;
    text-transform: uppercase;
    font-weight: 800;
    color: var(--text-tertiary);
    letter-spacing: 0.8px;
    background: var(--bg-secondary);
    border: 1px solid var(--border-color);
    padding: 2px 8px;
    border-radius: 4px;
}

.badge {
    padding: 4px 8px;
    border-radius: 4px;
    font-size: 10px;
    font-weight: 700;
    display: inline-block;

    &-success {
        background: rgba(16, 185, 129, 0.1);
        color: #10b981;
    }

    &-warning {
        background: rgba(245, 158, 11, 0.1);
        color: #f59e0b;
    }

    &-info {
        background: rgba(59, 130, 246, 0.1);
        color: #3b82f6;
    }
}

/* El estilo del switch se toma de los globales, 
   pero aseguramos que se vea bien aquí */
.switch {
    margin-left: auto;
}

.btn-icon-square {
    min-width: 44px;
    align-self: stretch;
    display: flex;
    align-items: center;
    justify-content: center;
    background: var(--bg-primary);
    border: 1px solid var(--border-color);
    border-radius: 0.85rem;
    color: var(--text-primary);
    cursor: pointer;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.05);

    &:hover {
        background: var(--primary);
        color: white;
        border-color: var(--primary);
        box-shadow: 0 4px 12px rgba(var(--primary-rgb), 0.3);
        transform: translateY(-1px);
    }

    &:active {
        transform: translateY(0);
    }
}

/* Estilos para el input de color */
:deep(input[type="color"]) {
    padding: 0;
    height: 42px;
    width: 100%;
    border: 1px solid var(--border-color);
    border-radius: 10px;
    background: var(--bg-tertiary);
    cursor: pointer;
    overflow: hidden;
    
    &::-webkit-color-swatch-wrapper {
        padding: 0;
    }
    &::-webkit-color-swatch {
        border: none;
    }
}

/* Reusable modal info styles moved to ModalInformation.vue */

.frequency-badge {
    padding: 2px 10px;
    background: var(--bg-tertiary);
    border: 1px solid var(--border-color);
    border-radius: 4px;
    font-size: 10px;
    font-weight: 800;
    text-transform: uppercase;
    color: var(--text-tertiary);
}

.status-pill {
    padding: 2px 10px;
    border-radius: 20px;
    font-size: 10px;
    font-weight: 800;
    text-transform: uppercase;
    
    &.activo {
        background: rgba(16, 185, 129, 0.1);
        color: #10b981;
    }
    &.pausado {
        background: rgba(245, 158, 11, 0.1);
        color: #f59e0b;
    }
}

/* Notes removed from here and integrated into rows */

/* Detail actions styles removed, using footer instead */
</style>
