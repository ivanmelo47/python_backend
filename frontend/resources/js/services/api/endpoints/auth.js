import apiClient from "../client";

/**
 * Authentication Endpoints
 */
const auth = {
    /**
     * Login user
     * @param {Object} credentials { email, password }
     */
    login: (credentials) => apiClient.post("/auth/login", credentials),

    /**
     * Register user
     * @param {Object} userData
     */
    register: (userData) => apiClient.post("/auth/register", userData),

    /**
     * Confirm account via token
     * @param {string} token
     */
    confirm: (token) => apiClient.get(`/auth/confirm/${token}`),

    /**
     * Logout user
     */
    logout: () => apiClient.post("/auth/logout"),

    /**
     * Get current user profile
     */
    me: () => apiClient.get("/auth/me"),

    /**
     * Update current user profile
     * @param {Object} data
     */
    updateProfile: (data) => {
        if (data.avatar_image) {
            const formData = new FormData();
            formData.append('_method', 'PUT');
            formData.append('name', data.name || '');

            if (data.current_password) formData.append('current_password', data.current_password);
            if (data.password) formData.append('password', data.password);
            if (data.password_confirmation) formData.append('password_confirmation', data.password_confirmation);
            if (data.avatar_image) formData.append('avatar_image', data.avatar_image, 'avatar.webp');

            return apiClient.post('/auth/me', formData, {
                headers: { 'Content-Type': 'multipart/form-data' },
            });
        }

        return apiClient.put('/auth/me', data);
    },

    /**
     * Refresh token
     */
    refresh: () => apiClient.post("/auth/refresh"),

    /**
     * Request password reset link
     * @param {Object} data { email }
     */
    forgotPassword: (data) => apiClient.post("/auth/forgot-password", data),

    /**
     * Validate reset token
     * @param {Object} data { token, email }
     */
    validateResetToken: (data) =>
        apiClient.post("/auth/validate-reset-token", data),

    /**
     * Reset password
     * @param {Object} data { token, email, password, password_confirmation }
     */
    resetPassword: (data) => apiClient.post("/auth/reset-password", data),

    /**
     * Get password reset tokens
     * @param {Object} params { page, per_page, search }
     */
    getPasswordResetTokens: (params = {}) =>
        apiClient.get("/auth/password-reset-tokens", { params }),

    /**
     * Get login activities
     * @param {Object} params { page, per_page, search }
     */
    getLoginActivities: (params = {}) =>
        apiClient.get("/auth/login-activities", { params }),

    /**
     * Resend password reset link
     * @param {number} id
     */
    resendResetLink: (id) => apiClient.post(`/auth/resend-reset-link/${id}`),

    /**
     * Send admin reset link (New Request)
     * @param {number} userId
     */
    sendAdminResetLink: (userId) =>
        apiClient.post("/auth/send-admin-reset-link", { user_id: userId }),

    /**
     * Force logout session
     * @param {number} id
     */
    forceLogout: (id) => apiClient.post(`/auth/force-logout/${id}`),

    /**
     * Update user app config
     * @param {Object} data { theme, color_palette, app_scale, table_view_mode }
     */
    updateAppConfig: (data) => apiClient.post("/auth/app-config", data),
};

export default auth;
