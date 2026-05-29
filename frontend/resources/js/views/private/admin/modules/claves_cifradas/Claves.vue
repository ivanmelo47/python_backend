<template>
    <div class="claves-list">
        <Table
            title="Gestor de Contraseñas"
            :columns="columns"
            :rows="vaultItems"
            :pagination="pagination"
            :search-query="searchQuery"
            v-model:items-per-page="itemsPerPage"
            @update:searchQuery="searchQuery = $event"
            @request-data="fetchVaultItems"

            :pagination-mode="'client'"
            :loading="isLoading"
            search-placeholder="Buscar servicio..."
            card-title-template="Servicio - {service}"
            :show-header-actions="true"
        >
            <!-- Header Actions -->
            <template #header-actions>
                <button class="btn-solid-dark" @click="openCreateModal">
                    <Icon name="plus" :size="16" />
                    NUEVA
                </button>
            </template>

            <!-- Custom Cell: Icon -->
            <template #cell-icon="{ row }">
                <div class="vault-icon-preview">
                    <DynamicIcon v-if="row.icon" :name="`db:${row.service}`" :databaseData="row.icon" :size="24" />
                    <div v-else class="vault-icon-placeholder">
                        <Icon name="lock" :size="20" />
                    </div>
                </div>
            </template>

            <!-- Custom Cell: Service -->
            <template #cell-service="{ value }">
                <span class="main-text font-bold">{{ value }}</span>
            </template>

            <!-- Custom Cell: Username -->
            <template #cell-username="{ value }">
                <span class="sub-text">{{ value || 'N/A' }}</span>
            </template>

            <!-- Custom Cell: Created At -->
            <template #cell-created_at="{ value }">
                <span class="sub-text">{{ formatDate(value) }}</span>
            </template>

            <!-- Custom Cell: Acciones -->
            <template #cell-actions="{ row }">
                <button class="dropdown-item" title="Ver Contraseña" @click.stop="handleViewPassword(row)">
                    <Icon name="eye" :size="16" />
                    <span>Ver</span>
                </button>
                <button class="dropdown-item" title="Editar" @click.stop="handleEdit(row)">
                    <Icon name="edit" :size="16" />
                    <span>Editar</span>
                </button>
                <button class="dropdown-item delete" title="Eliminar" @click.stop="handleDelete(row)">
                    <Icon name="trash" :size="16" />
                    <span>Eliminar</span>
                </button>
            </template>
        </Table>

        <!-- Create/Edit Vault Item Modal -->
        <ModalForm
            :isVisible="showFormModal"
            :title="isEditing ? 'Editar Registro' : 'Nueva Contraseña'"
            :loading="isSaving"
            size="md"
            :columns="1"
            @close="showFormModal = false"
            @submit="handleFormSubmit"
            :fields="activeFields"
            :modelValue="vaultForm"
            :errors="formErrors"
        >
            <template #header-icon>
                <Icon name="lock" :size="20" />
            </template>

            <template #default>
                <div class="icon-selector-field">
                    <label class="modal-field-label">Icono del Servicio</label>
                    <div class="icon-search-wrapper">
                        <Icon name="search" :size="16" />
                        <input v-model="iconSearch" type="text" placeholder="Buscar icono..." @click.stop />
                    </div>
                    <div class="icon-grid-selector">
                        <div v-for="icon in filteredIcons" :key="icon.id" class="icon-option"
                            :class="{ selected: vaultForm.icon_id === icon.id }" @click="vaultForm.icon_id = icon.id">
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
            </template>
        </ModalForm>

        <!-- Password Confirmation Modal -->
        <PasswordConfirmationModal
            ref="confirmModalRef"
            :isOpen="showConfirmModal"
            @close="showConfirmModal = false"
            @confirmed="handleConfirmation"
        />
        
        <!-- Revealed Password Overlay -->
        <!-- Revealed Password Modal -->
        <ModalForm
            :isVisible="!!revealedData"
            :title="revealedData?.service || 'Credenciales Descifradas'"
            size="md"
            :columns="1"
            @close="clearRevealedPassword"
            :show-footer="false"
        >
            <div class="reveal-content-body">
                <div class="reveal-header">
                    <div class="icon-glow"></div>
                    <div class="icon-wrapper">
                        <DynamicIcon v-if="revealedData.icon" :name="`db:${revealedData.service}`" :databaseData="revealedData.icon" :size="48" />
                        <i v-else class="fas fa-unlock-alt"></i>
                    </div>
                </div>

                <h3>Credenciales Descifradas</h3>
                <p class="subtitle">La información se ocultará automáticamente.</p>

                <div class="credentials-container">
                    <!-- Username Field -->
                    <div v-if="revealedData.username" class="credential-group">
                        <div class="label-badge">Usuario</div>
                        <div class="credential-box">
                            <span class="credential-val">{{ revealedData.username }}</span>
                            <button @click="copyToClipboard(revealedData.username, 'Usuario')" class="btn-copy" title="Copiar usuario">
                                <i class="far fa-copy"></i>
                            </button>
                        </div>
                    </div>

                    <!-- Password Field -->
                    <div class="credential-group">
                        <div class="label-badge highlight">Contraseña</div>
                        <div class="credential-box highlight-box">
                            <span class="credential-val">{{ revealedData.password }}</span>
                            <button @click="copyToClipboard(revealedData.password, 'Contraseña')" class="btn-copy" title="Copiar contraseña">
                                <i class="far fa-copy"></i>
                            </button>
                        </div>
                    </div>
                </div>

                <div class="timer-section">
                    <div class="timer-info">
                        <span>Tiempo restante</span>
                        <span class="time-val">{{ timeLeft }}s</span>
                    </div>
                    <div class="progress-track">
                        <div class="progress-fill" :style="{ width: `${timerProgress}%` }"></div>
                    </div>
                </div>

                <button @click="clearRevealedPassword" class="btn-hide">
                    Ocultar ahora
                </button>
            </div>
        </ModalForm>
    </div>
