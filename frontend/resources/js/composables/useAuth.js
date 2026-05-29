import { ref, computed } from "vue";
import { api } from "@/services/api";
import { useTheme } from "./useTheme";
import { useColorPalette } from "./useColorPalette";
import { useScale } from "./useScale";
import { useTableConfig } from "./useTableConfig";

const APP_CONFIG_VERSION_KEY = "app_config_version";

const getStoredConfigVersion = () => {
    const raw = Number(localStorage.getItem(APP_CONFIG_VERSION_KEY) || 0);
    return Number.isFinite(raw) ? raw : 0;
};

const parseConfigVersion = (config) => {
    const raw = config?.updated_at || config?.updatedAt || null;
    if (!raw) return 0;
    const timestamp = new Date(raw).getTime();
    return Number.isFinite(timestamp) ? timestamp : 0;
};

const setStoredConfigVersion = (version) => {
    const safeVersion = Number(version) || 0;
    localStorage.setItem(APP_CONFIG_VERSION_KEY, String(safeVersion));
};

// Shared state
const getUserFromStorage = () => {
    try {
        const stored = localStorage.getItem("user");
        if (!stored || stored === "undefined" || stored === "null") return null;
        return JSON.parse(stored);
    } catch {
        localStorage.removeItem("user");
        return null;
    }
};

const user = ref(getUserFromStorage());
const token = ref(localStorage.getItem("token") || null);
let syncInterval = null;
let bootSyncDone = false;
let storageConfigApplied = false;

