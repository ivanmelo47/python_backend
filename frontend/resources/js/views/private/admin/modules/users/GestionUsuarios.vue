<template>
    <div class="users-list">
        <Table
            title="Anfitriones"
            :columns="columns"
            :rows="users"
            :pagination="pagination"
            :search-query="searchQuery"
            v-model:items-per-page="itemsPerPage"
            @update:searchQuery="searchQuery = $event"
            @request-data="fetchUsers"
            @row-click="handleRowClick"
            :pagination-mode="CONFIG_PAGINATION_MODE === 'server' ? 'server' : 'client'"
            :loading="isLoading"
            search-placeholder="Buscar anfitrión..."
            :show-header-actions="true"
        >
            <template #header-actions>
                <button class="btn-solid-dark" @click="openCreateModal">
                    <Icon name="plus" :size="16" />
                    NUEVO
                </button>
            </template>

            <template #cell-email="{ row, value }">
                <div v-if="viewMode === 'grid'" class="user-card-title">
                    <div class="user-card-avatar">
                        <img v-if="row.avatar_url" :src="row.avatar_url" :alt="`Avatar de ${row.name || 'usuario'}`" />
                        <Icon v-else name="user" :size="16" />
                    </div>
                    <span class="main-text">Usuario - {{ value }}</span>
                </div>
                <div v-else class="user-list-email">
                    <div class="user-card-avatar user-list-avatar">
                        <img v-if="row.avatar_url" :src="row.avatar_url" :alt="`Avatar de ${row.name || 'usuario'}`" />
                        <Icon v-else name="user" :size="14" />
                    </div>
                    <span class="main-text">{{ value }}</span>
                </div>
            </template>

            <template #cell-name="{ value }">
                <span class="main-text">{{ value }}</span>
            </template>

            <template #cell-role="{ value }">
                <span class="main-text">{{ value }}</span>
            </template>

            <template #cell-account_status="{ row }">
                <div v-if="canToggleStatus(row)">
                    <label class="switch" v-if="row.account_status !== 'pending'" @click.stop>
                        <input
                            type="checkbox"
                            :checked="row.account_status === 'active'"
                            @change="handleToggleStatus(row)"
                            :disabled="row.uuid === currentUser?.uuid"
                        >
                        <span class="slider"></span>
                    </label>
                    <span v-else class="badge warning">Pendiente</span>
                </div>
                <div v-else>
                    <span v-if="row.account_status === 'active'" class="badge success">Activo</span>
                    <span v-else-if="row.account_status === 'inactive'" class="badge danger">Inactivo</span>
                    <span v-else class="badge warning">Pendiente</span>
                </div>
            </template>

            <template #cell-actions="{ row }">
                <button
                    class="dropdown-item"
                    title="Editar"
                    :disabled="!canEditUser(row)"
                    @click.stop="openEditModal(row)"
                >
                    <Icon name="pencil" :size="16" />
                    <span>Editar</span>
                </button>
            </template>
        </Table>

        <ModalForm
            :isVisible="showCreateModal"
            title="Nuevo Usuario"
            :loading="isCreating"
            size="md"
            :columns="4"
            @close="showCreateModal = false"
            @submit="handleCreateUser"
            :fields="createFields"
            :modelValue="createForm"
            :errors="createErrors"
        >
            <template #header-icon>
                <Icon name="plus" :size="20" />
            </template>
        </ModalForm>

        <ModalForm
            :isVisible="showEditModal"
            title="Editar Usuario"
            :loading="isUpdating"
            size="lg"
            :columns="4"
            @close="closeEditModal"
            @submit="handleUpdateUser"
            :fields="editFields"
            :modelValue="editForm"
            :errors="editErrors"
        >
            <template #header-icon>
                <Icon name="pencil" :size="20" />
            </template>

            <template #default>
                <div class="edit-avatar-panel">
                    <div class="avatar-preview-circle">
                        <img v-if="editAvatarPreviewUrl" :src="editAvatarPreviewUrl" alt="Avatar del usuario" />
                        <Icon v-else name="user" :size="34" />
                    </div>

                    <div class="avatar-panel-copy">
                        <h4>Avatar del usuario</h4>
                        <p>
                            Puedes cambiar la imagen con recorte circular. Se guarda en WebP 512 × 512.
                        </p>
                    </div>

                    <div class="avatar-panel-actions">
                        <button type="button" class="btn-ghost" @click="openAvatarPicker">
                            <Icon name="image" :size="16" />
                            Cambiar avatar
                        </button>
                        <button v-if="editForm.avatar_image" type="button" class="btn-ghost" @click="clearPendingAvatar">
                            <Icon name="x" :size="16" />
                            Limpiar cambio
                        </button>
                    </div>

                    <input
                        ref="avatarInput"
                        type="file"
                        accept="image/jpeg,image/png,image/webp"
                        class="hidden-file-input"
                        @change="handleAvatarSelected"
                    />
                </div>
            </template>
        </ModalForm>

        <ModalForm
            :isVisible="showCropModal"
            title="Recortar avatar"
            size="xl"
            :columns="1"
            @close="closeCropModal"
        >
            <template #header-icon>
                <Icon name="crop" :size="20" />
            </template>

            <template #default>
                <div class="cropper-shell">
                    <div class="cropper-main">
                        <cropper
                            v-if="cropperSource"
                            ref="cropperRef"
                            class="avatar-cropper"
                            :src="cropperSource"
                            :stencil-props="{ aspectRatio: 1 }"
                        />
                    </div>

                    <aside class="cropper-side">
                        <div class="cropper-preview-title">Vista previa</div>
                        <div class="cropper-preview-circle">
                            <img v-if="editAvatarPreviewUrl" :src="editAvatarPreviewUrl" alt="Vista previa de avatar" />
                            <Icon v-else name="user" :size="34" />
                        </div>
                        <p class="cropper-side-text">
                            Encadra la foto como perfil y confirma para usarla en el usuario seleccionado.
                        </p>
                    </aside>
                </div>
            </template>

            <template #footer>
                <button type="button" class="btn-ghost" @click="closeCropModal">Cancelar</button>
                <button type="button" class="btn-solid" @click="applyCrop">Usar imagen</button>
            </template>
        </ModalForm>

        <ModalInformation
            v-if="selectedUser"
            :is-open="showInfoModal"
            title="Detalles del Usuario"
            icon="user"
            :data="selectedUser"
            :columns="userColumns"
            show-edit-button
            submit-label="Editar este usuario"
            @edit="handleEditFromDetails"
            @close="showInfoModal = false"
        >
            <template #top-header>
                <div class="detail-hero">
                    <div class="detail-avatar">
                        <img v-if="selectedUser.avatar_url" :src="selectedUser.avatar_url" :alt="`Avatar de ${selectedUser.name || 'usuario'}`" />
                        <Icon v-else name="user" :size="36" />
                    </div>

                    <div class="detail-identity">
                        <h4>{{ selectedUser.name || 'usuario' }}</h4>
                        <p>{{ selectedUser.email || 'sin correo' }}</p>
                    </div>

                    <span class="detail-status-chip" :class="`status-${selectedUser.account_status || 'unknown'}`">
                        {{ getStatusLabel(selectedUser.account_status) }}
                    </span>
                </div>
            </template>

            <template #value-account_status>
                {{ getStatusLabel(selectedUser.account_status) }}
            </template>
        </ModalInformation>
    </div>
