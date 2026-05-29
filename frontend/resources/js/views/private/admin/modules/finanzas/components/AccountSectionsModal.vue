<template>
    <ModalForm
        :isVisible="show"
        :title="`Gestión de Secciones: ${account?.nombre || ''}`"
        size="full"
        @close="$emit('close')"
        :hideFooter="true"
        :class="['sections-management-modal', { 'sidebar-collapsed': !isSidebarOpen }]"
        :style="{ '--sidebar-offset': currentOffset }"
    >
        <template #header-icon>
            <Icon name="layers" :size="20" />
        </template>

        <div class="sections-manager-v3">
            <!-- Top Summary Bar -->
            <div class="summary-bar-premium mb-8">
                <div class="summary-item glass-panel total">
                    <div class="item-icon">
                        <Icon name="wallet" :size="20" />
                    </div>
                    <div class="item-details">
                        <span class="item-label">SALDO TOTAL EN CUENTA</span>
                        <span class="item-value">{{ formatCurrency(account?.saldo_actual || 0) }}</span>
                    </div>
                </div>
                <div class="summary-item glass-panel available" :class="{ 'is-negative': unassignedBalance < 0 }">
                    <div class="item-icon">
                        <Icon :name="unassignedBalance >= 0 ? 'unlock' : 'alert-triangle'" :size="20" />
                    </div>
                    <div class="item-details">
                        <span class="item-label">SALDO LIBRE / DISPONIBLE</span>
                        <span class="item-value">{{ formatCurrency(unassignedBalance) }}</span>
                    </div>
                </div>
            </div>

            <!-- Sections Table -->
            <div class="sections-table-container glass-panel animate-slide-up">
                <Table
                    title="Listado de Apartados"
                    :rows="sections"
                    :columns="tableColumns"
                    :loading="isLoading"
                    :search-query="searchQuery"
                    module-id="finanzas-secciones"
                    @update:searchQuery="searchQuery = $event"
                    @request-data="fetchSections"
                    :show-refresh="true"
                    :items-per-page="100"
                    :dropdown-z-index="1000000"
                >
                    <template #cell-nombre="{ value, row }">
                        <div class="flex items-center gap-3 w-full overflow-hidden" style="max-width: calc(100% - 40px);">
                            <div class="section-color-dot" :style="{ backgroundColor: row.color, boxShadow: `0 0 10px ${row.color}40` }"></div>
                            <div class="flex flex-col min-w-0 flex-1">
                                <span class="font-bold truncate" :title="value">{{ value }}</span>
                                <span class="text-xs text-tertiary truncate" v-if="row.notas" :title="row.notas">{{ row.notas }}</span>
                            </div>
                        </div>
                    </template>

                    <template #cell-saldo_actual="{ value }">
                        <span class="font-black text-lg">{{ formatCurrency(value) }}</span>
                    </template>

                    <template #cell-porcentaje="{ row }">
                        <div class="percentage-display">
                            <div class="mini-progress-track">
                                <div class="mini-progress-fill" :style="{ 
                                    width: `${calculatePercentage(row.saldo_actual)}%`, 
                                    backgroundColor: row.color || 'var(--primary)' 
                                }"></div>
                            </div>
                            <span class="percentage-label">{{ calculatePercentage(row.saldo_actual) }}%</span>
                        </div>
                    </template>

                    <template #cell-actions="{ row }">
                        <div class="actions-dropdown-container">
                            <button class="dropdown-item" @click="startTransfer('deposit', row)">
                                <Icon name="plus" :size="16" class="text-success" />
                                <span>Cargar dinero</span>
                            </button>
                            <button class="dropdown-item" @click="startTransfer('withdraw', row)">
                                <Icon name="minus" :size="16" class="text-warning" />
                                <span>Retirar dinero</span>
                            </button>
                            <button class="dropdown-item" @click="startTransfer('transfer', row)">
                                <Icon name="repeat" :size="16" class="text-primary" />
                                <span>Transferir entre apartados</span>
                            </button>
                            <div class="menu-divider"></div>
                            <button class="dropdown-item" @click="startEdit(row)">
                                <Icon name="pencil" :size="16" />
                                <span>Editar configuración</span>
                            </button>
                            <button class="dropdown-item delete" @click="handleDelete(row)">
                                <Icon name="trash" :size="16" />
                                <span>Eliminar apartado</span>
                            </button>
                        </div>
                    </template>

                    <template #header-actions>
                        <button class="btn-create-section" @click="openAddModal">
                            <Icon name="plus" :size="18" />
                            <span>Crear Nuevo Apartado</span>
                        </button>
                    </template>
                </Table>
            </div>

            <!-- Nested Form Modal -->
            <ModalForm
                :isVisible="isAdding || !!editingSection"
                :title="editingSection ? 'Editar Apartado' : 'Crear Apartado'"
                size="md"
                @close="cancelForm"
                @submit="handleSave"
                :loading="isSaving"
                submit-label="Confirmar"
            >
                <div class="grid grid-cols-1 gap-6">
                    <ModalField label="Nombre del Apartado" :required="true">
                        <input v-model="form.nombre" type="text" placeholder="Ej: Fondo de Viajes">
                    </ModalField>

                    <ModalField label="Identificador Visual (Color)">
                        <div class="color-picker-integrated">
                            <div class="picker-box" :style="{ backgroundColor: form.color }">
                                <input v-model="form.color" type="color">
                            </div>
                            <input v-model="form.color" type="text" class="form-control text-center font-mono" placeholder="#000000">
                        </div>
                    </ModalField>

                    <ModalField label="Notas Adicionales">
                        <textarea v-model="form.notas" rows="3" placeholder="Opcional: Detalles u objetivos..."></textarea>
                    </ModalField>
                </div>
            </ModalForm>

            <!-- Transfer/Movement Modal -->
            <ModalForm
                :isVisible="isTransferring"
                :title="transferForm.from_section_uuid && transferForm.to_section_uuid ? 'Transferir entre Apartados' : (transferForm.to_section_uuid ? 'Cargar dinero al Apartado' : 'Retirar dinero del Apartado')"
                size="md"
                @close="isTransferring = false"
                @submit="handleTransfer"
                :loading="isSaving"
                submit-label="Confirmar Movimiento"
            >
                <div class="grid grid-cols-1 gap-6">
                    <div class="transfer-info-panel glass-panel" v-if="transferForm.from_section_uuid && transferForm.to_section_uuid">
                        <div class="flex items-center justify-between gap-4">
                            <div class="entity-badge">
                                <span class="label">Origen</span>
                                <span class="value">{{ sections.find(s => s.uuid === transferForm.from_section_uuid)?.nombre }}</span>
                            </div>
                            <Icon name="arrow-right" :size="20" class="text-tertiary" />
                            <div class="entity-badge">
                                <span class="label">Destino</span>
                                <select v-model="transferForm.to_section_uuid" class="form-control select-minimal">
                                    <option v-for="s in sections.filter(sec => sec.uuid !== transferForm.from_section_uuid)" :key="s.uuid" :value="s.uuid">
                                        {{ s.nombre }}
                                    </option>
                                </select>
                            </div>
                        </div>
                    </div>

                    <ModalField label="Monto a Mover" :required="true">
                        <div class="input-group-premium">
                            <span class="currency-symbol">$</span>
                            <input v-model="transferForm.monto" type="number" step="0.01" min="0.01" placeholder="0.00" autofocus>
                        </div>
                        <div class="helper-text mt-2" v-if="!transferForm.from_section_uuid">
                            Saldo disponible en cuenta: <span class="font-bold">{{ formatCurrency(unassignedBalance) }}</span>
                        </div>
                        <div class="helper-text mt-2" v-else>
                            Saldo actual en sección: <span class="font-bold text-primary">{{ formatCurrency(sections.find(s => s.uuid === transferForm.from_section_uuid)?.saldo_actual || 0) }}</span>
                        </div>
                    </ModalField>

                    <ModalField label="Descripción / Concepto">
                        <input v-model="transferForm.descripcion" type="text" placeholder="Ej: Ahorro quincenal">
                    </ModalField>
                </div>
            </ModalForm>
        </div>
    </ModalForm>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch, inject } from 'vue';
