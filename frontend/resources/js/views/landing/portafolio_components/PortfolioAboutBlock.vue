<template>
    <PortfolioBlock kicker="Sobre mi" :title="profile.name" class="about-block reveal reveal-delay-1">
        <p>{{ profile.aboutText || profile.summary }}</p>
        <ul class="mini-stats">
            <li v-for="metric in metrics" :key="metric.label">
                <DynamicIcon
                    v-if="metric.icon_uuid && metric.icon_data"
                     :name="`db:${metric.icon_data.name || 'metric'}`"
                     :databaseData="metric.icon_data"
                     :size="26"
                     class="metric-dyn-icon"
                 />
                <div class="metric-text-box">
                    <strong>{{ metric.value }}</strong>
                    <span>{{ metric.label }}</span>
                </div>
            </li>
        </ul>
    </PortfolioBlock>
</template>

<script setup>
import PortfolioBlock from './PortfolioBlock.vue';
import DynamicIcon from '@/components/DynamicIcon.vue';

defineProps({
    profile: {
        type: Object,
        required: true
    },
    metrics: {
        type: Array,
        required: true
    }
});
</script>

<style scoped>
.about-block p {
    font-size: 1.05rem;
    line-height: 1.7;
    color: var(--text-secondary);
    margin-bottom: 1.5rem;
    white-space: pre-wrap;
}

.mini-stats {
    margin-top: 1.25rem;
    list-style: none;
    padding: 0;
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 0.75rem;
}

.mini-stats li {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 12px 16px;
    border-radius: 12px;
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(255, 255, 255, 0.06);
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.mini-stats li:hover {
    background: rgba(255, 255, 255, 0.05);
    border-color: var(--primary);
    transform: translateY(-2px);
}

.metric-text-box {
    display: flex;
    flex-direction: column;
}

.metric-dyn-icon {
    color: var(--primary);
    flex-shrink: 0;
    filter: drop-shadow(0 0 8px color-mix(in srgb, var(--primary), transparent 70%));
}

.mini-stats strong {
    color: var(--text-primary);
    font-size: 1.1rem;
    font-weight: 800;
}

.mini-stats span {
    color: var(--text-tertiary);
    font-size: 0.72rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

@media (max-width: 840px) {
    .mini-stats {
        grid-template-columns: repeat(2, 1fr);
    }
}

@media (max-width: 600px) {
    .mini-stats {
        grid-template-columns: 1fr;
    }
}
</style>
