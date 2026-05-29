import apiClient from "../client";

/**
 * Folder Management Endpoints
 */
const folders = {
    /**
     * List mixed explorer items (folders + files) paginated
     * @param {Object} params { parent, search, per_page, page }
     */
    getExplorerItems: (params = {}) => apiClient.get("/auth/explorer-items", { params }),

    /**
     * List folders
     * @param {Object} params { parent }
     */
    getFolders: (params = {}) => apiClient.get("/auth/folders", { params }),

    /**
     * Create folder
     * @param {Object} data { name, parent_uuid, is_public }
     */
    createFolder: (data) => apiClient.post("/auth/folders", data),

    /**
     * Update folder
     * @param {string} uuid
     * @param {Object} data { name, is_public }
     */
    updateFolder: (uuid, data) => apiClient.put(`/auth/folders/${uuid}`, data),

    /**
     * Delete folder
     * @param {string} uuid
     */
    deleteFolder: (uuid) => apiClient.delete(`/auth/folders/${uuid}`),

    /**
     * Get descendants tree for a folder
     * @param {string} uuid
     */
    getDescendants: (uuid) =>
        apiClient.get(`/auth/folders/${uuid}/descendants`),

    /**
     * Bulk update privacy for folders
     * @param {Object} data { uuids: [], is_public: boolean }
     */
    bulkUpdatePrivacy: (data) =>
        apiClient.post("/auth/folders/bulk-privacy", data),

    /**
     * Get users that can be shared with
     */
    getShareableUsers: () => apiClient.get("/auth/folders/shareable-users"),
};

export default folders;
