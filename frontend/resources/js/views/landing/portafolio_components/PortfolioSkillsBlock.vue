<template>
    <PortfolioBlock kicker="Habilidades" title="Capacidades clave" class="skills-block reveal reveal-delay-1">
        <ul class="list-grid">
            <li v-for="(skill, index) in skills" :key="index">
                <DynamicIcon v-if="skill.icon_uuid && skill.icon_data" :name="`db:${skill.icon_data.name || 'skill'}`"
                    :databaseData="skill.icon_data" :size="30" class="skill-icon" />
                <span>{{ skill.label || skill }}</span>
            </li>
        </ul>
    </PortfolioBlock>
</template>

<script setup>
import PortfolioBlock from './PortfolioBlock.vue';
import DynamicIcon from '@/components/DynamicIcon.vue';

defineProps({
    skills: {
        type: Array,
        required: true
    }
});
</script>

<style scoped>
.list-grid {
    margin-top: 1.25rem;
    list-style: none;
    padding: 0;
    display: flex;
    flex-wrap: wrap;
    gap: 0.6rem;
}

.list-grid li {
    padding: 8px 16px;
    border-radius: 10px;
    background: var(--bg-primary);
    border: 1px solid var(--border-color);
    color: var(--text-secondary);
    font-size: 0.88rem;
    font-weight: 600;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    display: flex;
    align-items: center;
    gap: 8px;
}

.skill-icon {
    opacity: 0.8;
}

.list-grid li:hover {
    background: color-mix(in srgb, var(--primary), transparent 90%);
    border-color: var(--primary);
    color: var(--primary);
    transform: translateY(-2px);
}
</style>
