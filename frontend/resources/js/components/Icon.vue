<template>
    <svg
        :width="size"
        :height="size"
        :viewBox="iconData.viewBox"
        :class="['icon', customClass]"
        :style="{ color: color }"
        xmlns="http://www.w3.org/2000/svg"
        v-html="iconData.path"
    />
</template>

<script setup>
import { computed } from 'vue';
import { getIcon } from '../utils/icons/index';

const props = defineProps({
    name: {
        type: String,
        required: true
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

const iconData = computed(() => getIcon(props.name));
</script>

<style scoped>
.icon {
    display: inline-block;
    vertical-align: middle;
    fill: currentColor;
    transition: all 0.3s ease;
}
</style>
