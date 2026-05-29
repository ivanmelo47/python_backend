<template>
    <component :is="tag" class="info-block" :id="id">
        <header class="block-header">
            <p class="kicker">{{ kicker }}</p>
            <h2>{{ title }}</h2>
        </header>
        <slot />
    </component>
</template>

<script setup>
defineProps({
    kicker: {
        type: String,
        required: true
    },
    title: {
        type: String,
        required: true
    },
    tag: {
        type: String,
        default: 'article'
    },
    id: {
        type: String,
        default: undefined
    }
});
</script>

<style scoped>
.info-block {
    position: relative;
    border: 1px solid var(--border-color);
    border-radius: 20px;
    background: var(--bg-primary);
    backdrop-filter: blur(24px) saturate(180%);
    padding: 24px;
    transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    overflow: hidden;
    box-shadow: 
        0 12px 40px var(--shadow-color),
        inset 0 0 0 1px rgba(255, 255, 255, 0.05);

    &::before {
        content: '';
        position: absolute;
        inset: 0;
        background: radial-gradient(circle at top left, rgba(255, 255, 255, 0.05), transparent 60%);
        pointer-events: none;
    }
}

.info-block:hover {
    transform: translateY(-5px);
    border-color: var(--primary);
    background: var(--bg-primary);
    box-shadow: 
        0 20px 60px var(--shadow-color),
        inset 0 0 20px color-mix(in srgb, var(--primary), transparent 95%);
}

.block-header {
    margin-bottom: 20px;
}

.kicker {
    margin: 0;
    font-size: 0.68rem;
    font-weight: 800;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--primary);
    opacity: 0.9;
}

h2 {
    margin: 6px 0 0;
    font-size: 1.5rem;
    font-weight: 800;
    color: var(--text-primary);
    letter-spacing: -0.01em;
}

:deep(p) {
    color: var(--text-secondary);
    line-height: 1.6;
}

@media (max-width: 768px) {
    .info-block {
        padding: 20px;
    }
    
    h2 {
        font-size: 1.35rem;
    }
}
</style>
