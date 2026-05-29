<template>
    <PortfolioBlock
        kicker="Redes"
        title="Presencia Profesional"
        id="redes"
        class="social-block reveal reveal-delay-3"
    >
        <div class="social-grid">
            <a 
                v-for="(link, index) in links" 
                :key="index"
                :href="link.url"
                target="_blank"
                rel="noopener noreferrer"
                class="social-card"
                :title="link.name"
            >
                <div class="social-icon-box">
                    <DynamicIcon
                        v-if="link.icon_uuid && link.icon_data"
                        :name="`db:${link.icon_data.name || 'social'}`"
                        :databaseData="link.icon_data"
                        :size="24"
                    />
                    <Icon v-else :name="link.icon || 'link'" :size="24" />
                </div>
                <div class="social-info">
                    <span class="social-name">{{ link.name }}</span>
                    <span class="social-handle">{{ link.handle }}</span>
                </div>
                <Icon name="chevron-right" :size="16" class="arrow-icon" />
            </a>
        </div>
    </PortfolioBlock>
</template>

<script setup>
import PortfolioBlock from './PortfolioBlock.vue';
import Icon from '@/components/Icon.vue';
import DynamicIcon from '@/components/DynamicIcon.vue';

defineProps({
    links: {
        type: Array,
        default: () => []
    }
});
</script>

<style scoped>
.social-grid {
    display: grid;
    grid-template-columns: 1fr;
    gap: 0.75rem;
    margin-top: 1rem;
}

@media (min-width: 480px) {
    .social-grid {
        grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
    }
}

.social-card {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 10px 14px;
    background: rgba(255, 255, 255, 0.02);
    border: 1px solid var(--border-color);
    border-radius: 12px;
    text-decoration: none;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    position: relative;
    overflow: hidden;
}

.social-card::before {
    content: '';
    position: absolute;
    inset: 0;
    background: radial-gradient(circle at top left, var(--primary) 0%, transparent 70%);
    opacity: 0;
    transition: opacity 0.4s ease;
}

.social-card:hover {
    transform: translateY(-2px);
    border-color: var(--primary);
    background: rgba(255, 255, 255, 0.05);
    box-shadow: 0 8px 16px color-mix(in srgb, var(--primary), transparent 90%);
}

.social-card:hover::before {
    opacity: 0.08;
}

.social-icon-box {
    position: relative;
    z-index: 1;
    width: 36px;
    height: 36px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: color-mix(in srgb, var(--primary), transparent 92%);
    color: var(--primary);
    border-radius: 10px;
    transition: all 0.3s ease;
}

.social-card:hover .social-icon-box {
    background: var(--primary);
    color: white;
    transform: rotate(-8deg) scale(1.05);
}

.social-info {
    position: relative;
    z-index: 1;
    flex: 1;
    display: flex;
    flex-direction: column;
    min-width: 0;
}

.social-name {
    font-size: 0.88rem;
    font-weight: 700;
    color: var(--text-primary);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.social-handle {
    font-size: 0.72rem;
    color: var(--text-muted);
    opacity: 0.7;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.arrow-icon {
    position: relative;
    z-index: 1;
    color: var(--text-muted);
    opacity: 0.3;
    transition: all 0.3s ease;
}

.social-card:hover .arrow-icon {
    color: var(--primary);
    opacity: 1;
    transform: translateX(2px);
}

@media (max-width: 480px) {
    .social-grid {
        grid-template-columns: 1fr;
    }
}
</style>