export function useAuth() {
    const isAuthenticated = computed(() => !!token.value);
    const userRole = computed(() => user.value?.role || "huesped");

    const theme = useTheme();
    const colorPalette = useColorPalette();
    const scale = useScale();
    const tableConfig = useTableConfig();

    /**
     * Synchronize user configuration with backend settings
     */
    const syncWithBackend = (userData, options = {}) => {
        if (!userData || !userData.config) {
            return false;
        }

        const { force = false } = options;
        const incomingVersion = parseConfigVersion(userData.config);
        const currentVersion = getStoredConfigVersion();

        if (!force && incomingVersion && currentVersion && incomingVersion < currentVersion) {
            return false;
        }

        theme.setTheme(userData.config.theme || "light", false);
        colorPalette.setPalette(
            userData.config.color_palette || "default",
            false,
        );
        scale.setScale(userData.config.app_scale || "100", false);
        tableConfig.initTableConfig(userData.config);

        const appliedVersion = incomingVersion || currentVersion || Date.now();
        setStoredConfigVersion(appliedVersion);
        return true;
    };

    /**
     * Set authentication data
     */
    const setAuth = (userData, userToken, userRefreshToken = null) => {
        user.value = userData;
        token.value = userToken;
        localStorage.setItem("user", JSON.stringify(userData));
        localStorage.setItem("token", userToken);
        if (userRefreshToken) localStorage.setItem("refresh_token", userRefreshToken);

        // Apply config if present
        syncWithBackend(userData, { force: true });

        startSync();
    };

    /**
     * Stop periodic synchronization
     */
    const stopSync = () => {
        if (syncInterval) {
            clearInterval(syncInterval);
            syncInterval = null;
        }
    };

    /**
     * Start periodic synchronization (every 10 minutes)
     */
    const startSync = () => {
        if (syncInterval) return;
        syncInterval = setInterval(syncProfile, 10 * 60 * 1000);
    };

    /**
     * Sync user profile with server
     */
    const syncProfile = async () => {
        if (!token.value) return;
        try {
            const response = await api.auth.me();
            if (!response || !response.data) {
                return;
            }
            const userData = response.data.data;
            user.value = userData;
            localStorage.setItem("user", JSON.stringify(userData));
            syncWithBackend(userData);
        } catch (error) {
            console.error("Error syncing profile:", error);
            // If it's a 401, the interceptor will handle it
        }
    };

    const updateProfile = async (data) => {
        const response = await api.auth.updateProfile(data);
        const userData = response?.data?.data?.user;

        if (userData) {
            user.value = userData;
            localStorage.setItem("user", JSON.stringify(userData));
            syncWithBackend(userData, { force: true });
        }

        return response;
    };

    /**
     * Clear authentication data
     */
    const clearAuth = () => {
        stopSync();
        user.value = null;
        token.value = null;
        bootSyncDone = false;
        storageConfigApplied = false;
        localStorage.removeItem(APP_CONFIG_VERSION_KEY);
        localStorage.clear();
    };

    /**
     * Login
     */
    const login = async (credentials) => {
        try {
            const response = await api.auth.login(credentials);
            const { user: userData, token: tokenData } = response.data.data;
            const { access_token, refresh_token } = tokenData || {};
            setAuth(userData, access_token, refresh_token);
            return {
                success: true,
                status: response.data.code === 200 ? "success" : "error",
                icon: response.data.code === 200 ? "success" : "error",
                data: response.data.data,
            };
        } catch (error) {
            const apiRes = error.response?.data;
            let errorMessage =
                apiRes?.message ||
                apiRes?.detail ||
                apiRes?.data?.message ||
                "Error al iniciar sesión";

            // If message is still generic or empty, check if 'data' is a string message
            if (typeof apiRes?.data === "string") {
                errorMessage = apiRes.data;
            }

            return {
                success: false,
                status: apiRes?.status || "error",
                icon: apiRes?.icon || "error",
                // Ensure we return the extracted message
                message: Array.isArray(errorMessage) ? errorMessage[0]?.msg || JSON.stringify(errorMessage) : errorMessage,
            };
        }
    };

    /**
     * Register
     */
    const register = async (userData) => {
        try {
            const response = await api.auth.register(userData);
            return {
                success: true,
                status: response.data.code === 201 || response.data.code === 200 ? "success" : "error",
                icon: response.data.code === 201 || response.data.code === 200 ? "success" : "error",
                data: response.data.data,
            };
        } catch (error) {
            const apiRes = error.response?.data;
            return {
                success: false,
                status: apiRes?.status || "error",
                icon: apiRes?.icon || "error",
                message: apiRes?.message || apiRes?.detail || apiRes?.data || "Error en el registro",
            };
        }
    };

    /**
     * Confirm Account
     */
    const confirmAccount = async (confirmationToken) => {
        try {
            await api.auth.confirm(confirmationToken);
            return { success: true };
        } catch (error) {
            return {
                success: false,
                message:
                    error.response?.data?.message || error.response?.data?.detail ||
                    "Token inválido o expirado",
            };
        }
    };

    /**
     * Refresh Token
     */
    const refreshToken = async (logoutOnError = true) => {
        try {
            const response = await api.auth.refresh();
            const { user: userData, token: tokenData } = response.data.data;
            const { access_token, refresh_token } = tokenData || {};
            setAuth(userData, access_token, refresh_token);
            return access_token;
        } catch (error) {
            if (logoutOnError) {
                clearAuth();
            }
            throw error;
        }
    };

    /**
     * Logout
     */
    const logout = async () => {
        try {
            // Local logout primarily. We omit api.auth.logout() because FastAPI doesn't have a generic /auth/logout
            // It uses /auth/sessions/{uuid} which we don't track client-side right now.
        } catch (error) {
            console.error("Error during logout:", error);
        } finally {
            clearAuth();
        }
    };

    /**
     * Request password reset link
     */
    const forgotPassword = async (email) => {
        try {
            const response = await api.auth.forgotPassword({ email });
            return {
                success: true,
                status: response.data.code === 200 ? "success" : "error",
                icon: response.data.code === 200 ? "success" : "error",
                data: response.data.data,
            };
        } catch (error) {
            const apiRes = error.response?.data;
            return {
                success: false,
                status: apiRes?.status || "error",
                icon: apiRes?.icon || "error",
                message:
                    apiRes?.message || apiRes?.detail || "Error al solicitar el enlace",
            };
        }
    };

    /**
     * Validate reset token
     */
    const validateResetToken = async (data) => {
        try {
            await api.auth.validateResetToken(data);
            return { success: true };
        } catch (error) {
            // Screenshot shows: { code: 400, data: { message: "..." } }
            // So we need error.response.data.data.message
            const apiRes = error.response?.data;
            const msg = apiRes?.message || apiRes?.detail || "Token inválido";

            return {
                success: false,
                message: msg,
            };
        }
    };

    /**
     * Reset password
     */
    const resetPassword = async (data) => {
        try {
            const response = await api.auth.resetPassword(data);
            return {
                success: true,
                status: response.data.code === 200 ? "success" : "error",
                icon: response.data.code === 200 ? "success" : "error",
                data: response.data.data,
            };
        } catch (error) {
            const apiRes = error.response?.data;
            return {
                success: false,
                status: apiRes?.status || "error",
                icon: apiRes?.icon || "error",
                message:
                    apiRes?.message || apiRes?.detail ||
                    "Error al restablecer la contraseña",
            };
        }
    };

    if (isAuthenticated.value && user.value?.config && !storageConfigApplied) {
        syncWithBackend(user.value);
        storageConfigApplied = true;
    }

    // Auto-start sync if already authenticated on load
    if (isAuthenticated.value && !syncInterval) {
        startSync();
    }

    // Force one immediate sync on app bootstrap so localStorage mirrors DB config
    if (isAuthenticated.value && !bootSyncDone) {
        bootSyncDone = true;
        syncProfile();
    }

    return {
        user,
        token,
        isAuthenticated,
        userRole,
        login,
        register,
        confirmAccount,
        forgotPassword,
        resetPassword,
        logout,
        refreshToken,
        syncProfile,
        updateProfile,
    };
}