</template>

<script setup>
import { computed, reactive, ref } from 'vue';
import { Cropper } from 'vue-advanced-cropper';
import 'vue-advanced-cropper/dist/style.css';
import Table from '@/views/private/admin/components/Table.vue';
import Icon from '@/components/Icon.vue';
import ModalInformation from '@/views/private/admin/components/ModalInformation.vue';
import ModalForm from '@/views/private/admin/components/ModalForm.vue';
import usersApi from '@/services/api/endpoints/users';
import { useTableData } from '@/composables/useTableData';
import { useTableConfig } from '@/composables/useTableConfig';
import { useAlert } from '@/composables/useAlert';
import { useAuth } from '@/composables/useAuth';

const columns = [
    { key: 'actions', label: 'ACCIONES', headerClass: 'compact', cellClass: 'compact' },
    { key: 'email', label: 'EMAIL' },
    { key: 'name', label: 'NOMBRE' },
    { key: 'role_name', label: 'POSICION' },
    { key: 'account_status', label: 'ESTADO' }
];

const alert = useAlert();
const { user: currentUser } = useAuth();

const CONFIG_PAGINATION_MODE = 'server';
const { itemsPerPage, viewMode } = useTableConfig();
const searchQuery = ref('');

const showInfoModal = ref(false);
const selectedUser = ref(null);

