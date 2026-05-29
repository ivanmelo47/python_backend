<template>
    <div class="dynamic-routes-manager">
        <Table title="Gestión de Rutas Dinámicas (Híbridas)" :columns="columns" :rows="parentRoutes" :loading="loading"
            searchPlaceholder="Buscar ruta..." cardTitleTemplate="{title}" @row-click="editRoute"
            @request-data="fetchData">
            <template #header-actions>
                <button class="btn-solid" @click="openCreateModal">
                    <DynamicIcon name="plus" :size="18" />
                    <span>Nueva Ruta</span>
                </button>
            </template>

            <!-- Custom Cell: Icon -->
            <template #cell-icon="{ row }">
                <div class="icon-preview" v-if="row.icon">
                    <DynamicIcon :name="`db:${row.name}`" :databaseData="{
                        type: row.icon.type,
                        file_path: row.icon.file_path,
                        svg_content: row.icon.svg_content,
                        viewBox: row.icon.viewBox,
                        color_mode: row.icon_color_mode || row.icon.color_mode
                    }" :size="24" />
                </div>
                <span v-else class="text-muted">-</span>
            </template>

            <!-- Custom Cell: Hierarchy -->
            <template #cell-role="{ row }">
                <span class="badge badge-info">{{ getRoleName(row) }}</span>
            </template>

            <!-- Custom Cell: Parent -->
            <template #cell-parent="{ row }">
                <span v-if="row.parent">{{ row.parent.title }}</span>
                <span v-else class="text-muted">-</span>
            </template>

            <!-- Custom Cell: Order -->
            <template #cell-order="{ row }">
                <span>{{ row.meta?.order ?? '-' }}</span>
            </template>

            <!-- Custom Cell: Status -->
            <template #cell-is_active="{ row }">
                <label class="switch" @click.stop>
                    <input type="checkbox" :checked="row.is_active" @change="handleToggleStatus(row)">
                    <span class="slider"></span>
                </label>
            </template>

            <!-- Actions -->
            <template #cell-actions="{ row }">
                <button @click.stop="editRoute(row)" class="dropdown-item">
                    <DynamicIcon name="edit" :size="16" />
                    <span>Editar</span>
                </button>
                <button @click.stop="confirmDelete(row)" class="dropdown-item delete">
                    <DynamicIcon name="trash" :size="16" />
                    <span>Eliminar</span>
                </button>
            </template>
        </Table>

        <!-- Modal Form -->
        <ModalForm :isVisible="showFormModal" :title="modalTitle" :loading="formLoading" submitLabel="Guardar" size="lg"
            :columns="2" @close="closeFormModal" @submit="submitForm">
            <template #header-title>
                <div class="modal-header-breadcrumb">
                    <button v-if="showChildBreadcrumb" type="button" class="breadcrumb-link"
                        @click="handleBackToParent">
                        {{ modalParentRoute?.title }}
                    </button>
                    <span v-if="showChildBreadcrumb" class="breadcrumb-separator">/</span>
                    <h3 class="modal-title">{{ breadcrumbCurrentLabel }}</h3>
                </div>
            </template>

            <ModalField label="Título del Módulo" :required="true" :span="1" :error="errors.title?.[0]">
                <input v-model="formData.title" type="text" placeholder="Ej: Reportes Avanzados" />
            </ModalField>

            <ModalField label="Nombre Único (ID)" :required="true" :span="1" :error="errors.name?.[0]">
                <input v-model="formData.name" type="text" placeholder="Ej: advanced-reports" />
            </ModalField>

            <ModalField label="Descripción" :span="2" :error="errors.description?.[0]">
                <textarea v-model="formData.description" rows="2"
                    placeholder="Breve descripción del módulo..."></textarea>
            </ModalField>

            <ModalField label="Ruta (URL Path)" :required="true" :span="1" :error="errors.path?.[0]"
                help="La URL relativa, ej: 'mi-herramienta' o 'herramientas/mi-modulo'">
                <input v-model="formData.path" type="text" placeholder="Ej: reportes-avanzados" />
            </ModalField>

            <ModalField label="Componente (.vue)" :required="true" :span="1" :error="errors.component_path?.[0]"
                help="Nombre del archivo en '@/views/', ej: 'private/admin/modules/MyView.vue'">
                <input v-model="formData.component_path" type="text" placeholder="private/admin/modules/MyView.vue" />
            </ModalField>

            <ModalField label="Rol de Acceso Mínimo" :required="true" :span="1" :error="errors.role_id?.[0]">
                <select v-model="formData.role_id" @change="onRoleChange">
                    <option v-for="role in roles" :key="role.id" :value="role.id">
                        {{ role.name }} (Jerarquía: {{ role.hierarchy }})
                    </option>
                </select>
            </ModalField>

            <ModalField label="Ruta Padre (Opcional)" :span="1" :error="errors.parent_id?.[0]"
                help="Si se selecciona, este módulo aparecerá anidado.">
                <select v-model="formData.parent_id">
                    <option :value="null">Ninguna (Ruta Raíz)</option>
                    <option v-for="route in availableParentRoutes" :key="route.id" :value="route.id">
                        {{ route.title }} ({{ route.path }})
                    </option>
                </select>
            </ModalField>

            <ModalField label="Orden de Visualización" :required="true" :span="1" :error="errors.order?.[0]"
                help="Menor número = mayor prioridad (ej: 1, 10, 20)">
                <input v-model.number="formData.meta.order" type="number" min="1" placeholder="Ej: 10" />
            </ModalField>

            <ModalField label="Modo de Color Icono" :required="true" :span="1">
                <select v-model="formData.icon_color_mode">
                    <option value="currentColor">currentColor (Heredar del sistema)</option>
                    <option value="original">Original (Colores del SVG)</option>
                </select>
            </ModalField>

            <ModalField label="Seleccionar Icono" :span="2">
                <div class="icon-selector">
                    <input v-model="iconSearch" type="text" placeholder="Buscar icono en la base de datos..."
                        class="mb-2" @input="fetchIconsDebounced" />
                    <div class="icon-grid-selector">
                        <div v-for="icon in availableIcons" :key="icon.id" class="icon-option"
                            :class="{ selected: formData.icon_id === icon.id }" @click="formData.icon_id = icon.id">
                            <div class="icon-svg-min">
                                <DynamicIcon :name="`db:${icon.name}`" :databaseData="{
                                    type: icon.type,
                                    file_path: icon.file_path,
                                    svg_content: icon.svg_content,
                                    viewBox: icon.viewBox,
                                    color_mode: icon.color_mode
                                }" :size="20" />
                            </div>
                            <span class="icon-name-min">{{ icon.name }}</span>
                        </div>
                    </div>
                </div>
            </ModalField>

            <div class="col-span-2 grid grid-cols-2 gap-4 border-t border-border-color pt-4 mt-2">
                <ModalField label="Mostrar en Sidebar">
                    <label class="switch">
                        <input type="checkbox" v-model="formData.meta.sidebar">
                        <span class="slider"></span>
                    </label>
                </ModalField>

                <ModalField label="Ajustar al Contenedor (Fit Screen)">
                    <label class="switch">
                        <input type="checkbox" v-model="formData.meta.fitScreen">
                        <span class="slider"></span>
                    </label>
                </ModalField>

                <ModalField label="Mostrar como Dropdown">
                    <label class="switch">
                        <input type="checkbox" v-model="formData.meta.showDropdown">
                        <span class="slider"></span>
                    </label>
                </ModalField>

                <ModalField label="Mostrar Tabs">
                    <label class="switch">
                        <input type="checkbox" v-model="formData.meta.showTabs">
                        <span class="slider"></span>
                    </label>
                </ModalField>

                <ModalField label="Mostrar Breadcrumbs">
                    <label class="switch">
                        <input type="checkbox" v-model="formData.meta.breadcrumbs">
                        <span class="slider"></span>
                    </label>
                </ModalField>
            </div>

            <ModalField label="Opciones Adicionales (Meta JSON)" :span="2"
                help="Configuración avanzada en formato JSON">
                <textarea v-model="metaString" rows="3" placeholder='{"exact": false}'
                    @blur="syncMetaFromText"></textarea>
                <p v-if="metaError" class="text-danger text-xs mt-1">{{ metaError }}</p>
            </ModalField>

            <div v-if="editingRoute && !editingRoute.parent_id" class="col-span-2 child-manager">
                <div class="child-manager-header">
                    <h3>Rutas hijas</h3>
                    <button type="button" class="btn-solid" @click="openCreateModal(editingRoute)">
                        <DynamicIcon name="plus" :size="16" />
                        <span>Nueva hija</span>
                    </button>
                </div>

                <div v-if="childRoutes.length === 0" class="child-empty">
                    Esta ruta aún no tiene hijas.
                </div>

                <div v-else class="child-list">
                    <div v-for="child in childRoutes" :key="child.id" class="child-item">
                        <div class="child-info">
                            <strong>{{ child.title }}</strong>
                            <span>{{ child.path }}</span>
                        </div>
                        <div class="child-actions">
                            <label class="switch" @click.stop>
                                <input type="checkbox" :checked="child.is_active" @change="handleToggleStatus(child)">
                                <span class="slider"></span>
                            </label>
                            <button type="button" class="child-action"
                                @click.stop="openChildEditor(child)">Editar</button>
                            <button type="button" class="child-action delete"
                                @click.stop="confirmDelete(child)">Eliminar</button>
                        </div>
                    </div>
                </div>
            </div>
        </ModalForm>
    </div>
