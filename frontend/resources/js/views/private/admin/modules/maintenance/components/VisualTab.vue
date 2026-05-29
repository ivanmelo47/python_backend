<template>
    <div class="maintenance-visual-tab">
        <section class="maintenance-card">
            <div class="card-heading">
                <div>
                    <span class="section-kicker">Diseño y Layout</span>
                    <h2>Configuración Visual</h2>
                </div>
            </div>

            <p class="maintenance-description">
                Administra los elementos visuales globales de la aplicación, como la visibilidad del pie de página (footer) en diferentes tipos de dispositivos.
            </p>

            <!-- Loading State -->
            <div v-if="isLoadingConfig" class="flex justify-center py-8">
                <Icon name="refresh" class="spinning text-primary" :size="32" />
            </div>

            <!-- Settings Form -->
            <div v-else class="space-y-6">
                <!-- Desktop Footer Toggle -->
                <div class="toggle-wrapper maintenance-control-row">
                    <div class="control-info">
                        <h3>Footer en Escritorio</h3>
                        <p>Mostrar la barra de derechos reservados y enlaces útiles al final de la pantalla en monitores y laptops (pantallas grandes).</p>
                    </div>
                    <label class="switch">
                        <input type="checkbox" v-model="form.visual_footer_desktop" :disabled="isSaving" />
                        <span class="slider round"></span>
                    </label>
                </div>

                <!-- Mobile Footer Toggle -->
                <div class="toggle-wrapper maintenance-control-row">
                    <div class="control-info">
                        <h3>Footer en Móvil</h3>
                        <p>Mostrar la barra inferior en teléfonos celulares. Puede ser útil desactivarla para ganar espacio en pantallas pequeñas.</p>
                    </div>
                    <label class="switch">
                        <input type="checkbox" v-model="form.visual_footer_mobile" :disabled="isSaving" />
                        <span class="slider round"></span>
                    </label>
                </div>

                <!-- Save Button -->
                <div class="flex justify-end pt-4 mt-6 border-t border-gray-200 dark:border-gray-700">
                    <button
                        @click="saveSettings"
                        class="maintenance-action-btn maintenance-action-btn-primary"
                        :disabled="isSaving || !hasChanges"
                    >
                        <Icon v-if="isSaving" name="refresh" :size="16" class="spinning" />
                        {{ isSaving ? 'Guardando...' : 'Guardar Configuración' }}
                    </button>
                </div>
            </div>
        </section>

        <!-- Color Palettes Management -->
        <section class="maintenance-card">
            <div class="card-heading">
                <div>
                    <span class="section-kicker">Personalización</span>
                    <h2>Gestor de Paletas de Color</h2>
                </div>
                <button @click="showAddPaletteForm = true" class="maintenance-action-btn maintenance-action-btn-primary text-sm py-1 px-3" v-if="!showAddPaletteForm">
                    <Icon name="plus" :size="16" />
                    Agregar Color
                </button>
            </div>
            
            <p class="maintenance-description">
                Agrega paletas de colores personalizados a la aplicación. Las paletas por defecto del sistema no pueden ser eliminadas.
            </p>

            <!-- Add Form -->
            <transition name="fade">
                <div v-if="showAddPaletteForm" class="palette-form-container">
                    <div class="form-header">
                        <Icon name="palette" :size="20" class="text-primary" />
                        <h3 class="form-title">Nueva Paleta de Color</h3>
                    </div>
                    
                    <div class="palette-form-grid">
                        <div class="form-group">
                            <label class="form-label">Nombre de la Paleta</label>
                            <input type="text" v-model="newPalette.name" class="custom-input" placeholder="Ej. Rosa Corporativo">
                        </div>
                        
                        <div class="form-group">
                            <label class="form-label">Color Principal</label>
                            <div class="custom-color-picker">
                                <div class="picker-input-wrapper">
                                    <input v-model="newPalette.color" type="color" class="color-picker-hidden">
                                    <div class="color-bar" :style="{ backgroundColor: newPalette.color }"></div>
                                </div>
                                <input v-model="newPalette.color" type="text" class="custom-input hex-input" placeholder="#000000">
                            </div>
                        </div>
                    </div>

                    <div class="form-actions">
                        <button @click="showAddPaletteForm = false" class="maintenance-action-btn maintenance-action-btn-secondary">
                            Cancelar
                        </button>
                        <button @click="addPalette" class="maintenance-action-btn maintenance-action-btn-primary" :disabled="!newPalette.name || !newPalette.color">
                            Guardar Paleta
                        </button>
                    </div>
                </div>
            </transition>

            <!-- List -->
            <div class="table-card mt-6" style="margin-top: 1.5rem; border: 1px solid var(--border-color); border-radius: 1rem; overflow: hidden; box-shadow: none;">
                <div class="table-wrapper">
                    <table>
                        <thead>
                            <tr>
                                <th>Color</th>
                                <th>Nombre</th>
                                <th>ID Interno</th>
                                <th>Tipo</th>
                                <th style="text-align: right;">Acciones</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr v-for="p in allPalettesList" :key="p.id">
                                <td>
                                    <div class="w-6 h-6 rounded-full border border-gray-300 dark:border-gray-600 shadow-sm" :style="{ backgroundColor: p.color }"></div>
                                </td>
                                <td style="font-weight: 600;">{{ p.name }}</td>
                                <td><span class="mono-badge">{{ p.id }}</span></td>
                                <td>
                                    <span v-if="p.isStatic" class="status-badge bg-gray">Sistema</span>
                                    <span v-else class="status-badge bg-primary">Personalizado</span>
                                </td>
                                <td style="text-align: right;">
                                    <button v-if="!p.isStatic" @click="deletePalette(p.id)" class="action-btn-danger" title="Eliminar">
                                        <Icon name="trash" :size="18" />
                                    </button>
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>

        </section>
    </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import Icon from '@/components/Icon.vue';
