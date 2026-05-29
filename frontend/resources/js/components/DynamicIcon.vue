<template>
    <img v-if="isDatabaseIcon && shouldRenderAsImage" :src="resolvedDatabaseIconFilePath" :class="customClass" :style="iconStyle" />
    <div v-else-if="isDatabaseIcon" class="dynamic-icon" :class="[customClass, dynamicModeClass]" :style="iconStyle" v-html="processedSvg"></div>
    <Icon v-else :name="name" :size="size" :color="color" :customClass="customClass" />
</template>

<script setup>
import { computed } from 'vue';
import Icon from './Icon.vue';
import { toAbsoluteBackendUrl } from '@/services/api/url';

const props = defineProps({
    // If name starts with 'db:', we look into the provided databaseData
    name: {
        type: String,
        required: true
    },
    databaseData: {
        type: Object,
        default: null // { svg_content, viewBox, icon_color_mode }
    },
    size: {
        type: [String, Number],
        default: 24
    },
    color: {
        type: String,
        default: 'currentColor'
    },
    customClass: {
        type: String,
        default: ''
    }
});

const isDatabaseIcon = computed(() => {
    return props.name.startsWith('db:') && props.databaseData;
});

const shouldRenderAsImage = computed(() => {
    if (!isDatabaseIcon.value) return false;
    const type = props.databaseData?.type;
    const hasFile = !!props.databaseData?.file_path;
    const hasSvgContent = !!props.databaseData?.svg_content;

    // Render as image for raster icons and file-based SVGs.
    return type === 'image' || (type === 'svg' && hasFile && !hasSvgContent);
});

const dynamicModeClass = computed(() => {
    if (!isDatabaseIcon.value) return '';
    const mode = props.databaseData?.color_mode || 'currentColor';
    return mode === 'original' ? 'dynamic-icon--original' : 'dynamic-icon--current';
});

const processedSvg = computed(() => {
    if (!isDatabaseIcon.value) return '';

    let svg = props.databaseData.svg_content;
    if (!svg) return '';

    const mode = props.databaseData.color_mode || 'currentColor';

    const shouldForceCurrentColor = (rawValue) => {
        if (!rawValue) return false;

        const normalized = String(rawValue).trim().toLowerCase();

        if (
            normalized === 'none' ||
            normalized === 'currentcolor' ||
            normalized === 'inherit' ||
            normalized === 'transparent' ||
            normalized.startsWith('url(')
        ) {
            return false;
        }

        return true;
    };

    if (mode === 'currentColor') {
        svg = svg.replace(/fill=("([^"]*)"|'([^']*)')/gi, (match, quotedValue, doubleValue, singleValue) => {
            const value = doubleValue ?? singleValue ?? '';
            if (!shouldForceCurrentColor(value)) {
                return match;
            }
            return 'fill="currentColor"';
        });

        svg = svg.replace(/stroke=("([^"]*)"|'([^']*)')/gi, (match, quotedValue, doubleValue, singleValue) => {
            const value = doubleValue ?? singleValue ?? '';
            if (!shouldForceCurrentColor(value)) {
                return match;
            }
            return 'stroke="currentColor"';
        });

        svg = svg.replace(/fill:\s*([^;"']+)/gi, (match, value) => {
            if (!shouldForceCurrentColor(value)) {
                return match;
            }
            return 'fill: currentColor';
        });

        svg = svg.replace(/stroke:\s*([^;"']+)/gi, (match, value) => {
            if (!shouldForceCurrentColor(value)) {
                return match;
            }
            return 'stroke: currentColor';
        });
    }

    // Keep original SVG geometry; forcing square width/height here can deform non-square icons.
    if (svg.includes('<svg')) {
        // Ensure preserveAspectRatio
        if (!/preserveAspectRatio\s*=\s*["'][^"']+["']/i.test(svg)) {
            svg = svg.replace('<svg', '<svg preserveAspectRatio="xMidYMid meet"');
        }

        // Inject viewBox if missing but provided in databaseData
        if (!/viewBox\s*=\s*["'][^"']+["']/i.test(svg) && props.databaseData.viewBox) {
            svg = svg.replace('<svg', `<svg viewBox="${props.databaseData.viewBox}"`);
        }

        // Force width and height to 100% so it fills the dynamic-icon container
        // We do this by removing existing width/height or overriding them
        svg = svg.replace(/<svg([^>]*)>/i, (match, attrs) => {
            let newAttrs = attrs
                .replace(/\s+(width|height)\s*=\s*["'][^"']+["']/gi, '') // Remove existing
                .trim();
            return `<svg ${newAttrs} width="100%" height="100%">`; // Set to 100%
        });
    }

    return svg;
});

const resolvedDatabaseIconFilePath = computed(() => {
    const rawPath = props.databaseData?.file_path || '';
    return toAbsoluteBackendUrl(rawPath);
});

const iconStyle = computed(() => {
    return {
        width: `${props.size}px`,
        height: `${props.size}px`,
        display: 'inline-flex',
        alignItems: 'center',
        justifyContent: 'center',
        verticalAlign: 'middle',
        color: props.color
    };
});
</script>

<style scoped>
.dynamic-icon {
    line-height: 0;
}

.dynamic-icon :deep(svg) {
    display: block;
    max-width: 100%;
    max-height: 100%;
}

.dynamic-icon.dynamic-icon--original {
    color: initial;
}

.dynamic-icon.dynamic-icon--original :deep(svg) {
    color: initial;
}
</style>
