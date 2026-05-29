<template>
    <AuthLayout
        :title="title"
        :width="2"
        align="center"
    >
        <template #form>
            <div class="confirm-content" style="text-align: center; padding: 20px 0;">
                <div class="status-icon" style="margin-bottom: 25px;">
                    <Icon v-if="status === 'loading'" name="settings" :size="60" class="rotate" style="color: var(--primary);" />
                    <Icon v-if="status === 'success'" name="check" :size="60" style="color: #42b983;" />
                    <Icon v-if="status === 'error'" name="error" :size="60" style="color: #ff5252;" />
                </div>

                <p class="confirm-message" style="font-size: 1.1rem; line-height: 1.6; margin-bottom: 30px; color: var(--text-secondary);">
                    {{ message }}
                </p>

                <div class="confirm-actions">
                    <router-link v-if="status !== 'loading'" to="/login" class="btn-primary" style="text-decoration: none; padding: 12px 30px;">
                        <Icon name="login" :size="20" />
                        Ir al Inicio de Sesión
                    </router-link>
                </div>
            </div>
        </template>
    </AuthLayout>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import { useAuth } from '@/composables/useAuth';
import Icon from '@/components/Icon.vue';
import AuthLayout from './components/AuthLayout.vue';

const route = useRoute();
const { confirmAccount } = useAuth();

const status = ref('loading');
const title = ref('Verificando cuenta...');
const message = ref('Por favor espera un momento mientras validamos tu token.');

onMounted(async () => {
    const token = route.params.token;
    
    if (!token) {
        status.value = 'error';
        title.value = 'Error de validación';
        message.value = 'No se encontró un token de confirmación válido.';
        return;
    }

    const result = await confirmAccount(token);
    
    if (result.success) {
        status.value = 'success';
        title.value = '¡Cuenta Confirmada!';
        message.value = 'Tu cuenta ha sido verificada exitosamente. Ya puedes iniciar sesión con tus credenciales.';
    } else {
        status.value = 'error';
        title.value = 'Token Inválido';
        message.value = result.message || 'El token de confirmación ha expirado o ya ha sido utilizado.';
    }
});
</script>

<style scoped>
.rotate {
    animation: spin 2s linear infinite;
}

@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}
</style>
