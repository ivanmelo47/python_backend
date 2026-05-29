<template>
    <div id="app">
        <div class="container text-center">
            <div class="card mt-4">
                <h1>404</h1>
                <h2>Página no encontrada</h2>
                <p class="mt-3">La página que buscas no existe.</p>
                <router-link to="/" class="btn mt-3">
                    Volver al inicio
                </router-link>
            </div>
        </div>
    </div>
</template>

<script setup>
// 404 Not Found page
</script>

<style scoped lang="scss">
h1 {
    font-size: 6rem;
    color: #35495e;
    margin-bottom: 1rem;
}

h2 {
    color: #42b983;
    margin-bottom: 0.5rem;
}

.card {
    max-width: 600px;
    margin: 4rem auto;
}
</style>