</template>

<script setup>
import { ref, onMounted, watch, computed } from 'vue';
import Table from '@/views/private/admin/components/Table.vue';
import ModalForm from '@/views/private/admin/components/ModalForm.vue';
import ModalField from '@/views/private/admin/components/ModalField.vue';
import DynamicIcon from '@/components/DynamicIcon.vue';
import dynamicRoutesApi from '@/services/api/endpoints/dynamic-routes';
import iconsApi from '@/services/api/endpoints/icons';
import { api } from '@/services/api'; // Import central api for roles
import { useAlert } from '@/composables/useAlert';

const alert = useAlert();
const routes = ref([]);
const loading = ref(false);
const formLoading = ref(false);
const showFormModal = ref(false);
const editingRoute = ref(null);
const modalParentRoute = ref(null);
const initialFormSnapshot = ref('');
const initialMetaString = ref('');

const columns = [
    { key: 'icon', label: 'Icono', cellClass: 'text-center' },
    { key: 'title', label: 'Título' },
    { key: 'path', label: 'Ruta' },
    { key: 'parent', label: 'Padre' },
    { key: 'order', label: 'Orden', cellClass: 'text-center' },
    { key: 'role', label: 'Rol Mínimo' },
    { key: 'is_active', label: 'Estatus', cellClass: 'text-center' },
    { key: 'actions', label: 'Acciones', cellClass: 'text-right' }
];

