import apiClient from "../client";

const ENDPOINT = '/auth/shared-links';

export default {
    /**
     * Get all shared links for the authenticated user.
     */
    getAll(params = {}) {
        return apiClient.get(ENDPOINT, { params });
    },

    /**
     * Create a new shared link for a file or folder.
     * @param {Object} data - { shareable_id, shareable_type, expires_at, passwords, excluded_folders }
     */
    create(data) {
        return apiClient.post(ENDPOINT, data);
    },

    /**
     * Update a shared link (is_active, expires_at, excluded_folders).
     * @param {String|Number} id
     * @param {Object} data 
     */
    update(id, data) {
        return apiClient.put(`${ENDPOINT}/${id}`, data);
    },

    /**
     * Delete a shared link permanently.
     * @param {String|Number} id 
     */
    delete(id) {
        return apiClient.delete(`${ENDPOINT}/${id}`);
    }
};
