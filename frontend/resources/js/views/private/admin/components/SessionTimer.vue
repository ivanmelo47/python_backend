<template>
    <div class="session-timer" :class="{ 'active': !endTime, 'inactive': endTime }">
        <Icon 
            :name="!endTime ? 'clock' : 'check-circle'" 
            :size="14" 
            class="mr-1" 
            :class="{ 'spin-slow': !endTime }" 
        />
        <span class="font-mono">{{ formattedDuration }}</span>
    </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue';
import Icon from '@/components/Icon.vue';

const props = defineProps({
    start: {
        type: [String, Date],
        required: true
    },
    end: {
        type: [String, Date],
        default: null
    }
});

const now = ref(new Date());
let timer = null;

// Use 'end' prop directly for computed logic
const endTime = computed(() => props.end);

const updateNow = () => {
    now.value = new Date();
};

onMounted(() => {
    if (!props.end) {
        timer = setInterval(updateNow, 1000);
    }
});

onUnmounted(() => {
    if (timer) clearInterval(timer);
});

// Watch for changes in 'end' prop
watch(() => props.end, (newEnd) => {
    if (newEnd) {
        if (timer) {
            clearInterval(timer);
            timer = null;
        }
    } else if (!timer) {
        timer = setInterval(updateNow, 1000);
    }
});

const formattedDuration = computed(() => {
    const startDate = new Date(props.start);
    const endDate = props.end ? new Date(props.end) : now.value;
    
    let diff = Math.max(0, Math.floor((endDate - startDate) / 1000));
    
    const hours = Math.floor(diff / 3600);
    diff %= 3600;
    const minutes = Math.floor(diff / 60);
    const seconds = diff % 60;
    
    const pad = (n) => n.toString().padStart(2, '0');
    
    if (hours >= 24) {
        const days = Math.floor(hours / 24);
        const remHours = hours % 24;
        return `${days}d ${pad(remHours)}:${pad(minutes)}:${pad(seconds)}`;
    }
    
    return `${pad(hours)}:${pad(minutes)}:${pad(seconds)}`;
});
</script>

<style scoped>
.session-timer {
    display: flex;
    align-items: center;
    gap: 6px;
    font-variant-numeric: tabular-nums;
    font-size: 0.9em;
    padding: 2px 6px;
    border-radius: 4px;
    width: fit-content;
}

/* Active Session: Use Primary Color (Green/Blue depending on theme) */
.session-timer.active {
    color: var(--primary-color, #28a745); /* Default green for active */
    background-color: rgba(40, 167, 69, 0.1);
    border: 1px solid rgba(40, 167, 69, 0.2);
}

/* Inactive Session: Use Danger/Muted Color (Red/Gray) */
.session-timer.inactive {
    color: var(--danger-color, #dc3545); /* Default red for inactive */
    background-color: rgba(220, 53, 69, 0.1);
    border: 1px solid rgba(220, 53, 69, 0.2);
    font-weight: 500;
}

.font-mono {
    font-family: 'Courier New', Courier, monospace;
    letter-spacing: -0.5px;
    font-weight: 600;
}

.spin-slow {
    animation: spin 3s linear infinite;
}

@keyframes spin {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
}
</style>