</template>

<script setup>
import { ref, reactive, computed, onUnmounted } from 'vue';
import Table from '@/views/private/admin/components/Table.vue';
import Icon from '@/components/Icon.vue';
import DynamicIcon from '@/components/DynamicIcon.vue';
import ModalForm from '@/views/private/admin/components/ModalForm.vue';
import PasswordConfirmationModal from '@/views/private/admin/components/PasswordConfirmationModal.vue';
import { useTableData } from '@/composables/useTableData';
import { useTableConfig } from '@/composables/useTableConfig';
import { useAlert } from '@/composables/useAlert';
import { useVault } from '@/composables/useVault'; // Assume useVault logic is here or inline

// API Logic
import { api } from '@/services/api';
import { formatDate } from '@/utils/format-date';

const alert = useAlert();

const columns = [
    { key: 'actions', label: 'ACCIONES', headerClass: 'compact', cellClass: 'compact' },
    { key: 'icon', label: 'ICONO', cellClass: 'text-center compact' },
    { key: 'service', label: 'SERVICIO' },
    { key: 'created_at', label: 'CREADO' },
];

const { itemsPerPage } = useTableConfig();
const searchQuery = ref('');

// Icons logic
const availableIcons = ref([]);
const iconSearch = ref('');
const fetchAvailableIcons = async () => {
    try {
        const response = await api.icons.getAll({ per_page: -1 });
        availableIcons.value = response.data.data || [];
    } catch (error) {
        console.error('Error fetching icons:', error);
    }
};

const filteredIcons = computed(() => {
    if (!iconSearch.value) return availableIcons.value;
    const query = iconSearch.value.toLowerCase();
    return availableIcons.value.filter(i => i.name.toLowerCase().includes(query));
});

// Modals State
const showFormModal = ref(false);
const showConfirmModal = ref(false);
const isSaving = ref(false);
const isEditing = ref(false);
const editingId = ref(null);
const confirmModalRef = ref(null);

