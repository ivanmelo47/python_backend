<template>
    <div class="shortcut-carousel-wrapper" ref="wrapper" :class="{ 'is-overflowing': hasOverflow }">
        <div class="carousel-main">
            <div class="carousel-controls" v-if="hasOverflow">
                <button class="control-btn prev" @click="scroll('left')" :disabled="isAtStart" aria-label="Anterior">
                    <Icon name="chevron-left" :size="20" />
                </button>
                <button class="control-btn next" @click="scroll('right')" :disabled="isAtEnd" aria-label="Siguiente">
                    <Icon name="chevron-right" :size="20" />
                </button>
            </div>

            <div class="carousel-container" ref="container" @scroll="checkScroll">
                <div class="carousel-track">
                    <router-link 
                        v-for="child in items" 
                        :key="child.path" 
                        :to="child.path" 
                        class="shortcut-card-item"
                    >
                        <div class="icon-wrapper">
                            <DynamicIcon 
                                :name="child.icon || 'circle'" 
                                :databaseData="child.dbIcon" 
                                :size="32" 
                            />
                        </div>
                        <div class="card-info">
                            <h3>{{ child.name }}</h3>
                            <p>{{ child.description }}</p>
                        </div>
                        <div class="card-arrow">
                            <Icon name="arrow-right" :size="16" />
                        </div>
                    </router-link>
                </div>
            </div>
        </div>

        <div class="carousel-pagination" v-if="hasOverflow">
            <div 
                v-for="(_, index) in items" 
                :key="index"
                class="pagination-dot"
                :class="{ active: currentActiveIndex === index }"
            ></div>
        </div>
    </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick } from 'vue';
import Icon from '@/components/Icon.vue';
import DynamicIcon from '@/components/DynamicIcon.vue';

const props = defineProps({
    items: {
        type: Array,
        default: () => []
    }
});

const container = ref(null);
const wrapper = ref(null);
const hasOverflow = ref(false);
const isAtStart = ref(true);
const isAtEnd = ref(false);
const currentActiveIndex = ref(0);

const checkOverflow = () => {
    if (!container.value) return;
    hasOverflow.value = container.value.scrollWidth > container.value.clientWidth;
    checkScroll();
};

const checkScroll = () => {
    if (!container.value) return;
    const { scrollLeft, scrollWidth, clientWidth } = container.value;
    isAtStart.value = scrollLeft <= 5;
    isAtEnd.value = scrollLeft + clientWidth >= scrollWidth - 5;

    // Estimate active index based on scroll position
    const cardWidth = 320; // Approx width of card + gap
    currentActiveIndex.value = Math.round(scrollLeft / cardWidth);
};

const scroll = (direction) => {
    if (!container.value) return;
    const scrollAmount = container.value.clientWidth * 0.8;
    container.value.scrollBy({
        left: direction === 'left' ? -scrollAmount : scrollAmount,
        behavior: 'smooth'
    });
};

let resizeObserver = null;

onMounted(() => {
    nextTick(() => {
        checkOverflow();
        if (wrapper.value) {
            resizeObserver = new ResizeObserver(checkOverflow);
            resizeObserver.observe(wrapper.value);
        }
    });
});

onUnmounted(() => {
    if (resizeObserver) {
        resizeObserver.disconnect();
    }
});
</script>

<style lang="scss" scoped>
@use "sass:map";
@use "../../../../../sass/shared/variables" as *;
@use "../../../../../sass/shared/mixins" as *;

.shortcut-carousel-wrapper {
    position: relative;
    margin: get-spacing(4) 0;
    width: 100%;
    padding: 0 get-spacing(12); // Dedicated space for buttons
    --carousel-gap: #{get-spacing(6)};
    --visible-items: 4;
    --gap-count: 3;

    @media (max-width: 1400px) { --visible-items: 3; --gap-count: 2; }
    @media (max-width: 1100px) { --visible-items: 2; --gap-count: 1; }
    @media (max-width: 768px) { 
        padding: 0 get-spacing(4); // Small padding for screen edges
        --visible-items: 1; 
        --gap-count: 0;
        --carousel-gap: #{get-spacing(4)};
    }
}

