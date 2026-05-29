<template>
    <article class="editor-card">
        <h3>Contacto y Redes Sociales</h3>
        <div class="form-grid">
            <label>
                Email de contacto
                <input v-model.trim="contact.email" type="email" maxlength="140" />
            </label>

            <label>
                Teléfono público (visible)
                <input v-model.trim="contact.phone" type="text" placeholder="Ej. +52 123 456 7890" maxlength="30" />
            </label>

            <label>
                Número de WhatsApp (con lada)
                <input v-model.trim="contact.whatsapp" type="text" placeholder="Ej. 521234567890" maxlength="20" />
            </label>
        </div>

        <div class="social-management">
            <header class="social-header">
                <h4>Redes Profesionales</h4>
                <button type="button" class="btn btn--compact btn--primary" @click="addSocialLink">
                    <Icon name="plus" :size="14" />
                    Añadir red
                </button>
            </header>

            <div v-if="social.length === 0" class="social-empty">
                <Icon name="users" :size="32" />
                <p>No has añadido redes sociales profesionales todavía.</p>
            </div>

            <div v-else class="social-list">
                <div v-for="(link, index) in social" :key="index" class="social-item" :class="{ 'is-hidden': link.is_active === false }">
                    <div class="social-item-row">
                        <div class="social-status-toggle">
                            <label class="toggle-switch" :title="link.is_active !== false ? 'Ocultar red' : 'Mostrar red'">
                                <input type="checkbox" v-model="link.is_active" />
                                <span class="toggle-slider"></span>
                            </label>
                            <span class="status-label">{{ link.is_active !== false ? 'Visible' : 'Oculto' }}</span>
                        </div>

                        <div class="social-icon-select">
                            <IconSelect
                                category="portafolio"
                                v-model="link.icon_uuid"
                                :selected-icon-data="link.icon_data"
                                @change="(icon) => handleSocialIconChange(index, icon)"
                            />
                        </div>

                        <div class="social-inputs">
                            <input v-model.trim="link.name" type="text" placeholder="Nombre (Ej. LinkedIn)" class="input-name" />
                            <input v-model.trim="link.handle" type="text" placeholder="Usuario (Ej. @usuario)" class="input-handle" />
                        </div>

                        <button type="button" class="btn-delete" @click="removeSocialLink(index)" title="Eliminar">
                            <Icon name="trash" :size="18" />
                        </button>
                    </div>
                    <input v-model.trim="link.url" type="url" placeholder="URL completa (https://...)" class="input-url" />
                </div>
            </div>
        </div>
    </article>
</template>

<script setup>
import Icon from '@/components/Icon.vue';
import IconSelect from '@/components/IconSelect.vue';

const props = defineProps({
    contact: {
        type: Object,
        required: true
    },
    social: {
        type: Array,
        required: true
    }
});

function addSocialLink() {
    props.social.push({
        name: '',
        handle: '',
        url: '',
        icon: 'link',
        icon_uuid: null,
        icon_data: null,
        is_active: true
    });
}

function handleSocialIconChange(index, iconData) {
    props.social[index].icon_data = iconData || null;
}

function removeSocialLink(index) {
    props.social.splice(index, 1);
}
</script>

<style scoped>
.social-management {
    margin-top: 2rem;
    padding-top: 2rem;
    border-top: 1px solid var(--border-color);
}

.social-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 1.5rem;
}

.social-header h4 {
    margin: 0;
    font-size: 1.1rem;
    color: var(--text-primary);
}

.social-empty {
    padding: 3rem 1rem;
    text-align: center;
    background: rgba(255, 255, 255, 0.02);
    border: 2px dashed var(--border-color);
    border-radius: 16px;
    color: var(--text-muted);
}

.social-empty p {
    margin-top: 1rem;
}

.social-list {
    display: flex;
    flex-direction: column;
    gap: 1rem;
}

.social-item {
    background: var(--bg-secondary);
    border: 1px solid var(--border-color);
    border-radius: 12px;
    padding: 1rem;
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
    transition: all 0.3s;
}

.social-item.is-hidden {
    opacity: 0.6;
    background: rgba(255, 255, 255, 0.01);
}

.social-item:hover {
    border-color: var(--primary);
    box-shadow: 0 4px 12px var(--shadow-color);
}

.social-item-row {
    display: flex;
    gap: 1rem;
    align-items: center;
}

.social-status-toggle {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 4px;
    min-width: 50px;
}

.status-label {
    font-size: 0.65rem;
    font-weight: 700;
    text-transform: uppercase;
    color: var(--text-muted);
}

.social-item:not(.is-hidden) .status-label {
    color: var(--primary);
}

/* Custom Toggle Switch */
.toggle-switch {
    position: relative;
    display: inline-block;
    width: 40px;
    height: 20px;
}

.toggle-switch input {
    opacity: 0;
    width: 0;
    height: 0;
}

.toggle-slider {
    position: absolute;
    cursor: pointer;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-color: rgba(255, 255, 255, 0.1);
    transition: .4s;
    border-radius: 20px;
    border: 1px solid var(--border-color);
}

.toggle-slider:before {
    position: absolute;
    content: "";
    height: 14px;
    width: 14px;
    left: 2px;
    bottom: 2px;
    background-color: white;
    transition: .4s;
    border-radius: 50%;
}

input:checked + .toggle-slider {
    background-color: var(--primary);
    border-color: var(--primary);
}

input:checked + .toggle-slider:before {
    transform: translateX(20px);
}

.social-icon-select {
    position: relative;
    width: 140px;
}

.social-icon-select select {
    width: 100%;
    padding-left: 36px;
}

.icon-preview {
    position: absolute;
    left: 10px;
    top: 50%;
    transform: translateY(-50%);
    color: var(--primary);
    pointer-events: none;
}

.social-inputs {
    flex: 1;
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 0.75rem;
}

.input-url {
    width: 100%;
    font-size: 0.85rem;
    color: var(--text-secondary);
}

.btn-delete {
    background: transparent;
    border: none;
    color: var(--text-muted);
    cursor: pointer;
    padding: 8px;
    border-radius: 8px;
    transition: all 0.2s;
}

.btn-delete:hover {
    background: rgba(239, 68, 68, 0.1);
    color: #ef4444;
}

@media (max-width: 600px) {
    .social-item-row {
        flex-direction: column;
        align-items: stretch;
    }
    
    .social-icon-select {
        width: 100%;
    }
    
    .social-inputs {
        grid-template-columns: 1fr;
    }
}
</style>
