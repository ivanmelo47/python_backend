import apiClient from "../client";

export const settingsApi = {
    /**
     * List file configurations
     * @param {Object} params { page, per_page, search }
     */
    getFileConfigurations: (params = {}) =>
        apiClient.get("/auth/settings/file-configuration", { params }),

    /**
     * Add new file configuration
     */
    createFileConfiguration: (data) =>
        apiClient.post("/auth/settings/file-configuration", data),

    /**
     * Update file configuration
     */
    updateFileConfiguration: (id, data) =>
        apiClient.put(`/auth/settings/file-configuration/${id}`, data),

    /**
     * Delete file configuration
     */
    deleteFileConfiguration: (id) =>
        apiClient.delete(`/auth/settings/file-configuration/${id}`),

    /**
     * Toggle status
     */
    toggleFileConfigurationStatus: (id) =>
        apiClient.patch(`/auth/settings/file-configuration/${id}/status`),
};
