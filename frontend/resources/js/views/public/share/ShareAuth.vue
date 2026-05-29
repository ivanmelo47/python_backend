<template>
    <div class="share-auth-container">
        <div class="auth-card">
            <div class="auth-icon-wrapper">
                <Icon name="lock" :size="42" />
            </div>
            <h2>Enlace Protegido</h2>
            <p>Este contenido está protegido por contraseña. Ingresa la clave para acceder.</p>
            
            <form @submit.prevent="submitPassword" class="auth-form">
                <div class="input-group" :class="{ 'has-error': error }">
                    <input 
                        type="password" 
                        v-model="password" 
                        placeholder="Contraseña del enlace"
                        required
                        :disabled="loading"
                        ref="passwordInput"
                    />
                    <button type="submit" class="btn btn-primary" :disabled="loading || !password">
                        <span v-if="!loading">Acceder</span>
                        <div v-else class="spinner-mini"></div>
                    </button>
                </div>
                <div v-if="error" class="error-message">
                    <Icon name="alert-circle" :size="14" />
                    <span>{{ errorMessage }}</span>
                </div>
            </form>
        </div>
    </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import Icon from '@/components/Icon.vue';
import axios from 'axios';
import { buildApiUrl } from '@/services/api/url';

const props = defineProps({
    token: {
        type: String,
        required: true
    }
});

const emit = defineEmits(['authenticated']);

const password = ref('');
const loading = ref(false);
const error = ref(false);
const errorMessage = ref('');
const passwordInput = ref(null);

onMounted(() => {
    // Auto focus the input on load
    if (passwordInput.value) {
        passwordInput.value.focus();
    }
});

const submitPassword = async () => {
    if (!password.value) return;
    
    try {
        loading.value = true;
        error.value = false;
        
        await axios.post(buildApiUrl(`s/${props.token}/authenticate`), 
            { password: password.value },
            { withCredentials: true }
        );
        
        // Let parent know to refresh Status
        emit('authenticated');
        
    } catch (e) {
        error.value = true;
        errorMessage.value = e.response?.data?.message || 'Contraseña incorrecta.';
        password.value = ''; // clear input
        if (passwordInput.value) passwordInput.value.focus();
    } finally {
        loading.value = false;
    }
};
</script>

<style lang="scss" scoped>
.share-auth-container {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 100%;
    margin-top: 2rem;
    animation: fadeIn 0.5s ease-out;
}

.auth-card {
    background: var(--bg-secondary);
    border: 1px solid var(--border-color);
    border-radius: 16px;
    padding: 3rem 2.5rem;
    text-align: center;
    max-width: 450px;
    width: 100%;
    box-shadow: 0 10px 40px rgba(0, 0, 0, 0.08);
    position: relative;
    overflow: hidden;

    &::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 6px;
        background: linear-gradient(90deg, var(--primary), var(--secondary));
    }

    h2 {
        margin: 1rem 0 0.5rem 0;
        font-size: 1.5rem;
        color: var(--text-primary);
    }

    p {
        color: var(--text-secondary);
        font-size: 0.95rem;
        margin-bottom: 2rem;
        line-height: 1.5;
    }
}

.auth-icon-wrapper {
    width: 80px;
    height: 80px;
    margin: 0 auto;
    background: rgba(var(--primary-rgb), 0.1);
    color: var(--primary);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 0 20px rgba(var(--primary-rgb), 0.2);
}

.auth-form {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    text-align: left;
}

.input-group {
    display: flex;
    gap: 0.5rem;
    background: var(--bg-primary);
    border: 2px solid var(--border-color);
    border-radius: 12px;
    padding: 0.5rem;
    transition: all 0.3s ease;

    &:focus-within {
        border-color: var(--primary);
        box-shadow: 0 0 0 3px rgba(var(--primary-rgb), 0.1);
    }

    &.has-error {
        border-color: var(--danger);
        animation: shake 0.4s ease-in-out;
    }

    input {
        flex: 1;
        border: none;
        background: transparent;
        padding: 0.5rem 0.5rem 0.5rem 1rem;
        color: var(--text-primary);
        font-size: 1rem;
        outline: none;

        &::placeholder {
            color: var(--text-muted);
        }
    }

    button {
        border-radius: 8px;
        padding: 0.5rem 1.5rem;
        font-weight: 600;
        min-width: 100px;
        display: flex;
        justify-content: center;
        align-items: center;
    }
}

.error-message {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    color: var(--danger);
    font-size: 0.85rem;
    padding-left: 0.5rem;
}

.spinner-mini {
    width: 20px;
    height: 20px;
    border: 2px solid rgba(255, 255, 255, 0.3);
    border-top-color: white;
    border-radius: 50%;
    animation: spin 0.8s linear infinite;
}

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
}

@keyframes shake {
    0%, 100% { transform: translateX(0); }
    25% { transform: translateX(-5px); }
    50% { transform: translateX(5px); }
    75% { transform: translateX(-5px); }
}

@keyframes spin {
    to { transform: rotate(360deg); }
}

@media (max-width: 480px) {
    .auth-card {
        padding: 2rem 1.5rem;
    }
    
    .input-group {
        flex-direction: column;
        background: transparent;
        border: none;
        padding: 0;
        gap: 1rem;

        input {
            background: var(--bg-primary);
            border: 2px solid var(--border-color);
            border-radius: 12px;
            padding: 1rem;
        }

        button {
            padding: 1rem;
            width: 100%;
        }
    }
}
</style>
