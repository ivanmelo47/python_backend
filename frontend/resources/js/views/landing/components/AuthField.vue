<template>
    <div class="form-group" :class="[colSpanClass, { 'centered': centered }]">
        <label :for="id">
            <Icon v-if="icon" :name="icon" :size="20" class="label-icon" />
            {{ label }}
        </label>
        
        <div :class="{ 'password-wrapper': isPassword }">
            <input
                :id="id"
                :type="computedType"
                :value="modelValue"
                @input="$emit('update:modelValue', $event.target.value)"
                :placeholder="placeholder"
                :disabled="disabled"
                v-bind="$attrs"
            />
            
            <button
                v-if="isPassword"
                type="button"
                class="toggle-password"
                @click="showPassword = !showPassword"
                :disabled="disabled"
            >
                <Icon :name="showPassword ? 'eyeOpen' : 'eyeClosed'" :size="22" />
            </button>
        </div>
        
        <span class="error" v-if="showError">{{ error }}</span>
    </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import Icon from '@/components/Icon.vue';

const props = defineProps({
    id: { type: String, required: true },
    label: { type: String, required: true },
    icon: { type: String, default: '' },
    type: { type: String, default: 'text' },
    placeholder: { type: String, default: '' },
    modelValue: { type: [String, Number], default: '' },
    error: { type: String, default: '' },
    showError: { type: Boolean, default: true },
    disabled: { type: Boolean, default: false },
    colSpan: { type: Number, default: 6 }, // Default to full width (6 columns)
    centered: { type: Boolean, default: false }
});

defineEmits(['update:modelValue']);

const showPassword = ref(false);
const isPassword = computed(() => props.type === 'password');

const computedType = computed(() => {
    if (isPassword.value) {
        return showPassword.value ? 'text' : 'password';
    }
    return props.type;
});

const colSpanClass = computed(() => `col-span-${props.colSpan}`);
</script>