// Forms
const vaultForm = reactive({
    service: '',
    username: '',
    password: '',
    master_password: '',
    icon_id: null
});
const formErrors = ref({});
const allFields = [
    { key: 'service', label: 'Servicio / Sitio Web', type: 'text', placeholder: 'Ej. Netflix, Gmail', required: true },
    { key: 'username', label: 'Nombre de Usuario / Email', type: 'text', placeholder: 'usuario@ejemplo.com', required: false },
    { key: 'password', label: 'Contraseña a Guardar', type: 'password', placeholder: 'Contraseña del servicio', required: true, autocomplete: 'new-password' },
    { key: 'master_password', label: 'Tu Contraseña de Login (para cifrar)', type: 'password', placeholder: 'Confirma tu clave para cifrar', required: true, autocomplete: 'current-password' }
];

const activeFields = computed(() => {
    if (isEditing.value) {
        // Only service field for editing (username/password are encrypted and shouldn't be edited here as per request)
        return allFields.filter(f => f.key === 'service');
    }
    return allFields;
});

// Confirmation Logic
const pendingAction = ref(null); // 'view'
const pendingData = ref(null);   // Data associated with the action

// Revealed Data State
const revealedData = ref(null); // { password: '...', username: '...', icon: null }
const timeLeft = ref(10);
const timerProgress = ref(100);
let destroyTimer = null;
let progressInterval = null;

// Table Data
const { 
    data: vaultItems, 
    loading: isLoading, 
    pagination, 
    fetchData: fetchVaultItems 
} = useTableData(() => api.vault.index(), {
    mode: 'client',
    itemsPerPage,
    searchQuery
});

// Handlers
const openCreateModal = () => {
    isEditing.value = false;
    editingId.value = null;
    vaultForm.service = '';
    vaultForm.username = '';
    vaultForm.password = '';
    vaultForm.master_password = '';
    vaultForm.icon_id = null;
    formErrors.value = {};
    fetchAvailableIcons();
    showFormModal.value = true;
};

const handleEdit = (row) => {
    isEditing.value = true;
    editingId.value = row.id;
    vaultForm.service = row.service;
    vaultForm.icon_id = row.icon_id;
    vaultForm.username = ''; // Not used in edit
    vaultForm.password = ''; // Not used in edit
    vaultForm.master_password = ''; // Not used in edit
    formErrors.value = {};
    fetchAvailableIcons();
    showFormModal.value = true;
};

const handleFormSubmit = async () => {
    // Validate locally
    if (!vaultForm.service) {
        alert.toast.error('Error', 'El nombre del servicio es obligatorio', 3000);
        return;
    }
    
    if (!isEditing.value && (!vaultForm.password || !vaultForm.master_password)) {
        alert.toast.error('Error', 'Todos los campos obligatorios deben completarse', 3000);
        return;
    }
    
    isSaving.value = true;
    try {
        if (isEditing.value) {
            await api.vault.update(editingId.value, {
                service: vaultForm.service,
                icon_id: vaultForm.icon_id
            });
            alert.toast.success('Actualizado', 'Datos actualizados correctamente.');
        } else {
            await api.vault.store({ ...vaultForm });
            alert.toast.success('Guardado', 'Contraseña cifrada y guardada.');
        }
        
        showFormModal.value = false;
        fetchVaultItems();
        
        // Clear sensitive data
        vaultForm.password = '';
        vaultForm.master_password = '';
    } catch (error) {
        formErrors.value = error.response?.data?.errors || {};
        if (error.response?.data?.message) {
             alert.toast.error('Error', error.response.data.message);
        }
    } finally {
        isSaving.value = false;
    }
};

const handleViewPassword = (row) => {
    pendingAction.value = 'view';
    pendingData.value = row;
    showConfirmModal.value = true;
};

const handleDelete = async (row) => {
    const confirmed = await alert.fire({
        title: '¿Eliminar contraseña?',
        text: `Esta acción no se puede deshacer.`,
        type: 'warning',
        showCancel: true,
        confirmText: 'Sí, eliminar',
    });

    if (confirmed) {
        try {
            await api.vault.destroy(row.id);
            alert.toast.success('Eliminado', 'Contraseña eliminada correctamente.');
            fetchVaultItems();
        } catch (error) {
            alert.toast.error('Error', 'No se pudo eliminar el item.');
        }
    }
};