import { api } from '@/services/api';
import { useAlert } from '@/composables/useAlert';
import { useColorPalette } from '@/composables/useColorPalette';

const alert = useAlert();

const isLoadingConfig = ref(true);
const isSaving = ref(false);

const originalConfig = ref({
    visual_footer_desktop: true,
    visual_footer_mobile: true,
    visual_color_palettes: []
});

const form = ref({
    visual_footer_desktop: true,
    visual_footer_mobile: true,
    visual_color_palettes: []
});

const hasChanges = computed(() => {
    return form.value.visual_footer_desktop !== originalConfig.value.visual_footer_desktop ||
           form.value.visual_footer_mobile !== originalConfig.value.visual_footer_mobile;
});

// Color Palettes Logic
const { staticPalettes, fetchDynamicPalettes } = useColorPalette();
const showAddPaletteForm = ref(false);
const newPalette = ref({ name: '', color: '#3b82f6' });

const allPalettesList = computed(() => {
    const statics = Object.values(staticPalettes);
    const dynamics = form.value.visual_color_palettes || [];
    return [...statics, ...dynamics];
});

const addPalette = () => {
    if (!newPalette.value.name || !newPalette.value.color) return;
    
    // Generate an ID
    const id = 'custom_' + newPalette.value.name.toLowerCase().replace(/[^a-z0-9]/g, '') + '_' + Date.now().toString().slice(-4);
    
    const paletteObj = {
        id: id,
        name: newPalette.value.name,
        color: newPalette.value.color,
        isStatic: false
    };
    
    form.value.visual_color_palettes.push(paletteObj);
    
    // Reset form
    newPalette.value = { name: '', color: '#3b82f6' };
    showAddPaletteForm.value = false;
    
    // Auto-save changes for palettes
    saveSettings();
};

const deletePalette = (id) => {
    if (confirm('¿Estás seguro de eliminar esta paleta de colores?')) {
        form.value.visual_color_palettes = form.value.visual_color_palettes.filter(p => p.id !== id);
        saveSettings();
    }
};

const fetchSettings = async () => {
    isLoadingConfig.value = true;
    try {
        const response = await api.system.getVisualSettings();
        if (response.data && response.data.data) {
            const data = response.data.data;
            originalConfig.value = { ...data };
            form.value = { ...data };
        }
    } catch (error) {
        console.error('Error fetching visual settings:', error);
        alert.toast.error('Error', 'No se pudo cargar la configuración visual.');
    } finally {
        isLoadingConfig.value = false;
    }
};

