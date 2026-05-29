<template>
    <div class="word-preview-wrapper">
        <div v-if="loading" class="state">Procesando documento Word...</div>
        <div v-else-if="error" class="state error">{{ error }}</div>
        <div v-else class="word-content">
            <p v-for="(paragraph, idx) in paragraphs" :key="`p-${idx}`" class="word-paragraph">
                {{ paragraph }}
            </p>
            <p v-if="!paragraphs.length" class="word-empty">No se encontró texto legible en el documento.</p>
        </div>
    </div>
</template>

<script setup>
import { ref, watch } from 'vue';
import JSZip from 'jszip';

const props = defineProps({
    fileUrl: {
        type: String,
        default: '',
    },
});

const loading = ref(false);
const error = ref('');
const paragraphs = ref([]);
const MAX_WORD_PARAGRAPHS = 300;

const parseWord = async () => {
    if (!props.fileUrl) return;

    loading.value = true;
    error.value = '';
    paragraphs.value = [];

    try {
        const response = await fetch(props.fileUrl);
        if (!response.ok) {
            throw new Error('No se pudo leer el archivo Word para la vista previa.');
        }

        const arrayBuffer = await response.arrayBuffer();
        const zip = await JSZip.loadAsync(arrayBuffer);
        const xml = await zip.file('word/document.xml')?.async('string');

        if (!xml) {
            throw new Error('No se encontró contenido DOCX legible.');
        }

        const parser = new DOMParser();
        const doc = parser.parseFromString(xml, 'application/xml');

        paragraphs.value = Array.from(doc.getElementsByTagName('w:p'))
            .map((node) => Array.from(node.getElementsByTagName('w:t')).map((n) => n.textContent || '').join('').trim())
            .filter(Boolean)
            .slice(0, MAX_WORD_PARAGRAPHS);
    } catch (err) {
        error.value = err?.message || 'No se pudo procesar el archivo Word.';
    } finally {
        loading.value = false;
    }
};

watch(
    () => props.fileUrl,
    () => {
        parseWord();
    },
    { immediate: true }
);
</script>

<style scoped lang="scss">
.word-preview-wrapper {
    width: 100%;
    height: 100%;
}

.state {
    width: 100%;
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    color: var(--text-secondary);
}

.state.error {
    color: var(--danger, #ff7070);
}

.word-content {
    border: 1px solid var(--border-color);
    border-radius: 10px;
    background: var(--bg-primary);
    padding: 1rem;
    overflow: auto;
    height: 100%;
}

.word-paragraph {
    margin: 0 0 0.75rem;
    color: var(--text-primary);
    font-size: 0.9rem;
    line-height: 1.45;
    white-space: pre-wrap;
}

.word-empty {
    margin: 0;
    color: var(--text-muted);
    font-size: 0.9rem;
}
</style>
