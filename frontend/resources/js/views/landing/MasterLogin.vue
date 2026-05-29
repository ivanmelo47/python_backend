<template>
    <div class="master-login-container">
        <div class="login-card">
            <div class="header">
                <div class="icon-wrapper">
                    <Icon name="shield-check" :size="48" />
                </div>
                <h1>Acceso de Emergencia</h1>
                <p>Solo para usuarios Supermaster en modo Mantenimiento</p>
            </div>
            
            <form @submit.prevent="handleLogin" class="login-form">
                <div class="form-group">
                    <label>Usuario o Correo</label>
                    <div class="input-wrapper">
                        <Icon name="user" :size="20" class="input-icon" />
                        <input 
                            v-model="form.email" 
                            type="text" 
                            placeholder="Usuario o correo electrónico" 
                            required
                            autofocus
                        >
                    </div>
                </div>

                <div class="form-group">
                    <label>Contraseña</label>
                    <div class="input-wrapper">
                        <Icon name="lock" :size="20" class="input-icon" />
                        <input 
                            v-model="form.password" 
                            :type="showPassword ? 'text' : 'password'" 
                            placeholder="••••••••" 
                            required
                        >
                        <button type="button" class="toggle-password" @click="showPassword = !showPassword">
                            <Icon :name="showPassword ? 'eye' : 'eye-off'" :size="20" />
                        </button>
                    </div>
                </div>
                
                <div v-if="error" class="error-message">
                    <Icon name="alert-circle" :size="18" />
                    <span>{{ error }}</span>
                </div>

                <div class="form-actions">
                    <button type="submit" class="btn-login" :disabled="loading">
                        <span v-if="loading" class="spinner"></span>
                        <span v-else>Acceder al Sistema</span>
                    </button>
                </div>
            </form>
            
            <div class="footer">
                <router-link to="/login">Volver al login normal</router-link>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, reactive } from 'vue';
import { useRouter } from 'vue-router';
import { useAuth } from '@/composables/useAuth';
import Icon from '@/components/Icon.vue';

const router = useRouter();
const { login } = useAuth();

const form = reactive({
    email: '',
    password: ''
});

const loading = ref(false);
const error = ref('');
const showPassword = ref(false);

const handleLogin = async () => {
    loading.value = true;
    error.value = '';
    
    try {
        const result = await login(form);
        
        if (result.success) {
            router.push('/dashboard');
        } else {
            error.value = result.error || 'Credenciales incorrectas';
            // If maintenance mode error returned 503, it means even supermaster check failed or logic is weird.
            // But AuthService should check supermaster and ALLOW it.
        }
    } catch (err) {
        console.error(err);
        error.value = 'Error al conectar con el servidor';
    } finally {
        loading.value = false;
    }
};
</script>


