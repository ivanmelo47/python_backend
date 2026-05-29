<template>
    <ModalForm
        :isVisible="isOpen"
        title="Enlace Público Existente"
        :loading="false"
        submitLabel="Cerrar"
        size="md"
        @close="$emit('close')"
        @submit="$emit('close')"
    >
        <template #header-icon>
            <Icon name="link" :size="20" style="color: var(--primary);" />
        </template>

        <div class="view-link-container">
            <div class="link-info-box">
                <Icon name="globe" :size="32" class="globe-icon" />
                <h3>Enlace Público Activo</h3>
                <p>Este elemento ya cuenta con un enlace público generado. Cualquier persona con la URL y la contraseña (si aplica) puede acceder a él.</p>
            </div>

            <ModalField label="URL Pública" span="full">
                <div class="url-copy-box">
                    <input
                        type="text"
                        readonly
                        :value="resolvedPublicUrl"
                        class="form-input"
                    />
                    <button type="button" class="btn-copy" @click="copyLink" title="Copiar al portapapeles">
                        <Icon name="copy" :size="18" />
                    </button>
                </div>
            </ModalField>

            <div class="meta-details">
                <div class="meta-item" v-if="sharedLink?.expires_at">
                    <Icon name="clock" :size="16" />
                    <span><strong>Caduca:</strong> {{ formatDate(sharedLink.expires_at) }}</span>
                </div>
                <div class="meta-item" v-else>
                    <Icon name="infinity" :size="16" />
                    <span><strong>Caducidad:</strong> Permanente</span>
                </div>
            </div>

            <div class="notice-box">
                <Icon name="info" :size="18" />
                <span>Para gestionar, modificar contraseñas o eliminar este enlace, dirígete a la pestaña <strong>"Enlaces Públicos"</strong> en el gestor.</span>
            </div>
        </div>
    </ModalForm>
</template>

<script setup>
import { computed } from 'vue';
import Icon from '@/components/Icon.vue';
import ModalForm from '@/views/private/admin/components/ModalForm.vue';
import ModalField from '@/views/private/admin/components/ModalField.vue';
import { useAlert } from '@/composables/useAlert';
import { buildPublicShareUrl } from '@/services/api/url';

const props = defineProps({
    isOpen: Boolean,
    sharedLink: {
        type: Object,
        default: null
    }
});

const emit = defineEmits(['close']);
const alert = useAlert();

const resolvedPublicUrl = computed(() => {
    const tokenOrUrl = props.sharedLink?.token || props.sharedLink?.public_url || '';
    return buildPublicShareUrl(tokenOrUrl);
});

const formatDate = (dateString) => {
    if (!dateString) return '';
    const date = new Date(dateString);
    return date.toLocaleDateString('es-ES', { day: '2-digit', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit' });
};

const copyLink = () => {
    if (resolvedPublicUrl.value) {
        navigator.clipboard.writeText(resolvedPublicUrl.value);
        alert.toast.success('¡Copiado!', 'El enlace público se ha copiado al portapapeles.');
    }
};
</script>

<style lang="scss" scoped>
.view-link-container {
    padding: 0.5rem 0;
}

.link-info-box {
    text-align: center;
    padding: 1.5rem;
    background: var(--bg-secondary);
    border: 1px dashed var(--border-color);
    border-radius: 12px;
    margin-bottom: 1.5rem;

    .globe-icon {
        color: var(--primary);
        margin-bottom: 0.75rem;
    }

    h3 {
        margin: 0 0 0.5rem 0;
        font-size: 1.2rem;
        color: var(--text-primary);
    }

    p {
        margin: 0;
        font-size: 0.9rem;
        color: var(--text-secondary);
        line-height: 1.5;
    }
}

.url-copy-box {
    display: flex;
    gap: 0.5rem;
    margin-bottom: 1.5rem;

    input {
        flex: 1;
        background: var(--bg-secondary);
        color: var(--text-primary);
        cursor: text;
    }

    .btn-copy {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 42px;
        height: 42px;
        background: var(--primary);
        color: white;
        border: none;
        border-radius: 8px;
        cursor: pointer;
        transition: all 0.2s;

        &:hover {
            filter: brightness(0.9);
            transform: scale(1.05);
        }
    }
}

.form-input {
    width: 100%;
    padding: 0.75rem 1rem;
    border: 1px solid var(--border-color);
    border-radius: 8px;
    background: var(--bg-primary);
    color: var(--text-primary);
    font-size: 0.95rem;

    &:focus {
        outline: none;
        border-color: var(--primary);
    }
}

.meta-details {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
    margin-bottom: 1.5rem;

    .meta-item {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        color: var(--text-secondary);
        font-size: 0.95rem;

        strong {
            color: var(--text-primary);
        }
    }
}

.notice-box {
    display: flex;
    align-items: flex-start;
    gap: 0.75rem;
    padding: 1rem;
    background: rgba(var(--primary-rgb), 0.1);
    border: 1px solid rgba(var(--primary-rgb), 0.2);
    border-radius: 8px;
    color: var(--text-primary);
    font-size: 0.85rem;
    line-height: 1.4;

    :deep(svg) {
        color: var(--primary);
        flex-shrink: 0;
        margin-top: 2px;
    }
}
</style>
