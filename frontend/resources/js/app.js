import { createApp } from "vue";
import App from "./App.vue";
import router from "./routes";
import "../sass/app.scss";

import { useDynamicRoutes } from './composables/useDynamicRoutes';

// Create and mount app
const app = createApp(App);

// Suppress console logs in production
if (import.meta.env.VITE_APP_ENV === "production") {
    const noop = () => { };
    console.log = noop;
    console.info = noop;
    console.debug = noop;
    // We keep console.warn and console.error for critical issues
}

// Custom directive for clicking outside
app.directive("click-outside", {
    mounted(el, binding) {
        el.clickOutsideEvent = function (event) {
            if (!(el === event.target || el.contains(event.target))) {
                binding.value(event, el);
            }
        };
        document.body.addEventListener("click", el.clickOutsideEvent);
    },
    unmounted(el) {
        document.body.removeEventListener("click", el.clickOutsideEvent);
    },
});

app.use(router);

/**
 * Async Bootstrap
 * Ensures critical data (like dynamic routes) is loaded before the first render
 * if the user is already authenticated.
 */
async function init() {
    const token = localStorage.getItem('token');

    if (token) {
        try {
            const { fetchAndRegisterRoutes } = useDynamicRoutes();

            console.debug('[Bootstrap] Usuario autenticado detectado. Cargando rutas...');
            await fetchAndRegisterRoutes(router);
        } catch (error) {
            console.error('[Bootstrap] Error durante la carga inicial:', error);
        }
    }

    app.mount("#app");
}

init();
