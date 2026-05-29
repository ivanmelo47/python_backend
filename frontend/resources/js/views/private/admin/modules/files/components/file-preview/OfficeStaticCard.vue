<template>
    <div class="office-preview-card">
        <div class="office-preview-ext">{{ extension || 'DOC' }}</div>
        <h4 class="office-preview-name">{{ name || 'Documento Office' }}</h4>
        <p class="office-preview-info">
            {{ size || 'Sin tamaño' }}
            <span class="separator-dot">•</span>
            {{ mime || 'application/octet-stream' }}
        </p>
        <p class="office-preview-note">
            {{ note || 'Vista rápida estática. Para edición o visualización completa, usa “Abrir en OnlyOffice”.' }}
        </p>
    </div>
</template>

<script setup>
defineProps({
    extension: {
        type: String,
        default: 'DOC',
    },
    name: {
        type: String,
        default: 'Documento Office',
    },
    size: {
        type: String,
        default: '-',
    },
    mime: {
        type: String,
        default: 'application/octet-stream',
    },
    note: {
        type: String,
        default: '',
    },
});
</script>

<style scoped lang="scss">
.office-preview-card {
    width: min(640px, 100%);
    min-height: 300px;
    border: 1px solid var(--border-color);
    border-radius: 12px;
    background: var(--bg-primary);
    padding: 1.2rem;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
    gap: 0.7rem;
}

.office-preview-ext {
    min-width: 78px;
    height: 38px;
    border-radius: 999px;
    border: 1px solid var(--border-color);
    background: var(--bg-tertiary);
    color: var(--text-primary);
    font-weight: 700;
    font-size: 0.9rem;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    text-transform: uppercase;
}

.office-preview-name {
    margin: 0;
    color: var(--text-primary);
    font-size: 1.12rem;
    max-width: 100%;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.office-preview-info {
    margin: 0;
    color: var(--text-secondary);
    font-size: 0.9rem;
    max-width: 100%;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.separator-dot {
    margin: 0 0.4rem;
}

.office-preview-note {
    margin: 0.2rem 0 0;
    color: var(--text-muted);
    font-size: 0.85rem;
    max-width: 460px;
}

@media (max-width: 768px) {
    .office-preview-name,
    .office-preview-info {
        white-space: normal;
        word-break: break-word;
    }
}
</style>
