import client from "../client";

const RESOURCE = "/auth/cus-alliance-complaints";

export default {
    /**
     * Get all complaints with pagination and search
     */
    getAll(params = {}) {
        return client.get(RESOURCE, { params });
    },

    /**
     * Get a single complaint by UUID
     */
    get(uuid) {
        return client.get(`${RESOURCE}/${uuid}`);
    },

    /**
     * Create a new complaint
     */
    create(data) {
        return client.post(RESOURCE, data);
    },

    /**
     * Update an existing complaint
     */
    update(uuid, data) {
        return client.put(`${RESOURCE}/${uuid}`, data);
    },

    /**
     * Delete a complaint
     */
    delete(uuid) {
        return client.delete(`${RESOURCE}/${uuid}`);
    },
};
