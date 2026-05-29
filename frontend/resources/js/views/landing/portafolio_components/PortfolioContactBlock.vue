<template>
    <PortfolioBlock
        kicker="Contacto"
        title="Construyamos algo potente"
        id="contacto"
        class="contact-block reveal reveal-delay-4"
    >
        <div class="contact-info-summary" v-if="phone">
            <div class="contact-item">
                <Icon name="phone" :size="18" class="contact-icon" />
                <span>{{ phone }}</span>
            </div>
            <div class="contact-item">
                <Icon name="mail" :size="18" class="contact-icon" />
                <span>{{ email }}</span>
            </div>
        </div>
        
        <p v-else>
            Este bloque puede conectarse al panel para mostrar redes, email, CV y boton de reunion.
        </p>

        <div class="contact-actions">
            <button type="button" class="landing-cta contact-cta" @click="$emit('open-contact')">
                <Icon name="send" :size="18" />
                Enviar correo
            </button>
            <a v-if="whatsappUrl" :href="whatsappUrl" target="_blank" class="whatsapp-btn">
                <Icon name="whatsapp" :size="20" />
                WhatsApp
            </a>
            <button type="button" class="btn-cv" @click="$emit('download-cv')">
                <Icon name="download" :size="18" />
                Descargar CV
            </button>
        </div>
    </PortfolioBlock>
</template>

<script setup>
import { computed } from 'vue';
import PortfolioBlock from './PortfolioBlock.vue';
import Icon from '@/components/Icon.vue';

defineEmits(['open-contact', 'download-cv']);

const props = defineProps({
    email: {
        type: String,
        default: ''
    },
    phone: {
        type: String,
        default: ''
    },
    whatsapp: {
        type: String,
        default: ''
    }
});

const whatsappUrl = computed(() => {
    const raw = props.whatsapp || props.phone;
    if (!raw) return null;
    const clean = String(raw).replace(/\D/g, '');
    return `https://wa.me/${clean}`;
});
</script>

<style scoped>
.contact-info-summary {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    margin-bottom: 1.5rem;
}

.contact-item {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    color: var(--text-secondary);
    font-size: 0.95rem;
    font-weight: 500;
}

.contact-icon {
    color: var(--primary);
}

.contact-actions {
    margin-top: 0.95rem;
    display: flex;
    gap: 0.8rem;
    flex-wrap: wrap;
}

.contact-cta, .whatsapp-btn, .btn-cv {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    height: 48px;
    padding: 0 1.5rem;
    border-radius: 12px;
    font-weight: 700;
    font-size: 0.92rem;
    text-decoration: none;
    border: none;
    cursor: pointer;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.contact-cta {
    background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
    color: white;
    box-shadow: 0 4px 15px color-mix(in srgb, var(--primary), transparent 80%);
}

.contact-cta:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 25px color-mix(in srgb, var(--primary), transparent 70%);
}

.whatsapp-btn {
    background: rgba(37, 211, 102, 0.1);
    color: #25D366;
    border: 1px solid rgba(37, 211, 102, 0.2);
}

.whatsapp-btn:hover {
    background: #25D366;
    color: white;
    transform: translateY(-2px);
    box-shadow: 0 8px 20px rgba(37, 211, 102, 0.3);
}

.btn-cv {
    color: var(--text-primary);
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid var(--border-color);
}

.btn-cv:hover {
    border-color: var(--primary);
    color: var(--primary);
    transform: translateY(-2px);
}

.contact-actions button:active,
.contact-actions a:active {
    transform: translateY(0);
}
</style>
