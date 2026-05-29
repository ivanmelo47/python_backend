<template>
    <AuthLayout
        :title="isMaintenance ? 'Sistema en Mantenimiento' : loginConfig.title"
        :subtitle="isMaintenance ? 'Volveremos pronto' : loginConfig.subtitle"
        :width="loginConfig.layout.width"
        :align="loginConfig.layout.align"
    >
        <template #header-icon>
            <Icon :name="isMaintenance ? 'tool' : 'user'" :size="40" />
        </template>

        <template #form>
            <div v-if="isMaintenance" class="maintenance-message text-center p-6">
                 <div class="mb-4 text-gray-600 dark:text-gray-300">
                    <p class="whitespace-pre-line">{{ maintenanceMessage }}</p>
                 </div>
                 <div class="mt-6">
                     <p class="text-sm text-gray-500">¿Eres administrador?</p>
                     <router-link to="/master-login" class="text-primary hover:underline font-medium">
                         Acceso de Emergencia
                     </router-link>
                 </div>
            </div>

            <form v-else @submit.prevent="handleLogin" class="login-form">
                <AuthField
                    v-for="field in loginConfig.fields"
                    :key="field.id"
                    :id="field.id"
                    v-model="form[field.id]"
                    :label="field.label"
                    :icon="field.icon"
                    :type="field.type"
                    :placeholder="field.placeholder"
                    :disabled="loading"
                    :error="errors[field.id]"
                    :showError="showInlineErrors"
                    :colSpan="field.colSpan"
                    @input="field.sanitize === 'username' ? sanitizeIdent() : (errors[field.id] = '')"
                />

                <div class="form-group checkbox-group col-span-6">
                    <label class="checkbox-label">
                        <input type="checkbox" v-model="form.remember" :disabled="loading" />
                        <span class="checkmark"></span>
                        Mantener sesión iniciada
                    </label>
                </div>

                <button
                    type="submit"
                    class="btn-primary"
                    :disabled="loading"
                >
                    <Icon v-if="!loading" name="login" :size="20" />
                    <span v-if="loading">Iniciando sesión...</span>
                    <span v-else>Entrar al Portal</span>
                </button>
            </form>
        </template>

        <template #footer>
            <div v-if="!isMaintenance">
                <p v-if="loginConfig.footer.showRegister" class="auth-links">
                    ¿No tienes cuenta?
                    <router-link to="/register" class="link">Regístrate gratis</router-link>
                </p>
                <p v-if="loginConfig.footer.showForgot" class="auth-links secondary">
                    <router-link to="/recuperar-cuenta" class="link">¿Olvidaste tu contraseña?</router-link>
                </p>
            </div>
        </template>
    </AuthLayout>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useAuth } from '@/composables/useAuth';
import { useAlert } from '@/composables/useAlert';
import Icon from '@/components/Icon.vue';
import AuthLayout from './components/AuthLayout.vue';
import AuthField from './components/AuthField.vue';
import { loginConfig } from './config/login-config';
import { api } from '@/services/api';

const router = useRouter();
const { login } = useAuth();
const alert = useAlert();

const isMaintenance = ref(false);
const maintenanceMessage = ref('Estamos realizando mejoras en la plataforma. Por favor, intenta ingresar más tarde.');
const requireGeolocation = ref(false);

onMounted(async () => {
    // 1. Initial check via URL param (fast, but potentially stale)
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.get('maintenance')) {
        isMaintenance.value = true;
    }

    // 2. Verified check via API (source of truth)
    try {
        const response = await api.system.getMaintenanceMode();
        const mode = response.data.data.maintenance_mode;
        requireGeolocation.value = !!response.data.data.require_geolocation;

        // Sync state with API
        isMaintenance.value = !!mode;

        if (mode && response.data.data.maintenance_message) {
            maintenanceMessage.value = response.data.data.maintenance_message;
        }

        // If maintenance is OFF but we have the param in URL, clean it up for better UX
        if (!mode && urlParams.get('maintenance')) {
            router.replace({ query: {} });
        }
    } catch (error) {
        console.error('Error checking maintenance mode:', error);
    }
});

// Dynamically initialize form state from config
const form = reactive({
    ...loginConfig.fields.reduce((acc, f) => ({ ...acc, [f.id]: '' }), {}),
    remember: false
});

// Dynamically initialize error state
const errors = reactive({
    ...loginConfig.fields.reduce((acc, f) => ({ ...acc, [f.id]: '' }), {})
});

const loading = ref(false);
const message = ref('');
const messageType = ref('');
const appEnv = (import.meta.env.VITE_APP_ENV || '').toLowerCase();
const isLocalEnv = appEnv === 'local';

