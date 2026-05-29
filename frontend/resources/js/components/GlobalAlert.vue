<template>
    <Teleport to="body">
        <div class="global-alerts">
        <!-- 1. Toast Container (Top Right) -->
        <div class="toast-container">
            <TransitionGroup name="toast">
                <div
                    v-for="toast in toasts"
                    :key="toast.id"
                    class="toast-item"
                    :class="toast.type"
                    @click="removeToast(toast.id)"
                >
                    <div class="icon-wrapper">
                        <Icon :name="getIconName(toast.type)" :size="20" />
                    </div>
                    <div class="toast-content">
                        <h4>{{ toast.title }}</h4>
                        <p v-if="toast.text">{{ toast.text }}</p>
                    </div>
                    <button class="toast-close">×</button>
                </div>
            </TransitionGroup>
        </div>

        <!-- 2. Modal Overlay (Centered) -->
        <Transition name="modal">
            <div v-if="modal.show" class="alert-overlay" @click.self="modal.onCancel">
                <div class="alert-modal" role="dialog" aria-modal="true">
                    <!-- Icon -->
                    <div class="modal-icon" :class="modal.type">
                        <template v-if="modal.type === 'loading'">
                            <div class="alert-spinner"></div>
                            <div class="loading-pulse">
                                <Icon name="clock" class="loading-inner-icon" />
                            </div>
                        </template>
                        <Icon v-else :name="getIconName(modal.type)" :size="40" />
                    </div>

                    <!-- Content -->
                    <h2>{{ modal.title }}</h2>
                    <p>{{ modal.text }}</p>

                    <!-- Actions -->
                    <div class="modal-actions" v-if="modal.confirmText || modal.cancelText || modal.neutralText">
                        <button
                            v-if="modal.showCancel && modal.cancelText"
                            class="btn-cancel"
                            @click="modal.onCancel"
                        >
                            {{ modal.cancelText }}
                        </button>
                        <button
                            v-if="modal.showNeutral && modal.neutralText"
                            class="btn-neutral"
                            @click="modal.onNeutral"
                        >
                            {{ modal.neutralText }}
                        </button>
                        <button
                            v-if="modal.confirmText"
                            class="btn-confirm"
                            @click="modal.onConfirm"
                        >
                            {{ modal.confirmText }}
                        </button>
                    </div>
                </div>
            </div>
        </Transition>
        </div>
    </Teleport>
</template>

<script setup>
import { useAlert } from '../composables/useAlert';
import Icon from './Icon.vue';

const { toasts, modal, removeToast } = useAlert();

const getIconName = (type) => {
    switch (type) {
        case 'success': return 'alertSuccess';
        case 'error': return 'alertError';
        case 'warning': return 'alertWarning';
        case 'info': return 'alertInfo';
        case 'loading': return 'clock'; // Temporary placeholder, or we can use a spinner
        default: return 'alertInfo';
    }
};
</script>

<style scoped>
/* 1. Toast Container (Top Right) */
.toast-container {
    position: fixed;
    top: 24px;
    right: 24px;
    z-index: 2100000;
    display: flex;
    flex-direction: column;
    gap: 12px;
    pointer-events: none;
    width: 350px;
    max-width: calc(100vw - 40px);
}

.toast-item {
    pointer-events: auto;
    background: rgba(var(--bg-secondary-rgb), 0.9);
    backdrop-filter: blur(16px);
    border: 1px solid var(--border-color);
    border-radius: 18px;
    padding: 16px;
    display: flex;
    align-items: center;
    gap: 14px;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
    cursor: pointer;
    transition: all 0.3s ease;
    border-left: 4px solid var(--primary);
}

