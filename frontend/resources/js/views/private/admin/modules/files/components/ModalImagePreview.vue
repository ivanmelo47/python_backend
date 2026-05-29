<template>
    <div class="preview-overlay" @click.self="$emit('close')">
        <div class="preview-modal">
            <div class="preview-header">
                <button
                    v-if="showOpenInOffice && (previewType === 'pdf' || previewType === 'office' || previewType === 'excel' || previewType === 'word' || previewType === 'powerpoint')"
                    class="office-btn"
                    type="button"
                    @click="$emit('open-onlyoffice')"
                >
                    Abrir en OnlyOffice
                </button>
                <h3 class="preview-title">{{ title || 'Vista previa' }}</h3>
                <button class="close-btn" type="button" @click="$emit('close')" aria-label="Cerrar">
                    ×
                </button>
            </div>

            <div class="preview-body">
                <img
                    v-if="previewType === 'image' && imageUrl"
                    :src="imageUrl"
                    :alt="title || 'Vista previa de imagen'"
                    class="preview-image"
                >
                <iframe
                    v-else-if="previewType === 'pdf' && imageUrl"
                    :src="imageUrl"
                    title="Vista previa PDF"
                    class="preview-pdf"
                ></iframe>
                <OfficeStaticCard
                    v-else-if="previewType === 'office'"
                    :extension="officeMeta?.extension || 'DOC'"
                    :name="officeMeta?.name || title || 'Documento Office'"
                    :size="officeMeta?.size || 'Sin tamaño'"
                    :mime="officeMeta?.mime || 'application/octet-stream'"
                    :note="officeMeta?.note || ''"
                />

                <ExcelStaticPreview
                    v-else-if="previewType === 'excel' && imageUrl"
                    :fileUrl="imageUrl"
                />

                <WordStaticPreview
                    v-else-if="previewType === 'word' && imageUrl"
                    :fileUrl="imageUrl"
                />

                <PowerPointStaticPreview
                    v-else-if="previewType === 'powerpoint' && imageUrl"
                    :fileUrl="imageUrl"
                />
            </div>
        </div>
    </div>
</template>

<script setup>
import OfficeStaticCard from './file-preview/OfficeStaticCard.vue';
import ExcelStaticPreview from './file-preview/ExcelStaticPreview.vue';
import WordStaticPreview from './file-preview/WordStaticPreview.vue';
import PowerPointStaticPreview from './file-preview/PowerPointStaticPreview.vue';

defineEmits(['close', 'open-onlyoffice']);

const props = defineProps({
    imageUrl: {
        type: String,
        default: '',
    },
    title: {
        type: String,
        default: '',
    },
    previewType: {
        type: String,
        default: 'image',
    },
    showOpenInOffice: {
        type: Boolean,
        default: false,
    },
    officeMeta: {
        type: Object,
        default: null,
    },
});
</script>

<style scoped lang="scss">
.preview-overlay {
    position: fixed;
    inset: 0;
    z-index: 9999;
    background: rgba(0, 0, 0, 0.7);
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 1rem;
}

.preview-modal {
    width: 920px;
    height: 620px;
    max-width: 95vw;
    max-height: 92vh;
    background: var(--bg-secondary);
    border: 1px solid var(--border-color);
    border-radius: 14px;
    display: flex;
    flex-direction: column;
    overflow: hidden;
}

.preview-header {
    height: 56px;
    padding: 0 1rem;
    border-bottom: 1px solid var(--border-color);
    display: flex;
    align-items: center;
    justify-content: center;
    position: relative;
}

.preview-title {
    margin: 0;
    font-size: 1rem;
    color: var(--text-primary);
    text-align: center;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.close-btn {
    position: absolute;
    right: 1rem;
    width: 34px;
    height: 34px;
    border-radius: 8px;
    border: 1px solid var(--border-color);
    background: var(--bg-tertiary);
    color: var(--text-primary);
    font-size: 1.2rem;
    line-height: 1;
    cursor: pointer;
}

.office-btn {
    position: absolute;
    left: 1rem;
    height: 34px;
    padding: 0 0.75rem;
    border-radius: 8px;
    border: 1px solid var(--border-color);
    background: var(--bg-tertiary);
    color: var(--text-primary);
    font-size: 0.85rem;
    cursor: pointer;
}

.preview-body {
    padding: 1rem;
    display: flex;
    align-items: center;
    justify-content: center;
    width: 100%;
    height: calc(620px - 56px);
    min-height: 0;
}

.preview-image {
    width: 100%;
    height: 100%;
    max-width: 880px;
    max-height: 532px;
    object-fit: contain;
    border-radius: 10px;
    border: 1px solid var(--border-color);
}

.preview-pdf {
    width: 100%;
    height: 100%;
    max-width: 880px;
    max-height: 532px;
    border: 1px solid var(--border-color);
    border-radius: 10px;
    background: var(--bg-primary);
}

@media (max-width: 768px) {
    .preview-modal {
        width: 95vw;
        height: 82vh;
    }

    .preview-body {
        height: calc(82vh - 56px);
    }

    .preview-image,
    .preview-pdf {
        max-width: 100%;
        max-height: 100%;
    }
}
</style>
