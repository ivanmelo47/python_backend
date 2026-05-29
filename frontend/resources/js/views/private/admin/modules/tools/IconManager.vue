<template>
    <div class="icon-manager-container">
        <Table title="Gestión de Iconos" :columns="columns" :rows="icons" :loading="loading" :pagination="pagination"
            :searchQuery="searchQuery" @update:searchQuery="searchQuery = $event" searchPlaceholder="Buscar icono..."
            paginationMode="server" @request-data="fetchIcons" @row-click="viewIcon" cardTitleTemplate="{name}">
            <!-- Header Actions -->
            <template #header-actions>
                <div style="display: flex; gap: 12px; align-items: center;">
                    <div class="search-input-wrapper" style="width: auto; min-width: 150px;">
                        <select v-model="filterCategory"
                            style="padding-left: 10px; border: 1px solid var(--border-color); border-radius: 6px; background: var(--bg-secondary); color: var(--text-primary); height: 38px; outline: none;">
                            <option value="">Todas las Categorías</option>
                            <option value="dashboard">Dashboard</option>
                            <option value="login">Login</option>
                            <option value="custom">Custom</option>
                            <option value="social">Social</option>
                            <option value="portafolio">Portafolio</option>
                        </select>
                    </div>
                    <button type="button" class="outline-action-btn" :style="{ '--btn-size': '46px' }"
                        @click="openImportExportModal" title="Importar / Exportar">
                        <Icon name="excel" :size="30" />
                    </button>
                    <button type="button" class="outline-action-btn" :style="{ '--btn-size': '46px' }"
                        @click="openCreateModal" title="Nuevo Icono">
                        <Icon name="plus" :size="30" />
                    </button>
                </div>
            </template>

            <!-- Custom Cell: Icon Preview -->
            <template #cell-preview="{ row }">
                <div class="icon-preview-cell">
                    <img v-if="row.type === 'image'" :src="row.file_path" class="icon-preview-image" />
                    <img v-else-if="row.type === 'svg' && row.storage_mode === 'file' && row.file_path"
                        :src="row.file_path" class="icon-preview-image" />
                    <div v-else v-html="row.svg_content"></div>
                </div>
            </template>

            <!-- Custom Cell: Category-->
            <template #cell-category="{ row }">
                <span v-if="row.category" class="badge" :style="{
                    padding: '4px 8px',
                    borderRadius: '4px',
                    color: 'white',
                    fontWeight: 'bold',
                    fontSize: '0.8em',
                    backgroundColor: getCategoryColor(row.category)
                }">
                    {{ row.category }}
                </span>
                <span v-else class="text-muted">Sin categoría</span>
            </template>

            <!-- Custom Cell: Status -->
            <template #cell-is_active="{ row }">
                <div v-if="['master', 'admin'].includes(currentUser?.role?.name)">
                    <label class="switch" @click.stop>
                        <input type="checkbox" :checked="row.is_active" @change="handleToggleStatus(row)">
                        <span class="slider"></span>
                    </label>
                </div>
                <div v-else>
                    <span v-if="row.is_active" class="badge success">Activo</span>
                    <span v-else class="badge danger">Inactivo</span>
                </div>
            </template>

            <!-- Actions Dropdown -->
            <template #cell-actions="{ row }">
                <button @click.stop="viewIcon(row)" class="dropdown-item">
                    <Icon name="eye" :size="16" />
                    <span>Ver Detalles</span>
                </button>
                <button @click.stop="editIcon(row)" class="dropdown-item">
                    <Icon name="edit" :size="16" />
                    <span>Editar</span>
                </button>
                <button @click.stop="confirmDelete(row)" class="dropdown-item delete">
                    <Icon name="trash" :size="16" />
                    <span>Eliminar</span>
                </button>
            </template>
        </Table>

        <!-- Modal Form for Create/Edit -->
        <ModalForm :isVisible="showFormModal" :title="editingIcon ? 'Editar Icono' : 'Nuevo Icono'"
            :loading="formLoading" submitLabel="Guardar" size="lg" :columns="2" @close="closeFormModal"
            @submit="submitForm">
            <template #header-icon>
                <Icon name="image" :size="18" />
            </template>

            <!-- Name -->
            <ModalField label="Nombre del Icono" :required="true" :span="1" :error="errors.name?.[0]">
                <input v-model="formData.name" type="text" placeholder="Ej: user-custom" />
            </ModalField>

            <!-- Category -->
            <ModalField label="Categoría" :span="1" :error="errors.category?.[0]">
                <select v-model="formData.category">
                    <option value="">Sin categoría</option>
                    <option value="dashboard">Dashboard</option>
                    <option value="login">Login</option>
                    <option value="custom">Custom</option>
                    <option value="social">Social</option>
                    <option value="portafolio">Portafolio</option>
                </select>
            </ModalField>

            <!-- Input Method Toggle -->
            <ModalField label="Tipo de Icono" :required="true" :span="2">
                <div class="input-method-toggle">
                    <button type="button" class="toggle-btn" :class="{ active: inputMethod === 'file' }"
                        @click="inputMethod = 'file'">
                        <Icon name="upload" :size="16" />
                        SVG (Archivo)
                    </button>
                    <button type="button" class="toggle-btn" :class="{ active: inputMethod === 'paste' }"
                        @click="inputMethod = 'paste'">
                        <Icon name="code" :size="16" />
                        SVG (Código)
                    </button>
                    <button type="button" class="toggle-btn" :class="{ active: inputMethod === 'image' }"
                        @click="inputMethod = 'image'">
                        <Icon name="image" :size="16" />
                        Imagen (JPG/PNG)
                    </button>
                </div>
            </ModalField>

            <!-- File Upload -->
            <ModalField v-if="inputMethod === 'file'" label="Archivo SVG" :span="2" :required="!editingIcon"
                :error="errors.svg_file?.[0]">
                <div class="file-upload-wrapper">
                    <input ref="fileInput" type="file" accept=".svg" @change="handleFileUpload" id="svg-file-input"
                        class="file-input-hidden" />
                    <label for="svg-file-input" class="file-upload-label">
                        <div class="file-upload-content">
                            <Icon name="upload" :size="24" />
                            <span class="file-upload-text">
                                {{ selectedFileName || 'Arrastra un archivo SVG o haz click para seleccionar' }}
                            </span>
                            <span class="file-upload-hint">Solo archivos .svg</span>
                        </div>
                    </label>
                </div>
            </ModalField>

            <!-- Color Mode -->
            <ModalField v-if="inputMethod !== 'image'" label="Modo de Color SVG" :span="2">
                <select v-model="formData.color_mode" :disabled="formData.storage_mode === 'file'">
                    <option value="currentColor">Adaptar al Tema (Monocromático)</option>
                    <option value="original">Preservar Colores Originales</option>
                </select>
                <small class="text-muted d-block mt-1">
                    "Adaptar al Tema" forzará el icono a cambiar de color según el modo claro/oscuro (útil para iconos
                    de menú).
                    "Preservar" mantendrá los colores originales del logo/icono multicromático.
                </small>
            </ModalField>

            <ModalField v-if="inputMethod !== 'image'" label="Guardar SVG En" :span="2">
                <select v-model="formData.storage_mode" @change="handleStorageModeChange">
                    <option value="database">Base de datos (svg_content)</option>
                    <option value="file">Archivo .svg (storage/icons/svg)</option>
                </select>
                <small class="text-muted d-block mt-1">
                    En modo "Archivo" se preserva el SVG original y el color se mantiene en "Original".
                </small>
            </ModalField>

            <!-- Paste Code -->
            <ModalField v-if="inputMethod === 'paste'" label="Código SVG" :span="2" :required="!editingIcon"
                :error="errors.svg_content?.[0]">
                <textarea v-model="formData.svg_content" rows="6" placeholder="<svg>...</svg>"
                    @input="updatePreview"></textarea>
            </ModalField>

            <!-- Image Upload -->
            <ModalField v-if="inputMethod === 'image'" label="Imagen para el Icono" :span="2" :required="!editingIcon">
                <div class="file-upload-wrapper" style="margin-bottom: 16px;">
                    <input ref="imageInput" type="file" accept="image/jpeg, image/png, image/webp"
                        @change="handleImageUpload" id="image-file-input" class="file-input-hidden" />
                    <label for="image-file-input" class="file-upload-label">
                        <div class="file-upload-content">
                            <Icon name="image" :size="24" />
                            <span class="file-upload-text">
                                {{ selectedImageName || 'Arrastra una imagen o haz click para seleccionar (JPG/PNG)' }}
                            </span>
                        </div>
                    </label>
                </div>

                <div v-if="imageSrc" class="cropper-wrapper">
                    <cropper ref="cropperRef" class="cropper" :src="imageSrc" :stencil-props="{
                        aspectRatio: 1
                    }" />
                </div>
                <div v-else-if="editingIcon && editingIcon.type === 'image'"
                    class="text-center text-muted p-4 border border-dashed rounded-lg">
                    <p>El icono actual es una imagen.</p>
                    <p>Sube una nueva foto para sobreescribirla.</p>
                </div>
            </ModalField>

            <!-- Live Preview -->
            <ModalField label="Vista Previa" :span="2">
                <div class="icon-preview-box">
                    <div v-if="previewSvg" class="icon-preview-container">
                        <div class="icon-preview-large" v-html="previewSvg"
                            :style="{ transform: `scale(${zoomLevel})` }"></div>
                    </div>
                    <div v-else class="empty-preview">
                        <Icon name="image" :size="48" />
                        <span>No hay vista previa</span>
                    </div>

                    <!-- Zoom Controls -->
                    <div v-if="previewSvg" class="zoom-controls">
                        <button type="button" class="zoom-btn" @click="zoomOut" title="Reducir">
                            <Icon name="minus" :size="14" />
                        </button>
                        <span class="zoom-level">{{ Math.round(zoomLevel * 100) }}%</span>
                        <button type="button" class="zoom-btn" @click="zoomIn" title="Aumentar">
                            <Icon name="plus" :size="14" />
                        </button>
                    </div>
                </div>
            </ModalField>

            <!-- Color Customization -->
            <ModalField v-if="detectedColors.length > 0" label="Personalizar Colores" :span="2">
                <div class="color-customization-section">
                    <p class="text-xs text-muted mb-2">Se detectaron los siguientes colores en el SVG. Haz clic para
                        cambiarlos.
                    </p>
                    <div class="colors-list">
                        <div v-for="(color, index) in detectedColors" :key="index" class="color-row">
                            <!-- Original/Current Color Indicator -->
                            <div class="color-indicator" :style="{ backgroundColor: color.current }"
                                :title="color.original">
                            </div>

                            <!-- Color Value -->
                            <div class="color-info">
                                {{ color.current.toUpperCase() }}
                            </div>

                            <!-- Actions -->
                            <div class="color-actions">
                                <!-- Native Picker -->
                                <div class="color-picker-wrapper" title="Elegir color personalizado">
                                    <Icon name="palette" :size="18" class="picker-icon" />
                                    <input type="color" :value="color.current"
                                        @input="updateColor(index, $event.target.value)" class="color-picker-input" />
                                </div>

                                <!-- Presets -->
                                <div class="preset-swatches">
                                    <button v-for="preset in presetColors" :key="preset.value" type="button"
                                        class="preset-swatch" :style="{ backgroundColor: preset.value }"
                                        :title="preset.name" @click="updateColor(index, preset.value)"></button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </ModalField>
        </ModalForm>

        <!-- Modal Import/Export -->
        <ModalForm :isVisible="showImportExportModal" title="Importar / Exportar Iconos" :loading="importExportLoading"
            submitLabel="Cerrar" :hideCancel="true" size="md" :columns="1" @close="closeImportExportModal"
            @submit="closeImportExportModal">
            <template #header-icon>
                <Icon name="file-text" :size="18" />
            </template>

            <ModalField :span="1">
                <div class="action-cards">
                    <!-- Export Option -->
                    <div class="action-card" @click="!importExportLoading ? handleExport() : null">
                        <div class="action-icon-wrapper export-icon">
                            <Icon name="download" :size="28" />
                        </div>
                        <div class="action-title">Exportar Sistema</div>
                        <div class="action-desc">Descarga una copia de seguridad en formato Excel con todos los iconos
                            actuales.
                        </div>
                        <button class="btn-solid w-100" :disabled="importExportLoading" @click.stop="handleExport">
                            <span v-if="exporting">Generando...</span>
                            <span v-else>Generar Excel</span>
                        </button>
                    </div>

                    <!-- Import Option -->
                    <div class="action-card" @click="!importExportLoading ? triggerImportFile() : null">
                        <div class="action-icon-wrapper import-icon">
                            <Icon name="upload" :size="28" />
                        </div>
                        <div class="action-title">Importar Excel</div>
                        <div class="action-desc">Carga tu plantilla descargada previamente. Los duplicados serán
                            renombrados.
                        </div>

                        <input type="file" accept=".xlsx, .xls, .csv" @change="handleImportFileSelect"
                            ref="importFileInput" style="display: none;" />

                        <button class="btn-solid btn-transparent w-100" :disabled="importExportLoading"
                            @click.stop="triggerImportFile">
                            <span v-if="importing">Subiendo...</span>
                            <span v-else>Elegir Archivo</span>
                        </button>
                    </div>
                </div>

                <div v-if="importSummary" class="mt-3 p-3 text-center"
                    style="background: rgba(16, 185, 129, 0.1); border-radius: 8px;">
                    <Icon name="check-circle" :size="24" class="text-success mb-2" />
                    <h6>Importación Exitosa</h6>
                    <p class="mb-1 text-sm">Se importaron <strong>{{ importSummary.imported }}</strong> iconos nuevos.
                    </p>
                    <p class="mb-0 text-sm" v-if="importSummary.duplicated_renamed > 0">
                        <strong>{{ importSummary.duplicated_renamed }}</strong> iconos fueron renombrados por
                        duplicidad.
                    </p>
                </div>
            </ModalField>
        </ModalForm>

        <!-- Modal Information for View -->
        <ModalInformation 
            v-if="selectedIcon"
            :is-open="showInfoModal" 
            :title="selectedIcon.name || 'Detalles del Icono'" 
            icon="image"
            :data="selectedIcon"
            :columns="iconColumns"
            show-edit-button
            @edit="showInfoModal = false; openEditModal(selectedIcon)"
            @close="closeInfoModal"
        >
            <template #top-header>
                <div class="icon-display-hero">
                    <div class="icon-preview-large-wrapper">
                        <div v-if="selectedIcon.type === 'svg'" class="icon-svg-render" v-html="selectedIcon.svg_content"></div>
                        <img v-else-if="selectedIcon.type === 'image'" :src="selectedIcon.file_path" alt="Icon preview" />
                    </div>
                    <div class="icon-identity-info">
                        <h4>{{ selectedIcon.name }}</h4>
                        <span v-if="selectedIcon.category" class="badge" :style="{ backgroundColor: getCategoryColor(selectedIcon.category) }">
                            {{ selectedIcon.category }}
                        </span>
                    </div>
                </div>
            </template>

            <template #value-creator>
                {{ selectedIcon.creator?.name || 'Sistema' }}
            </template>

            <template #value-svg_content>
                <pre class="code-block-minimal">{{ selectedIcon.svg_content }}</pre>
            </template>
        </ModalInformation>
    </div>
