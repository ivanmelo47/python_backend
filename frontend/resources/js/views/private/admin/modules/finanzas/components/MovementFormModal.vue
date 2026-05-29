<template>
    <ModalForm
        :isVisible="isVisible"
        :title="movementModalTitle"
        :isLoading="isLoading"
        :errors="errors"
        @submit="handleSubmit"
        @close="$emit('close')"
    >
        <!-- Date Field -->
        <ModalField
            key="fecha"
            label="Fecha"
            type="date"
            v-model="form.fecha"
            :errors="errors.fecha"
            required
        />

        <!-- Account Selection -->
        <ModalField
            key="cuenta_uuid"
            label="Cuenta de Ahorro"
            type="select"
            v-model="form.cuenta_uuid"
            :options="accountOptions"
            :errors="errors.cuenta_uuid"
            required
        />

        <!-- Display Available Balance -->
        <div v-if="form.cuenta_uuid && form.tipo === 'gasto'" class="balance-info">
            <small>💰 Saldo Disponible: <strong>{{ formatCurrency(selectedAccountBalance) }}</strong></small>
        </div>

        <!-- Description -->
        <ModalField
            key="descripcion"
            label="Concepto"
            type="text"
            placeholder="Ej. Compra Súper, Pago Nómina"
            v-model="form.descripcion"
            :errors="errors.descripcion"
            required
        />

        <!-- Amount -->
        <ModalField
            key="monto"
            label="Monto ($)"
            type="number"
            placeholder="0.00"
            v-model="form.monto"
            :errors="errors.monto"
            required
            currency
        />

        <!-- Source/Destination -->
        <ModalField
            key="fuente_fondos_uuid"
            :label="form.tipo === 'ingreso' ? '¿De dónde viene el dinero?' : '¿A dónde va el dinero?'"
            type="select"
            v-model="form.fuente_fondos_uuid"
            :options="sourcDestinationOptions"
            :errors="errors.fuente_fondos_uuid"
            required
        />

        <!-- Category -->
        <div class="category-field-wrapper">
            <ModalField
                key="categoria_uuid"
                label="Categoría"
                type="select"
                v-model="form.categoria_uuid"
                :options="categoryOptions"
                :errors="errors.categoria_uuid"
            />
            <button
                v-if="showQuickCategoryBtn"
                type="button"
                class="btn-quick-category"
                @click="$emit('open-quick-category')"
                title="Crear categoría rápidamente"
            >
                ➕ Crear
            </button>
        </div>

        <!-- Sections (if available) -->
        <ModalField
            v-if="sectionsOptions.length > 0"
            key="seccion_uuid"
            label="Sección / Apartado (Opcional)"
            type="select"
            v-model="form.seccion_uuid"
            :options="sectionsOptions"
            :errors="errors.seccion_uuid"
        />

        <!-- Notes -->
        <ModalField
            key="notas"
            label="Notas"
            type="textarea"
            placeholder="Notas adicionales..."
            v-model="form.notas"
            :errors="errors.notas"
        />

        <!-- File Upload -->
        <div class="files-upload-section">
            <label class="upload-label">📎 Comprobantes (Opcional)</label>
            <div
                class="drop-zone"
                :class="{ 'is-dragging': isDraggingFiles }"
                @dragover.prevent="isDraggingFiles = true"
                @dragleave="isDraggingFiles = false"
                @drop.prevent="handleFilesDrop"
            >
                <input
                    type="file"
                    multiple
                    hidden
                    ref="fileInput"
                    @change="handleFilesSelect"
                />
                <div class="drop-content" @click="$refs.fileInput?.click()">
                    <Icon name="upload" :size="32" />
                    <p>Arrastra archivos aquí o <strong>haz clic</strong></p>
                    <small>Máx. 10MB por archivo (imágenes, PDF)</small>
                </div>
            </div>

            <!-- File List -->
            <div v-if="selectedFiles.length > 0" class="file-list">
                <div v-for="(file, idx) in selectedFiles" :key="idx" class="file-item">
                    <Icon :name="getFileIcon(file.name)" :size="20" />
                    <div class="file-info">
                        <span class="file-name">{{ file.name }}</span>
                        <span class="file-size">{{ formatFileSize(file.size) }}</span>
                    </div>
                    <button
                        type="button"
                        class="btn-remove"
                        @click="selectedFiles.splice(idx, 1)"
                        title="Eliminar archivo"
                    >
                        ✕
                    </button>
                </div>
            </div>
        </div>
    </ModalForm>
</template>

<script setup>
import { ref, reactive, computed, watch } from 'vue';
import ModalForm from '@/views/private/admin/components/ModalForm.vue';
import ModalField from '@/views/private/admin/components/ModalField.vue';
import Icon from '@/components/Icon.vue';
import { api } from '@/services/api';
import { useAlert } from '@/composables/useAlert';