const formData = ref({
    title: '',
    name: '',
    description: '',
    path: '',
    component_path: '',
    parent_id: null,
    min_hierarchy: 1,
    role_id: null,
    icon_id: null,
    icon_color_mode: 'currentColor',
    is_active: true,
    meta: {
        sidebar: true,
        fitScreen: true,
        showDropdown: false,
        showTabs: false,
        breadcrumbs: false,
        order: 10
    }
});

// Sync meta switches with metaString
watch(() => formData.value.meta, (newMeta) => {
    metaString.value = JSON.stringify(newMeta, null, 2);
}, { deep: true });
const metaString = ref('{}');
const metaError = ref('');
const errors = ref({});
const roles = ref([]); // Available roles

// Icon Selector
const iconSearch = ref('');
const availableIcons = ref([]);
const iconLoading = ref(false);

const parentRoutes = computed(() => {
    return routes.value
        .filter(route => !route.parent_id)
        .sort((a, b) => (a.meta?.order ?? 999) - (b.meta?.order ?? 999));
});

const availableParentRoutes = computed(() => {
    if (!editingRoute.value) {
        return routes.value;
    }

    return routes.value.filter(route => route.id !== editingRoute.value.id);
});

const childRoutes = computed(() => {
    if (!editingRoute.value) {
        return [];
    }

    return routes.value
        .filter(route => route.parent_id === editingRoute.value.id)
        .sort((a, b) => (a.meta?.order ?? 999) - (b.meta?.order ?? 999));
});

