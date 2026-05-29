<template>
    <ModalForm
        :isVisible="isVisible"
        :title="'Crear Categoría Rápida'"
        :isLoading="isLoading"
        :errors="errors"
        @submit="handleSubmit"
        @close="$emit('close')"
    >
        <ModalField
            key="nombre"
            label="Nombre de la Categoría"
            type="text"
            placeholder="Ej. Supermercado, Transporte"
            v-model="form.nombre"
            :errors="errors.nombre"
            required
        />

        <ModalField
            key="icon"
            label="Icono (Opcional)"
            type="icon-select"
            v-model="form.icon"
        />

        <ModalField
            key="color"
            label="Color"
            type="color"
            v-model="form.color"
        />
    </ModalForm>
</template>

<script setup>
import { ref, reactive } from 'vue';
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
    movementType: {
        type: String,
        default: 'gasto' // 'ingreso' or 'gasto'
    }
});

const alert = useAlert();
const isLoading = ref(false);
const errors = ref({});

const form = reactive({
    nombre: '',
    tipo: props.movementType,
    icon: null,
    color: props.movementType === 'ingreso' ? '#10b981' : '#3b82f6',
    status: true
});

const handleSubmit = async () => {
    isLoading.value = true;
    errors.value = {};

    try {
        const payload = { ...form, tipo: props.movementType };
        await api.finanzas.storeCategoria(payload);
        alert.toast.success('¡Listo!', 'Categoría añadida exitosamente.');
        emit('saved');
        emit('close');
    } catch (error) {
        if (error.response?.data?.errors) {
            errors.value = error.response.data.errors;
        } else {
            alert.toast.error('Error', 'No se pudo crear la categoría.');
        }
    } finally {
        isLoading.value = false;
    }
};

const openForType = (type) => {
    form.nombre = '';
    form.tipo = type;
    form.icon = null;
    form.color = type === 'ingreso' ? '#10b981' : '#3b82f6';
    errors.value = {};
};

defineExpose({
    openForType
});
</script>
