import apiClient from "../client";

/**
 * Files Management Endpoints
 */
const files = {
    /**
     * List files in a folder context
     * @param {Object} params { folder_uuid, search, per_page, page }
     */
    getFiles: (params = {}) => apiClient.get("/auth/files", { params }),

    /**
     * Upload a file
     * @param {File|Blob} file
     * @param {string|null} folderUuid
     * @param {Object} options Axios request options
     * @param {string} conflictStrategy
     * @param {string|null} encryptionPassword
     */
    uploadFile: (
        file,
        folderUuid = null,
        options = {},
        conflictStrategy = "ask",
        encryptionPassword = null,
    ) => {
        const formData = new FormData();
        formData.append("file", file);

        if (folderUuid) {
            formData.append("folder_uuid", folderUuid);
        }

        if (conflictStrategy) {
            formData.append("conflict_strategy", conflictStrategy);
        }

        if (encryptionPassword) {
            formData.append("encryption_password", encryptionPassword);
        }

        return apiClient.post("/auth/files/upload", formData, {
            headers: {
                "Content-Type": "multipart/form-data",
            },
            timeout: 0,
            maxBodyLength: Infinity,
            maxContentLength: Infinity,
            ...options,
        });
    },

    /**
     * Create an external link as managed item
     * @param {Object} payload { name, url, icon_uuid?, folder_uuid? }
     */
    createLink: (payload = {}) => apiClient.post("/auth/files/link", payload),

    /**
     * Delete file by uuid
     * @param {string} uuid
     */
    deleteFile: (uuid) => apiClient.delete(`/auth/files/${uuid}`),

    /**
     * Update file metadata
     * @param {string} uuid
     * @param {Object} payload
     */
    updateFile: (uuid, payload = {}) =>
        apiClient.put(`/auth/files/${uuid}`, payload),

    /**
     * Move file to another folder (or root with null folder_uuid)
     * @param {string} uuid
     * @param {Object} payload { folder_uuid: string|null }
     */
    moveFile: (uuid, payload = {}) =>
        apiClient.post(`/auth/files/${uuid}/move`, payload),

    /**
     * Download file by uuid
     * @param {string} uuid
     */
    downloadFile: (uuid) =>
        apiClient.get(`/auth/files/${uuid}/download`, {
            responseType: "blob",
        }),

    /**
     * Get file preview (optimized WebP for images when available)
     * @param {string} uuid
     */
    previewFile: (uuid) =>
        apiClient.get(`/auth/files/${uuid}/preview`, {
            responseType: "blob",
        }),

    /**
     * Verify password for encrypted file
     * @param {string} uuid
     * @param {string} password
     */
    verifyPassword: (uuid, password) =>
        apiClient.post(`/auth/files/${uuid}/verify-password`, {
            password,
        }),

    /**
     * Download encrypted file with password
     * @param {string} uuid
     * @param {string} password
     */
    downloadEncryptedFile: (uuid, password) =>
        apiClient.post(
            `/auth/files/${uuid}/download-encrypted`,
            {
                password,
            },
            {
                responseType: "blob",
            },
        ),

    /**
     * Get OnlyOffice viewer config for office-compatible files
     * @param {string} uuid
     */
    getOnlyOfficeConfig: (uuid) =>
        apiClient.get(`/auth/files/${uuid}/onlyoffice-config`),

    /**
     * Request fallback conversion from PDF to editable Word in OnlyOffice flow
     * @param {string} uuid
     */
    requestOnlyOfficePdfFallback: (uuid) =>
        apiClient.post(`/auth/files/${uuid}/onlyoffice-pdf-fallback`),

    /**
     * Trigger manual synchronization from OnlyOffice editor to original file
     * @param {string} uuid
     * @param {Object} payload { document_key? }
     */
    syncOnlyOfficeFile: (uuid, payload = {}) =>
        apiClient.post(`/auth/files/${uuid}/onlyoffice-sync`, payload),

    /**
     * Encrypt an existing unencrypted file
     * @param {string} uuid
     * @param {Object} payload { password }
     */
    encryptFile: (uuid, payload = {}) =>
        apiClient.post(`/auth/files/${uuid}/encrypt`, payload),

    /**
     * Decrypt an existing encrypted file
     * @param {string} uuid
     * @param {Object} payload { password }
     */
    decryptFile: (uuid, payload = {}) =>
        apiClient.post(`/auth/files/${uuid}/decrypt`, payload),
};

export default files;