const userColumns = [
    { key: 'name', label: 'Nombre usuario' },
    { key: 'email', label: 'Correo electrónico' },
    { key: 'role_name', label: 'Rol asignado' },
    { key: 'account_status', label: 'Estado cuenta' }
];

const showCreateModal = ref(false);
const isCreating = ref(false);
const createForm = reactive({
    name: '',
    email: '',
    password: '',
    password_confirmation: '',
    role_id: ''
});
const createErrors = ref({});

const showEditModal = ref(false);
const isUpdating = ref(false);
const editingUserId = ref(null);
const editForm = reactive({
    name: '',
    email: '',
    password: '',
    password_confirmation: '',
    role_id: '',
    avatar_image: null,
});
const editErrors = ref({});
const editAvatarPreviewUrl = ref(null);

const roles = ref([]);

const avatarInput = ref(null);
const cropperRef = ref(null);
const showCropModal = ref(false);
const cropperSource = ref(null);

const createFields = computed(() => [
    {
        key: 'name',
        label: 'Nombre de Usuario',
        type: 'text',
        placeholder: 'Ej. juanperez',
        required: true,
        span: 4
    },
    {
        key: 'email',
        label: 'Correo Electronico',
        type: 'email',
        placeholder: 'ejemplo@correo.com',
        required: true,
        span: 4
    },
    {
        key: 'password',
        label: 'Contrasena',
        type: 'password',
        placeholder: 'Contrasena segura',
        required: true,
        span: 2,
        autocomplete: 'new-password'
    },
    {
        key: 'password_confirmation',
        label: 'Confirmar Contrasena',
        type: 'password',
        placeholder: 'Repita la contrasena',
        required: true,
        span: 2,
        autocomplete: 'new-password'
    },
    {
        key: 'role_id',
        label: 'Rol',
        type: 'select',
        placeholder: 'Seleccionar rol',
        required: true,
        span: 4,
        options: roles.value
    }
]);

const editFields = computed(() => [
    {
        key: 'name',
        label: 'Nombre de Usuario',
        type: 'text',
        placeholder: 'Ej. juanperez',
        required: true,
        span: 2
    },
    {
        key: 'email',
        label: 'Correo Electronico',
        type: 'email',
        placeholder: 'ejemplo@correo.com',
        required: true,
        span: 2
    },
    {
        key: 'role_id',
        label: 'Rol',
        type: 'select',
        placeholder: 'Seleccionar rol',
        required: true,
        span: 4,
        options: roles.value
    },
    {
        key: 'password',
        label: 'Nueva Contrasena',
        type: 'password',
        placeholder: 'Solo si quieres cambiarla',
        required: false,
        span: 2,
        autocomplete: 'new-password'
    },
    {
        key: 'password_confirmation',
        label: 'Confirmar Nueva Contrasena',
        type: 'password',
        placeholder: 'Repite la nueva contrasena',
        required: false,
        span: 2,
        autocomplete: 'new-password'
    },
]);