const validationMode = ref('inline'); // Options: 'inline', 'toast', 'both'
const showInlineErrors = computed(() => validationMode.value === 'inline' || validationMode.value === 'both');

const canRequestPreciseLocation = () => {
    if (!navigator.geolocation) return false;
    if (isLocalEnv) return true;
    return window.isSecureContext;
};

const sanitizeIdent = () => {
    // Basic sanitization for the first field (usually email or username)
    form.email = form.email.toLowerCase().replace(/\s/g, '');
    errors.email = '';
};

const validateForm = () => {
    // Reset errors
    Object.keys(errors).forEach(key => errors[key] = '');

    let isValid = true;
    const showToast = validationMode.value === 'toast' || validationMode.value === 'both';
    const showInline = showInlineErrors.value;

    let errorCount = 0;

    // Generic required validation for all config fields
    loginConfig.fields.forEach(field => {
        if (!form[field.id]) {
            const msg = `El campo ${field.label.toLowerCase()} es obligatorio`;
            if (showToast) alert.toast.error('Campo Requerido', msg, 3000 + (errorCount * 500));
            if (showInline) errors[field.id] = msg;
            isValid = false;
            errorCount++;
        }
    });

    return isValid;
};

const getUserLocation = () => {
    return new Promise((resolve) => {
        if (!navigator.geolocation) {
            resolve(null);
            return;
        }

        // Increase timeout to 10s to account for slow devices or user prompt interaction
        const timeoutId = setTimeout(() => {
            console.warn("Geolocation timed out");
            resolve(null);
        }, 10000);

        navigator.geolocation.getCurrentPosition(
            (position) => {
                clearTimeout(timeoutId);
                resolve(position);
            },
            (error) => {
                clearTimeout(timeoutId);
                console.warn("Geolocation denied or error:", error.message, error.code);
                resolve(null);
            },
            {
                enableHighAccuracy: true,
                timeout: 10000,
                maximumAge: 60000 // Accept positions up to 1 minute old
            }
        );
    });
};

const handleLogin = async () => {
    if (!validateForm()) return;
    if (loading.value) return;

    loading.value = true;
    message.value = '';

    try {
        // Show loading screen immediately
        alert.showLoading('Iniciando Sesión', 'Verificando credenciales...');

        // Check if Geolocation is required
        let location = null;

        if (requireGeolocation.value) {
            if (!canRequestPreciseLocation()) {
                loading.value = false;
                alert.closeLoading();
                const msg = isLocalEnv
                    ? 'Tu navegador no tiene disponible la API de geolocalización para este origen.'
                    : 'La ubicación exacta en producción requiere HTTPS o localhost. Accede por un origen seguro.';
                alert.toast.error('Ubicación Requerida', msg, 6000, 'map-marker-off');
                message.value = msg;
                messageType.value = 'error';
                return;
            }

            alert.showLoading('Iniciando Sesión', 'Obteniendo ubicación del dispositivo...');
            location = await getUserLocation();

            if (!location) {
                loading.value = false;
                alert.closeLoading();
                const msg = 'La ubicación es obligatoria para iniciar sesión. Por favor, permite el acceso a tu ubicación.';
                alert.toast.error('Ubicación Requerida', msg, 5000, 'map-marker-off');
                message.value = msg;
                messageType.value = 'error';
                return;
            }
        }

        const credentials = {
            email: form.email,
            password: form.password,
            latitude: location?.coords?.latitude || null,
            longitude: location?.coords?.longitude || null,
        };

        const result = await login(credentials);

        alert.closeLoading(); // Close loading before showing success/error

        if (result.success) {
            alert.toast.success(result.status.charAt(0).toUpperCase() + result.status.slice(1), 'Sesión iniciada correctamente', 3000, result.icon);

            setTimeout(() => {
                router.push('/dashboard');
            }, 1000);
        } else {
            // Always show toast for errors per user preference
            alert.toast.error(
                result.status === 'error' ? 'Error de Inicio de Sesión' : result.status,
                result.message,
                4000,
                result.icon
            );

            // Clear password on error
            form.password = '';
            message.value = result.message;
            messageType.value = 'error';
        }
    } catch (error) {
        alert.closeLoading(); // Ensure closed on error
        console.error("Login Error:", error);
        alert.toast.error('Error', 'Ocurrió un error inesperado', 4000, 'error');
    } finally {
        loading.value = false;
        // alert.closeLoading(); // Already handled above in try/catch to avoid closing success toast prematurely if it overlapped
    }
};
</script>