</template>

<script setup>
import { ref, onMounted, watch, nextTick } from 'vue';
import { useAlert } from '@/composables/useAlert';
import Table from '@/views/private/admin/components/Table.vue';
import ModalForm from '@/views/private/admin/components/ModalForm.vue';
import ModalField from '@/views/private/admin/components/ModalField.vue';
import ModalInformation from '@/views/private/admin/components/ModalInformation.vue';
import Icon from '@/components/Icon.vue';
import iconsApi from '@/services/api/endpoints/icons';
import { useAuth } from '@/composables/useAuth';
import { Cropper } from 'vue-advanced-cropper';
import 'vue-advanced-cropper/dist/style.css';

// Auth & Alerts
const alert = useAlert();
const { user: currentUser } = useAuth();

// Table Data
const icons = ref([]);
const loading = ref(false);
const pagination = ref(null);
const searchQuery = ref('');
const filterCategory = ref('');

const columns = [
    { key: 'actions', label: 'ACCIONES', headerClass: 'compact', cellClass: 'compact' },
    { key: 'preview', label: 'Icono', cellClass: 'text-center' },
    { key: 'name', label: 'Nombre' },
    { key: 'category', label: 'Categoría' },
    { key: 'is_active', label: 'ESTATUS', cellClass: 'text-center' },
    { key: 'creator', label: 'Creador' }
];

