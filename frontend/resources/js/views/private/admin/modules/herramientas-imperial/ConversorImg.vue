<template>
    <div class="image-converter-container">
        <!-- Header & Global Controls -->
        <header class="converter-header">
            <div class="header-top">
                <h2>
                    <Icon name="image" :size="20" />
                    <span>Conversor de Imágenes</span>
                </h2>
                <div class="header-actions">
                    <button class="btn-solid btn-success" :disabled="!canConvert" @click="processAll">
                        <Icon name="refresh" :size="18" :class="{ 'spinning': processing }" />
                        <span>Convertir Todo</span>
                    </button>
                </div>
            </div>

            <div class="controls-grid">
                <!-- Formato -->
                <div class="control-item">
                    <label>Formato de Salida</label>
                    <select v-model="config.outputFormat">
                        <option value="image/jpeg">Imagen JPG</option>
                        <option value="image/png">Imagen PNG</option>
                        <option value="image/webp">Imagen WebP</option>
                    </select>
                </div>

                <!-- Nivel de Compresión -->
                <div class="control-item">
                    <label>Compresión (Nv {{ config.level }})</label>
                    <input type="range" v-model.number="config.level" min="1" max="5" step="1" />
                    <div class="level-indicator">
                        <span>Original</span>
                        <span>Mínimo</span>
                    </div>
                </div>

                <!-- Prefijo/Sufijo (Opcional) -->
                <div class="control-item">
                    <label>Sufijo de archivo</label>
                    <input type="text" v-model="config.suffix" placeholder="Ej: _converted" />
                </div>
            </div>
        </header>

        <!-- Dropzone -->
        <div class="dropzone-area" :class="{ 'is-dragover': isDragging, 'compact': files.length > 0 }"
            @dragover.prevent="isDragging = true" @dragleave.prevent="isDragging = false" @drop.prevent="handleDrop"
            @click="triggerFileInput">
            <input type="file" ref="fileInput" multiple accept="image/*,.heic,.heif" class="hidden"
                @change="handleFileChange" />
            <div class="dropzone-icon">
                <Icon :name="files.length > 0 ? 'plus' : 'upload'" :size="files.length > 0 ? 24 : 48" />
            </div>
            <div class="dropzone-text">
                <h3>{{ files.length > 0 ? 'Añadir más imágenes' : 'Suelta tus imágenes aquí' }}</h3>
                <p v-if="files.length === 0">O haz clic para seleccionar archivos (JPG, PNG, WebP, etc.)</p>
            </div>
        </div>

        <!-- Files List -->
        <div class="files-list-section" v-if="files.length > 0">
            <div class="section-header">
                <h3>Cola de procesado ({{ files.length }})</h3>
                <div class="actions-row">
                    <button class="btn-solid" v-if="hasProcessed" @click="downloadZip">
                        <Icon name="download" :size="18" />
                        <span>Descargar ZIP</span>
                    </button>
                    <button class="btn-ghost" @click="clearFiles">
                        <Icon name="trash" :size="18" />
                        <span>Limpiar</span>
                    </button>
                </div>
            </div>

            <div class="files-grid-wrapper">
                <div class="files-grid">
                    <div v-for="(file, index) in files" :key="index" class="file-card">
                        <div class="file-preview">
                            <img v-if="file.preview" :src="file.preview" />
                            <div v-else class="placeholder-icon">
                                <Icon name="image" :size="24" />
                            </div>
                        </div>
                        <div class="file-info">
                            <div class="file-name" :title="file.name">{{ file.name }}</div>
                            <div class="file-meta">
                                <span>{{ formatSize(file.size) }}</span>
                                <span>{{ file.type.split('/')[1].toUpperCase() }}</span>
                            </div>
                        </div>
                        <div class="file-status">
                            <span class="status-badge" :class="file.status">
                                {{ statusLabels[file.status] }}
                            </span>
                        </div>

                        <div class="remove-btn" @click.stop="removeFile(index)">
                            <Icon name="plus" :size="12" style="transform: rotate(45deg)" />
                        </div>

                        <div v-if="file.status === 'processing' || file.status === 'done'" class="progress-bar"
                            :style="{ width: (file.status === 'done' ? 100 : file.progress) + '%' }"></div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Empty State -->
        <div class="empty-state" v-else>
            <div class="icon">
                <Icon name="image" :size="80" />
            </div>
            <p>Sube imágenes para comenzar la conversión</p>
        </div>
    </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import Icon from '@/components/Icon.vue';
import { useAlert } from '@/composables/useAlert';
import JSZip from 'jszip';

const alert = useAlert();
const fileInput = ref(null);
const isDragging = ref(false);
const processing = ref(false);

const config = ref({
    outputFormat: 'image/webp',
    level: 3,
    suffix: '_imperial'
});

const files = ref([]);

const statusLabels = {
    pending: 'Pendiente',
    processing: 'Procesando...',
    done: 'Listo',
    error: 'Error'
};

