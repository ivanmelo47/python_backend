<template>
    <div class="example-component">
        <div class="icon">{{ icon }}</div>
        <h3>{{ title }}</h3>
        <p>{{ description }}</p>
        <slot></slot>
    </div>
</template>

<script setup>
import { defineProps } from 'vue';

const props = defineProps({
    title: {
        type: String,
        required: true
    },
    description: {
        type: String,
        default: ''
    },
    icon: {
        type: String,
        default: '📦'
    }
});
</script>

<style scoped lang="scss">
.example-component {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 2rem;
    border-radius: 12px;
    text-align: center;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    transition: all 0.3s ease;
    
    &:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 12px rgba(0, 0, 0, 0.2);
    }
    
    .icon {
        font-size: 3rem;
        margin-bottom: 1rem;
    }
    
    h3 {
        font-size: 1.5rem;
        margin-bottom: 0.5rem;
    }
    
    p {
        opacity: 0.9;
        line-height: 1.6;
    }
}
</style>