const emit = defineEmits(['close', 'saved', 'open-quick-category']);

const props = defineProps({
    isVisible: {
        type: Boolean,
        default: false
    },
    accounts: {
        type: Array,
        default: () => []
    },
    categories: {
        type: Array,
        default: () => []
    }
});

const alert = useAlert();
const isLoading = ref(false);
const errors = ref({});
const isDraggingFiles = ref(false);
const selectedFiles = ref([]);
const fileInput = ref(null);

const form = reactive({
    cuenta_uuid: '',
    tipo: 'ingreso',
    monto: '',
    descripcion: '',
    fecha: new Date().toISOString().split('T')[0],
    categoria_uuid: '',
    notas: '',
    fuente_fondos_uuid: 'externo',
    seccion_uuid: ''
});

const selectedAccountBalance = computed(() => {
    if (!form.cuenta_uuid) return 0;
    const uuid = form.cuenta_uuid.replace('cuenta_', '');
    const account = props.accounts.find(a => a.uuid === uuid);
    return account ? parseFloat(account.saldo_actual) : 0;
});

const movementModalTitle = computed(() => {
    return form.tipo === 'ingreso' ? 'Registrar Ingreso' : 'Registrar Gasto';
});

const accountOptions = computed(() => {
    return props.accounts
        .filter(a => a.status === true || a.status === 1 || a.status === 'activa')
        .map(a => ({
            id: `cuenta_${a.uuid}`,
            name: `🏦 ${a.nombre} (${a.banco || 'N/A'})`
        }));
});

const sourcDestinationOptions = computed(() => {
    return [
        { id: 'externo', name: '💸 Externo (Efectivo / Terceros)' },
        ...props.accounts
            .filter(a => a.status === true || a.status === 1 || a.status === 'activa')
            .map(a => ({
                id: `cuenta_${a.uuid}`,
                name: `🏦 ${a.nombre} (${a.banco})`
            }))
    ];
});

const categoryOptions = computed(() => {
    return props.categories
        .filter(c => c.tipo === form.tipo || c.tipo === 'mixto')
        .map(c => ({ id: c.uuid, name: c.nombre }));
});

const showQuickCategoryBtn = computed(() => {
    return categoryOptions.value.length > 0;
});

const sectionsOptions = computed(() => {
    if (!form.cuenta_uuid || !selectedAccountBalance.value) return [];
    
    const uuid = form.cuenta_uuid.replace('cuenta_', '');
    const account = props.accounts.find(a => a.uuid === uuid);
    
    if (!account || !account.secciones) return [];
    
    return [
        { id: '', name: '💰 Saldo Principal (Sin sección)' },
        ...account.secciones.map(s => ({
            id: s.uuid,
            name: `${s.nombre} (${formatCurrency(s.saldo_actual)})`
        }))
    ];
});

const formatCurrency = (val) => {
    return new Intl.NumberFormat('es-MX', { style: 'currency', currency: 'MXN' }).format(val);
};

const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};

const getFileIcon = (filename) => {
    const ext = (filename || '').split('.').pop().toLowerCase();
    if (['jpg', 'jpeg', 'png', 'gif', 'webp'].includes(ext)) return 'image';
    if (ext === 'pdf') return 'filePdf';
    return 'file';
};

const handleFilesSelect = (e) => {
    const files = Array.from(e.target.files);
    addFiles(files);
};

const handleFilesDrop = (e) => {
    isDraggingFiles.value = false;
    const files = Array.from(e.dataTransfer.files);
    addFiles(files);
};

const addFiles = (files) => {
    const validFiles = files.filter(f => {
        const isTooLarge = f.size > 10 * 1024 * 1024;
        if (isTooLarge) alert.toast.warning('Archivo muy grande', `${f.name} excede los 10MB`);
        return !isTooLarge;
    });
    selectedFiles.value = [...selectedFiles.value, ...validFiles];
};