const getRoleHierarchy = (entity) => {
    if (typeof entity?.role_hierarchy === 'number') return entity.role_hierarchy;
    if (typeof entity?.role?.hierarchy === 'number') return entity.role.hierarchy;
    return 999;
};

const canEditUser = (row) => {
    if (!currentUser.value || !row) return false;
    if (row.uuid === currentUser.value.uuid) return false;

    if (row.is_supermaster && !currentUser.value.is_supermaster) {
        return false;
    }

    if (currentUser.value.is_supermaster) {
        return true;
    }

    const currentHierarchy = getRoleHierarchy(currentUser.value);
    const targetHierarchy = getRoleHierarchy(row);

    return targetHierarchy > currentHierarchy;
};

const canToggleStatus = (row) => {
    if (!currentUser.value) return false;
    return currentUser.value.role?.name === 'master' && canEditUser(row);
};

const fetchRoles = async () => {
    try {
        const response = await usersApi.getRoles();
        roles.value = response.data || response;
    } catch (error) {
        alert.toast.error('Error', 'No se pudieron cargar los roles', 3000);
    }
};

const handleRowClick = (row) => {
    selectedUser.value = row;
    showInfoModal.value = true;
};

const handleEditFromDetails = async () => {
    if (!selectedUser.value) return;

    if (!canEditUser(selectedUser.value)) {
        alert.toast.error('Sin permisos', 'No puedes editar este usuario.', 3000);
        return;
    }

    const row = selectedUser.value;
    showInfoModal.value = false;
    await openEditModal(row);
};

const getStatusLabel = (status) => {
    if (status === 'active') return 'Activo';
    if (status === 'inactive') return 'Inactivo';
    if (status === 'pending') return 'Pendiente';
    return 'Desconocido';
};

const openCreateModal = async () => {
    createForm.name = '';
    createForm.email = '';
    createForm.password = '';
    createForm.password_confirmation = '';
    createForm.role_id = '';
    createErrors.value = {};

    if (roles.value.length === 0) {
        await fetchRoles();
    }

    showCreateModal.value = true;
};

const resetEditForm = () => {
    editForm.name = '';
    editForm.email = '';
    editForm.role_id = '';
    editForm.password = '';
    editForm.password_confirmation = '';
    editForm.avatar_image = null;
    editErrors.value = {};
    editingUserId.value = null;
    if (editAvatarPreviewUrl.value && editAvatarPreviewUrl.value.startsWith('blob:')) {
        URL.revokeObjectURL(editAvatarPreviewUrl.value);
    }
    editAvatarPreviewUrl.value = null;
};

const openEditModal = async (row) => {
    if (!canEditUser(row)) {
        alert.toast.error('Sin permisos', 'No puedes editar este usuario.', 3000);
        return;
    }

    if (roles.value.length === 0) {
        await fetchRoles();
    }

    editErrors.value = {};
    editForm.name = row.name || '';
    editForm.email = row.email || '';
    editForm.role_id = row.role_id || '';
    editForm.password = '';
    editForm.password_confirmation = '';
    editForm.avatar_image = null;
    editingUserId.value = row.uuid;
    editAvatarPreviewUrl.value = row.avatar_url || null;

    showEditModal.value = true;
};

const closeEditModal = () => {
    showEditModal.value = false;
    resetEditForm();
};

const openAvatarPicker = () => {
    avatarInput.value?.click();
};

const handleAvatarSelected = (event) => {
    const file = event.target.files?.[0];
    if (!file) return;

    if (cropperSource.value) {
        URL.revokeObjectURL(cropperSource.value);
    }

    cropperSource.value = URL.createObjectURL(file);
    showCropModal.value = true;
};

const closeCropModal = () => {
    showCropModal.value = false;
    if (cropperSource.value) {
        URL.revokeObjectURL(cropperSource.value);
        cropperSource.value = null;
    }
    if (avatarInput.value) {
        avatarInput.value.value = '';
    }
};

