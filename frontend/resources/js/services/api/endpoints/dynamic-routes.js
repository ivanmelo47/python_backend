import client from "../client";

export default {
    getAll: (params) => client.get("/auth/dynamic-routes", { params }),
    getActive: () => client.get("/auth/active-dynamic-routes"),
    create: (data) => client.post("/auth/dynamic-routes", data),
    update: (uuid, data) => client.put(`/auth/dynamic-routes/${uuid}`, data),
    delete: (uuid) => client.delete(`/auth/dynamic-routes/${uuid}`),
    toggleStatus: (uuid) => client.patch(`/auth/dynamic-routes/${uuid}/status`),
};