const handleConfirmation = async (masterPassword) => {
    if (pendingAction.value === 'create') {
        confirmModalRef.value.setLoading(true);
        try {
            await api.vault.store({
                ...pendingData.value,
                master_password: masterPassword
            });
            alert.toast.success('Guardado', 'Contraseña cifrada y guardada.');
            showConfirmModal.value = false;
            showCreateModal.value = false;
            fetchVaultItems();
            
            // Clear sensitive data
            createForm.password = '';
            pendingData.value = null;
        } catch (error) {
            confirmModalRef.value.setError(error.response?.data?.message || 'Error al guardar');
        } finally {
            confirmModalRef.value.setLoading(false);
        }
    } else if (pendingAction.value === 'view') {
        confirmModalRef.value.setLoading(true);
        try {
            const response = await api.vault.show(pendingData.value.id, masterPassword);
            showConfirmModal.value = false;
            revealPassword({ 
                password: response.data.password,
                username: response.data.username,
                service: response.data.service || pendingData.value.service,
                icon: pendingData.value.icon
            });
            pendingData.value = null;
        } catch (error) {
            confirmModalRef.value.setError(error.response?.data?.message || 'Contraseña incorrecta o error interno');
        } finally {
            confirmModalRef.value.setLoading(false);
        }
    }
};

// Password Reveal Logic
const revealPassword = (data) => {
    revealedData.value = data;
    timeLeft.value = 10;
    timerProgress.value = 100;

    if (destroyTimer) clearTimeout(destroyTimer);
    if (progressInterval) clearInterval(progressInterval);

    destroyTimer = setTimeout(() => {
        clearRevealedPassword();
    }, 10000);

    progressInterval = setInterval(() => {
        timeLeft.value--;
        timerProgress.value = (timeLeft.value / 10) * 100;
        if (timeLeft.value <= 0) clearInterval(progressInterval);
    }, 1000);
};

const clearRevealedPassword = () => {
    revealedData.value = null;
    if (destroyTimer) clearTimeout(destroyTimer);
    if (progressInterval) clearInterval(progressInterval);
};

const copyToClipboard = async (text, type = 'Contraseña') => {
    if (text) {
        try {
            await navigator.clipboard.writeText(text);
            alert.toast.success('Copiado', `${type} copiada al portapapeles`);
        } catch (e) {
            alert.toast.error('Error', 'No se pudo copiar');
        }
    }
};



onUnmounted(() => {
    clearRevealedPassword();
});
</script>

<style scoped>
.vault-icon-preview {
    display: flex;
    justify-content: center;
    align-items: center;
}

.vault-icon-placeholder {
    width: 24px;
    height: 24px;
    border-radius: 50%;
    background: rgba(255, 255, 255, 0.05);
    display: flex;
    justify-content: center;
    align-items: center;
    color: rgba(255, 255, 255, 0.3);
}

/* Icon Selector Styles (Consistency with DynamicRoutesView) */
.icon-selector-field {
    margin-top: 1rem;
    padding-top: 1rem;
    border-top: 1px solid rgba(255, 255, 255, 0.05);
}

.icon-search-wrapper {
    position: relative;
    margin-bottom: 0.75rem;
}

.icon-search-wrapper :deep(svg) {
    position: absolute;
    left: 10px;
    top: 50%;
    transform: translateY(-50%);
    color: rgba(255, 255, 255, 0.5);
}

.icon-search-wrapper input {
    width: 100%;
    padding: 8px 12px 8px 34px;
    background: rgba(0, 0, 0, 0.2);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 6px;
    color: white;
}

.icon-grid-selector {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(80px, 1fr));
    gap: 8px;
    max-height: 200px;
    overflow-y: auto;
    padding: 8px;
    background: rgba(0, 0, 0, 0.1);
    border-radius: 8px;
    border: 1px solid rgba(255, 255, 255, 0.05);
}

.icon-option {
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 8px;
    border-radius: 6px;
    cursor: pointer;
    transition: all 0.2s;
    border: 2px solid transparent;
}

.icon-option:hover {
    background: rgba(255, 255, 255, 0.05);
}

