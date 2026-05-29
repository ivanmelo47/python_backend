<template>
    <ModalForm
        :is-visible="isVisible"
        title="Registrar Compra / Gasto"
        :loading="isSaving"
        :fields="fields"
        :model-value="form"
        :errors="errors"
        @submit="$emit('submit')"
        @close="$emit('close')"
    >
        <template #field-monto="{ modelValue }">
            <div class="currency-input-container">
                <span class="symbol">$</span>
                <input type="number" v-model="modelValue.monto" placeholder="0.00" step="0.01">
            </div>
        </template>

        <template #field-plan_financiero="{ modelValue }">
            <div class="premium-switch-container">
                <div class="info">
                    <span class="title">Compra a Meses</span>
                    <span class="desc">Diferir el pago en mensualidades</span>
                </div>
                <label class="switch">
                    <input type="checkbox" v-model="modelValue.a_meses">
                    <span class="slider"></span>
                </label>
            </div>

            <div v-if="modelValue.a_meses" class="animate-fade-in">
                <div class="premium-switch-container mt-3" :class="{ 'msi-active': modelValue.es_msi }">
                    <div class="info">
                        <span class="title">Sin Intereses (MSI)</span>
                        <span class="desc">{{ modelValue.es_msi ? 'Plan sin cargos extra' : 'Plan con intereses calculados' }}</span>
                    </div>
                    <label class="switch">
                        <input type="checkbox" v-model="modelValue.es_msi">
                        <span class="slider"></span>
                    </label>
                </div>

                <div v-if="!modelValue.es_msi"
                    class="animate-fade-in mt-3 p-3 bg-error/5 border border-dashed border-error/20 rounded-xl">
                    <label class="form-label text-error fw-bold mb-2 block"
                        style="font-size: 0.75rem; letter-spacing: 0.05em;">MONTO TOTAL A PAGAR (CON
                        INTERESES)</label>
                    <div class="currency-input-container is-error">
                        <span class="symbol">$</span>
                        <input type="number" v-model="modelValue.monto_final" placeholder="Monto total final">
                    </div>
                    <div v-if="modelValue.monto_final > 0 && modelValue.monto > 0" class="mt-2 text-tertiary"
                        style="font-size: 0.7rem;">
                        <Icon name="trendingUp" :size="12" class="text-error mr-1" />
                        Costo por financiamiento:
                        <span class="text-error fw-bold">{{ formatCurrency(modelValue.monto_final - modelValue.monto) }}</span>
                        ({{ (((modelValue.monto_final / modelValue.monto) - 1) * 100).toFixed(1) }}% de interés total)
                    </div>
                </div>

                <div class="msi-plazo-input mt-3">
                    <label class="form-label">Plazo (Meses)</label>
                    <div class="input-wrapper">
                        <Icon name="calendar" :size="14" />
                        <input type="number" v-model="modelValue.plazo" min="2" placeholder="Ej. 12">
                    </div>
                </div>

                <div v-if="isHistorical(modelValue.fecha)" class="premium-switch-container mt-3">
                    <div class="info">
                        <span class="title">Desglosar Historial</span>
                        <span class="desc">Crear registros individuales por meses ya pagados</span>
                    </div>
                    <label class="switch">
                        <input type="checkbox" v-model="modelValue.desglosar_pagos">
                        <span class="slider"></span>
                    </label>
                </div>
            </div>
        </template>
    </ModalForm>
</template>

<script setup>
import ModalForm from '@/views/private/admin/components/ModalForm.vue';
import Icon from '@/components/Icon.vue';

defineProps({
    isVisible: {
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

const isHistorical = (dateStr) => {
    if (!dateStr) return false;
    const today = new Date().toISOString().split('T')[0];
    return dateStr < today;
};

const formatCurrency = (value) => {
    return new Intl.NumberFormat('es-MX', { style: 'currency', currency: 'MXN' }).format(value || 0);
};
</script>
