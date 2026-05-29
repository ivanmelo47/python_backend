import apiClient from "../client";

export const finanzasApi = {
    // Summary
    getResumen: () => apiClient.get("/finanzas/resumen"),

    // Savings Accounts
    getCuentasAhorro: (params) => apiClient.get("/finanzas/cuentas-ahorro", { params }),
    storeCuentaAhorro: (data) => apiClient.post("/finanzas/cuentas-ahorro", data),
    showCuentaAhorro: (id) => apiClient.get(`/finanzas/cuentas-ahorro/${id}`),
    updateCuentaAhorro: (id, data) => apiClient.put(`/finanzas/cuentas-ahorro/${id}`, data),
    deleteCuentaAhorro: (id) => apiClient.delete(`/finanzas/cuentas-ahorro/${id}`),
    calculateYield: (id) => apiClient.post(`/finanzas/cuentas-ahorro/${id}/calculate-yield`),
    rebalanceYields: (id) => apiClient.post(`/finanzas/cuentas-ahorro/${id}/rebalance`),
    getAccountMovements: (id) => apiClient.get(`/finanzas/movimientos`, { params: { cuenta_id: id, per_page: 100 } }),
    getCuentaProyeccion: (id) => apiClient.get(`/finanzas/cuentas-ahorro/${id}/proyeccion`),
    getProyeccionGeneralAhorro: (params) => apiClient.get("/finanzas/cuentas-ahorro/proyeccion-general", { params }),

    // Sections (Buckets)
    getSecciones: (cuentaUuid) => apiClient.get(`/finanzas/cuentas-ahorro/${cuentaUuid}/secciones`),
    storeSeccion: (data) => apiClient.post("/finanzas/secciones", data),
    updateSeccion: (uuid, data) => apiClient.put(`/finanzas/secciones/${uuid}`, data),
    deleteSeccion: (uuid) => apiClient.delete(`/finanzas/secciones/${uuid}`),
    transferSeccion: (data) => apiClient.post("/finanzas/secciones/transfer", data),

    // Movements
    getMovimientos: (params) => apiClient.get("/finanzas/movimientos", { params }),
    storeMovimiento: (data) => apiClient.post("/finanzas/movimientos", data),
    deleteMovimiento: (id) => apiClient.delete(`/finanzas/movimientos/${id}`),
    // Historical Rates
    getTasas: (id) => apiClient.get(`/finanzas/cuentas-ahorro/${id}/tasas`),
    storeTasa: (id, data) => apiClient.post(`/finanzas/cuentas-ahorro/${id}/tasas`, data),
    deleteTasa: (id, tasaId) => apiClient.delete(`/finanzas/cuentas-ahorro/${id}/tasas/${tasaId}`),

    // Scheduled Movements
    getProgramados: () => apiClient.get("/finanzas/movimientos-programados"),
    storeProgramado: (data) => apiClient.post("/finanzas/movimientos-programados", data),
    updateProgramado: (id, data) => apiClient.put(`/finanzas/movimientos-programados/${id}`, data),
    deleteProgramado: (id) => apiClient.delete(`/finanzas/movimientos-programados/${id}`),

    // Categories
    getCategorias: () => apiClient.get("/finanzas/categorias"),
    storeCategoria: (data) => apiClient.post("/finanzas/categorias", data),
    updateCategoria: (id, data) => apiClient.put(`/finanzas/categorias/${id}`, data),
    deleteCategoria: (id) => apiClient.delete(`/finanzas/categorias/${id}`),

    // Credit Cards
    getTarjetas: (params) => apiClient.get("/finanzas/tarjetas-credito", { params }),
    storeTarjeta: (data) => apiClient.post("/finanzas/tarjetas-credito", data),
    showTarjeta: (id) => apiClient.get(`/finanzas/tarjetas-credito/${id}`),
    updateTarjeta: (id, data) => apiClient.put(`/finanzas/tarjetas-credito/${id}`, data),
    deleteTarjeta: (id) => apiClient.delete(`/finanzas/tarjetas-credito/${id}`),
    pagarTarjeta: (id, data) => apiClient.post(`/finanzas/tarjetas-credito/${id}/pagar`, data),
    compraHistoricaTarjeta: (id, data) => apiClient.post(`/finanzas/tarjetas-credito/${id}/compra-historica`, data),
    getTarjetaCompras: (id, params) => apiClient.get(`/finanzas/tarjetas-credito/${id}/compras`, { params }),
    getTarjetaAbonos: (id, movimientoId) => apiClient.get(`/finanzas/tarjetas-credito/${id}/movimientos/${movimientoId}/abonos`),
    getTarjetaMovimientos: (id) => apiClient.get(`/finanzas/tarjetas-credito/${id}/movimientos`),
    deleteTarjetaMovimiento: (tarjetaId, movId) => apiClient.delete(`/finanzas/tarjetas-credito/${tarjetaId}/movimientos/${movId}`),
    getTarjetaProyeccion: (id) => apiClient.get(`/finanzas/tarjetas-credito/${id}/proyeccion`),
    getProyeccionGeneralTarjetas: () => apiClient.get("/finanzas/tarjetas-credito/proyeccion-general"),

    // Attachments (Adjuntos)
    getAdjuntos: (movimientoUuid) => apiClient.get(`/finanzas/movimientos/${movimientoUuid}/adjuntos`),
    uploadAdjunto: (movimientoUuid, file) => {
        const formData = new FormData();
        formData.append('file', file);
        return apiClient.post(`/finanzas/movimientos/${movimientoUuid}/adjuntos`, formData, {
            headers: { 'Content-Type': 'multipart/form-data' }
        });
    },
    deleteAdjunto: (uuid) => apiClient.delete(`/finanzas/adjuntos/${uuid}`),
};
