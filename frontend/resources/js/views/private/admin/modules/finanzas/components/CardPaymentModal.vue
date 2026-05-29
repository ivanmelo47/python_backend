<template>
    <ModalForm
        :is-visible="isVisible"
        title="Pagar Tarjeta"
        :loading="isSaving"
        :fields="fields"
        :model-value="form"
        :errors="errors"
        @submit="$emit('submit')"
        @close="$emit('close')"
    >
        <template #field-monto="{ modelValue }">
            <div class="currency-input-container">
                <span class="symbol">$</span>
                <input type="number" v-model="modelValue.monto" placeholder="0.00" step="0.01">
            </div>
        </template>
    </ModalForm>
</template>

<script setup>
import ModalForm from '@/views/private/admin/components/ModalForm.vue';

defineProps({
    isVisible: {
        type: Boolean,
        default: false
    },
    isSaving: {
        type: Boolean,
        default: false
    },
    fields: {
        type: Array,
        default: () => []
    },
    form: {
        type: Object,
        required: true
    },
    errors: {
        type: Object,
        default: () => ({})
    }
});

defineEmits(['close', 'submit']);
</script>
