<template>
  <div class="forbidden-page">
    <div class="content">
      <h1 class="error-code">403</h1>
      <h2 class="error-title">Acceso Denegado</h2>
      <p class="error-message">
        No tienes los permisos necesarios para acceder a esta sección. 
        Si crees que esto es un error, contacta con tu administrador.
      </p>
      <router-link to="/dashboard" class="back-btn">
        <Icon name="dashboard" :size="20" />
        <span>Volver al Inicio</span>
      </router-link>
    </div>
  </div>
</template>

<script setup>
import Icon from '@/components/Icon.vue';
</script>

<style lang="scss" scoped>
.forbidden-page {
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-primary);
  color: var(--text-primary);
  text-align: center;
  padding: 2rem;

  .content {
    max-width: 500px;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 1.5rem;
  }

  .error-code {
    font-size: 8rem;
    font-weight: 800;
    line-height: 1;
    background: linear-gradient(135deg, var(--primary), #8b5cf6);
    -webkit-background-clip: text;
    background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 0;
  }

  .error-title {
    font-size: 2rem;
    font-weight: 700;
    margin: 0;
  }

  .error-message {
    font-size: 1.125rem;
    color: var(--text-secondary);
    line-height: 1.6;
    margin: 0;
  }

  .back-btn {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 0.875rem 1.5rem;
    background: var(--primary);
    color: white;
    border-radius: 12px;
    text-decoration: none;
    font-weight: 600;
    transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
    box-shadow: 0 4px 12px rgba(var(--primary-rgb), 0.3);

    &:hover {
      transform: translateY(-2px);
      box-shadow: 0 6px 16px rgba(var(--primary-rgb), 0.4);
      filter: brightness(1.1);
    }

    &:active {
      transform: translateY(0);
    }
  }
}
</style>
