<template>
    <ModalForm
        :isVisible="isOpen"
        title="Confirmar Contraseña"
        :loading="isLoading"
        submitLabel="Confirmar"
        @close="handleClose"
        @submit="handleConfirm"
    >
        <p class="description">
            Por seguridad, por favor confirma tu contraseña maestra para continuar.
        </p>

        <div class="form-group">
            <label for="password">Contraseña</label>
            <div class="input-wrapper">
                <input 
                    ref="passwordInput"
                    type="password" 
                    id="password" 
                    v-model="password" 
                    class="form-control"
                    placeholder="Ingresa tu contraseña"
                    required
                    autocomplete="current-password"
                    @keyup.enter="handleConfirm"
                >
            </div>
            <span v-if="error" class="error-text">{{ error }}</span>
        </div>
    </ModalForm>
</template>

<script setup>
import { ref, nextTick, watch } from 'vue';
import Icon from '@/components/Icon.vue';
import ModalForm from '@/views/private/admin/components/ModalForm.vue';

const props = defineProps({
    isOpen: {
        type: Boolean,
        default: false
    }
});

const emit = defineEmits(['close', 'confirmed']);

const password = ref('');
const error = ref('');
const isLoading = ref(false);
const passwordInput = ref(null);

watch(() => props.isOpen, (newVal) => {
    if (newVal) {
        password.value = '';
        error.value = '';
        nextTick(() => {
            passwordInput.value?.focus();
        });
    }
});

const handleClose = () => {
    password.value = '';
    error.value = '';
    emit('close');
};

const handleConfirm = async () => {
    if (!password.value) {
        error.value = 'La contraseña es requerida';
        return;
    }

    emit('confirmed', password.value);
};

// Expose setError to parent to display server errors
const setError = (msg) => {
    error.value = msg;
    isLoading.value = false;
};

const setLoading = (val) => {
    isLoading.value = val;
};

defineExpose({ setError, setLoading });
</script>


