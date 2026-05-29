<template>
    <ModalForm
        :is-visible="isOpen"
        title="Encriptar Archivo"
        :loading="isSubmitting"
        submit-label="Encriptar Ahora"
        size="md"
        @close="$emit('close')"
        @submit="handleSubmit"
    >
        <template #header-icon>
            <Icon name="lock" :size="20" />
        </template>

        <div class="encryption-warning">
            <Icon name="alertTriangle" :size="20" />
            <div class="warning-text">
                <p><strong>¿Estás seguro de encriptar este archivo?</strong></p>
                <p>Una vez encriptado, se requerirá esta contraseña para descargarlo. No hay forma de recuperar la contraseña si la olvidas.</p>
            </div>
        </div>

        <ModalField label="Contraseña de Encriptación" required span="full">
            <input
                v-model="form.password"
                type="password"
                placeholder="Mínimo 6 caracteres"
                minlength="6"
                maxlength="255"
                required
                autofocus
            />
        </ModalField>

        <ModalField label="Confirmar Contraseña" required span="full">
            <input
                v-model="form.password_confirmation"
                type="password"
                placeholder="Repite la contraseña"
                minlength="6"
                maxlength="255"
                required
            />
        </ModalField>
    </ModalForm>
</template>

<script setup>
import { reactive, ref } from 'vue';
import Icon from '@/components/Icon.vue';
import ModalForm from '@/views/private/admin/components/ModalForm.vue';
import ModalField from '@/views/private/admin/components/ModalField.vue';
import filesApi from '@/services/api/endpoints/files';
import { useAlert } from '@/composables/useAlert';

const props = defineProps({
    isOpen: {
        type: Boolean,
        default: false,
    },
    file: {
        type: Object,
        default: null,
    },
});

const emit = defineEmits(['close', 'success']);
const alert = useAlert();
const isSubmitting = ref(false);

const form = reactive({
    password: '',
    password_confirmation: '',
});

const handleSubmit = async () => {
    if (!props.file) return;

    if (!form.password || form.password.length < 6) {
        alert.toast.error('Error', 'La contraseña debe tener al menos 6 caracteres.');
        return;
    }

    if (form.password !== form.password_confirmation) {
        alert.toast.error('Error', 'Las contraseñas no coinciden.');
        return;
    }

    isSubmitting.value = true;
    try {
        await filesApi.encryptFile(props.file.uuid, { password: form.password });
        alert.toast.success('Éxito', 'Archivo encriptado correctamente.');
        emit('success');
    } catch (error) {
        alert.toast.error('Error', error?.response?.data?.message || 'No se pudo encriptar el archivo.');
    } finally {
        isSubmitting.value = false;
    }
};
</script>

<style lang="scss" scoped>
.encryption-warning {
    display: flex;
    gap: 1rem;
    padding: 1rem;
    background: rgba(var(--warning-rgb), 0.1);
    border-radius: 12px;
    border: 1px solid rgba(var(--warning-rgb), 0.2);
    margin-bottom: 1.5rem;
    color: var(--warning-color);

    .warning-text {
        font-size: 0.9rem;
        line-height: 1.4;
        p { margin: 0; }
    }
}
</style>
