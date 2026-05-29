import client from "../client";

export default {
    getUsers(params = {}) {
        return client.get("/auth/users", { params });
    },
    createUser(data) {
        return client.post("/auth/users", data);
    },
    getRoles() {
        return client.get("/auth/roles");
    },
    /**
     * Get selectable users for dropdowns
     */
    getSelectableUsers: () => client.get("/auth/users/selectable"),
    toggleStatus(id) {
        return client.patch(`/auth/users/${id}/status`);
    },
    updateUser(id, data) {
        if (data.avatar_image) {
            const formData = new FormData();
            formData.append('_method', 'PUT');
            formData.append('name', data.name || '');
            formData.append('email', data.email || '');
            formData.append('role_id', String(data.role_id || ''));

            if (data.password) formData.append('password', data.password);
            if (data.password_confirmation) formData.append('password_confirmation', data.password_confirmation);
            if (data.avatar_image) formData.append('avatar_image', data.avatar_image, 'avatar.webp');

            return client.post(`/auth/users/${id}`, formData, {
                headers: { 'Content-Type': 'multipart/form-data' },
            });
        }

        return client.put(`/auth/users/${id}`, data);
    },
};