// Form Modal
const showFormModal = ref(false);
const formLoading = ref(false);
const editingIcon = ref(null);
const formData = ref({
    name: '',
    category: '',
    svg_content: '',
    svg_file: null,
    color_mode: 'currentColor',
    storage_mode: 'database'
});
const errors = ref({});
const inputMethod = ref('file');
const fileInput = ref(null);
const previewSvg = ref('');
const zoomLevel = ref(1);
const selectedFileName = ref('');

// Intelligent Color Editing
const originalSvgContent = ref(''); // Store original for non-destructive editing
const detectedColors = ref([]);

// Image Cropper Support
const imageSrc = ref(null);
const selectedImageName = ref('');
const imageInput = ref(null);
const cropperRef = ref(null);

// Import/Export Modal
const showImportExportModal = ref(false);
const importExportLoading = ref(false);
const exporting = ref(false);
const importing = ref(false);
const importFileInput = ref(null);
const importSummary = ref(null);

const presetColors = [
    { name: 'Primary', value: '#42b983' },
    { name: 'Secondary', value: '#35495e' },
    { name: 'Accent', value: '#667eea' },
    { name: 'Success', value: '#10b981' },
    { name: 'Warning', value: '#f59e0b' },
    { name: 'Error', value: '#ef4444' },
    { name: 'White', value: '#ffffff' },
    { name: 'Black', value: '#000000' },
    { name: 'Gray', value: '#6b7280' }
];