.toast-item.success { border-left-color: #10b981; }
.toast-item.error { border-left-color: #ef4444; }
.toast-item.warning { border-left-color: #f59e0b; }
.toast-item.info { border-left-color: #3b82f6; }

.icon-wrapper {
    width: 36px;
    height: 36px;
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: rgba(var(--primary-rgb), 0.1);
    color: var(--primary);
}

.success .icon-wrapper { background: rgba(16, 185, 129, 0.1); color: #10b981; }
.error .icon-wrapper { background: rgba(239, 68, 68, 0.1); color: #ef4444; }

.toast-content h4 {
    margin: 0;
    font-size: 0.95rem;
    font-weight: 700;
    color: var(--text-primary);
}

.toast-content p {
    margin: 4px 0 0;
    font-size: 0.85rem;
    color: var(--text-secondary);
}

.toast-close {
    margin-left: auto;
    background: transparent;
    border: none;
    color: var(--text-tertiary);
    font-size: 1.2rem;
    cursor: pointer;
}

/* Modal Structure & Glassmorphism */
.alert-overlay {
    position: fixed;
    inset: 0;
    z-index: 2000000;
    background: rgba(var(--bg-primary-rgb), 0.7);
    backdrop-filter: blur(20px);
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 20px;
}

.alert-modal {
    background: rgba(var(--bg-secondary-rgb), 0.85);
    border: 1px solid var(--border-color);
    backdrop-filter: blur(40px);
    border-radius: 32px;
    padding: 40px;
    width: 100%;
    max-width: 420px;
    text-align: center;
    box-shadow: 0 40px 100px var(--shadow-color);
    color: var(--text-primary);
}

.alert-modal h2 {
    font-size: 1.6rem;
    font-weight: 800;
    margin-bottom: 12px;
    letter-spacing: -0.02em;
}

.alert-modal p {
    font-size: 1rem;
    color: var(--text-secondary);
    line-height: 1.6;
    margin-bottom: 30px;
}

/* Premium Loading State */
.modal-icon.loading {
    position: relative;
    width: 100px;
    height: 100px;
    margin: 0 auto 30px;
    display: flex;
    align-items: center;
    justify-content: center;
}

.alert-spinner {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    border: 3px solid transparent;
    border-top-color: var(--primary, #5ce8bf);
    border-radius: 50%;
    animation: spin 1s cubic-bezier(0.4, 0, 0.2, 1) infinite;
}



.loading-pulse {
    width: 60px;
    height: 60px;
    background: radial-gradient(circle, var(--primary, #5ce8bf) 0%, transparent 70%);
    border-radius: 50%;
    opacity: 0.4;
    animation: pulse 1.5s ease-out infinite;
    display: flex;
    align-items: center;
    justify-content: center;
}

.loading-inner-icon {
    font-size: 24px;
    color: var(--primary);
    z-index: 2;
    animation: float 3s ease-in-out infinite;
}

@keyframes spin {
    to { transform: rotate(360deg); }
}

@keyframes pulse {
    0% { transform: scale(0.8); opacity: 0.6; }
    100% { transform: scale(1.6); opacity: 0; }
}

@keyframes float {
    0%, 100% { transform: translateY(0); }
    50% { transform: translateY(-5px); }
}

/* Actions Styles */
.modal-actions {
    display: flex;
    gap: 12px;
    justify-content: center;
}

.btn-confirm, .btn-cancel, .btn-neutral {
    padding: 12px 24px;
    border-radius: 14px;
    font-weight: 700;
    font-size: 0.95rem;
    cursor: pointer;
    transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
}

.btn-confirm {
    background: var(--primary, #5ce8bf);
    color: #08090c;
    border: none;
    box-shadow: 0 10px 20px rgba(92, 232, 191, 0.2);
}

.btn-confirm:hover {
    transform: translateY(-2px);
    box-shadow: 0 15px 30px rgba(92, 232, 191, 0.3);
}

.btn-cancel {
    background: var(--bg-tertiary);
    border: 1px solid var(--border-color);
    color: var(--text-primary);
}

.btn-cancel:hover {
    background: var(--bg-secondary);
    border-color: var(--primary);
}

/* Transition Animations */
.modal-enter-active, .modal-leave-active {
    transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.modal-enter-from, .modal-leave-to {
    opacity: 0;
    transform: scale(0.95) translateY(20px);
}
</style>
