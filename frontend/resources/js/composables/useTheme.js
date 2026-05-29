import { ref, onMounted } from "vue";
import { api } from "@/services/api";

const APP_CONFIG_VERSION_KEY = "app_config_version";

// Shared state
const theme = ref("light");

export function useTheme() {
    // Initialize theme from localStorage or system preference
    // This should only happen once or be checked on mount
    const initTheme = () => {
        const savedTheme = localStorage.getItem("theme");
        if (savedTheme) {
            theme.value = savedTheme;
        } else {
            const prefersDark = window.matchMedia(
                "(prefers-color-scheme: dark)",
            ).matches;
            theme.value = prefersDark ? "dark" : "light";
        }
        applyTheme();
    };

    const applyTheme = () => {
        document.documentElement.setAttribute("data-theme", theme.value);
        localStorage.setItem("theme", theme.value);
    };

    const setTheme = (newTheme, save = true) => {
        theme.value = newTheme;
        applyTheme();

        if (save) {
            localStorage.setItem(APP_CONFIG_VERSION_KEY, String(Date.now()));
        }

        // Sync with API if user is authenticated (we need to check auth outside or pass it)
        // Since we can't easily access useAuth here (circular dep), we might rely on the caller
        // OR we can import useAuth but that causes circular dependency (useAuth uses useTheme).
        // Solution: useAuth calls setAuth, which updates state.
        // When USER interacts, they call setTheme.
        // We can check if token exists in localStorage as a proxy for auth, or import apiClient.
        if (save && localStorage.getItem("token")) {
            api.auth
                .updateAppConfig({ theme: newTheme })
                .catch((err) => console.error("Failed to save theme", err));
        }
    };

    const toggleTheme = () => {
        setTheme(theme.value === "light" ? "dark" : "light");
    };

    // Apply theme immediately
    applyTheme();

    // Call init only if not set? Or always?
    // If we use shared state, we might initialize it at module level if possible,
    // but we need window access.
    // Let's rely on onMounted to init if current value is default?
    // Or just run initTheme() once at module level?
    // Window is available.

    return {
        theme,
        toggleTheme,
        setTheme,
        initTheme, // Expose for initial setup if needed
    };
}

// Initialize once
try {
    const savedTheme = localStorage.getItem("theme");
    if (savedTheme) {
        theme.value = savedTheme;
    } else if (
        window.matchMedia &&
        window.matchMedia("(prefers-color-scheme: dark)").matches
    ) {
        theme.value = "dark";
    }
} catch (e) {
    // SSR or other error
}
