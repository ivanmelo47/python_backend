import client from '../client';

export default {
    getPortfolios(params = {}) {
        return client.get('/auth/portfolios', { params });
    },
    getPortfolio(id) {
        return client.get(`/auth/portfolios/${id}`);
    },
    createPortfolio(data) {
        return client.post('/auth/portfolios', data);
    },
    updatePortfolio(id, data) {
        return client.put(`/auth/portfolios/${id}`, data);
    },
    uploadAvatar(id, file) {
        const formData = new FormData();
        formData.append('avatar_image', file);

        return client.post(`/auth/portfolios/${id}/avatar`, formData, {
            headers: {
                'Content-Type': 'multipart/form-data',
            },
        });
    },
    uploadJobImage(id, file) {
        return this.uploadPortfolioImage(id, file, 'job');
    },
    uploadPortfolioImage(id, file, mediaType = 'job') {
        const formData = new FormData();
        formData.append('image', file);
        formData.append('media_type', mediaType);

        return client.post(`/auth/portfolios/${id}/media`, formData, {
            headers: {
                'Content-Type': 'multipart/form-data',
            },
        });
    },
    uploadPortfolioCertificate(id, file) {
        const formData = new FormData();
        formData.append('file', file);
        formData.append('media_type', 'certificate');

        return client.post(`/auth/portfolios/${id}/media`, formData, {
            headers: {
                'Content-Type': 'multipart/form-data',
            },
        });
    },
    deletePortfolio(id) {
        return client.delete(`/auth/portfolios/${id}`);
    },
    getPublicPortfolio(token) {
        return client.get(`/auth/portfolios/public/${token}`);
    },
    sendPublicContact(token, payload) {
        return client.post(`/auth/portfolios/public/${token}/contact`, payload);
    },
    getDefaultPublicPortfolio() {
        return client.get('/auth/portfolios/public');
    },
    getPublicList() {
        return client.get('/auth/portfolios/public/list');
    },
};
