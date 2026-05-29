import client from "../client";

export default {
    getAll: (params) => client.get("/auth/icons", { params }),
    create: (data) => {
        // If svg_file or image_file is present, use FormData
        if (data.svg_file || data.image_file) {
            const formData = new FormData();
            formData.append("name", data.name);
            formData.append("type", data.type || "svg");
            if (data.color_mode) formData.append("color_mode", data.color_mode);
            if (data.storage_mode) formData.append("storage_mode", data.storage_mode);
            if (data.category) formData.append("category", data.category);
            
            if (data.svg_file) formData.append("svg_file", data.svg_file);
            if (data.svg_content) formData.append("svg_content", data.svg_content);
            if (data.image_file) formData.append("image_file", data.image_file, "cropped-image.webp");

            return client.post("/auth/icons", formData);
        }

        // Otherwise, send JSON
        return client.post("/auth/icons", data);
    },
    update: (uuid, data) => {
        // If file is present, use FormData
        if (data.svg_file || data.image_file) {
            const formData = new FormData();
            if (data.name) formData.append("name", data.name);
            if (data.type) formData.append("type", data.type);
            if (data.color_mode) formData.append("color_mode", data.color_mode);
            if (data.storage_mode) formData.append("storage_mode", data.storage_mode);
            if (data.category) formData.append("category", data.category);
            
            if (data.svg_file) formData.append("svg_file", data.svg_file);
            if (data.svg_content) formData.append("svg_content", data.svg_content);
            if (data.image_file) formData.append("image_file", data.image_file, "cropped-image.webp");
            
            formData.append("_method", "PUT"); // Laravel method spoofing

            return client.post(`/auth/icons/${uuid}`, formData);
        }

        return client.put(`/auth/icons/${uuid}`, data);
    },
    delete: (uuid) => client.delete(`/auth/icons/${uuid}`),
    toggleStatus: (uuid) => client.post(`/auth/icons/${uuid}/toggle-status`),
    export: () => client.get('/auth/icons/export', { responseType: 'blob' }),
    import: (file) => {
        const formData = new FormData();
        formData.append('file', file);
        return client.post('/auth/icons/import', formData);
    },
};
