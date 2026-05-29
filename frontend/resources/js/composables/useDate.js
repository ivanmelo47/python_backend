export const useDate = () => {
    const formatDate = (dateString, options = {}) => {
        if (!dateString) return '';
        try {
            // Se asume que si tiene 'T' ya es un ISO completo, si no, se fuerza a medianoche local
            const date = dateString.includes('T') ? new Date(dateString) : new Date(dateString + 'T00:00:00');
            return new Intl.DateTimeFormat('es-MX', {
                day: '2-digit',
                month: 'short',
                year: 'numeric',
                ...options
            }).format(date);
        } catch (e) {
            return dateString;
        }
    };

    const formatDateTime = (dateString) => {
        if (!dateString) return '';
        const date = new Date(dateString);
        return new Intl.DateTimeFormat('es-MX', {
            day: '2-digit',
            month: '2-digit',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        }).format(date);
    };

    return {
        formatDate,
        formatDateTime,
    };
};
