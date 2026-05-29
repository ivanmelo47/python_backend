<template>
    <transition name="modal-fade">
        <div v-if="isOpen" class="modal-overlay" @click="handleOverlayClick">
            <div class="modal-container" @click.stop>
                <div class="modal-header">
                    <h3>{{ title }}</h3>
                    <button class="close-btn" @click="$emit('close')">
                        <Icon name="x" :size="20" />
                    </button>
                </div>

                <div class="modal-body email-preview-body">
                    <div v-if="emailData?.content" class="email-html-wrapper" v-html="emailData.content"></div>
                    <div v-else class="no-content">No hay contenido disponible para este correo.</div>
                </div>
            </div>
        </div>
    </transition>
</template>

<script setup>
import Icon from '@/components/Icon.vue';

const props = defineProps({
    isOpen: {
        type: Boolean,
        default: false
    },
    title: {
        type: String,
        default: 'Vista Previa del Correo'
    },
    emailData: {
        type: Object,
        default: () => ({})
    }
});

const emit = defineEmits(['close']);

const handleOverlayClick = () => {
    emit('close');
};
</script>

<style scoped lang="scss">
.modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    background: rgba(0, 0, 0, 0.5);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 3000;
    backdrop-filter: blur(4px);
}

.modal-container {
    background: var(--bg-secondary, #fff);
    width: 90%;
    max-width: 700px;
    max-height: 90vh;
    border-radius: 16px;
    box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
    display: flex;
    flex-direction: column;
    overflow: hidden;
    animation: modal-slide-in 0.3s ease-out;
}

.modal-header {
    padding: 1.25rem 1.5rem;
    border-bottom: 1px solid var(--border-color, #e5e7eb);
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: var(--bg-secondary, #fff);

    h3 {
        font-size: 1.25rem;
        font-weight: 600;
        color: var(--text-primary, #111827);
        margin: 0;
    }

    .close-btn {
        background: transparent;
        border: none;
        color: var(--text-tertiary, #9ca3af);
        cursor: pointer;
        padding: 0.5rem;
        border-radius: 50%;
        transition: all 0.2s;
        display: flex;
        align-items: center;
        justify-content: center;

        &:hover {
            background: var(--bg-tertiary, #f3f4f6);
            color: var(--error, #ef4444);
        }
    }
}

.modal-body {
    padding: 0;
    overflow-y: auto;
    background: #f4f7f6;
    min-height: 400px;
    display: flex;
    flex-direction: column;
}

.email-html-wrapper {
    width: 100%;
    margin: 0 auto;
    background: #ffffff;

    // We want the injected HTML to be centered if it's a fixed-width table
    :deep(table) {
        margin: 0 auto !important;
    }
}

.no-content {
    padding: 3rem;
    text-align: center;
    color: var(--text-tertiary);
    font-style: italic;
}

/* Transitions */
.modal-fade-enter-active,
.modal-fade-leave-active {
    transition: opacity 0.3s ease;
}

.modal-fade-enter-from,
.modal-fade-leave-to {
    opacity: 0;
}

@keyframes modal-slide-in {
    from {
        opacity: 0;
        transform: translateY(20px) scale(0.95);
    }

    to {
        opacity: 1;
        transform: translateY(0) scale(1);
    }
}
</style>
