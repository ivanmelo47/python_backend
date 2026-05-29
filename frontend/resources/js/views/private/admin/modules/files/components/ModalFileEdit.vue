<template>
    <ModalForm
        :is-visible="isOpen"
        title="Editar Archivo"
        :loading="isSubmitting"
        submit-label="Guardar Cambios"
        size="md"
        @close="$emit('close')"
        @submit="handleSubmit"
    >
        <template #header-icon>
            <Icon name="pencil" :size="20" />
        </template>

        <ModalField :label="isLink ? 'Nombre del enlace' : 'Nombre del archivo'" required span="full">
            <input
                v-model="form.name"
                type="text"
                :placeholder="isLink ? 'Ej: Enlace de trabajo' : 'Ej: reporte-final'"
                maxlength="255"
                required
                autofocus
            />
        </ModalField>

        <div v-if="!isLink" class="file-hint">
            <Icon name="info" :size="14" />
            <span>La extensión <strong>.{{ file?.extension }}</strong> se conserva automáticamente.</span>
        </div>
    </ModalForm>
</template>

<script setup>
import { computed, reactive, ref, watch } from 'vue';
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
    files: {
        type: Array,
        default: () => [],
    },
});

const emit = defineEmits(['close', 'updated']);
const alert = useAlert();
const isSubmitting = ref(false);

const form = reactive({
    name: '',
});

const isLink = computed(() => !!props.file?.is_link);

const normalize = (value) => String(value || '').trim().toLowerCase();

const extractEditableName = (file) => {
    if (!file) return '';

    if (file.is_link) return file.name || '';

    const originalName = String(file.original_name || '');
    const extension = String(file.extension || '').toLowerCase();

    if (!extension || !originalName.toLowerCase().endsWith(`.${extension}`)) {
        return originalName;
    }

    return originalName.slice(0, -(extension.length + 1));
};

watch(() => props.isOpen, (isOpen) => {
    if (!isOpen) return;
    form.name = extractEditableName(props.file);
}, { immediate: true });

const hasDuplicateName = (candidateName) => {
    if (!props.file) return false;

    const normalizedCandidate = normalize(candidateName);

    return props.files.some((item) => {
        if (!item || item.uuid === props.file.uuid) return false;
        if (!!item.is_link !== !!props.file.is_link) return false;

        const itemName = item.is_link
            ? item.name
            : String(item.original_name || '').replace(/\.[^.]+$/, '');

        return normalize(itemName) === normalizedCandidate;
    });
};

const handleSubmit = async () => {
    if (!props.file) return;

    const candidate = String(form.name || '').trim();
    if (!candidate) {
        alert.toast.error('Error', 'Debes ingresar un nombre válido.');
        return;
    }

    if (hasDuplicateName(candidate)) {
        await alert.fire({
            title: 'Nombre duplicado',
            text: 'Ya existe un archivo con ese nombre en esta carpeta. Usa otro nombre para continuar.',
            type: 'warning',
            confirmText: 'Entendido',
        });
        return;
    }

    isSubmitting.value = true;
    try {
        await filesApi.updateFile(props.file.uuid, { name: candidate });
        alert.toast.success('Éxito', 'Archivo actualizado correctamente.');
        emit('updated');
    } catch (error) {
        if (error?.response?.status === 409) {
            await alert.fire({
                title: 'Nombre duplicado',
                text: error?.response?.data?.message || 'Ya existe un archivo con ese nombre en esta carpeta.',
                type: 'warning',
                confirmText: 'Entendido',
            });
        } else {
            alert.toast.error('Error', error?.response?.data?.message || 'No se pudo actualizar el archivo.');
        }
    } finally {
        isSubmitting.value = false;
    }
};
</script>

<style lang="scss" scoped>
.file-hint {
    display: flex;
    align-items: center;
    gap: 0.45rem;
    padding: 0.75rem 0.9rem;
    border-radius: 10px;
    border: 1px dashed var(--border-color);
    color: var(--text-secondary);
    font-size: 0.82rem;
}
</style>
