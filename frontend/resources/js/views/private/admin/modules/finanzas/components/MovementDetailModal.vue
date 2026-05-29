<template>
    <ModalForm
        :isVisible="isVisible"
        :title="`Gestión de Comprobantes: ${movimiento?.descripcion || 'Movimiento'}`"
        size="full"
        @close="$emit('close')"
        :hideFooter="true"
        class="movement-detail-modal"
        :style="{ '--sidebar-offset': currentOffset }"
    >
        <template #header-icon>
            <Icon name="paperclip" :size="20" />
        </template>

        <div class="movement-manager-v3" v-if="movimiento">
            <!-- Top Summary Bar -->
            <div class="summary-bar-premium mb-8">
                <div class="summary-item glass-panel amount" :class="movimiento.tipo">
                    <div class="item-icon">
                        <Icon :name="movimiento.tipo === 'ingreso' ? 'trendingUp' : 'trendingDown'" :size="20" />
                    </div>
                    <div class="item-details">
                        <span class="item-label">MONTO TRANSACCIÓN</span>
                        <span class="item-value" :class="movimiento.tipo === 'ingreso' ? 'text-success' : 'text-danger'">
                            {{ movimiento.tipo === 'ingreso' ? '+' : '-' }}{{ formatCurrency(movimiento.monto) }}
                        </span>
                    </div>
                </div>

                <div class="summary-item glass-panel date">
                    <div class="item-icon">
                        <Icon name="calendar" :size="20" />
                    </div>
                    <div class="item-details">
                        <span class="item-label">FECHA REGISTRO</span>
                        <span class="item-value">{{ formatDate(movimiento.fecha) }}</span>
                    </div>
                </div>

                <div class="summary-item glass-panel source">
                    <div class="item-icon">
                        <Icon :name="movimiento.tarjeta_id ? 'credit-card' : 'wallet'" :size="20" />
                    </div>
                    <div class="item-details">
                        <span class="item-label">{{ movimiento.tarjeta_id ? 'TARJETA' : 'CUENTA' }}</span>
                        <span class="item-value">{{ movimiento.tarjeta?.nombre || movimiento.cuenta?.nombre || 'N/A' }}</span>
                    </div>
                </div>
            </div>

            <!-- Attachments Management -->
            <div class="attachments-container glass-panel animate-slide-up">
                <MovementAttachments 
                    :movimientoUuid="movimiento.uuid" 
                    @updated="$emit('updated')" 
                />
            </div>
        </div>
    </ModalForm>
</template>

<script setup>
import { computed, ref, onMounted, onUnmounted, inject } from 'vue';
import ModalForm from '@/views/private/admin/components/ModalForm.vue';
import Icon from '@/components/Icon.vue';
import MovementAttachments from './MovementAttachments.vue';
import { formatDate } from '@/utils/format-date';

const props = defineProps({
    isVisible: Boolean,
    movimiento: Object
});

defineEmits(['close', 'updated']);

const layoutConfig = inject('layoutConfig', { isSidebarOpen: ref(true) });
const isSidebarOpen = computed(() => layoutConfig.isSidebarOpen?.value ?? true);
const windowWidth = ref(window.innerWidth);

const updateWidth = () => {
    windowWidth.value = window.innerWidth;
};

onMounted(() => {
    window.addEventListener('resize', updateWidth);
});

onUnmounted(() => {
    window.removeEventListener('resize', updateWidth);
});

const currentOffset = computed(() => {
    if (windowWidth.value < 1200) return '0px';
    return isSidebarOpen.value ? '260px' : '80px';
});

const formatCurrency = (val) => {
    return new Intl.NumberFormat('es-MX', { style: 'currency', currency: 'MXN' }).format(val);
};
</script>

<style lang="scss">
.movement-detail-modal.modal-overlay {
    left: var(--sidebar-offset, 0px) !important;
    width: calc(100% - var(--sidebar-offset, 0px)) !important;
    z-index: 99999 !important;
    transition: all 0.3s ease !important;

    .modal-container.modal-full {
        width: 96% !important;
        max-width: 1400px !important;
        transition: all 0.3s ease !important;
    }
}
</style>

<style lang="scss" scoped>
.movement-manager-v3 {
    padding: 1.5rem 2rem 2rem;

    @media (max-width: 768px) {
        padding: 1rem;
    }
}

.summary-bar-premium {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 1.5rem;

    .summary-item {
        display: flex;
        align-items: center;
        gap: 1.5rem;
        padding: 1.5rem 2rem;
        border-radius: 1.5rem;
        border: 1px solid rgba(255, 255, 255, 0.05);
        background: rgba(255, 255, 255, 0.02);
        transition: all 0.3s ease;

        &:hover {
            transform: translateY(-5px);
            border-color: rgba(var(--primary-rgb), 0.2);
            background: rgba(var(--primary-rgb), 0.03);
        }

        .item-icon {
            width: 54px;
            height: 54px;
            border-radius: 16px;
            display: flex;
            align-items: center;
            justify-content: center;
            background: rgba(var(--primary-rgb), 0.1);
            color: var(--primary);
            box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
        }

        .item-label {
            display: block;
            font-size: 0.7rem;
            font-weight: 800;
            color: var(--text-tertiary);
            letter-spacing: 0.1em;
            margin-bottom: 0.25rem;
        }

        .item-value {
            font-size: 1.5rem;
            font-weight: 900;
            letter-spacing: -0.02em;
        }

        &.amount {
            &.ingreso .item-icon { background: rgba(16, 185, 129, 0.1); color: #10b981; }
            &.gasto .item-icon { background: rgba(239, 68, 68, 0.1); color: #ef4444; }
        }
    }
}

.attachments-container {
    background: rgba(255, 255, 255, 0.02);
    border-radius: 24px;
    border: 1px solid rgba(255, 255, 255, 0.05);
    overflow: hidden;
}

.animate-slide-up {
    animation: slideUp 0.5s cubic-bezier(0.4, 0, 0.2, 1);
}

@keyframes slideUp {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
}
</style>
