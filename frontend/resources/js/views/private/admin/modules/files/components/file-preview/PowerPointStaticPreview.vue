<template>
    <div class="ppt-preview-wrapper">
        <div v-if="loading" class="state">Procesando presentación...</div>
        <div v-else-if="error" class="state error">{{ error }}</div>
        <template v-else>
            <div class="slide-tabs">
                <button
                    v-for="(slide, idx) in slides"
                    :key="`slide-${idx}`"
                    type="button"
                    class="slide-tab"
                    :class="{ active: selectedSlideIndex === idx }"
                    @click="selectedSlideIndex = idx"
                >
                    {{ slide.name }}
                </button>
            </div>

            <div class="ppt-slide-card">
                <p v-for="(line, lineIdx) in currentSlideLines" :key="`line-${lineIdx}`" class="ppt-line">
                    {{ line }}
                </p>
                <p v-if="!currentSlideLines.length" class="ppt-empty">No se encontró texto legible en esta diapositiva.</p>
            </div>
        </template>
    </div>
</template>

<script setup>
import { computed, ref, watch } from 'vue';
import JSZip from 'jszip';

const props = defineProps({
    fileUrl: {
        type: String,
        default: '',
    },
});

const loading = ref(false);
const error = ref('');
const slides = ref([]);
const selectedSlideIndex = ref(0);
const MAX_PPT_LINES = 250;

const currentSlideLines = computed(() => slides.value[selectedSlideIndex.value]?.lines || []);

const parsePowerPoint = async () => {
    if (!props.fileUrl) return;

    loading.value = true;
    error.value = '';
    slides.value = [];
    selectedSlideIndex.value = 0;

    try {
        const response = await fetch(props.fileUrl);
        if (!response.ok) {
            throw new Error('No se pudo leer el archivo PowerPoint para la vista previa.');
        }

        const arrayBuffer = await response.arrayBuffer();
        const zip = await JSZip.loadAsync(arrayBuffer);
        const slideEntries = Object.keys(zip.files)
            .filter((name) => /^ppt\/slides\/slide\d+\.xml$/i.test(name))
            .sort((a, b) => {
                const na = Number((a.match(/slide(\d+)\.xml/i) || [])[1] || 0);
                const nb = Number((b.match(/slide(\d+)\.xml/i) || [])[1] || 0);
                return na - nb;
            });

        if (!slideEntries.length) {
            throw new Error('No se encontraron diapositivas legibles en el archivo.');
        }

        const parsedSlides = [];
        let totalLines = 0;

        for (const entry of slideEntries) {
            const xml = await zip.file(entry)?.async('string');
            if (!xml) continue;

            const parser = new DOMParser();
            const doc = parser.parseFromString(xml, 'application/xml');
            const lines = Array.from(doc.getElementsByTagName('a:t'))
                .map((n) => (n.textContent || '').trim())
                .filter(Boolean);

            const slideNumber = Number((entry.match(/slide(\d+)\.xml/i) || [])[1] || parsedSlides.length + 1);
            parsedSlides.push({
                name: `Diapositiva ${slideNumber}`,
                lines,
            });

            totalLines += lines.length;
            if (totalLines >= MAX_PPT_LINES) {
                break;
            }
        }

        slides.value = parsedSlides;
    } catch (err) {
        error.value = err?.message || 'No se pudo procesar el archivo PowerPoint.';
    } finally {
        loading.value = false;
    }
};

watch(
    () => props.fileUrl,
    () => {
        parsePowerPoint();
    },
    { immediate: true }
);
</script>

<style scoped lang="scss">
.ppt-preview-wrapper {
    width: 100%;
    height: 100%;
    display: flex;
    flex-direction: column;
    gap: 0.6rem;
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

.slide-tabs {
    display: flex;
    gap: 0.45rem;
    overflow-x: auto;
    padding-bottom: 0.25rem;
}

.slide-tab {
    height: 32px;
    border-radius: 8px;
    border: 1px solid var(--border-color);
    background: var(--bg-tertiary);
    color: var(--text-primary);
    padding: 0 0.75rem;
    font-size: 0.82rem;
    white-space: nowrap;
    cursor: pointer;
}

.slide-tab.active {
    border-color: var(--primary);
    color: var(--primary);
}

.ppt-slide-card {
    border: 1px solid var(--border-color);
    border-radius: 10px;
    background: var(--bg-primary);
    padding: 1rem;
    overflow: auto;
    height: 100%;
}

.ppt-line {
    margin: 0 0 0.75rem;
    color: var(--text-primary);
    font-size: 0.9rem;
    line-height: 1.45;
    white-space: pre-wrap;
}

.ppt-empty {
    margin: 0;
    color: var(--text-muted);
    font-size: 0.9rem;
}
</style>