// Debounce helper
const debounce = (fn, delay) => {
    let timeoutId;
    return (...args) => {
        clearTimeout(timeoutId);
        timeoutId = setTimeout(() => fn(...args), delay);
    };
};


// Info Modal
const showInfoModal = ref(false);
const selectedIcon = ref(null);

const iconColumns = [
    { key: 'name', label: 'Nombre' },
    { key: 'category', label: 'Categoría' },
    { key: 'viewBox', label: 'ViewBox' },
    { key: 'creator', label: 'Creado por' },
    { key: 'svg_content', label: 'Código SVG', fullWidth: true, isNote: true }
];

// Fetch Icons
const fetchIcons = async (params = {}) => {
    loading.value = true;
    try {
        const finalParams = { ...params };
        if (filterCategory.value) {
            finalParams.category = filterCategory.value;
        }

        const response = await iconsApi.getAll(finalParams);
        if (response.data.success) {
            if (params.per_page === -1) {
                icons.value = response.data.data.map(processIcon);
            } else {
                const paginatedData = response.data.data;
                icons.value = (paginatedData.data || []).map(processIcon);

                // Laravel Resources wrap pagination in 'meta'
                const meta = paginatedData.meta || paginatedData;

                pagination.value = {
                    current_page: meta.current_page,
                    last_page: meta.last_page,
                    from: meta.from,
                    to: meta.to,
                    total: meta.total
                };
            }
        }
    } catch (error) {
        alert.toast.error('Error', 'Error al cargar los iconos', 3000);
        console.error(error);
    } finally {
        loading.value = false;
    }
};

