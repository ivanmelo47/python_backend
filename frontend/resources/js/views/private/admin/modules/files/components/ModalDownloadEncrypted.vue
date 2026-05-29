<template>
    <ModalForm
        :is-visible="isOpen"
        title="Descargar Archivo Protegido"
        :loading="isSubmitting"
        submit-label="Descargar"
        size="md"
        @close="$emit('close')"
        @submit="handleSubmit"
    >
        <template #header-icon>
            <Icon name="download" :size="20" />
        </template>

        <div class="download-info">
            <Icon name="info" :size="20" />
            <div class="info-text">
                <p><strong>Descarga Segura</strong></p>
                <p>El archivo se desencriptará temporalmente para su descarga, pero <strong>permanecerá encriptado y seguro</strong> en el servidor.</p>
            </div>
        </div>

        <ModalField label="Contraseña del Archivo" required span="full">
            <input
                v-model="password"
                type="password"
                placeholder="Ingresa la contraseña para descargar"
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
        const response = await filesApi.downloadEncryptedFile(props.file.uuid, password.value);
        
        // Handle Blob download
        const blob = new Blob([response.data], {
            type: response.headers?.['content-type'] || props.file.mime_type || 'application/octet-stream'
        });

        const link = document.createElement('a');
        const objectUrl = URL.createObjectURL(blob);
        link.href = objectUrl;
        
        // Use original name but remove .enc extension if present for the download
        let downloadName = props.file.original_name || props.file.name || 'archivo';
        if (downloadName.endsWith('.enc')) {
            downloadName = downloadName.substring(0, downloadName.length - 4);
        }
        
        link.download = downloadName;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(objectUrl);

        alert.toast.success('Éxito', 'Descarga iniciada.');
        emit('success');
        password.value = ''; // Reset password
        emit('close');
    } catch (error) {
        if (error?.response?.status === 401) {
             alert.toast.error('Error', 'Contraseña incorrecta.');
        } else {
             alert.toast.error('Error', error?.response?.data?.message || 'No se pudo descargar el archivo.');
        }
    } finally {
        isSubmitting.value = false;
    }
};
</script>

<style lang="scss" scoped>
.download-info {
    display: flex;
    gap: 1rem;
    padding: 1rem;
    // Blue/Info color scheme
    background: rgba(59, 130, 246, 0.1); 
    border-radius: 12px;
    border: 1px solid rgba(59, 130, 246, 0.2);
    margin-bottom: 1.5rem;
    color: #3b82f6;

    .info-text {
        font-size: 0.9rem;
        line-height: 1.4;
        p { margin: 0; }
    }
}
</style>