const createWebpBlobFromCanvas = (sourceCanvas) => {
    const targetCanvas = document.createElement('canvas');
    targetCanvas.width = 512;
    targetCanvas.height = 512;

    const context = targetCanvas.getContext('2d');
    if (!context) {
        return Promise.resolve(null);
    }

    context.drawImage(sourceCanvas, 0, 0, 512, 512);

    return new Promise((resolve) => {
        targetCanvas.toBlob((blob) => resolve(blob), 'image/webp', 0.92);
    });
};

const applyCrop = async () => {
    const cropper = cropperRef.value;
    if (!cropper) {
        alert.toast.error('Error', 'No se pudo cargar el recorte de imagen', 3000);
        return;
    }

    const result = cropper.getResult();
    if (!result?.canvas) {
        alert.toast.error('Error', 'Selecciona una imagen valida antes de continuar', 3000);
        return;
    }

    const blob = await createWebpBlobFromCanvas(result.canvas);
    if (!blob) {
        alert.toast.error('Error', 'No se pudo procesar la imagen recortada', 3000);
        return;
    }

    if (editAvatarPreviewUrl.value && editAvatarPreviewUrl.value.startsWith('blob:')) {
        URL.revokeObjectURL(editAvatarPreviewUrl.value);
    }

    editForm.avatar_image = blob;
    editAvatarPreviewUrl.value = URL.createObjectURL(blob);

    closeCropModal();
};

const clearPendingAvatar = () => {
    editForm.avatar_image = null;
    if (editAvatarPreviewUrl.value && editAvatarPreviewUrl.value.startsWith('blob:')) {
        URL.revokeObjectURL(editAvatarPreviewUrl.value);
    }

    const currentRow = users.value.find((item) => item.uuid === editingUserId.value);
    editAvatarPreviewUrl.value = currentRow?.avatar_url || null;
};

const validateCreateForm = () => {
    createErrors.value = {};

    createFields.value.forEach((field) => {
        if (field.required && !createForm[field.key]) {
            createErrors.value[field.key] = [`El campo ${field.label.toLowerCase()} es obligatorio`];
        }
    });

    if (createForm.password && createForm.password !== createForm.password_confirmation) {
        createErrors.value.password_confirmation = ['Las contrasenas no coinciden'];
    }

    return Object.keys(createErrors.value).length === 0;
};

const validateEditForm = () => {
    editErrors.value = {};

    if (!editForm.name) {
        editErrors.value.name = ['El nombre de usuario es obligatorio'];
    }

    if (!editForm.email) {
        editErrors.value.email = ['El correo electronico es obligatorio'];
    }

    if (!editForm.role_id) {
        editErrors.value.role_id = ['Debe seleccionar un rol'];
    }

    if (editForm.password && editForm.password !== editForm.password_confirmation) {
        editErrors.value.password_confirmation = ['Las contrasenas no coinciden'];
    }

    return Object.keys(editErrors.value).length === 0;
};

const handleCreateUser = async () => {
    if (!validateCreateForm()) return;

    isCreating.value = true;

    try {
        await usersApi.createUser(createForm);
        showCreateModal.value = false;
        fetchUsers();
        alert.toast.success('Usuario Creado', 'El usuario se ha registrado correctamente', 4000);
    } catch (error) {
        if (error.response?.data?.errors) {
            createErrors.value = error.response.data.errors;
            alert.toast.error('Error de Creacion', 'Por favor revise los campos marcados', 4000);
        } else {
            alert.toast.error('Error del Sistema', 'Ocurrio un error inesperado', 4000);
        }

        createForm.password = '';
        createForm.password_confirmation = '';
    } finally {
        isCreating.value = false;
    }
};

