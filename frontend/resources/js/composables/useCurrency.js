export const useCurrency = () => {
    const formatCurrency = (value, currency = 'MXN') => {
        if (value === null || value === undefined) return '';
        return new Intl.NumberFormat('es-MX', {
            style: 'currency',
            currency: currency,
        }).format(value);
    };

    return {
        formatCurrency,
    };
};
