import { ref } from "vue";
import axios from "axios";
import { API_BASE_URL } from "@/services/api/url";

const apiBaseURL = API_BASE_URL;
const BASE_URL = `${apiBaseURL.replace(/\/$/, "")}/vault`;

export function useVault() {
    const loading = ref(false);
    const error = ref(null);

    const getItems = async () => {
        loading.value = true;
        try {
            const response = await axios.get(BASE_URL);
            return response.data;
        } catch (err) {
            error.value =
                err.response?.data?.message || "Error al cargar items";
            throw err;
        } finally {
            loading.value = false;
        }
    };

    const storeItem = async (data) => {
        loading.value = true;
        try {
            const response = await axios.post(BASE_URL, data);
            return response.data;
        } catch (err) {
            error.value =
                err.response?.data?.message || "Error al guardar contraseña";
            throw err;
        } finally {
            loading.value = false;
        }
    };

    const showPassword = async (id, masterPassword) => {
        loading.value = true;
        try {
            const response = await axios.post(`${BASE_URL}/${id}/show`, {
                master_password: masterPassword,
            });
            return response.data.password;
        } catch (err) {
            error.value =
                err.response?.data?.message || "Error al descifrar contraseña";
            throw err;
        } finally {
            loading.value = false;
        }
    };

    const deleteItem = async (id) => {
        loading.value = true;
        try {
            await axios.delete(`${BASE_URL}/${id}`);
        } catch (err) {
            error.value =
                err.response?.data?.message || "Error al eliminar item";
            throw err;
        } finally {
            loading.value = false;
        }
    };

    return {
        loading,
        error,
        getItems,
        storeItem,
        showPassword,
        deleteItem,
    };
}
