import { ref, watch, onMounted } from "vue";
import { api } from "@/services/api";

const APP_CONFIG_VERSION_KEY = "app_config_version";

const palette = ref("default"); // default (Green), blue, purple, orange

// Hybrid Palettes Management
const staticPalettes = {
    default: { id: 'default', name: 'Verde', isStatic: true, color: '#42b983' },
    blue: { id: 'blue', name: 'Azul', isStatic: true, color: '#3b82f6' },
    purple: { id: 'purple', name: 'Morado', isStatic: true, color: '#8b5cf6' },
    orange: { id: 'orange', name: 'Naranja', isStatic: true, color: '#f97316' },
    red: { id: 'red', name: 'Rojo', isStatic: true, color: '#ef4444' },
    gold: { id: 'gold', name: 'Dorado', isStatic: true, color: '#f59e0b' }
};

const dynamicPalettes = ref([]);

const injectDynamicPaletteStyles = (palettes) => {
    let styleEl = document.getElementById('dynamic-color-palettes');
    if (!styleEl) {
        styleEl = document.createElement('style');
        styleEl.id = 'dynamic-color-palettes';
        document.head.appendChild(styleEl);
    }

    let css = '';
    palettes.forEach(p => {
        if (!p.isStatic) {
            css += `
[data-color-theme="${p.id}"] {
    --primary: ${p.color};
    --primary-dark: color-mix(in srgb, ${p.color} 85%, black);
    --accent: ${p.color};
}
[data-theme="dark"][data-color-theme="${p.id}"] {
    --primary: color-mix(in srgb, ${p.color} 85%, white);
    --primary-dark: ${p.color};
    --accent: color-mix(in srgb, ${p.color} 85%, white);
}
`;
        }
    });

    styleEl.innerHTML = css;
};

export function useColorPalette() {
    const fetchDynamicPalettes = async () => {
        try {
            // Load from localStorage cache first to avoid flashing default color
            const cached = localStorage.getItem('visual_color_palettes');
            if (cached) {
                dynamicPalettes.value = JSON.parse(cached);
                injectDynamicPaletteStyles(dynamicPalettes.value);
            }

            // Only fetch if authenticated
            if (localStorage.getItem("token")) {
                const response = await api.system.getVisualSettings();
                if (response.data && response.data.data) {
                    const palettes = response.data.data.visual_color_palettes || [];
                    dynamicPalettes.value = palettes;
                    localStorage.setItem('visual_color_palettes', JSON.stringify(palettes));
                    injectDynamicPaletteStyles(palettes);
                }
            }
        } catch (error) {
            console.error('Failed to fetch dynamic color palettes', error);
        }
    };

    const setPalette = (newPalette, save = true) => {
        palette.value = newPalette;
        localStorage.setItem("color-palette", newPalette);
        document.documentElement.setAttribute("data-color-theme", newPalette);

        if (save) {
            localStorage.setItem(APP_CONFIG_VERSION_KEY, String(Date.now()));
        }

        if (save && localStorage.getItem("token")) {
            api.auth
                .updateAppConfig({ color_palette: newPalette })
                .catch((err) => console.error(err));
        }
    };

    const initPalette = () => {
        const stored = localStorage.getItem("color-palette");
        if (stored) {
            setPalette(stored, false); // Don't save on init
        } else {
            setPalette("default", false);
        }
    };

    // Initialize immediately
    initPalette();
    fetchDynamicPalettes();

    return {
        palette,
        setPalette,
        staticPalettes,
        dynamicPalettes,
        fetchDynamicPalettes
    };
}