const showChildBreadcrumb = computed(() => {
    return !!modalParentRoute.value;
});

const modalTitle = computed(() => {
    return editingRoute.value ? 'Editar Ruta Dinámica' : 'Nueva Ruta Dinámica';
});

const breadcrumbCurrentLabel = computed(() => {
    if (editingRoute.value?.title) {
        return editingRoute.value.title;
    }

    if (showChildBreadcrumb.value) {
        return 'Nueva Ruta Hija';
    }

    return modalTitle.value;
});

const buildFormSnapshot = () => {
    return JSON.stringify({
        ...formData.value,
        meta: { ...(formData.value.meta || {}) }
    });
};

const markSnapshotAsSaved = () => {
    initialFormSnapshot.value = buildFormSnapshot();
    initialMetaString.value = metaString.value;
};

const hasUnsavedChanges = computed(() => {
    if (!showFormModal.value) {
        return false;
    }

    return buildFormSnapshot() !== initialFormSnapshot.value || metaString.value !== initialMetaString.value;
});

const fetchData = async () => {
    loading.value = true;
    try {
        const [routesRes, rolesRes] = await Promise.all([
            dynamicRoutesApi.getAll(),
            api.users.getRoles()
        ]);

        // Ensure we handle different response structures if they arise
        routes.value = routesRes.data.data || routesRes.data || [];
        roles.value = rolesRes.data.data || rolesRes.data || [];

        // Load icons if not already loaded
        if (availableIcons.value.length === 0) {
            await fetchIcons();
        }
    } catch (error) {
        console.error("Fetch Data Error:", error);
        alert.toast.error('Error', 'No se pudieron cargar los datos. Revisa la consola para más detalles.');
    } finally {
        loading.value = false;
    }
};

const fetchIcons = async () => {
    iconLoading.value = true;
    try {
        const response = await api.icons.getAll({
            search: iconSearch.value,
            per_page: -1 // Get all for the selector
        });

        // Handle both paginated and non-paginated responses
        const iconData = response.data.data || response.data;
        availableIcons.value = Array.isArray(iconData) ? iconData : (iconData.data || []);

        if (availableIcons.value.length === 0) {
            console.warn('[DynamicRoutes] No se encontraron iconos.');
        }
    } catch (error) {
        console.error('Error fetching icons:', error);
    } finally {
        iconLoading.value = false;
    }
};

let debounceTimeout;
const fetchIconsDebounced = () => {
    clearTimeout(debounceTimeout);
    debounceTimeout = setTimeout(fetchIcons, 300);
};

const syncMetaFromText = () => {
    try {
        const parsed = JSON.parse(metaString.value);
        formData.value.meta = {
            ...formData.value.meta,
            ...parsed
        };
        metaError.value = '';
        return true;
    } catch (e) {
        metaError.value = 'JSON inválido';
        return false;
    }
};

const openCreateModal = (parentRoute = null) => {
    editingRoute.value = null;
    modalParentRoute.value = parentRoute;
    formData.value = {
        title: '',
        name: '',
        description: '',
        path: '',
        component_path: '',
        parent_id: parentRoute?.id ?? null,
        min_hierarchy: 1,
        role_id: roles.value.length > 0 ? roles.value[0].id : null,
        icon_id: null,
        icon_color_mode: 'currentColor',
        is_active: true,
        meta: {
            sidebar: true,
            fitScreen: true,
            showDropdown: false,
            showTabs: false,
            breadcrumbs: false,
            order: 10
        }
    };
    if (roles.value.length > 0) {
        formData.value.min_hierarchy = roles.value[0].hierarchy;
    }
    metaString.value = JSON.stringify(formData.value.meta, null, 2);
    showFormModal.value = true;
    markSnapshotAsSaved();
};