watch(filterCategory, () => {
    fetchIcons({ page: 1, per_page: 10, search: searchQuery.value });
});

// Process icon for table display
const processIcon = (icon) => ({
    id: icon.uuid,
    ...icon,
    creator: icon.creator?.name || 'Sistema',
    _original: icon  // Keep original data for modal
});

// Open Create Modal
const openCreateModal = () => {
    editingIcon.value = null;
    resetForm();
    showFormModal.value = true;
};

// Update Preview
const updatePreview = () => {
    // Manual edit resets the "Original" source to the new content
    originalSvgContent.value = formData.value.svg_content;
    previewSvg.value = formData.value.svg_content;
    extractColors(formData.value.svg_content);
};

// Reset Form
const resetForm = () => {
    formData.value = {
        name: '',
        category: '',
        svg_content: '',
        svg_file: null,
        color_mode: 'currentColor',
        storage_mode: 'database'
    };
    errors.value = {};
    previewSvg.value = '';
    selectedFileName.value = '';
    inputMethod.value = 'file';
    originalSvgContent.value = '';
    detectedColors.value = [];
    zoomLevel.value = 1;
    imageSrc.value = null;
    selectedImageName.value = '';
    if (fileInput.value) {
        fileInput.value.value = '';
    }
    if (imageInput.value) {
        imageInput.value.value = '';
    }
};

