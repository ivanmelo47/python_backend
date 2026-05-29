<template>
    <AuthLayout
        :title="registerConfig.title"
        :subtitle="registerConfig.subtitle"
        :width="registerConfig.layout.width"
        :align="registerConfig.layout.align"
    >
        <template #header-icon>
            <Icon name="user" :size="40" />
        </template>

        <template #form>
            <form @submit.prevent="handleRegister" class="login-form">
                <AuthField
                    v-for="field in registerConfig.fields"
                    :key="field.id"
                    :id="field.id"
                    v-model="form[field.id]"
                    :label="field.label"
                    :icon="field.icon"
                    :type="field.type"
                    :placeholder="field.placeholder"
                    :disabled="loading"
                    :error="localErrors[field.id] || (serverErrors[field.id] ? serverErrors[field.id][0] : '')"
                    :showError="showInlineErrors"
                    :colSpan="field.colSpan"
                    @input="field.sanitize === 'username' ? sanitizeUsername() : (localErrors[field.id] = '')"
                />

                <button
                    type="submit"
                    class="btn-primary"
                    :disabled="loading"
                >
                    <Icon v-if="!loading" name="check" :size="20" />
                    <span v-if="loading">Registrando...</span>
                    <span v-else>Registrarse</span>
                </button>

            </form>
        </template>

        <template #footer>
            <p v-if="registerConfig.footer.showLogin" class="auth-links">
                ¿Ya tienes cuenta?
                <router-link to="/login" class="link">Inicia sesión</router-link>
            </p>
        </template>
    </AuthLayout>
</template>

<script setup>
import { reactive, ref, computed } from 'vue';
import { useRouter } from 'vue-router';
import { useAuth } from '@/composables/useAuth';
import { useAlert } from '@/composables/useAlert';
import Icon from '@/components/Icon.vue';
import AuthLayout from './components/AuthLayout.vue';
import AuthField from './components/AuthField.vue';
import { registerConfig } from './config/register-config';

const router = useRouter();
const { register } = useAuth();
const alert = useAlert();

// Dynamically initialize form state
const form = reactive({
    ...registerConfig.fields.reduce((acc, f) => ({ ...acc, [f.id]: '' }), {})
});

const serverErrors = ref({});

// Dynamically initialize local errors
const localErrors = reactive({
    ...registerConfig.fields.reduce((acc, f) => ({ ...acc, [f.id]: '' }), {})
});

const validationMode = ref('inline'); // Options: 'inline', 'toast', 'both'
const showInlineErrors = computed(() => validationMode.value === 'inline' || validationMode.value === 'both');

const sanitizeUsername = () => {
    if (form.name) {
        form.name = form.name.toLowerCase().replace(/\s/g, '');
    }
    localErrors.name = '';
};

const validateForm = () => {
    let isValid = true;
    let errorCount = 0;
    const showToast = validationMode.value === 'toast' || validationMode.value === 'both';
    const showInline = showInlineErrors.value;

    // Reset local errors
    Object.keys(localErrors).forEach(key => localErrors[key] = '');

    // Required check for all fields
    registerConfig.fields.forEach(field => {
        if (!form[field.id]) {
            const msg = `El campo ${field.label.toLowerCase()} es obligatorio`;
            if (showToast) alert.toast.error('Requerido', msg, 3000 + (errorCount * 500));
            if (showInline) localErrors[field.id] = msg;
            isValid = false;
            errorCount++;
        }
    });

    if (isValid) {
        // Specific checks
        if (form.email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email)) {
            const msg = 'El formato del correo no es válido';
            if (showToast) alert.toast.error('Formato Inválido', msg, 3000 + (errorCount * 500));
            if (showInline) localErrors.email = msg;
            isValid = false;
            errorCount++;
        }

        if (form.password && form.password.length < 8) {
            const msg = 'La contraseña debe tener al menos 8 caracteres';
            if (showToast) alert.toast.error('Seguridad', msg, 3000 + (errorCount * 500));
            if (showInline) localErrors.password = msg;
            isValid = false;
            errorCount++;
        }

        if (form.password && form.password !== form.password_confirmation) {
            const msg = 'Las contraseñas no coinciden';
            if (showToast) alert.toast.error('Validación', msg, 3000 + (errorCount * 500));
            if (showInline) localErrors.password_confirmation = msg;
            isValid = false;
            errorCount++;
        }
    }

    return isValid;
};

const loading = ref(false);

const handleRegister = async () => {
    if (!validateForm()) return;

    loading.value = true;
    loading.value = true;
    serverErrors.value = {};
    
    const result = await register(form);
    
    if (result.success) {
        alert.toast.success(result.status.charAt(0).toUpperCase() + result.status.slice(1), result.data.message, 5000, result.icon);
        router.push('/login');
    } else {
        serverErrors.value = result.message || {};
        
        const showToast = validationMode.value === 'toast' || validationMode.value === 'both';
        if (showToast) {
            let errorFound = false;
            let delay = 0;
            Object.values(serverErrors.value).forEach(errorGroup => {
                errorGroup.forEach(errorMsg => {
                    alert.toast.error('Error de registro', errorMsg, 3000 + delay, result.icon);
                    delay += 500;
                    errorFound = true;
                });
            });
            
            if (!errorFound) {
                alert.toast.error('Error de registro', 'Revisa los datos ingresados', 3000, result.icon);
            }
        }
    }
    
    loading.value = false;
};
</script>
