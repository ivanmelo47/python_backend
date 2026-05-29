<template>
    <PortfolioBlock kicker="Tecnologias" title="Stack tecnico" class="tech-block reveal reveal-delay-2">
        <div class="chip-row">
            <span v-for="(tech, index) in technologies" :key="index" class="tech-chip">
                <DynamicIcon v-if="tech.icon_uuid && tech.icon_data" :name="`db:${tech.icon_data.name || 'tech'}`"
                    :databaseData="tech.icon_data" :size="30" class="tech-icon" />
                <span>{{ tech.label || tech }}</span>
            </span>
        </div>
    </PortfolioBlock>
</template>

<script setup>
import PortfolioBlock from './PortfolioBlock.vue';
import DynamicIcon from '@/components/DynamicIcon.vue';

defineProps({
    technologies: {
        type: Array,
        required: true
    }
});
</script>

<style scoped>
.chip-row {
    margin-top: 1.25rem;
    display: flex;
    flex-wrap: wrap;
    gap: 0.6rem;
}

.tech-chip {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 6px 14px;
    border-radius: 10px;
    background: var(--bg-primary);
    border: 1px solid var(--border-color);
    color: var(--text-secondary);
    font-size: 0.82rem;
    font-weight: 700;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.tech-icon {
    opacity: 0.85;
}

.tech-chip:hover {
    background: color-mix(in srgb, var(--primary), transparent 90%);
    border-color: var(--primary);
    color: var(--primary);
    transform: translateY(-2px);
}
</style>
