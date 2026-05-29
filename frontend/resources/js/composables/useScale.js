import { ref } from "vue";
import { api } from "@/services/api";

const APP_CONFIG_VERSION_KEY = "app_config_version";

// Read from localStorage immediately (module-level state)
const getStoredScale = () => {
    try {
        const saved = localStorage.getItem("app-scale");
        return saved || "100";
    } catch (e) {
        return "100";
    }
};

// Initialize ref with stored value immediately
const scale = ref(getStoredScale());

export function useScale() {
    const setScale = (newScale, save = true) => {
        scale.value = newScale;
        document.documentElement.setAttribute("data-scale", newScale);
        localStorage.setItem("app-scale", newScale);

        if (save) {
            localStorage.setItem(APP_CONFIG_VERSION_KEY, String(Date.now()));
        }

        if (save && localStorage.getItem("token")) {
            api.auth
                .updateAppConfig({ app_scale: newScale })
                .catch((err) => console.error(err));
        }
    };

    // Apply the attribute immediately when this composable is used
    // This ensures it runs as soon as App.vue imports/uses it
    if (scale.value) {
        document.documentElement.setAttribute("data-scale", scale.value);
    }

    return {
        scale,
        setScale,
    };
}
