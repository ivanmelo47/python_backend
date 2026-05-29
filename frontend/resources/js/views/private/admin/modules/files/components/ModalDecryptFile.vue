<template>
    <ModalForm
        :is-visible="isOpen"
        title="Desencriptar Archivo"
        :loading="isSubmitting"
        submit-label="Desencriptar Ahora"
        size="md"
        @close="$emit('close')"
        @submit="handleSubmit"
    >
        <template #header-icon>
            <Icon name="unlock" :size="20" />
        </template>

        <div class="decryption-warning">
            <Icon name="alertTriangle" :size="20" />
            <div class="warning-text">
                <p><strong>¿Estás seguro de desencriptar este archivo?</strong></p>
                <p>El archivo volverá a ser visible y descargable para cualquier usuario con permisos de lectura, sin necesidad de contraseña.</p>
            </div>
        </div>

        <ModalField label="Contraseña de Desencriptación" required span="full">
            <input
                v-model="password"
                type="password"
                placeholder="Ingresa la contraseña del archivo"
                required
                autofocus
                @keyup.enter="handleSubmit"
            />
        </ModalField>
    </ModalForm>
</template>

<script setup>
import { ref } from 'vue';
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
const password = ref('');

const handleSubmit = async () => {
    if (!props.file) return;

    if (!password.value) {
        alert.toast.error('Error', 'Debes ingresar la contraseña.');
        return;
    }

    isSubmitting.value = true;
    try {
        await filesApi.decryptFile(props.file.uuid, { password: password.value });
        alert.toast.success('Éxito', 'Archivo desencriptado correctamente.');
        emit('success');
        password.value = ''; // Reset password
    } catch (error) {
        if (error?.response?.status === 401) {
             alert.toast.error('Error', 'Contraseña incorrecta.');
        } else {
             alert.toast.error('Error', error?.response?.data?.message || 'No se pudo desencriptar el archivo.');
        }
    } finally {
        isSubmitting.value = false;
    }
};
</script>

<style lang="scss" scoped>
.decryption-warning {
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