const saveSettings = async () => {
    isSaving.value = true;
    try {
        await api.system.updateVisualSettings(form.value);
        
        // Update original to match saved
        originalConfig.value = { ...form.value };
        
        // Emitting event to layout or letting reactivity handle it via page refresh
        // For simplicity and to ensure layout updates properly:
        alert.toast.success('Guardado', 'La configuración visual ha sido actualizada.');
        
        // Refresh global palettes
        fetchDynamicPalettes();
        
        // Optional: Dispatch a custom event to update dashboard state without reloading
        window.dispatchEvent(new CustomEvent('visual-settings-updated', { detail: form.value }));
        
    } catch (error) {
        console.error('Error saving visual settings:', error);
        alert.toast.error('Error', 'No se pudo guardar la configuración.');
    } finally {
        isSaving.value = false;
    }
};

onMounted(() => {
    fetchSettings();
});
</script>

<style lang="scss" scoped>
.maintenance-visual-tab {
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
}

/* Premium Form Container */
.palette-form-container {
    background: var(--bg-secondary);
    border: 1px solid var(--border-color);
    border-radius: 1rem;
    padding: 1.5rem;
    margin-bottom: 1.5rem;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);

    .form-header {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        margin-bottom: 1.25rem;
        
        .form-title {
            font-size: 1.1rem;
            font-weight: 700;
            color: var(--text-primary);
            margin: 0;
        }
    }

    .palette-form-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 1.5rem;
        margin-bottom: 1.5rem;

        @media (max-width: 768px) {
            grid-template-columns: 1fr;
        }
    }

    .form-group {
        display: flex;
        flex-direction: column;
        gap: 0.5rem;

        .form-label {
            font-size: 0.85rem;
            font-weight: 600;
            color: var(--text-secondary);
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .custom-input {
            width: 100%;
            padding: 0.75rem 1rem;
            border-radius: 0.85rem;
            border: 1px solid var(--border-color);
            background: var(--bg-primary);
            color: var(--text-primary);
            font-size: 0.95rem;
            transition: all 0.2s ease;
            
            &:focus {
                outline: none;
                border-color: var(--primary);
                box-shadow: 0 0 0 3px rgba(var(--primary-rgb), 0.15);
            }
        }
    }

    .form-actions {
        display: flex;
        justify-content: flex-end;
        gap: 0.75rem;
        border-top: 1px solid var(--border-color);
        padding-top: 1.25rem;
        margin-top: 0.5rem;
    }
}

/* Custom Color Picker (Extracted from ModalForm) */
.custom-color-picker {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    width: 100%;

    .picker-input-wrapper {
        position: relative;
        height: 48px;
        width: 100%;
        border-radius: 0.85rem;
        overflow: hidden;
        border: 1px solid var(--border-color);
        cursor: pointer;
        transition: all 0.2s ease;

        &:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 16px rgba(0, 0, 0, 0.1);
        }

        .color-picker-hidden {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            opacity: 0;
            cursor: pointer;
            z-index: 2;
        }

        .color-bar {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: 1;
            transition: background-color 0.3s ease;
            
            &::after {
                content: 'Seleccionar color (Click)';
                position: absolute;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                color: white;
                font-size: 0.85rem;
                font-weight: 700;
                letter-spacing: 0.5px;
                text-shadow: 0 1px 4px rgba(0,0,0,0.5);
                pointer-events: none;
            }
        }
    }

    .hex-input {
        font-family: monospace;
        font-weight: 600;
        letter-spacing: 1px;
    }
}

/* Badges & Actions for Table */
.mono-badge {
    font-family: monospace;
    font-size: 0.85rem;
    color: var(--text-secondary);
    background: var(--bg-secondary);
    padding: 0.25rem 0.5rem;
    border-radius: 0.5rem;
    border: 1px solid var(--border-color);
}

.status-badge {
    display: inline-flex;
    align-items: center;
    padding: 0.25rem 0.75rem;
    border-radius: 99px;
    font-size: 0.75rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    
    &.bg-gray {
        background: var(--bg-secondary);
        color: var(--text-secondary);
        border: 1px solid var(--border-color);
    }
    
    &.bg-primary {
        background: rgba(var(--primary-rgb), 0.15);
        color: var(--primary);
        border: 1px solid rgba(var(--primary-rgb), 0.3);
    }
}

.action-btn-danger {
    background: transparent;
    color: var(--text-tertiary);
    border: none;
    padding: 0.5rem;
    border-radius: 0.5rem;
    cursor: pointer;
    transition: all 0.2s;
    
    &:hover {
        background: rgba(239, 68, 68, 0.1);
        color: #ef4444;
        transform: scale(1.05);
    }
}
</style>