import { finanzasApi } from '@/services/api/endpoints/finanzas';
import ModalForm from '@/views/private/admin/components/ModalForm.vue';
import ModalField from '@/views/private/admin/components/ModalField.vue';
import Table from '@/views/private/admin/components/Table.vue';
import Icon from '@/components/Icon.vue';
import { useAlert } from '@/composables/useAlert';

const props = defineProps({
    show: Boolean,
    account: Object
});

const emit = defineEmits(['close', 'updated']);
const alert = useAlert();

const layoutConfig = inject('layoutConfig', { isSidebarOpen: ref(true) });
const isSidebarOpen = computed(() => layoutConfig.isSidebarOpen?.value ?? true);
const windowWidth = ref(window.innerWidth);

const updateWidth = () => {
    windowWidth.value = window.innerWidth;
};

onMounted(() => {
    window.addEventListener('resize', updateWidth);
});

onUnmounted(() => {
    window.removeEventListener('resize', updateWidth);
});

const currentOffset = computed(() => {
    if (windowWidth.value < 1200) return '0px';
    return isSidebarOpen.value ? '260px' : '80px';
});

const sections = ref([]);
const isLoading = ref(false);
const isSaving = ref(false);
const isAdding = ref(false);
const editingSection = ref(null);

// Transfer state
const isTransferring = ref(false);
const transferForm = ref({
    from_section_uuid: null, // null = Account unassigned
    to_section_uuid: null,
    monto: 0,
    descripcion: ''
});
const searchQuery = ref('');

