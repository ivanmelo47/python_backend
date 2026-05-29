import apiClient from "../client";

const RESOURCE = "/auth/vault"; // Correct prefix based on api.php group

export default {
    index() {
        return apiClient.get(`${RESOURCE}`);
    },

    store(data) {
        return apiClient.post(`${RESOURCE}`, data);
    },

    show(id, masterPassword) {
        return apiClient.post(`${RESOURCE}/${id}/show`, {
            master_password: masterPassword,
        });
    },

    update(id, data) {
        return apiClient.put(`${RESOURCE}/${id}`, data);
    },

    destroy(id) {
        return apiClient.delete(`${RESOURCE}/${id}`);
    },
};