// Zoom Controls
const zoomIn = () => {
    if (zoomLevel.value < 5) zoomLevel.value += 0.5;
};

const zoomOut = () => {
    if (zoomLevel.value > 0.5) zoomLevel.value -= 0.5;
};

// Handle File Upload
const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    formData.value.svg_file = file;
    selectedFileName.value = file.name;

    // Read file for preview
    const reader = new FileReader();
    reader.onload = (e) => {
        const content = e.target.result;
        originalSvgContent.value = content;
        formData.value.svg_content = content;
        previewSvg.value = content;
        extractColors(content);
    };
    reader.readAsText(file);
};

const handleStorageModeChange = () => {
    if (formData.value.storage_mode === 'file') {
        formData.value.color_mode = 'original';
    }
};

// Handle Image Upload for Cropper
const handleImageUpload = (event) => {
    const file = event.target.files[0];
    if (!file) return;

    selectedImageName.value = file.name;

    // Revoke previous blob if any
    if (imageSrc.value) {
        URL.revokeObjectURL(imageSrc.value);
    }

    // Create new object URL
    imageSrc.value = URL.createObjectURL(file);
};

// Edit Icon
const editIcon = (icon) => {
    editingIcon.value = icon;
    formData.value = {
        name: icon.name,
        category: icon.category || '',
        svg_content: icon.svg_content || '',
        svg_file: null,
        color_mode: icon.color_mode || 'currentColor',
        storage_mode: icon.storage_mode || (icon.type === 'svg' && icon.file_path ? 'file' : 'database')
    };

    if (icon.type === 'image') {
        inputMethod.value = 'image';
        imageSrc.value = null; // Don't preload image into cropper unless changing
        selectedImageName.value = '';
    } else {
        inputMethod.value = 'paste'; // Default to paste for SVG editing
        originalSvgContent.value = icon.svg_content;
        previewSvg.value = icon.svg_content;
        extractColors(icon.svg_content);
    }

    selectedFileName.value = '';
    errors.value = {};
    showFormModal.value = true;
};

// Close Form Modal
const closeFormModal = () => {
    showFormModal.value = false;
    resetForm();
};

// Extract unique colors from SVG
const extractColors = (svgContent) => {
    if (!svgContent) {
        detectedColors.value = [];
        return;
    }

    const hexRegex = /#([a-fA-F0-9]{6}|[a-fA-F0-9]{3})\b/g;
    const rgbRegex = /rgba?\([\d\s,.]+\)/g;

    const colors = new Set();
    let match;

    while ((match = hexRegex.exec(svgContent)) !== null) {
        colors.add(match[0]);
    }
    while ((match = rgbRegex.exec(svgContent)) !== null) {
        colors.add(match[match.length - 1]);
    }

    const uniqueColors = Array.from(colors);

    detectedColors.value = uniqueColors.map(c => ({
        original: c,
        current: c
    }));
};