const tableColumns = [
    { key: 'nombre', label: 'NOMBRE APARTADO' },
    { key: 'saldo_actual', label: 'SALDO', cellClass: 'text-right font-bold' },
    { key: 'porcentaje', label: '% DEL TOTAL', width: '150px' },
    { key: 'actions', label: '', headerClass: 'compact', cellClass: 'compact' }
];

const form = ref({
    nombre: '',
    color: '#6366f1',
    notas: ''
});

const unassignedBalance = computed(() => {
    const assigned = sections.value.reduce((sum, s) => sum + parseFloat(s.saldo_actual), 0);
    return (props.account?.saldo_actual || 0) - assigned;
});

const fetchSections = async () => {
    if (!props.account?.uuid) return;
    isLoading.value = true;
    try {
        const response = await finanzasApi.getSecciones(props.account.uuid);
        sections.value = response.data || response;
    } catch (error) {
        alert.toast.error('Error', 'No se pudieron cargar los apartados');
    } finally {
        isLoading.value = false;
    }
};

const openAddModal = () => {
    form.value = {
        nombre: '',
        color: '#6366f1',
        notas: ''
    };
    isAdding.value = true;
};

const startEdit = (section) => {
    editingSection.value = section;
    form.value = {
        nombre: section.nombre,
        color: section.color,
        notas: section.notas
    };
};

const cancelForm = () => {
    isAdding.value = false;
    editingSection.value = null;
};

const handleSave = async () => {
    isSaving.value = true;
    try {
        if (editingSection.value) {
            await finanzasApi.updateSeccion(editingSection.value.uuid, form.value);
            alert.toast.success('Actualizado', 'Apartado actualizado correctamente');
        } else {
            await finanzasApi.storeSeccion({
                ...form.value,
                cuenta_id: props.account.uuid
            });
            alert.toast.success('Creado', 'Nuevo apartado registrado');
        }
        fetchSections();
        emit('updated');
        cancelForm();
    } catch (error) {
        alert.toast.error('Error', 'No se pudo guardar el apartado');
    } finally {
        isSaving.value = false;
    }
};

const handleDelete = async (section) => {
    const confirmed = await alert.confirm(
        '¿Eliminar Apartado?',
        `Esto no eliminará el dinero, simplemente se reintegrará al saldo libre de la cuenta.`,
        'trash'
    );

    if (confirmed) {
        try {
            await finanzasApi.deleteSeccion(section.uuid);
            alert.toast.success('Eliminado', 'El apartado ha sido removido');
            fetchSections();
            emit('updated');
        } catch (error) {
            alert.toast.error('Error', 'No se pudo eliminar el apartado');
        }
    }
};

const startTransfer = (type, section = null) => {
    transferForm.value = {
        from_section_uuid: type === 'withdraw' ? section.uuid : (type === 'transfer' ? section.uuid : null),
        to_section_uuid: type === 'deposit' ? section.uuid : null,
        monto: 0,
        descripcion: type === 'deposit' ? 'Asignación de saldo' : (type === 'withdraw' ? 'Retiro a disponible' : 'Transferencia interna')
    };
    isTransferring.value = true;
};

const handleTransfer = async () => {
    const monto = parseFloat(transferForm.value.monto);
    if (monto <= 0) return;

    // Frontend validation of available funds
    if (!transferForm.value.from_section_uuid) {
        // Source is the unassigned account balance
        if (monto > unassignedBalance.value) {
            alert.toast.error('Saldo insuficiente', 'No puedes asignar más dinero del que tienes disponible en la cuenta');
            return;
        }
    } else {
        // Source is a specific section
        const source = sections.value.find(s => s.uuid === transferForm.value.from_section_uuid);
        if (source && monto > parseFloat(source.saldo_actual)) {
            alert.toast.error('Saldo insuficiente', `El apartado "${source.nombre}" solo tiene ${formatCurrency(source.saldo_actual)}`);
            return;
        }
    }

    isSaving.value = true;
    try {
        await finanzasApi.transferSeccion({
            ...transferForm.value,
            monto: monto,
            cuenta_uuid: props.account.uuid
        });
        alert.toast.success('Éxito', 'Movimiento interno completado');
        fetchSections();
        emit('updated');
        isTransferring.value = false;
    } catch (error) {
        alert.toast.error('Error', error.response?.data?.message || 'No se pudo completar el movimiento');
    } finally {
        isSaving.value = false;
    }
};

