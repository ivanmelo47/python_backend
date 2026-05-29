<template>
    <div class="public-share-layout">
        <header class="public-header">
            <div class="brand-group">
                <div class="brand">
                    <Icon name="cloud" :size="28" style="color: var(--primary);" />
                    <span>Mi Nube Publica</span>
                </div>
                <div class="header-separator" v-if="shareableName"></div>
                <div class="share-title" v-if="shareableName">
                    {{ shareableName }}
                </div>
            </div>
            <div class="owner-info" v-if="ownerName">
                Compartido por <strong>{{ ownerName }}</strong>
            </div>
        </header>

        <main class="public-main-content">
            <div v-if="loading" class="public-loading">
                <div class="loader"></div>
                <p>Verificando enlace seguro...</p>
            </div>
            
            <div v-else-if="error" class="public-error">
                <Icon name="info" :size="48" style="color: var(--danger);" />
                <h2>Enlace no disponible</h2>
                <p>{{ errorMessage }}</p>
                <button class="btn btn-secondary mt-1rem" @click="$router.push('/')">Volver al inicio</button>
            </div>

            <ShareAuth 
                v-else-if="requiresPassword && !hasAccess" 
                :token="token"
                @authenticated="onAuthenticated"
            />

            <div v-else class="share-viewer-host">
                <ShareViewer :token="token" />
            </div>
        </main>

        <footer class="public-footer">
            <p>&copy; {{ new Date().getFullYear() }} Plataforma de Archivos. Todos los derechos reservados.</p>
        </footer>
    </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import Icon from '@/components/Icon.vue';
import ShareAuth from './ShareAuth.vue';
import ShareViewer from './ShareViewer.vue';
import axios from 'axios';
import { buildApiUrl } from '@/services/api/url';

const route = useRoute();
const token = route.params.token;

const loading = ref(true);
const error = ref(false);
const errorMessage = ref('');
const requiresPassword = ref(false);
const hasAccess = ref(false);
const ownerName = ref('');
const shareableName = ref('');

const checkLinkStatus = async () => {
    try {
        loading.value = true;
        
        // We use a custom axios instance or raw axios for public routes to avoid sending Admin Tokens
        const res = await axios.get(buildApiUrl(`s/${token}/verify`), {
             // Necessary for session cookie storage from backend auth
            withCredentials: true 
        });
        
        const data = res.data;
        requiresPassword.value = data.requires_password;
        hasAccess.value = data.has_access;
        ownerName.value = data.owner_name;
        shareableName.value = data.shareable_name;
        
    } catch (e) {
        error.value = true;
        errorMessage.value = e.response?.data?.message || 'Error al conectar con el servidor.';
    } finally {
        loading.value = false;
    }
};

const onAuthenticated = () => {
    hasAccess.value = true;
    checkLinkStatus(); // re-verify
};

onMounted(() => {
    checkLinkStatus();
});
</script>

<style lang="scss" scoped>
.public-share-layout {
    display: flex;
    flex-direction: column;
    min-height: 100vh;
    height: 100vh;
    overflow: hidden;
    background: var(--bg-primary);
    background-image: radial-gradient(circle at top center, rgba(var(--primary-rgb), 0.05), transparent 40%);
    color: var(--text-primary);
}

.public-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 1rem 2rem;
    background: var(--bg-secondary);
    border-bottom: 1px solid var(--border-color);
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
    height: 70px;
    flex-shrink: 0;
    position: sticky;
    top: 0;
    z-index: 10;

    .brand-group {
        display: flex;
        align-items: center;
        gap: 1.25rem;
    }

    .brand {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        font-weight: 700;
        font-size: 1.25rem;
        letter-spacing: -0.5px;
    }

    .header-separator {
        width: 1px;
        height: 24px;
        background: var(--border-color);
    }

    .share-title {
        font-size: 1.1rem;
        font-weight: 500;
        color: var(--text-primary);
        opacity: 0.9;
    }

    .owner-info {
        font-size: 0.9rem;
        color: var(--text-secondary);

        strong {
            color: var(--text-primary);
        }
    }
}

.public-main-content {
    flex: 1;
    min-height: 0;
    display: flex;
    flex-direction: column;
    padding: 2rem;
    max-width: 1200px;
    margin: 0 auto;
    width: 100%;
    overflow: hidden;
    
    // Smooth transitions
    transition: all 0.3s ease;
}

.share-viewer-host {
    flex: 1;
    min-height: 0;
    display: flex;
    overflow: hidden;
}

.public-loading {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    flex: 1;
    gap: 1.5rem;
    color: var(--text-secondary);
    
    .loader {
        width: 40px;
        height: 40px;
        border: 4px solid var(--border-color);
        border-top-color: var(--primary);
        border-radius: 50%;
        animation: spin 1s linear infinite;
    }
}

.public-error {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
    flex: 1;
    background: var(--bg-secondary);
    border: 1px dashed var(--border-color);
    border-radius: 16px;
    padding: 3rem;
    max-width: 500px;
    margin: auto;
    
    h2 {
        margin: 1rem 0 0.5rem 0;
    }
    
    p {
        color: var(--text-secondary);
    }
}

.public-footer {
    padding: 1.5rem;
    text-align: center;
    font-size: 0.85rem;
    color: var(--text-secondary);
    background: var(--bg-secondary);
    border-top: 1px solid var(--border-color);
    flex-shrink: 0;
    position: sticky;
    bottom: 0;
    z-index: 10;
}

.mt-1rem {
    margin-top: 1rem;
}

@keyframes spin {
    to { transform: rotate(360deg); }
}

@media (max-width: 768px) {
    .public-header {
        flex-direction: column;
        height: auto;
        padding: 1rem;
        gap: 0.5rem;
        
        .owner-info {
            font-size: 0.8rem;
        }
    }
    
    .public-main-content {
        padding: 1rem;
    }
}
</style>
