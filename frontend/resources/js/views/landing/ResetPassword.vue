<template>
    <AuthLayout
        :width="resetPasswordConfig.layout.width"
        :align="resetPasswordConfig.layout.align"
        :subtitle="resetPasswordConfig.subtitle"
    >
        <template #header>
            <h1 style="display: flex; align-items: center; justify-content: center; gap: 15px; margin: 0; width: 100%;">
                <span>{{ resetPasswordConfig.title }}</span>
                <Icon name="lock" :size="40" />
            </h1>
        </template>

        <template #form>
            <div v-if="verifying" class="text-center py-8">
                <div class="spinner mx-auto mb-4"></div>
                <p class="text-gray-500">Verificando enlace...</p>
            </div>

            <form v-else-if="isTokenValid" @submit.prevent="handleSubmit" class="login-form">
                <AuthField
                    v-for="field in resetPasswordConfig.fields"
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
                        <Icon v-if="!loading" name="check" :size="20" />
                        <span v-if="loading">Restableciendo...</span>
                        <span v-else>Cambiar Contraseña</span>
                    </button>
                </div>
            </form>
        </template>

        <template #footer>
            <p v-if="resetPasswordConfig.footer.showLogin" class="auth-links">
                ¿Recordaste tu contraseña? 
                <router-link to="/login" class="link">Inicia sesión</router-link>
            </p>
        </template>
    </AuthLayout>
</template>

<script setup>
import { reactive, ref, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useAuth } from '@/composables/useAuth';
import { useAlert } from '@/composables/useAlert';
import { api } from '@/services/api';
import Icon from '@/components/Icon.vue';
import AuthLayout from './components/AuthLayout.vue';
import AuthField from './components/AuthField.vue';
import { resetPasswordConfig } from './config/reset-password-config';

const route = useRoute();
const router = useRouter();
const { resetPassword } = useAuth();
const alert = useAlert();

const form = reactive({
    token: '',
    email: '',
    password: '',
    password_confirmation: ''
});

const serverErrors = ref({});
const localErrors = reactive({
    password: '',
    password_confirmation: ''
});
const loading = ref(false);
const verifying = ref(true); // New state for initial check
const isTokenValid = ref(false);

onMounted(async () => {
    form.token = route.params.token;
    form.email = route.query.email || '';
    
    // Validacion local antes de llamar al servidor
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

    if (!form.token || !form.email) {
        await alert.fire({
            type: 'error',
            title: 'Error',
            text: 'Información de restablecimiento no válida o incompleta.',
            confirmText: 'Volver al Login'
        });
        router.push('/login');
        return;
    }

    if (!emailRegex.test(form.email)) {
        await alert.fire({
            type: 'error',
            title: 'Error',
            text: 'El formato del correo electrónico no es válido.',
            confirmText: 'Volver al Login'
        });
        router.push('/login');
        return;
    }

    // Server-side validation
    try {
        await api.auth.validateResetToken({
            token: form.token,
            email: form.email
        });
        isTokenValid.value = true;
    } catch (error) {
        // Extract error message
        const apiRes = error.response?.data;
        const msg = apiRes?.data?.message || 'Token inválido';

        await alert.fire({
            type: 'error',
            title: 'Enlace Inválido',
            text: msg,
            confirmText: 'Entendido'
        });
        router.push('/login'); // Redirect after error
    }
    
    verifying.value = false;
});

const validateForm = () => {
    let isValid = true;
    localErrors.password = '';
    localErrors.password_confirmation = '';

    if (!form.password) {
        localErrors.password = 'La nueva contraseña es obligatori';
        isValid = false;
    } else if (form.password.length < 8) {
        localErrors.password = 'La contraseña debe tener al menos 8 caracteres';
        isValid = false;
    }

    if (form.password !== form.password_confirmation) {
        localErrors.password_confirmation = 'Las contraseñas no coinciden';
        isValid = false;
    }

    return isValid;
};

const handleSubmit = async () => {
    if (!validateForm()) return;

    loading.value = true;
    serverErrors.value = {};
    
    const result = await resetPassword(form);
    
    if (result.success) {
        alert.toast.success('¡Éxito!', result.data.message, 5000, result.icon);
        router.push('/login');
    } else {
        serverErrors.value = result.message || {};
        const msg = typeof result.message === 'string' ? result.message : 'No se pudo restablecer la contraseña';
        alert.toast.error('Error', msg, 4000, result.icon);
    }
    
    loading.value = false;
};
</script>