// Regenerate SVG from Original + Mappings
const regenerateSvg = () => {
    let content = originalSvgContent.value;

    detectedColors.value.forEach(colorObj => {
        if (colorObj.current !== colorObj.original) {
            const escapedOriginal = colorObj.original.replace(/[-\/\\^$*+?.()|[\]{}]/g, '\\$&');
            const regex = new RegExp(escapedOriginal, 'g');
            content = content.replace(regex, colorObj.current);
        }
    });

    formData.value.svg_content = content;
    previewSvg.value = content;
};

// Update Color
const updateColor = (index, newColor) => {
    const colorObj = detectedColors.value[index];
    if (!colorObj) return;

    // Update State
    colorObj.current = newColor;

    // Regenerate
    regenerateSvg();
};


// Submit Form
const submitForm = async () => {
    formLoading.value = true;
    errors.value = {};

    try {
        const payload = {
            name: formData.value.name,
            category: formData.value.category || null,
            type: inputMethod.value === 'image' ? 'image' : 'svg',
            color_mode: inputMethod.value === 'image' ? null : formData.value.color_mode,
            storage_mode: inputMethod.value === 'image' ? null : formData.value.storage_mode
        };

        if (inputMethod.value === 'file') {
            if (formData.value.svg_content) {
                payload.svg_content = formData.value.svg_content;
            } else if (formData.value.svg_file) {
                payload.svg_file = formData.value.svg_file;
            }
        } else if (inputMethod.value === 'paste') {
            payload.svg_content = formData.value.svg_content;
        } else if (inputMethod.value === 'image') {
            if (cropperRef.value && imageSrc.value) {
                const { canvas } = cropperRef.value.getResult();
                if (canvas) {
                    const blob = await new Promise(resolve => canvas.toBlob(resolve, 'image/webp', 0.9));
                    payload.image_file = blob;
                }
            } else if (!editingIcon.value) {
                // Return explicitly if required image is missing on create
                alert.toast.error('Atención', 'Debes subir y recortar una imagen', 3000);
                formLoading.value = false;
                return;
            }
        }

        if (editingIcon.value) {
            await iconsApi.update(editingIcon.value.uuid, payload);
            alert.toast.success('Éxito', 'Icono actualizado exitosamente', 3000);
        } else {
            await iconsApi.create(payload);
            alert.toast.success('Éxito', 'Icono creado exitosamente', 3000);
        }

        closeFormModal();
        fetchIcons({ page: pagination.value?.current_page || 1, per_page: 10, search: searchQuery.value });
    } catch (error) {
        if (error.response?.data?.errors) {
            errors.value = error.response.data.errors;
        }
        alert.toast.error('Error', error.response?.data?.message || 'Error al guardar el icono', 3000);
    } finally {
        formLoading.value = false;
    }
};

// View Icon
const viewIcon = (icon) => {
    // Use original icon data if available (has full creator object)
    selectedIcon.value = icon._original || icon;
    showInfoModal.value = true;
};

// Close Info Modal
const closeInfoModal = () => {
    showInfoModal.value = false;
    selectedIcon.value = null;
};

// Get color for category badge
const getCategoryColor = (category) => {
    const colors = {
        'dashboard': '#007bff',  // Blue
        'login': '#28a745',      // Green
        'custom': '#6f42c1',     // Purple
        'social': '#fd7e14',     // Orange
        'portafolio': '#17a2b8', // Cyan
        'default': '#6c757d'     // Gray
    };
    return colors[category.toLowerCase()] || colors.default;
};

// Confirm Delete
const confirmDelete = async (icon) => {
    if (!confirm(`¿Estás seguro de eliminar el icono "${icon.name}"?`)) return;

    try {
        await iconsApi.delete(icon.uuid);
        alert.toast.success('Éxito', 'Icono eliminado exitosamente', 3000);
        fetchIcons({ page: pagination.value?.current_page || 1, per_page: 10, search: searchQuery.value });
    } catch (error) {
        alert.toast.error('Error', error.response?.data?.message || 'Error al eliminar el icono', 3000);
    }
};

