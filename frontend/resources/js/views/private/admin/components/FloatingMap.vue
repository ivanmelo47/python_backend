<template>
    <Transition name="modal-fade">
        <div v-if="isOpen" class="modal-overlay" @click.self="close">
            <div class="modal-container modal-lg">
                <!-- Header -->
                <div class="modal-header">
                    <div class="header-content">
                        <div class="header-icon">
                            <Icon name="map-pin" :size="18" />
                        </div>
                        <h3 class="modal-title">
                            {{ title }}
                        </h3>
                    </div>
                    
                    <button @click="close" class="close-btn" title="Cerrar">
                        <Icon name="x" :size="20" />
                    </button>
                </div>

                <!-- Body -->
                <div class="modal-body map-body">
                    <div ref="mapContainer" class="map-container"></div>
                </div>
            </div>
        </div>
    </Transition>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch, nextTick } from 'vue';
import Icon from '@/components/Icon.vue';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

// Fix for default marker icons in Leaflet with build tools
import markerIcon from 'leaflet/dist/images/marker-icon.png';
import markerIconRetina from 'leaflet/dist/images/marker-icon-2x.png';
import markerShadow from 'leaflet/dist/images/marker-shadow.png';

const props = defineProps({
    isOpen: {
        type: Boolean,
        default: false
    },
    title: {
        type: String,
        default: 'Ubicación en Mapa'
    },
    lat: {
        type: [Number, String],
        required: true
    },
    lon: {
        type: [Number, String],
        required: true
    },
    zoom: {
        type: Number,
        default: 13
    }
});

const emit = defineEmits(['close']);

const mapContainer = ref(null);
let map = null;
let marker = null;

const close = () => {
    emit('close');
};

const initMap = () => {
    if (!mapContainer.value) return;

    // Use a custom icon logic that is more reliable with Vite
    const leafIcon = L.icon({
        iconUrl: markerIcon,
        iconRetinaUrl: markerIconRetina,
        shadowUrl: markerShadow,
        iconSize: [25, 41],
        iconAnchor: [12, 41],
        popupAnchor: [1, -34],
        shadowSize: [41, 41]
    });

    const lat = parseFloat(props.lat);
    const lon = parseFloat(props.lon);

    if (isNaN(lat) || isNaN(lon)) return;

    map = L.map(mapContainer.value, {
        zoomControl: true,
        attributionControl: true
    }).setView([lat, lon], props.zoom);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
    }).addTo(map);

    marker = L.marker([lat, lon], { icon: leafIcon }).addTo(map)
        .bindPopup(props.title)
        .openPopup();
    
    // Crucial for modals: invalidate size after the transition/render
    setTimeout(() => {
        if (map) map.invalidateSize();
    }, 400); 
};

const destroyMap = () => {
    if (map) {
        map.remove();
        map = null;
    }
};

watch(() => props.isOpen, async (newVal) => {
    if (newVal) {
        await nextTick();
        initMap();
    } else {
        destroyMap();
    }
});

onUnmounted(() => {
    destroyMap();
});
</script>

<style scoped>
.map-body {
    padding: 0;
    overflow: hidden;
    height: 400px;
}

.map-container {
    width: 100%;
    height: 100%;
    z-index: 1;
}

.modal-fade-enter-active,
.modal-fade-leave-active {
    transition: opacity 0.2s ease, transform 0.2s ease;
}

.modal-fade-enter-from,
.modal-fade-leave-to {
    opacity: 0;
    transform: scale(0.95);
}
</style>
