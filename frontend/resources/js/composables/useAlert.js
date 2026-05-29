import { ref, reactive } from "vue";

// Global state
const toasts = ref([]);
const modal = reactive({
    show: false,
    type: "info", // success, error, warning, info
    title: "",
    text: "",
    showCancel: false,
    showNeutral: false,
    confirmText: "Aceptar",
    cancelText: "Cancelar",
    neutralText: "",
    onConfirm: null,
    onCancel: null,
    onNeutral: null,
});

// Counter for unique Toast IDs
let toastId = 0;

export function useAlert() {
    // ============================
    // TOAST METHODS
    // ============================

    const toast = (type, title, text = "", duration = 3000) => {
        const id = toastId++;
        const newToast = { id, type, title, text };

        toasts.value.push(newToast);

        // Auto remove
        if (duration > 0) {
            setTimeout(() => {
                removeToast(id);
            }, duration);
        }
    };

    const removeToast = (id) => {
        const index = toasts.value.findIndex((t) => t.id === id);
        if (index !== -1) {
            toasts.value.splice(index, 1);
        }
    };

    // Convenience methods
    const toastSuccess = (title, text, duration) =>
        toast("success", title, text, duration);
    const toastError = (title, text, duration) =>
        toast("error", title, text, duration);
    const toastWarning = (title, text, duration) =>
        toast("warning", title, text, duration);
    const toastInfo = (title, text, duration) =>
        toast("info", title, text, duration);

    // ============================
    // MODAL METHODS
    // ============================

    const fireModal = (options) => {
        return new Promise((resolve, reject) => {
            modal.type = options.type || "info";
            modal.title = options.title || "Alerta";
            modal.text = options.text || "";
            modal.showCancel = options.showCancel || false;
            modal.showNeutral = options.showNeutral || false;
            modal.confirmText = options.confirmText || "Aceptar";
            modal.cancelText = options.cancelText || "Cancelar";
            modal.neutralText = options.neutralText || "";
            modal.show = true;

            modal.onConfirm = () => {
                modal.show = false;
                resolve(true);
            };

            modal.onCancel = () => {
                modal.show = false;
                resolve(false);
            };

            modal.onNeutral = () => {
                modal.show = false;
                resolve('neutral');
            };
        });
    };

    // Loading Method
    const showLoading = (title = "Cargando...", text = "Por favor espere") => {
        modal.type = "loading"; // New type for loading
        modal.title = title;
        modal.text = text;
        modal.showCancel = false;
        modal.showNeutral = false;
        modal.confirmText = "";
        modal.cancelText = "";
        modal.neutralText = "";
        modal.show = true;
        // No callbacks needed as it's programmatically closed
    };

    const closeLoading = () => {
        if (modal.type === "loading") {
            modal.show = false;
        }
    };

    const confirm = (title, text, type = "warning") => {
        return fireModal({
            title,
            text,
            type,
            showCancel: true,
            confirmText: "Aceptar",
            cancelText: "Cancelar",
        });
    };

    return {
        toasts,
        modal,
        removeToast,
        // Toast API
        toast: {
            success: toastSuccess,
            error: toastError,
            warning: toastWarning,
            info: toastInfo,
        },
        // Modal API
        fire: fireModal,
        confirm,
        showLoading,
        closeLoading,
    };
}
