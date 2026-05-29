import { ref } from "vue";
import { api } from "@/services/api";

const APP_CONFIG_VERSION_KEY = "app_config_version";

// Global state
const itemsPerPage = ref(
    parseInt(localStorage.getItem("table_items_per_page")) || 10,
);
const viewMode = ref(localStorage.getItem("table_view_mode") || "grid");

// Scoped configurations map: { moduleId: { sortBy, sortOrder, itemsPerPage, viewMode } }
const tableConfigs = ref(JSON.parse(localStorage.getItem("table_configs") || "{}"));

export function useTableConfig() {
    /**
     * Get config for a specific module, falling back to global defaults
     */
    const getModuleConfig = (moduleId) => {
        const defaults = {
            itemsPerPage: itemsPerPage.value,
            viewMode: viewMode.value,
            sortBy: "",
            sortOrder: "desc"
        };
        
        if (!moduleId || !tableConfigs.value[moduleId]) {
            return defaults;
        }
        
        return {
            ...defaults,
            ...tableConfigs.value[moduleId]
        };
    };

    /**
     * Update configuration for a specific module
     */
    const updateModuleConfig = (moduleId, updates, save = true) => {
        if (!moduleId) return;

        tableConfigs.value[moduleId] = {
            ...(tableConfigs.value[moduleId] || {}),
            ...updates
        };

        localStorage.setItem("table_configs", JSON.stringify(tableConfigs.value));

        if (save && localStorage.getItem("token")) {
            api.auth
                .updateAppConfig({ 
                    table_configs: { 
                        [moduleId]: updates 
                    } 
                })
                .catch((err) => console.error(`Error updating config for ${moduleId}:`, err));
        }
    };

    /**
     * Set items per page globally (legacy support and fallback)
     */
    const setItemsPerPage = (value, save = true) => {
        const val = parseInt(value);
        itemsPerPage.value = val;
        localStorage.setItem("table_items_per_page", val);

        if (save && localStorage.getItem("token")) {
            api.auth.updateAppConfig({ items_per_page: val });
        }
    };

    const setViewMode = (mode, save = true) => {
        viewMode.value = mode;
        localStorage.setItem("table_view_mode", mode);

        if (save && localStorage.getItem("token")) {
            api.auth.updateAppConfig({ table_view_mode: mode });
        }
    };

    /**
     * Initialize config from user object
     */
    const initTableConfig = (config) => {
        if (!config) return;

        if (config.items_per_page) {
            itemsPerPage.value = parseInt(config.items_per_page);
            localStorage.setItem("table_items_per_page", config.items_per_page);
        }

        if (config.table_view_mode) {
            viewMode.value = config.table_view_mode;
            localStorage.setItem("table_view_mode", config.table_view_mode);
        }

        if (config.table_configs) {
            tableConfigs.value = config.table_configs;
            localStorage.setItem("table_configs", JSON.stringify(config.table_configs));
        }
    };

    return {
        itemsPerPage,
        viewMode,
        tableConfigs,
        getModuleConfig,
        updateModuleConfig,
        setItemsPerPage,
        setViewMode,
        initTableConfig,
    };
}
