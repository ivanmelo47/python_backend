import client from '../client';

const emailsApi = {
    /**
     * Get system emails with pagination and search
     */
    getEmails(params = {}) {
        return client.get('/auth/system-emails', { params });
    },

    /**
     * Get a specific email
     */
    getEmail(uuid) {
        return client.get(`/auth/system-emails/${uuid}`);
    },

    /**
     * Delete an email
     */
    deleteEmail(uuid) {
        return client.delete(`/auth/system-emails/${uuid}`);
    }
};

export default emailsApi;
