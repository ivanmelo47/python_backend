<template>
    <component
        :is="embedded ? 'div' : ModalForm"
        v-bind="modalProps"
        class="link-form-shell"
        :class="{ 'link-form-embedded': embedded }"
        @close="$emit('close')"
        @submit="handleSubmit"
    >
        <template v-if="!embedded" #header-icon>
            <Icon name="link" :size="20" />
        </template>

        <ModalField label="Nombre del enlace" required span="full">
            <input
                v-model="form.name"
                type="text"
                placeholder="Ej: Carpeta compartida de Drive"
                maxlength="255"
                required
                autofocus
            />
        </ModalField>

        <ModalField label="URL del enlace" required span="full">
            <input
                v-model="form.url"
                type="url"
                placeholder="https://..."
                required
            />
        </ModalField>

        <ModalField label="Icono" span="full">
            <IconSelect
                v-model="form.icon_uuid"
                :selected-icon-data="initialIconData"
            />
        </ModalField>

        <div class="link-info">
            <Icon name="info" :size="14" />
            <span>Este enlace heredará los permisos de la carpeta actual.</span>
        </div>
    </component>
</template>

<script setup>
import { computed, reactive, ref, watch } from 'vue';
import Icon from '@/components/Icon.vue';
import IconSelect from '@/components/IconSelect.vue';
import ModalForm from '@/views/private/admin/components/ModalForm.vue';
import ModalField from '@/views/private/admin/components/ModalField.vue';
import filesApi from '@/services/api/endpoints/files';
import { useAlert } from '@/composables/useAlert';

const props = defineProps({
    isOpen: {
        type: Boolean,
        default: false,
    },
    embedded: {
        type: Boolean,
        default: false,
    },
    folderUuid: {
        type: String,
        default: null,
    },
});

const emit = defineEmits(['close', 'created']);
const alert = useAlert();
const isSubmitting = ref(false);
const initialIconData = ref(null);

const form = reactive({
    name: '',
    url: '',
    icon_uuid: null,
});

const embedded = computed(() => props.embedded);

const modalProps = computed(() => {
    if (embedded.value) return {};

    return {
        isVisible: props.isOpen,
        title: 'Nuevo Enlace',
        loading: isSubmitting.value,
        submitLabel: 'Guardar Enlace',
        size: 'md',
    };
});

watch(() => props.isOpen, (isOpen) => {
    if (!isOpen) return;

    form.name = '';
    form.url = '';
    form.icon_uuid = null;
    initialIconData.value = null;
}, { immediate: true });

const handleSubmit = async () => {
    if (!form.name?.trim()) {
        alert.toast.error('Error', 'Debes ingresar el nombre del enlace.');
        return;
    }

    if (!form.url?.trim()) {
        alert.toast.error('Error', 'Debes ingresar una URL válida.');
        return;
    }

    isSubmitting.value = true;

    try {
        await filesApi.createLink({
            name: form.name.trim(),
            url: form.url.trim(),
            icon_uuid: form.icon_uuid,
            folder_uuid: props.folderUuid,
        });

        alert.toast.success('Éxito', 'Enlace guardado correctamente.');
        emit('created');
    } catch (error) {
        alert.toast.error('Error', error?.response?.data?.message || 'No se pudo guardar el enlace.');
    } finally {
        isSubmitting.value = false;
    }
};

defineExpose({
    submitForm: handleSubmit,
    isSubmitting,
});
</script>

<style lang="scss" scoped>
.link-form-embedded {
    display: grid;
    grid-template-columns: repeat(1, minmax(0, 1fr));
    gap: 1.25rem;
}

.link-info {
    grid-column: 1 / -1;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.75rem 0.9rem;
    border-radius: 10px;
    border: 1px dashed var(--border-color);
    color: var(--text-secondary);
    font-size: 0.82rem;
}
</style>