.carousel-main {
    position: relative;
    width: 100%;
}

.carousel-container {
    overflow-x: auto;
    overflow-y: hidden;
    scroll-behavior: smooth;
    -webkit-overflow-scrolling: touch;
    @include hide-scrollbar;
    scroll-snap-type: x mandatory;
    padding: get-spacing(4) 2px;
}

.carousel-track {
    display: flex;
    gap: var(--carousel-gap);
    width: 100%;
}

.shortcut-card-item {
    // Calculate width to fit exactly --visible-items
    flex: 0 0 calc((100% - (var(--carousel-gap) * var(--gap-count))) / var(--visible-items));
    scroll-snap-align: start;
    background: var(--bg-primary);
    border: 1px solid var(--border-color);
    border-radius: map.get($radius, xl);
    padding: get-spacing(6);
    display: flex;
    align-items: center;
    gap: get-spacing(5);
    text-decoration: none;
    @include transition(all);
    position: relative;
    overflow: hidden;

    @media (max-width: 768px) {
        padding: get-spacing(4);
        gap: get-spacing(3);
    }

    &::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: linear-gradient(135deg, rgba(var(--primary-rgb), 0.05) 0%, transparent 100%);
        opacity: 0;
        @include transition(opacity);
    }

    &:hover {
        transform: translateY(-5px);
        border-color: var(--primary);
        box-shadow: map.get($shadows, xl);
        
        &::before {
            opacity: 1;
        }

        .icon-wrapper {
            background: var(--primary);
            color: white;
            transform: scale(1.1);
        }

        .card-arrow {
            transform: translateX(3px);
            color: var(--primary);
            opacity: 1;
        }
    }

    .icon-wrapper {
        width: 54px;
        height: 54px;
        border-radius: map.get($radius, lg);
        background: var(--bg-secondary);
        @include flex-center;
        color: var(--primary);
        @include transition(all);
        flex-shrink: 0;
        z-index: 1;

        @media (max-width: 768px) {
            width: 44px;
            height: 44px;
            min-width: 44px;
        }
    }

    .card-info {
        flex: 1;
        min-width: 0;
        z-index: 1;

        h3 {
            font-size: 1.05rem;
            font-weight: 700;
            color: var(--text-primary);
            margin: 0;
            margin-bottom: 4px;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }

        p {
            font-size: 0.85rem;
            color: var(--text-tertiary);
            line-height: 1.4;
            margin: 0;
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
            overflow: hidden;
        }
    }

    .card-arrow {
        color: var(--text-tertiary);
        opacity: 0.3;
        @include transition(all);
    }
}

.carousel-controls {
    .control-btn {
        position: absolute;
        top: 50%;
        transform: translateY(-50%);
        width: 42px;
        height: 42px;
        border-radius: 50%;
        background: var(--bg-primary);
        border: 1px solid var(--border-color);
        color: var(--text-primary);
        box-shadow: map.get($shadows, lg);
        @include flex-center;
        cursor: pointer;
        z-index: 10;
        @include transition(all);
        
        backdrop-filter: blur(8px);

        &:hover:not(:disabled) {
            background: var(--primary);
            color: white;
            border-color: var(--primary);
            transform: translateY(-50%) scale(1.1);
        }

        &:disabled {
            opacity: 0;
            pointer-events: none;
        }

        &.prev { left: - get-spacing(10); }
        &.next { right: - get-spacing(10); }

        @media (max-width: 768px) {
            display: none;
        }
    }
}

.carousel-pagination {
    display: flex;
    justify-content: center;
    gap: 8px;
    margin-top: get-spacing(6);

    .pagination-dot {
        width: 6px;
        height: 6px;
        border-radius: 50%;
        background: var(--border-color);
        @include transition(all);

        &.active {
            background: var(--primary);
            width: 18px;
            border-radius: 3px;
        }
    }
}

@media (max-width: 768px) {
    .shortcut-card-item {
        width: 280px;
        padding: get-spacing(4);
    }
    
    .carousel-controls {
        display: none; // Use native scroll on mobile
    }
    
    .carousel-track {
        gap: get-spacing(4);
    }
}
</style>
