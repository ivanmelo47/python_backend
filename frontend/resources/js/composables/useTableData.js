import { ref } from "vue";
import { useAlert } from "@/composables/useAlert";

export function useTableData(apiFetcher, options = {}) {
    const {
        transformer = (item) => item,
        mode = "server", // 'server' | 'client'
        onError = (error) => console.error("Data fetch error:", error),
    } = options;

    const { toast } = useAlert();

    const data = ref([]);
    const loading = ref(false);
    const pagination = ref({
        current_page: 1,
        last_page: 1,
        from: 0,
        to: 0,
        total: 0,
    });

    const fetchData = async (params = {}) => {
        loading.value = true;

        // Use provided refs as defaults if params are missing keys
        const finalParams = {
            per_page:
                params.per_page !== undefined
                    ? params.per_page
                    : options.itemsPerPage?.value || 10,
            search:
                params.search !== undefined
                    ? params.search
                    : options.searchQuery?.value || "",
            sort_by:
                params.sort_by !== undefined
                    ? params.sort_by
                    : options.sortBy?.value || "",
            sort_order:
                params.sort_order !== undefined
                    ? params.sort_order
                    : options.sortOrder?.value || "desc",
            page: params.page || 1,
            ...params,
        };

        try {
            const response = await apiFetcher(finalParams);
            const responseData = response.data;

            // Format data using the provided transformer
            data.value = (responseData.data || []).map(transformer);

            // Update pagination only if in server mode and metadata exists
            if (mode === "server" && responseData.meta) {
                pagination.value = {
                    current_page: responseData.meta.current_page,
                    last_page: responseData.meta.last_page,
                    from: responseData.meta.from,
                    to: responseData.meta.to,
                    total: responseData.meta.total,
                };
            }
            return response;
        } catch (error) {
            onError(error);
            const message =
                error.response?.data?.message || "Error al cargar datos";
            toast.error("Error", message);
        } finally {
            loading.value = false;
        }
    };

    return {
        data,
        loading,
        pagination,
        fetchData,
    };
}