.icon-option.selected {
    background: rgba(16, 185, 129, 0.1);
    border-color: #10b981;
}

.icon-svg-min {
    margin-bottom: 4px;
}

.icon-name-min {
    font-size: 10px;
    width: 100%;
    text-overflow: ellipsis;
    overflow: hidden;
    white-space: nowrap;
    text-align: center;
    color: rgba(255, 255, 255, 0.6);
}

/* Reveal Modal Styles */
.reveal-content-body {
    text-align: center;
    padding: 1rem 0;
}

.reveal-header {
    position: relative;
    display: flex;
    justify-content: center;
    align-items: center;
    margin-bottom: 1.5rem;
    height: 100px;
}

.icon-glow {
    position: absolute;
    width: 110px;
    height: 110px;
    background: radial-gradient(circle, rgba(16, 185, 129, 0.2) 0%, transparent 70%);
    border-radius: 50%;
    z-index: 1;
    animation: pulse-glow 2s infinite;
}

@keyframes pulse-glow {
    0% { transform: scale(1); opacity: 0.5; }
    50% { transform: scale(1.1); opacity: 0.8; }
    100% { transform: scale(1); opacity: 0.5; }
}

.icon-wrapper {
    position: relative;
    width: 80px;
    height: 80px;
    background: rgba(16, 185, 129, 0.1);
    border: 1px solid rgba(16, 185, 129, 0.3);
    border-radius: 50%;
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 2;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
}

.reveal-content-body h3 {
    font-size: 1.5rem;
    font-weight: 700;
    margin-bottom: 0.5rem;
    color: white;
}

.reveal-content-body .subtitle {
    color: rgba(255, 255, 255, 0.5);
    font-size: 0.9rem;
    margin-bottom: 2rem;
}

.credentials-container {
    display: flex;
    flex-direction: column;
    gap: 1.25rem;
    margin-bottom: 2rem;
}

.credential-group {
    text-align: left;
}

.label-badge {
    display: inline-block;
    font-size: 11px;
    font-weight: 700;
    text-transform: uppercase;
    background: rgba(255, 255, 255, 0.1);
    color: rgba(255, 255, 255, 0.7);
    padding: 2px 8px;
    border-radius: 4px;
    margin-bottom: 6px;
}

.label-badge.highlight {
    background: rgba(16, 185, 129, 0.2);
    color: #10b981;
}

.credential-box {
    background: rgba(0, 0, 0, 0.2);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 8px;
    padding: 12px 14px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    transition: all 0.2s;
}

.credential-box.highlight-box {
    border-color: rgba(16, 185, 129, 0.3);
    background: rgba(16, 185, 129, 0.05);
}

.credential-val {
    font-family: 'JetBrains Mono', 'Fira Code', monospace;
    font-size: 1.1rem;
    color: white;
    letter-spacing: 0.5px;
}

.btn-copy {
    background: transparent;
    border: none;
    color: rgba(255, 255, 255, 0.4);
    cursor: pointer;
    padding: 4px;
    border-radius: 4px;
    transition: all 0.2s;
}

.btn-copy:hover {
    color: #10b981;
    background: rgba(16, 185, 129, 0.1);
}

.timer-section {
    margin-bottom: 2rem;
}

.timer-info {
    display: flex;
    justify-content: space-between;
    font-size: 0.85rem;
    color: rgba(255, 255, 255, 0.5);
    margin-bottom: 8px;
}

.time-val {
    color: #10b981;
    font-weight: 700;
}

.progress-track {
    height: 4px;
    background: rgba(255, 255, 255, 0.05);
    border-radius: 2px;
    overflow: hidden;
}

.progress-fill {
    height: 100%;
    background: #10b981;
    transition: width 1s linear;
}

.btn-hide {
    width: 100%;
    padding: 12px;
    background: transparent;
    border: 1px solid rgba(255, 255, 255, 0.1);
    color: rgba(255, 255, 255, 0.7);
    border-radius: 8px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s;
}

.btn-hide:hover {
    background: rgba(255, 255, 255, 0.05);
    color: white;
}
</style>


