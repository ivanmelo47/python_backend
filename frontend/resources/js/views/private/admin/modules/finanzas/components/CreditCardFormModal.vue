<template>
    <ModalForm
        :is-visible="isVisible"
        :title="isEditing ? 'Editar Tarjeta' : 'Nueva Tarjeta'"
        :loading="isSaving"
        :fields="fields"
        :model-value="form"
        :errors="errors"
        @submit="$emit('submit')"
        @close="$emit('close')"
    />
</template>

<script setup>
import ModalForm from '@/views/private/admin/components/ModalForm.vue';

defineProps({
    isVisible: {
        type: Boolean,
        default: false
    },
    isEditing: {
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
