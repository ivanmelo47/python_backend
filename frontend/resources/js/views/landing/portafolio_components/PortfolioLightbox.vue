<template>
    <teleport to="body">
        <transition name="carousel-fade">
            <div v-if="isVisible" class="lightbox-overlay" @click="$emit('close')">
                <div class="lightbox-content" @click.stop>
                    <button type="button" class="lightbox-close" @click="$emit('close')">
                        <Icon name="x" :size="24" />
                    </button>

                    <div class="lightbox-topbar">
                        <div class="lightbox-title-block">
                            <span class="lightbox-kicker">{{ kicker }}</span>
                            <h3>{{ title }}</h3>
                        </div>
                        <div v-if="images.length > 1" class="lightbox-counter">
                            {{ index + 1 }} / {{ images.length }}
                        </div>
                    </div>

                    <div class="lightbox-stage">
                        <button
                            type="button"
                            class="lightbox-nav lightbox-nav-prev"
                            :disabled="images.length <= 1"
                            @click.stop="prev"
                        >
                            <Icon name="chevron-left" :size="22" />
                        </button>

                        <div class="lightbox-image-frame">
                            <transition name="carousel-fade" mode="out-in">
                                <img
                                    v-if="currentImage"
                                    :key="currentImage"
                                    :src="currentImage"
                                    :alt="title"
                                    class="lightbox-img"
                                />
                                <div v-else key="empty" class="lightbox-empty">
                                    <Icon name="image" :size="48" />
                                    <span>No hay imágenes para mostrar</span>
                                </div>
                            </transition>
                        </div>

                        <button
                            type="button"
                            class="lightbox-nav lightbox-nav-next"
                            :disabled="images.length <= 1"
                            @click.stop="next"
                        >
                            <Icon name="chevron-right" :size="22" />
                        </button>
                    </div>

                    <div v-if="images.length > 1" class="lightbox-dots">
                        <button
                            v-for="(image, idx) in images"
                            :key="`${image}-${idx}`"
                            type="button"
                            class="carousel-dot"
                            :class="{ active: index === idx }"
                            :aria-label="`Ir a imagen ${idx + 1}`"
                            @click.stop="$emit('update:index', idx)"
                        ></button>
                    </div>
                </div>
            </div>
        </transition>
    </teleport>
</template>

<script setup>
import { computed, onMounted, onBeforeUnmount, watch } from 'vue';
import Icon from '@/components/Icon.vue';

const props = defineProps({
    isVisible: { type: Boolean, default: false },
    images: { type: Array, default: () => [] },
    index: { type: Number, default: 0 },
    title: { type: String, default: 'Vista previa' },
    kicker: { type: String, default: 'Portfolio' }
});

const emit = defineEmits(['close', 'update:index']);

const currentImage = computed(() => props.images[props.index] || props.images[0] || '');

function next() {
    if (props.images.length <= 1) return;
    const nextIdx = (props.index + 1) % props.images.length;
    emit('update:index', nextIdx);
}

function prev() {
    if (props.images.length <= 1) return;
    const prevIdx = (props.index - 1 + props.images.length) % props.images.length;
    emit('update:index', prevIdx);
}

function onKeyDown(event) {
    if (!props.isVisible) return;
    if (event.key === 'Escape') emit('close');
    if (event.key === 'ArrowRight') next();
    if (event.key === 'ArrowLeft') prev();
}

watch(() => props.isVisible, (val) => {
    if (val) {
        document.body.style.overflow = 'hidden';
    } else {
        document.body.style.overflow = '';
    }
});

onMounted(() => {
    window.addEventListener('keydown', onKeyDown);
});

onBeforeUnmount(() => {
    window.removeEventListener('keydown', onKeyDown);
});
</script>

<style scoped>
.lightbox-empty {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 12px;
    color: rgba(255, 255, 255, 0.4);
    font-size: 0.9rem;
}
</style>