// Toggle Status
const handleToggleStatus = async (row) => {
    const originalStatus = row.is_active;
    const newStatus = !originalStatus;
    const actionText = newStatus ? 'activar' : 'desactivar';

    // 1. Confirm action
    const confirmed = await alert.fire({
        title: `¿${actionText.charAt(0).toUpperCase() + actionText.slice(1)} icono?`,
        text: `¿Estás seguro de que deseas ${actionText} el icono "${row.name}"?`,
        type: 'warning',
        showCancel: true,
        confirmText: `Sí, ${actionText}`,
        cancelText: 'Cancelar'
    });

    if (!confirmed) {
        // Force revert UI
        row.is_active = !originalStatus;
        setTimeout(() => {
            row.is_active = originalStatus;
        }, 0);
        return;
    }

    // 2. Optimistic Update (UI)
    row.is_active = newStatus;

    try {
        await iconsApi.toggleStatus(row.uuid);
        alert.toast.success('Estado Actualizado', `El icono ha sido ${newStatus ? 'activado' : 'desactivado'}.`, 3000);
    } catch (error) {
        // Revert on error
        row.is_active = originalStatus;
        console.error('Error toggling status:', error);
        alert.toast.error('Error', 'No se pudo cambiar el estado del icono', 3000);
    }
};

// Import/Export Logic
const openImportExportModal = () => {
    importSummary.value = null;
    showImportExportModal.value = true;
};

const closeImportExportModal = () => {
    showImportExportModal.value = false;
    importSummary.value = null;
    if (importFileInput.value) importFileInput.value.value = '';
};

const handleExport = async () => {
    exporting.value = true;
    importExportLoading.value = true;
    try {
        const response = await iconsApi.export();
        // Create an anchor element and trigger download
        const url = window.URL.createObjectURL(new Blob([response.data]));
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', 'iconos_exportados.xlsx');
        document.body.appendChild(link);
        link.click();
        link.remove();
        alert.toast.success('Éxito', 'Iconos exportados exitosamente', 3000);
    } catch (error) {
        console.error('Error exporting icons:', error);
        alert.toast.error('Error', 'Ocurrió un error al exportar', 3000);
    } finally {
        exporting.value = false;
        importExportLoading.value = false;
    }
};

const triggerImportFile = () => {
    if (importFileInput.value) importFileInput.value.click();
};

const handleImportFileSelect = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    importing.value = true;
    importExportLoading.value = true;
    importSummary.value = null;

    try {
        const response = await iconsApi.import(file);
        if (response.data.success) {
            importSummary.value = response.data.summary;
            fetchIcons({ page: pagination.value?.current_page || 1, per_page: 10, search: searchQuery.value });
        }
    } catch (error) {
        console.error('Error importing icons:', error);
        alert.toast.error('Error', error.response?.data?.message || 'Error al importar los iconos', 3000);
    } finally {
        importing.value = false;
        importExportLoading.value = false;
        // Reset file input so we can select same file again if needed
        event.target.value = '';
    }
};

onMounted(() => {
    // Initial fetch handled by Table component via @request-data
});
</script>

<style scoped>
.outline-action-btn {
    background: transparent;
    border: 2px solid var(--primary-color, #42b983);
    color: var(--primary-color, #42b983);
    width: var(--btn-size, 38px);
    height: var(--btn-size, 38px);
    border-radius: 6px;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    transition: all 0.3s ease;
}

.outline-action-btn:hover {
    background: rgba(66, 185, 131, 0.08);
    /* Suave fondo al hacer hover */
    animation: blink-border 1.2s infinite;
    /* Animación de parpadeo */
}

@keyframes blink-border {

    0%,
    100% {
        border-color: var(--primary-color, #42b983);
        transform: scale(1);
    }

    50% {
        border-color: rgba(66, 185, 131, 0.2);
        transform: scale(1.05);
    }
}
</style>
