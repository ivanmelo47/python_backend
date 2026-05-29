import apiClient from "../client";

export default {
    getMaintenanceMode() {
        return apiClient.get("/auth/system-config/maintenance");
    },
    toggleMaintenanceMode(payload) {
        // Support both boolean (legacy) and object (new)
        const data =
            typeof payload === "object" ? payload : { status: payload };
        return apiClient.post("/auth/system-config/maintenance", data);
    },
    getPerformanceMetrics() {
        return apiClient.get("/auth/system-config/performance");
    },
    requestFullBackup() {
        return apiClient.post("/auth/system-config/full-backup/request");
    },
    cancelActiveBackups() {
        return apiClient.post("/auth/system-config/full-backup/cancel-active");
    },
    requestFullRestore(formData) {
        return apiClient.post("/auth/system-config/full-restore/request", formData, {
            timeout: 0,
        });
    },
    getLatestFullBackup() {
        return apiClient.get("/auth/system-config/full-backup/latest");
    },
    getFullBackupHistory() {
        return apiClient.get("/auth/system-config/full-backup/history");
    },
    getLocalBackups() {
        return apiClient.get("/auth/system-config/local-backups");
    },
    getMailSettings() {
        return apiClient.get("/auth/system-config/mail");
    },
    updateMailSettings(data) {
        return apiClient.post("/auth/system-config/mail", data);
    },
    getOnlyOfficeSettings() {
        return apiClient.get("/auth/system-config/onlyoffice");
    },
    updateOnlyOfficeSettings(data) {
        return apiClient.post("/auth/system-config/onlyoffice", data);
    },
    getVisualSettings() {
        return apiClient.get("/auth/system-config/visual");
    },
    updateVisualSettings(data) {
        return apiClient.post("/auth/system-config/visual", data);
    }
};