const handleUpdateUser = async () => {
    if (!validateEditForm() || !editingUserId.value) return;

    isUpdating.value = true;
    try {
        await usersApi.updateUser(editingUserId.value, editForm);
        alert.toast.success('Usuario actualizado', 'Los datos del usuario fueron modificados correctamente.', 3500);
        closeEditModal();
        fetchUsers();
    } catch (error) {
        if (error.response?.data?.errors) {
            editErrors.value = error.response.data.errors;
        }
        alert.toast.error('Error', error.response?.data?.message || 'No se pudo actualizar el usuario', 4000);
    } finally {
        isUpdating.value = false;
    }
};

const handleToggleStatus = async (row) => {
    const originalStatus = row.account_status;
    const newStatus = originalStatus === 'active' ? 'inactive' : 'active';
    const actionText = newStatus === 'active' ? 'activar' : 'desactivar';

    const confirmed = await alert.fire({
        title: `¿${actionText.charAt(0).toUpperCase() + actionText.slice(1)} usuario?`,
        text: `¿Estas seguro de que deseas ${actionText} a ${row.name}?`,
        type: 'warning',
        showCancel: true,
        confirmText: `Si, ${actionText}`,
        cancelText: 'Cancelar'
    });

    if (!confirmed) {
        row.account_status = originalStatus === 'active' ? 'inactive' : 'active';
        setTimeout(() => {
            row.account_status = originalStatus;
        }, 0);
        return;
    }

    row.account_status = newStatus;

    try {
        await usersApi.toggleStatus(row.uuid);
        alert.toast.success('Estado Actualizado', `El usuario ha sido ${newStatus === 'active' ? 'activado' : 'desactivado'}.`, 3000);
    } catch (error) {
        row.account_status = originalStatus;
        alert.toast.error('Error', 'No se pudo cambiar el estado del usuario', 3000);
    }
};

const transformUser = (user) => ({
    id: user.uuid,
    uuid: user.uuid,
    name: user.name,
    email: user.email,
    role_id: user.role?.id,
    role_name: user.role?.name || 'sin rol',
    role_hierarchy: user.role?.hierarchy,
    role_slug: user.role?.slug,
    account_status: user.account_status,
    is_supermaster: !!user.is_supermaster,
    avatar_url: user.avatar_url || null,
    role: user.role?.name || 'sin rol',
});

const {
    data: users,
    loading: isLoading,
    pagination,
    fetchData: fetchUsers
} = useTableData(usersApi.getUsers, {
    transformer: transformUser,
    mode: CONFIG_PAGINATION_MODE,
    itemsPerPage,
    searchQuery
});
</script>

<style scoped>
.edit-avatar-panel {
    grid-column: 1 / -1;
    margin-top: 0.35rem;
    padding: 0.9rem;
    border-radius: 14px;
    background: var(--bg-secondary);
    border: 1px solid var(--border-color);
    display: grid;
    grid-template-columns: auto 1fr auto;
    gap: 0.9rem;
    align-items: center;
}

.user-card-title {
    display: flex;
    align-items: center;
    gap: 0.55rem;
}

.user-detail-modal {
    display: flex;
    flex-direction: column;
    gap: 1rem/* User detail modal styles migrated to ModalInformation.vue where possible */
}

.detail-hero {
    display: flex;
    align-items: center;
    gap: 1rem;
    padding: 1rem;
    border-radius: 12px;
    background: var(--bg-tertiary);
    border: 1px solid var(--border-color);
    margin-bottom: 0.5rem;

    .detail-avatar {
        width: 54px;
        height: 54px;
        border-radius: 50%;
        overflow: hidden;
        background: var(--bg-secondary);
        display: flex;
        align-items: center;
        justify-content: center;
        border: 2px solid var(--border-color);
    }

    .detail-identity {
        flex: 1;
        h4 {
            margin: 0;
            font-size: 1.1rem;
            color: var(--text-primary);
        }
        p {
            margin: 0;
            font-size: 0.85rem;
            color: var(--text-tertiary);
        }
    }
}