const calculatePercentage = (amount) => {
    if (!props.account?.saldo_actual || props.account.saldo_actual <= 0) return 0;
    return Math.round((amount / props.account.saldo_actual) * 100);
};

const formatCurrency = (value) => {
    return new Intl.NumberFormat('es-MX', {
        style: 'currency',
        currency: props.account?.moneda || 'MXN'
    }).format(value);
};

watch(() => props.show, (newVal) => {
    if (newVal) {
        fetchSections();
    }
});
</script>

<style lang="scss">
/* Global fix for this specific modal to avoid sidebar overlap */
.sections-management-modal.modal-overlay {
    left: var(--sidebar-offset, 0px) !important;
    width: calc(100% - var(--sidebar-offset, 0px)) !important;
    z-index: 99999 !important;
    transition: all 0.3s ease !important;

    .modal-container.modal-full {
        width: 96% !important;
        max-width: 1600px !important;
        transition: all 0.3s ease !important;

        @media (max-width: 768px) {
            width: 100% !important;
            max-width: 100% !important;
            height: 100% !important;
            max-height: 100% !important;
            margin: 0 !important;
            border-radius: 0 !important;
            border: none !important;
        }
    }
}
</style>

<style lang="scss" scoped>
.sections-manager-v3 {
    padding: 1.5rem 2rem 2rem;

    @media (max-width: 768px) {
        padding: 1rem;
    }
}