const handleSubmit = async () => {
    isLoading.value = true;
    errors.value = {};

    try {
        // Validate insufficient funds
        if (form.tipo === 'gasto' && form.cuenta_uuid) {
            const monto = parseFloat(form.monto);
            if (monto > selectedAccountBalance.value) {
                errors.value = {
                    monto: [`Saldo insuficiente. Disponible: ${formatCurrency(selectedAccountBalance.value)}`]
                };
                isLoading.value = false;
                return;
            }
        }

        const payload = { ...form };

        if (payload.cuenta_uuid.startsWith('cuenta_')) {
            payload.cuenta_uuid = payload.cuenta_uuid.replace('cuenta_', '');
        }

        if (payload.fuente_fondos_uuid?.startsWith('cuenta_')) {
            payload.cuenta_cargo_uuid = payload.fuente_fondos_uuid.replace('cuenta_', '');
        }
        delete payload.fuente_fondos_uuid;

        const response = await api.finanzas.storeMovimiento(payload);
        const movementUuid = response.data.uuid;

        // Upload files if any
        if (selectedFiles.value.length > 0) {
            alert.showLoading('Subiendo comprobantes...', `Enviando ${selectedFiles.value.length} archivo(s)`);
            for (const file of selectedFiles.value) {
                try {
                    await api.finanzas.uploadAdjunto(movementUuid, file);
                } catch (uploadErr) {
                    console.error("Error uploading file", file.name, uploadErr);
                    alert.toast.error('Error de subida', `No se pudo subir: ${file.name}`);
                }
            }
            alert.closeLoading();
        }

        alert.toast.success('¡Éxito!', `Movimiento registrado${selectedFiles.value.length > 0 ? ' con adjuntos' : ''}.`);
        emit('saved');
        emit('close');
    } catch (error) {
        if (error.response?.data?.errors) {
            errors.value = error.response.data.errors;
        } else {
            alert.toast.error('Error', error.message || 'Ocurrió un error inesperado.');
        }
    } finally {
        isLoading.value = false;
    }
};

const openForType = (type) => {
    form.tipo = type;
    form.cuenta_uuid = props.accounts[0] ? `cuenta_${props.accounts[0].uuid}` : '';
    form.monto = '';
    form.descripcion = '';
    form.fecha = new Date().toISOString().split('T')[0];
    form.categoria_uuid = '';
    form.notas = '';
    form.fuente_fondos_uuid = 'externo';
    form.seccion_uuid = '';
    selectedFiles.value = [];
    errors.value = {};
};

defineExpose({
    openForType
});
</script>

<style lang="scss" scoped>
.balance-info {
    background: rgba(16, 185, 129, 0.05);
    border: 1px solid rgba(16, 185, 129, 0.2);
    border-radius: 8px;
    padding: 0.75rem 1rem;
    margin: 0.5rem 0 1rem;
    color: #10b981;
    font-size: 0.9rem;
}

.category-field-wrapper {
    display: flex;
    gap: 0.5rem;
    align-items: flex-end;

    :deep(.modal-field) {
        flex: 1;
    }
}

.btn-quick-category {
    background: rgba(var(--primary-rgb), 0.1);
    border: 1px solid rgba(var(--primary-rgb), 0.2);
    color: var(--primary);
    padding: 0.625rem 1rem;
    border-radius: 8px;
    cursor: pointer;
    font-size: 0.85rem;
    font-weight: 600;
    transition: all 0.2s;

    &:hover {
        background: var(--primary);
        color: white;
    }
}

.files-upload-section {
    margin-top: 1.5rem;
}

.upload-label {
    display: block;
    font-size: 0.9rem;
    font-weight: 600;
    color: var(--text-primary);
    margin-bottom: 0.75rem;
}

.drop-zone {
    border: 2px dashed rgba(var(--primary-rgb), 0.2);
    border-radius: 12px;
    padding: 2rem;
    text-align: center;
    cursor: pointer;
    transition: all 0.3s;
    background: rgba(var(--primary-rgb), 0.02);

    &:hover {
        border-color: var(--primary);
        background: rgba(var(--primary-rgb), 0.04);
    }

    &.is-dragging {
        border-color: #10b981;
        background: rgba(16, 185, 129, 0.1);
    }
}

.drop-content {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.75rem;
    pointer-events: none;

    p {
        margin: 0;
        color: var(--text-primary);
        font-weight: 600;
    }

    small {
        color: var(--text-tertiary);
    }
}

.file-list {
    margin-top: 1rem;
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
}

.file-item {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 0.75rem;
    background: rgba(255, 255, 255, 0.04);
    border: 1px solid rgba(255, 255, 255, 0.06);
    border-radius: 8px;
    transition: all 0.2s;

    &:hover {
        background: rgba(255, 255, 255, 0.08);
    }
}

.file-info {
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
    min-width: 0;
}

.file-name {
    font-weight: 600;
    color: var(--text-primary);
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.file-size {
    font-size: 0.75rem;
    color: var(--text-tertiary);
}

.btn-remove {
    background: rgba(239, 68, 68, 0.1);
    border: 1px solid rgba(239, 68, 68, 0.2);
    color: #ef4444;
    width: 32px;
    height: 32px;
    border-radius: 6px;
    cursor: pointer;
    transition: all 0.2s;
    flex-shrink: 0;

    &:hover {
        background: #ef4444;
        color: white;
    }
}
</style>
