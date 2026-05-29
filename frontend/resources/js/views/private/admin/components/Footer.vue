<template>
    <footer class="dashboard-footer">
        <div class="footer-content">
            <p>&copy; {{ new Date().getFullYear() }} AdminPanel. Todos los derechos reservados.</p>
            <div class="footer-links">
                <a href="#" class="link">Términos</a>
                <a href="#" class="link">Privacidad</a>
                <a href="#" class="link">Soporte</a>
            </div>
        </div>
    </footer>
</template>

<style scoped>
.dashboard-footer {
    padding: 1.5rem 0 0 0;
    margin-top: auto;
    border-top: 1px solid var(--border-color);
    color: var(--text-tertiary);
    font-size: 0.875rem;
}

.footer-content {
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 1rem;
}

.footer-links {
    display: flex;
    gap: 1.5rem;
}

.link {
    color: var(--text-secondary);
    text-decoration: none;
    transition: color 0.2s;

    &:hover {
        color: var(--primary);
    }
}

@media (max-width: 768px) {
    .footer-content {
        flex-direction: column;
        text-align: center;
    }
}
</style>