/* Summary Bar */
.summary-bar-premium {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 1.5rem;

    @media (max-width: 600px) {
        grid-template-columns: 1fr;
    }

    .summary-item {
        display: flex;
        align-items: center;
        gap: 1.5rem;
        padding: 1.5rem 2rem;
        border-radius: 1.5rem;
        border: 1px solid rgba(255, 255, 255, 0.05);
        background: rgba(255, 255, 255, 0.02);
        transition: transform 0.3s ease;

        @media (max-width: 768px) {
            padding: 1.25rem;
            gap: 1rem;
            border-radius: 1rem;
        }

        &:hover {
            transform: translateY(-5px);
            border-color: rgba(var(--primary-rgb), 0.2);
            background: rgba(var(--primary-rgb), 0.03);
        }

        .item-icon {
            width: 54px;
            height: 54px;
            border-radius: 16px;
            display: flex;
            align-items: center;
            justify-content: center;
            background: rgba(var(--primary-rgb), 0.1);
            color: var(--primary);
            box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);

            @media (max-width: 768px) {
                width: 42px;
                height: 42px;
                border-radius: 12px;
                
                :deep(svg) {
                    width: 20px;
                    height: 20px;
                }
            }
        }

        .item-label {
            display: block;
            font-size: 0.7rem;
            font-weight: 800;
            color: var(--text-tertiary);
            letter-spacing: 0.1em;
            margin-bottom: 0.25rem;

            @media (max-width: 768px) {
                font-size: 0.6rem;
            }
        }

        .item-value {
            font-size: 1.75rem;
            font-weight: 900;
            letter-spacing: -0.02em;

            @media (max-width: 768px) {
                font-size: 1.35rem;
            }
        }

        &.available {
            .item-icon { background: rgba(16, 185, 129, 0.1); color: #10b981; }
            &.is-negative {
                .item-icon { background: rgba(239, 68, 68, 0.1); color: #ef4444; }
                .item-value { color: #ef4444; }
            }
        }
    }
}

/* Sections Table overrides */
.sections-table-container {
    background: rgba(255, 255, 255, 0.02);
    border-radius: 24px;
    border: 1px solid rgba(255, 255, 255, 0.05);
    overflow: hidden;

    :deep(.table-header) {
        background: transparent;
        border-bottom: 1px solid rgba(255, 255, 255, 0.05);
        padding: 1.5rem 2rem;

        .title {
            font-size: 1.1rem;
            font-weight: 800;
            color: var(--text-secondary);
            letter-spacing: 0.05em;
        }

        .search-input-wrapper {
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid rgba(255, 255, 255, 0.05);
            border-radius: 12px;
            padding: 0.5rem 1rem;
            transition: all 0.3s ease;

            &:focus-within {
                background: rgba(255, 255, 255, 0.08);
                border-color: var(--primary);
                box-shadow: 0 0 0 2px rgba(var(--primary-rgb), 0.2);
            }

            input {
                background: transparent !important;
                border: none !important;
                color: var(--text-primary) !important;
                font-size: 0.9rem !important;
            }
        }
    }
}

/* Indicators */
.section-color-dot {
    width: 14px;
    height: 14px;
    border-radius: 50%;
    position: relative;
    box-shadow: 0 0 12px rgba(0,0,0,0.4);
    flex-shrink: 0;

    &::after {
        content: '';
        position: absolute;
        top: 20%;
        left: 20%;
        width: 35%;
        height: 35%;
        background: rgba(255, 255, 255, 0.6);
        border-radius: 50%;
        filter: blur(0.5px);
    }
}

.percentage-display {
    display: flex;
    align-items: center;
    gap: 1rem;

    .mini-progress-track {
        flex: 1;
        height: 6px;
        background: rgba(255, 255, 255, 0.05);
        border-radius: 3px;
        overflow: hidden;
        min-width: 120px;
    }

    .mini-progress-fill {
        height: 100%;
        border-radius: 3px;
        transition: width 0.8s cubic-bezier(0.4, 0, 0.2, 1);
    }

    .percentage-label {
        font-size: 0.85rem;
        font-weight: 800;
        color: var(--text-tertiary);
        min-width: 40px;
    }
}

.btn-create-section {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 0.7rem 1.25rem;
    background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
    color: white;
    border: none;
    border-radius: 12px;
    font-weight: 700;
    font-size: 0.9rem;
    cursor: pointer;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    box-shadow: 0 4px 12px rgba(var(--primary-rgb), 0.3);

    &:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(var(--primary-rgb), 0.4);
        filter: brightness(1.1);
    }

    &:active {
        transform: translateY(1px);
    }

    span {
        white-space: nowrap;
    }
}

.actions-dropdown-container {
    display: flex;
    flex-direction: column;
    min-width: 220px;

    .dropdown-divider {
        height: 1px;
        background: rgba(255, 255, 255, 0.08);
        margin: 4px 0;
    }
}

/* Transfer UI */
.transfer-info-panel {
    padding: 1.25rem;
    background: rgba(255, 255, 255, 0.03);
    border-radius: 16px;
    
    .entity-badge {
        display: flex;
        flex-direction: column;
        gap: 0.25rem;
        flex: 1;

        .label {
            font-size: 0.65rem;
            font-weight: 800;
            text-transform: uppercase;
            color: var(--text-tertiary);
            letter-spacing: 0.05em;
        }

        .value {
            font-size: 1rem;
            font-weight: 700;
            color: var(--text-primary);
        }

        .select-minimal {
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
            color: var(--text-primary);
            padding: 0.4rem 0.75rem;
            border-radius: 8px;
            font-weight: 700;
            outline: none;
            cursor: pointer;

            &:focus {
                border-color: var(--primary);
            }
        }
    }
}

.input-group-premium {
    position: relative;
    display: flex;
    align-items: center;
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 14px;
    padding: 0 1rem;
    transition: all 0.3s ease;

    &:focus-within {
        background: rgba(255, 255, 255, 0.06);
        border-color: var(--primary);
        box-shadow: 0 0 0 4px rgba(var(--primary-rgb), 0.15);
    }

    .currency-symbol {
        font-size: 1.5rem;
        font-weight: 900;
        color: var(--primary);
        margin-right: 0.75rem;
    }

    input {
        background: transparent !important;
        border: none !important;
        padding: 1.25rem 0 !important;
        font-size: 2rem !important;
        font-weight: 900 !important;
        color: var(--text-primary) !important;
        width: 100%;
        outline: none;

        &::placeholder {
            color: rgba(255, 255, 255, 0.1);
        }
    }
}

.helper-text {
    font-size: 0.8rem;
    color: var(--text-tertiary);
}

.color-picker-integrated {
    display: flex;
    align-items: center;
    gap: 1rem;

    .picker-box {
        width: 48px;
        height: 48px;
        border-radius: 12px;
        position: relative;
        overflow: hidden;
        border: 2px solid rgba(255, 255, 255, 0.1);
        cursor: pointer;

        input[type="color"] {
            position: absolute;
            inset: -10px;
            width: 200%;
            height: 200%;
            cursor: pointer;
            opacity: 0;
        }
    }
}
</style>