// Mappings for compression levels (1-5)
const levelMappings = {
    1: { quality: 1.0, scale: 1.0 },
    2: { quality: 0.8, scale: 0.9 },
    3: { quality: 0.6, scale: 0.75 },
    4: { quality: 0.4, scale: 0.5 },
    5: { quality: 0.1, scale: 0.25 }
};

const canConvert = computed(() => {
    return files.value.some(f => f.status === 'pending' || f.status === 'error') && !processing.value;
});

const hasProcessed = computed(() => {
    return files.value.some(f => f.status === 'done');
});

const triggerFileInput = () => fileInput.value.click();

const handleFileChange = (e) => {
    addFiles(e.target.files);
};

const handleDrop = (e) => {
    isDragging.value = false;
    addFiles(e.dataTransfer.files);
};

const addFiles = async (newFiles) => {
    for (const file of newFiles) {
        const isHeic = file.name.toLowerCase().endsWith('.heic') || file.name.toLowerCase().endsWith('.heif');

        if (!file.type.startsWith('image/') && !isHeic) continue;

        let processableFile = file;
        let originalName = file.name;

        // Convert HEIC to readable JPEG if necessary
        if (isHeic) {
            try {
                alert.toast.info('Procesando HEIC', `Convirtiendo ${file.name}...`);
                const heic2any = (await import('heic2any')).default || (await import('heic2any'));
                const convertedBlob = await heic2any({
                    blob: file,
                    toType: 'image/jpeg',
                    quality: 0.8
                });

                // heic2any can return an array or a single blob
                const blob = Array.isArray(convertedBlob) ? convertedBlob[0] : convertedBlob;
                processableFile = new File([blob], file.name.replace(/\.(heic|heif)$/i, '.jpg'), {
                    type: 'image/jpeg'
                });
            } catch (err) {
                console.error('HEIC conversion failed:', err);
                alert.toast.error('Error', `No se pudo convertir el archivo HEIC: ${file.name}`);
                continue;
            }
        }

        const reader = new FileReader();
        const fileObj = {
            file: processableFile,
            name: originalName,
            size: processableFile.size,
            type: processableFile.type,
            status: 'pending',
            progress: 0,
            preview: null,
            processedBlob: null
        };

        reader.onload = (e) => {
            fileObj.preview = e.target.result;
        };
        reader.readAsDataURL(processableFile);

        files.value.push(fileObj);
    }
};

const removeFile = (index) => {
    files.value.splice(index, 1);
};

const clearFiles = () => {
    files.value = [];
};

const formatSize = (bytes) => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};

const processAll = async () => {
    if (processing.value) return;
    processing.value = true;

    const toProcess = files.value.filter(f => f.status === 'pending' || f.status === 'error');

    for (const fileObj of toProcess) {
        try {
            fileObj.status = 'processing';
            fileObj.progress = 30;

            const processed = await convertImage(fileObj);

            fileObj.processedBlob = processed.blob;
            fileObj.status = 'done';
            fileObj.progress = 100;
        } catch (err) {
            console.error(err);
            fileObj.status = 'error';
        }
    }

    processing.value = false;
    alert.toast.success('Conversión Completa', 'Todas las imágenes han sido procesadas.');
};

const convertImage = (fileObj) => {
    return new Promise((resolve, reject) => {
        const { quality, scale } = levelMappings[config.value.level];
        const img = new Image();
        const url = URL.createObjectURL(fileObj.file);

        img.onload = () => {
            const canvas = document.createElement('canvas');
            const ctx = canvas.getContext('2d');

            const width = img.width * scale;
            const height = img.height * scale;

            canvas.width = width;
            canvas.height = height;

            ctx.drawImage(img, 0, 0, width, height);

            canvas.toBlob((blob) => {
                URL.revokeObjectURL(url);
                if (blob) {
                    resolve({ blob, width, height });
                } else {
                    reject(new Error('Canvas toBlob failed'));
                }
            }, config.value.outputFormat, quality);
        };

        img.onerror = () => {
            URL.revokeObjectURL(url);
            reject(new Error('Image load failed'));
        };

        img.src = url;
    });
};

const downloadZip = async () => {
    const zip = new JSZip();
    const processed = files.value.filter(f => f.status === 'done' && f.processedBlob);

    if (processed.length === 0) return;

    processed.forEach(f => {
        const extension = config.value.outputFormat.split('/')[1];
        const newName = f.name.substring(0, f.name.lastIndexOf('.')) + config.value.suffix + '.' + extension;
        zip.file(newName, f.processedBlob);
    });

    const content = await zip.generateAsync({ type: 'blob' });
    const url = URL.createObjectURL(content);
    const link = document.createElement('a');
    link.href = url;
    link.download = `imperial_images_${Date.now()}.zip`;
    link.click();
    URL.revokeObjectURL(url);
};
</script>

<style lang="scss">
// El estilo ya está definido en el archivo externalizado _conversor-img.scss
// Pero podemos agregar ajustes finos aquí si fuera necesario.
.hidden {
    display: none;
}
</style>