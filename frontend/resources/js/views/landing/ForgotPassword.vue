<template>
    <AuthLayout
        :width="forgotPasswordConfig.layout.width"
        :align="forgotPasswordConfig.layout.align"
        :subtitle="forgotPasswordConfig.subtitle"
    >
        <template #header>
            <h1 style="display: flex; align-items: center; justify-content: center; gap: 15px; margin: 0; width: 100%;">
                <span>{{ forgotPasswordConfig.title }}</span>
                <Icon name="email" :size="40" />
            </h1>
        </template>

        <template #form>
            <form @submit.prevent="handleSubmit" class="login-form">
                <AuthField
                    v-for="field in forgotPasswordConfig.fields"
                    :key="field.id"
                    :id="field.id"
                    v-model="form[field.id]"
                    :label="field.label"
                    :icon="field.icon"
                    :type="field.type"
                    :placeholder="field.placeholder"
                    :disabled="loading"
                    :error="localErrors[field.id] || (serverErrors[field.id] ? serverErrors[field.id][0] : '')"
                    :showError="true"
                    :colSpan="field.colSpan"
                    @input="localErrors[field.id] = ''"
                    :centered="true"
                />

                <div style="grid-column: 1 / -1; display: flex; justify-content: center;">
                    <button
                        type="submit"
                        class="btn-primary"
                        :disabled="loading"
                        style="display: flex; align-items: center; justify-content: center; gap: 10px; width: 100%;"
                    >
                        <Icon v-if="!loading" name="send" :size="20" />
                        <span v-if="loading">Enviando enlace...</span>
                        <span v-else>Enviar Enlace de Recuperación</span>
                    </button>
                </div>
            </form>
        </template>

        <template #footer>
            <p v-if="forgotPasswordConfig.footer.showLogin" class="auth-links">
                ¿Recordaste tu contraseña? 
                <router-link to="/login" class="link">Inicia sesión</router-link>
            </p>
        </template>
    </AuthLayout>
</template>

<script setup>
import { reactive, ref } from 'vue';
import { useAuth } from '@/composables/useAuth';
import { useAlert } from '@/composables/useAlert';
import Icon from '@/components/Icon.vue';
import AuthLayout from './components/AuthLayout.vue';
import AuthField from './components/AuthField.vue';
import { forgotPasswordConfig } from './config/forgot-password-config';

const { forgotPassword } = useAuth();
const alert = useAlert();

const form = reactive({
    email: ''
});

const serverErrors = ref({});
const localErrors = reactive({
    email: ''
});
const loading = ref(false);

const validateForm = () => {
    let isValid = true;
    localErrors.email = '';

    if (!form.email) {
        localErrors.email = 'El correo electrónico es obligatorio';
        isValid = false;
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email)) {
        localErrors.email = 'El formato del correo no es válido';
        isValid = false;
    }

    return isValid;
};

const handleSubmit = async () => {
    if (!validateForm()) return;

    loading.value = true;
    serverErrors.value = {};
    
    const result = await forgotPassword(form.email);
    
    if (result.success) {
        alert.toast.success('Petición Enviada', result.data.message, 6000, result.icon);
        form.email = ''; // Clear email on success
    } else {
        serverErrors.value = result.message || {};
        const msg = typeof result.message === 'string' ? result.message : 'No se pudo procesar la solicitud';
        alert.toast.error('Error', msg, 4000, result.icon);
    }
    
    loading.value = false;
};
</script>