.detail-status-chip {
    background: rgba(16, 185, 129, 0.18);
    color: #10b981;
}

.detail-status-chip.status-inactive {
    background: rgba(239, 68, 68, 0.18);
    color: #ef4444;
}

.detail-status-chip.status-pending {
    background: rgba(245, 158, 11, 0.18);
    color: #f59e0b;
}

.detail-grid {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 0.7rem;
}

.detail-actions {
    display: flex;
    justify-content: flex-end;
}

.detail-edit-btn {
    display: inline-flex;
    align-items: center;
    gap: 0.45rem;
}

.detail-item {
    padding: 0.7rem 0.75rem;
    border-radius: 12px;
    background: var(--bg-secondary);
    border: 1px solid var(--border-color);
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
}

.detail-item .label {
    color: var(--text-secondary);
    font-size: 0.72rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

.detail-item .value {
    color: var(--text-primary);
    font-weight: 700;
    font-size: 0.9rem;
}

.user-list-email {
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.user-card-avatar {
    width: 30px;
    height: 30px;
    border-radius: 999px;
    overflow: hidden;
    display: grid;
    place-items: center;
    background: var(--bg-secondary);
    border: 1px solid rgba(var(--primary-rgb), 0.25);
    color: var(--primary);
    flex: 0 0 auto;
}

.user-card-avatar img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    display: block;
}

.user-list-avatar {
    width: 26px;
    height: 26px;
}

.avatar-preview-circle {
    width: 74px;
    height: 74px;
    border-radius: 50%;
    overflow: hidden;
    display: grid;
    place-items: center;
    background: var(--bg-primary);
    border: 2px solid rgba(var(--primary-rgb), 0.22);
    color: var(--primary);
}

.avatar-preview-circle img,
.cropper-preview-circle img {
    width: 100%;
    height: 100%;
    object-fit: cover;
}

.avatar-panel-copy h4 {
    margin: 0 0 0.2rem;
    color: var(--text-primary);
}

.avatar-panel-copy p {
    margin: 0;
    color: var(--text-secondary);
    font-size: 0.88rem;
}

.avatar-panel-actions {
    display: flex;
    flex-direction: column;
    gap: 0.45rem;
}

.hidden-file-input {
    display: none;
}

.cropper-shell {
    display: grid;
    grid-template-columns: minmax(0, 1fr) 240px;
    gap: 0.9rem;
    min-height: 420px;
}

.cropper-main {
    min-height: 420px;
    border-radius: 14px;
    overflow: hidden;
    background: var(--bg-secondary);
    border: 1px solid var(--border-color);
}

.avatar-cropper {
    width: 100%;
    min-height: 420px;
}

.cropper-side {
    border: 1px solid var(--border-color);
    border-radius: 14px;
    background: var(--bg-secondary);
    padding: 0.9rem;
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
}

.cropper-preview-title {
    color: var(--text-primary);
    font-weight: 700;
}

.cropper-preview-circle {
    width: 140px;
    height: 140px;
    border-radius: 50%;
    overflow: hidden;
    margin: 0 auto;
    display: grid;
    place-items: center;
    color: var(--primary);
    border: 2px solid rgba(var(--primary-rgb), 0.24);
    background: var(--bg-primary);
}

.cropper-side-text {
    color: var(--text-secondary);
    font-size: 0.86rem;
    line-height: 1.45;
}

@media (max-width: 1024px) {
    .cropper-shell {
        grid-template-columns: 1fr;
    }
}

@media (max-width: 720px) {
    .edit-avatar-panel {
        grid-template-columns: 1fr;
    }

    .detail-hero {
        grid-template-columns: 1fr;
        justify-items: start;
    }

    .detail-grid {
        grid-template-columns: 1fr;
    }

    .detail-actions {
        justify-content: stretch;
    }

    .detail-edit-btn {
        width: 100%;
        justify-content: center;
    }

    .avatar-panel-actions {
        width: 100%;
    }
}
</style>
