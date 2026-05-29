<template>
    <ModalForm
        :isVisible="isVisible"
        :title="isEditMode ? 'Editar Cuenta de Ahorro' : 'Nueva Cuenta de Ahorro'"
        :isLoading="isLoading"
        :errors="errors"
        @submit="handleSubmit"
        @close="$emit('close')"
    >
        <ModalField
            key="nombre"
            label="Nombre de la Cuenta"
            type="text"
            placeholder="Ej. Ahorro para Viajes"
            v-model="form.nombre"
            :errors="errors.nombre"
            required
        />

        <ModalField
            key="banco"
            label="Institución Financiera"
            type="text"
            placeholder="Ej. Banco ABC, Caja de Ahorros"
            v-model="form.banco"
            :errors="errors.banco"
            required
        />

        <ModalField
            key="icon"
            label="Icono (Selecciona o personaliza)"
            type="icon-select"
            v-model="form.icon"
            :databaseIcon="form.icon_data"
            :errors="errors.icon"
        />

        <ModalField
            key="tipo"
            label="Tipo de Cuenta"
            type="select"
            v-model="form.tipo"
            :options="[
                { id: 'debito', name: '💳 Débito / Corriente' },
                { id: 'ahorro', name: '🏦 Ahorro' },
                { id: 'inversion', name: '📈 Inversión' },
                { id: 'efectivo', name: '💵 Efectivo' }
            ]"
            :errors="errors.tipo"
            required
        />

        <ModalField
            key="moneda"
            label="Moneda"
            type="select"
            v-model="form.moneda"
            :options="[
                { id: 'MXN', name: '🇲🇽 MXN - Peso Mexicano' },
                { id: 'USD', name: '🇺🇸 USD - Dólar Estadounidense' },
                { id: 'EUR', name: '🇪🇺 EUR - Euro' }
            ]"
            :errors="errors.moneda"
            required
        />

        <ModalField
            key="saldo_apertura"
            label="Saldo Inicial ($)"
            type="number"
            placeholder="0.00"
            v-model="form.saldo_apertura"
            :errors="errors.saldo_apertura"
            required
            currency
        />

        <!-- Income Generation Section -->
        <div class="form-section-divider">
            <h4>⚡ Rendimiento (Opcional)</h4>
        </div>

        <ModalField
            key="genera_rendimiento"
            label="¿Genera rendimiento/interés?"
            type="checkbox"
            v-model="form.genera_rendimiento"
        />

        <template v-if="form.genera_rendimiento">
            <ModalField
                key="tasa_rendimiento_anual"
                label="Tasa de Rendimiento Anual (%)"
                type="number"
                placeholder="0.00"
                v-model="form.tasa_rendimiento_anual"
                :errors="errors.tasa_rendimiento_anual"
                step="0.01"
                min="0"
            />

            <ModalField
                key="hora_rendimiento"
                label="Hora de Cálculo de Rendimiento"
                type="time"
                v-model="form.hora_rendimiento"
                :errors="errors.hora_rendimiento"
            />
        </template>

        <!-- Notes -->
        <ModalField
            key="notas"
            label="Notas"
            type="textarea"
            placeholder="Ej. Cuenta empresarial, requiere firma conjunta..."
            v-model="form.notas"
            :errors="errors.notas"
        />
    </ModalForm>
</template>

<script setup>
import { ref, reactive, computed, watch } from 'vue';
import ModalForm from '@/views/private/admin/components/ModalForm.vue';
import ModalField from '@/views/private/admin/components/ModalField.vue';
import { api } from '@/services/api';
import { useAlert } from '@/composables/useAlert';

const emit = defineEmits(['close', 'saved']);

const props = defineProps({
    isVisible: {
        type: Boolean,
        default: false
    },
    editingAccount: {
        type: Object,
        default: null
    }
});

// Sync form with props when modal opens
watch(() => props.isVisible, (visible) => {
    if (visible) {
        if (props.editingAccount) {
            openForEdit(props.editingAccount);
        } else {
            openForCreate();
        }
    }
});

const alert = useAlert();
const isLoading = ref(false);
const errors = ref({});

const form = reactive({
    nombre: '',
    banco: '',
    icon: null,
    icon_data: null,
    tipo: 'debito',
    moneda: 'MXN',
    saldo_apertura: 0,
    saldo_actual: 0,
    genera_rendimiento: false,
    tasa_rendimiento_anual: 0,
    hora_rendimiento: '00:00',
    notas: '',
    status: 'activa'
});

const isEditMode = computed(() => !!props.editingAccount);

const handleSubmit = async () => {
    isLoading.value = true;
    errors.value = {};

    try {
        const payload = { ...form };

        if (isEditMode.value) {
            await api.finanzas.updateCuentaAhorro(props.editingAccount.uuid, payload);
            alert.toast.success('¡Actualizado!', 'La cuenta ha sido actualizada.');
        } else {
            await api.finanzas.storeCuentaAhorro(payload);
            alert.toast.success('¡Creado!', 'Nueva cuenta añadida exitosamente.');
        }

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

const openForCreate = () => {
    Object.assign(form, {
        nombre: '',
        banco: '',
        icon: null,
        icon_data: null,
        tipo: 'debito',
        moneda: 'MXN',
        saldo_apertura: 0,
        genera_rendimiento: false,
        tasa_rendimiento_anual: 0,
        hora_rendimiento: '00:00',
        notas: ''
    });
    errors.value = {};
};

const openForEdit = (account) => {
    Object.assign(form, {
        nombre: account.nombre,
        banco: account.banco,
        icon: account.icon,
        icon_data: account.icon_data,
        tipo: account.tipo,
        moneda: account.moneda,
        saldo_apertura: account.saldo_apertura,
        saldo_actual: account.saldo_actual,
        genera_rendimiento: account.genera_rendimiento,
        tasa_rendimiento_anual: account.tasa_rendimiento_anual,
        hora_rendimiento: account.hora_rendimiento,
        notas: account.notas,
        status: account.status
    });
    errors.value = {};
};

defineExpose({
    openForCreate,
    openForEdit
});
</script>

<style lang="scss" scoped>
.form-section-divider {
    margin: 1.5rem 0 1rem;
    padding-top: 1rem;
    border-top: 1px solid var(--border-color);

    h4 {
        margin: 0;
        font-size: 0.9rem;
        color: var(--text-tertiary);
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
}
</style>