const editRoute = (route, options = {}) => {
    const { parentContext = null } = options;
    editingRoute.value = route;
    modalParentRoute.value = parentContext;
    formData.value = {
        title: route.title,
        name: route.name,
        description: route.description || '',
        path: route.path,
        component_path: route.component_path,
        parent_id: route.parent_id,
        min_hierarchy: route.min_hierarchy,
        role_id: route.role_id,
        icon_id: route.icon_id,
        icon_color_mode: route.icon_color_mode,
        is_active: route.is_active,
        meta: {
            sidebar: true,
            fitScreen: true,
            showDropdown: false,
            showTabs: false,
            breadcrumbs: false,
            order: 10,
            ...(route.meta || {})
        }
    };
    metaString.value = JSON.stringify(formData.value.meta, null, 2);
    showFormModal.value = true;
    markSnapshotAsSaved();
};

const openChildEditor = (childRoute) => {
    if (!editingRoute.value) {
        return;
    }

    editRoute(childRoute, { parentContext: editingRoute.value });
};

const handleBackToParent = async () => {
    if (!modalParentRoute.value) {
        return;
    }

    if (hasUnsavedChanges.value) {
        const confirmed = await alert.fire({
            title: 'Cambios sin guardar',
            text: 'Tienes cambios sin guardar. Si regresas al módulo padre, se perderán. ¿Deseas continuar?',
            type: 'warning',
            showCancel: true,
            confirmText: 'Sí, regresar',
            cancelText: 'Cancelar'
        });

        if (!confirmed) {
            return;
        }
    }

    const parent = routes.value.find(route => route.id === modalParentRoute.value.id) || modalParentRoute.value;
    editRoute(parent);
};

// Method to update hierarchy when a role is selected
const onRoleChange = (event) => {
    const rId = event.target.value;
    const role = roles.value.find(r => r.id == rId);
    if (role) {
        formData.value.role_id = role.id;
        formData.value.min_hierarchy = role.hierarchy;
    }
};

// Helper to get role name
const getRoleName = (route) => {
    if (route.role) return route.role.name;
    const role = roles.value.find(r => r.hierarchy == route.min_hierarchy);
    return role ? role.name : `Nivel ${route.min_hierarchy}`;
};

const closeFormModal = () => {
    showFormModal.value = false;
    editingRoute.value = null;
    modalParentRoute.value = null;
    errors.value = {};
};

const submitForm = async () => {
    if (!syncMetaFromText()) return;

    formLoading.value = true;
    errors.value = {};
    const parentContext = modalParentRoute.value ? { ...modalParentRoute.value } : null;
    try {
        if (editingRoute.value) {
            await dynamicRoutesApi.update(editingRoute.value.uuid, formData.value);
            alert.toast.success('Éxito', 'Ruta actualizada');
        } else {
            await dynamicRoutesApi.create(formData.value);
            alert.toast.success('Éxito', 'Ruta creada');
        }

        await fetchData();

        if (parentContext) {
            const parentRoute = routes.value.find(route => route.id === parentContext.id);
            if (parentRoute) {
                editRoute(parentRoute);
            } else {
                closeFormModal();
            }
        } else {
            closeFormModal();
        }
    } catch (error) {
        if (error.response?.status === 422) {
            errors.value = error.response.data.errors;
        }
        alert.toast.error('Error', 'No se pudo guardar la ruta');
    } finally {
        formLoading.value = false;
    }
};

const handleToggleStatus = async (row) => {
    try {
        await dynamicRoutesApi.toggleStatus(row.uuid);
        await fetchData();
        alert.toast.success('Éxito', 'Estado actualizado');
    } catch (error) {
        alert.toast.error('Error', 'No se pudo cambiar el estado');
    }
};

const confirmDelete = async (row) => {
    const confirmed = await alert.fire({
        title: '¿Eliminar ruta?',
        text: 'Esta acción no se puede deshacer.',
        type: 'warning',
        showCancel: true
    });

    if (confirmed) {
        try {
            await dynamicRoutesApi.delete(row.uuid);
            alert.toast.success('Éxito', 'Ruta eliminada');
            fetchData();
        } catch (error) {
            alert.toast.error('Error', 'No se pudo eliminar la ruta');
        }
    }
};

onMounted(() => {
    fetchData();
});
</script>
