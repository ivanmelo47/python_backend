<template>
    <div class="public-links-manager">
        <div class="manager-header">
            <div class="manager-nav-bar">
                <div class="nav-left">
                    <div class="nav-chip active">
                        <Icon name="link" :size="14" />
                        <span>Enlaces públicos</span>
                    </div>
                    <span class="nav-counter">{{ filteredLinks.length }} enlaces</span>
                </div>

                <div class="nav-controls">
                    <div class="search-box">
                        <Icon name="search" :size="18" />
                        <input v-model="searchQuery" type="text" :placeholder="isPrivilegedUser ? 'Buscar entre enlaces públicos...' : 'Buscar entre tus archivos públicos...'" />
                    </div>

                    <div v-if="isPrivilegedUser" class="creator-filter">
                        <Icon name="user" :size="16" class="creator-filter-icon" />
                        <select v-model="selectedCreator">
                            <option value="">Todos los usuarios</option>
                            <option v-for="opt in creatorOptions" :key="opt.uuid" :value="opt.uuid">
                                {{ opt.name }}
                            </option>
                        </select>
                    </div>

                    <div class="view-toggles">
                        <button class="toggle-btn" :class="{ active: viewMode === 'grid' }" @click="setLocalViewMode('grid')" title="Vista tarjetas">
                            <Icon name="grid" :size="16" />
                        </button>
                        <button class="toggle-btn" :class="{ active: viewMode === 'list' }" @click="setLocalViewMode('list')" title="Vista lista">
                            <Icon name="list" :size="16" />
                        </button>
                    </div>
                </div>
            </div>
        </div>

        <!-- Links Grid/List -->
        <div v-if="loading" class="manager-loading">
            <div class="loader"></div>
            <span>Cargando enlaces...</span>
        </div>

        <div v-else-if="filteredLinks.length === 0" class="manager-empty">
            <div class="empty-icon">
                <Icon name="link" :size="64" />
            </div>
            <h3>No hay enlaces públicos</h3>
            <p>{{ emptyStateMessage }}</p>
        </div>

        <div v-else class="manager-body" :class="viewMode">
            <div v-for="link in filteredLinks" :key="link.uuid" class="link-card" :class="viewMode">
                <div class="link-icon-section">
                    <div class="file-icon-wrapper">
                         <Icon v-if="link.icon" :name="link.icon" :size="viewMode === 'grid' ? 48 : 24" />
                         <Icon v-else :name="getFileIcon(link.extension)" :size="viewMode === 'grid' ? 48 : 24" />
                         <div class="extension-badge">{{ link.extension.toUpperCase() }}</div>
                    </div>
                </div>

                <div class="link-details">
                    <div class="link-main-info">
                        <span class="file-name" :title="link.name">{{ link.name }}</span>
                        <div class="folder-ref">
                            <Icon name="folder" :size="12" />
                            <span>{{ link.folder_name }}</span>
                        </div>
                        <div v-if="link.creator_name" class="creator-ref" :title="`Creado por ${link.creator_name}`">
                            <Icon name="user" :size="12" />
                            <span>{{ link.creator_name }}</span>
                        </div>
                    </div>

                    <div v-if="viewMode === 'grid'" class="link-meta">
                        <div class="meta-item">
                            <Icon :name="link.is_active ? 'check' : 'x'" :size="12" />
                            <span>{{ link.is_active ? 'Activo' : 'Inactivo' }}</span>
                        </div>
                        <div class="meta-item" v-if="link.expires_at">
                            <Icon name="clock" :size="12" />
                            <span>Caduca: {{ formatDate(link.expires_at) }}</span>
                        </div>
                        <div class="meta-item" v-else>
                            <Icon name="check" :size="12" />
                            <span>Permanente</span>
                        </div>
                        <div class="meta-item" v-if="link.downloads !== undefined">
                            <Icon name="download" :size="12" />
                            <span>{{ link.downloads }} dl</span>
                        </div>
                    </div>

                    <div v-else class="link-meta list-meta">
                        <div class="meta-item" :class="{ 'is-active': link.is_active, 'is-inactive': !link.is_active }">
                            <Icon :name="link.is_active ? 'check' : 'x'" :size="12" />
                            <span>{{ link.is_active ? 'Activo' : 'Inactivo' }}</span>
                        </div>
                        <div class="meta-item" v-if="link.expires_at">
                            <Icon name="clock" :size="12" />
                            <span>Caduca: {{ formatDate(link.expires_at) }}</span>
                        </div>
                        <div class="meta-item" v-else>
                            <Icon name="check" :size="12" />
                            <span>Permanente</span>
                        </div>
                        <div class="meta-item" v-if="link.downloads !== undefined">
                            <Icon name="download" :size="12" />
                            <span>{{ link.downloads }} descargas</span>
                        </div>
                    </div>
                </div>

                <div class="link-actions">
                    <label
                        class="inline-status-switch"
                        :class="{ disabled: !canToggleLink(link) || isLinkToggling(link) }"
                        :title="
                            !canToggleLink(link)
                                ? 'No tienes permisos para activar o desactivar este enlace'
                                : link.is_active
                                    ? 'Desactivar enlace'
                                    : 'Activar enlace'
                        "
                        @click.stop
                    >
                        <input
                            type="checkbox"
                            :checked="!!link.is_active"
                            :disabled="!canToggleLink(link) || isLinkToggling(link)"
                            @change="toggleLinkActive(link)"
                        />
                        <span class="inline-slider round">
                            <span class="inline-slider-knob">
                                <Icon :name="link.is_active ? 'check' : 'x'" :size="10" />
                            </span>
                        </span>
                    </label>
                    <button @click="openLink(link)" class="btn-open-link" title="Abrir en pestaña nueva">
                        <Icon name="external-link" :size="16" />
                    </button>
                    <button
                        @click="link.can_edit && openEditModal(link)"
                        class="btn-open-link"
                        :class="{ disabled: !link.can_edit }"
                        :disabled="!link.can_edit"
                        :title="link.can_edit ? 'Editar enlace' : 'Solo puedes editar tus propios enlaces'"
                    >
                        <Icon name="pencil" :size="16" />
                    </button>
                    <button @click="copyPublicLink(link)" class="btn-copy-link" title="Copiar enlace de descarga">
                        <Icon name="link" :size="16" />
                        <span v-if="viewMode === 'list'">Copiar Enlace</span>
                    </button>
                    <button
                        @click="link.can_edit && deleteLink(link)"
                        class="btn-open-link btn-delete"
                        :class="{ disabled: !link.can_edit }"
                        :disabled="!link.can_edit"
                        :title="link.can_edit ? 'Eliminar enlace' : 'Solo puedes editar o eliminar tus propios enlaces'"
                    >
                        <Icon name="trash" :size="16" />
                    </button>
                </div>
            </div>
        </div>

        <div v-if="showEditModal" class="edit-modal-overlay" @click.self="closeEditModal">
            <div class="edit-modal-card custom-scroll">
                <div class="edit-modal-header">
                    <h3>Editar Enlace Público</h3>
                    <button class="btn-open-link" @click="closeEditModal" title="Cerrar">
                        <Icon name="x" :size="16" />
                    </button>
                </div>

                <p class="edit-modal-subtitle" v-if="editingLink">
                    {{ editingLink.name }}
                </p>

                <div class="edit-field">
                    <label class="switch-row">
                        <span class="switch-label">Enlace activo</span>
                        <label class="switch" @click.stop>
                            <input type="checkbox" v-model="editForm.is_active" />
                            <span class="slider round">
                                <span class="slider-knob">
                                    <Icon :name="editForm.is_active ? 'check' : 'x'" :size="10" />
                                </span>
                            </span>
                        </label>
                    </label>
                </div>

                <div class="edit-field">
                    <label for="edit-expires">Fecha de expiración (opcional)</label>
                    <input id="edit-expires" type="datetime-local" v-model="editForm.expires_at" class="form-input" />
                    <small>Si lo dejas vacío, el enlace será permanente.</small>
                </div>

                <div class="section-divider"></div>

                <div class="passwords-section">
                    <div class="section-header">
                        <div class="section-title">
                            <Icon name="lock" :size="18" />
                            <span>Contraseñas de Acceso</span>
                        </div>
                        <button type="button" class="btn-add-password" @click="addEditPassword">
                            <Icon name="plus" :size="14" />
                            Añadir Contraseña
                        </button>
                    </div>

                    <div v-if="editForm.passwords.length === 0" class="empty-passwords">
                        Este enlace será público y accesible por cualquiera que tenga la URL.
                    </div>

                    <div class="password-list" v-else>
                        <div v-for="(pw, index) in editForm.passwords" :key="index" class="password-item">
                            <div class="pwd-inputs">
                                <input
                                    v-model="pw.password"
                                    type="text"
                                    :placeholder="pw.id ? 'Dejar vacío para no cambiar' : 'Introduce la contraseña'"
                                    class="form-input pwd-field"
                                    :required="!pw.id"
                                />
                                <div class="limit-input">
                                    <input
                                        v-model.number="pw.usage_limit"
                                        type="number"
                                        placeholder="∞ Usos"
                                        min="1"
                                        class="form-input"
                                        title="Dejar en blanco para usos ilimitados"
                                    />
                                    <span class="limit-label">usos máx.</span>
                                </div>
                            </div>
                            <button type="button" class="btn-remove" @click="removeEditPassword(index)" title="Eliminar">
                                <Icon name="trash-2" :size="16" />
                            </button>
                        </div>
                    </div>
                </div>

                <div class="edit-modal-actions">
                    <button class="btn-cancel" @click="closeEditModal">Cancelar</button>
                    <button class="btn-save" @click="saveEditModal" :disabled="savingEdit">
                        <Icon v-if="!savingEdit" name="check" :size="16" />
                        <span class="spinner-small" v-else></span>
                        <span>{{ savingEdit ? 'Guardando...' : 'Guardar cambios' }}</span>
                    </button>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue';
import Icon from '@/components/Icon.vue';
import { useAlert } from '@/composables/useAlert';
import { useAuth } from '@/composables/useAuth';
import { useTableConfig } from '@/composables/useTableConfig';
import { buildPublicShareUrl } from '@/services/api/url';
import sharedLinksApi from '@/services/api/endpoints/sharedLinks';
import usersApi from '@/services/api/endpoints/users';

const alert = useAlert();
const { user } = useAuth();
const { viewMode: globalTableViewMode, setViewMode } = useTableConfig();

const links = ref([]);
const searchQuery = ref('');
const viewMode = ref(globalTableViewMode.value === 'list' ? 'list' : 'grid');
const loading = ref(true);
const selectedCreator = ref('');
const creatorOptions = ref([]);
const showEditModal = ref(false);
const savingEdit = ref(false);
const editingLink = ref(null);
const togglingLinks = ref({});
const editForm = ref({
    is_active: true,
    expires_at: '',
    passwords: [],
});

const isPrivilegedUser = computed(() => {
    const roleName = String(user.value?.role?.name || '').toLowerCase();
    return roleName === 'admin' || roleName === 'master' || !!user.value?.is_supermaster;
});

const emptyStateMessage = computed(() => {
    if (isPrivilegedUser.value && selectedCreator.value) {
        return 'No hay enlaces públicos para el usuario seleccionado.';
    }

    return isPrivilegedUser.value
        ? 'No hay enlaces públicos registrados actualmente.'
        : 'Los archivos que estén en tus carpetas públicas aparecerán aquí automáticamente.';
});

const fetchLinks = async () => {
    loading.value = true;
    try {
        const params = {};

        if (isPrivilegedUser.value && selectedCreator.value) {
            params.created_by = selectedCreator.value;
        }

        const res = await sharedLinksApi.getAll(params);
        links.value = res.data.data || [];
    } catch (error) {
        console.error('Error fetching shared links:', error);
        alert.toast.error('Error', 'No se pudieron cargar los enlaces públicos.');
    } finally {
        loading.value = false;
    }
};

const fetchCreatorOptions = async () => {
    if (!isPrivilegedUser.value) {
        creatorOptions.value = [];
        selectedCreator.value = '';
        return;
    }

    try {
        const response = await usersApi.getSelectableUsers();
        const usersData = response.data?.data || response.data || [];
        creatorOptions.value = usersData
            .map((u) => ({
                uuid: u.uuid,
                name: u.name,
            }))
            .filter((u) => !!u.uuid && !!u.name);
    } catch (error) {
        console.error('Error loading creator options:', error);
        creatorOptions.value = [];
    }
};

onMounted(() => {
    fetchCreatorOptions();
    fetchLinks();
});

watch(selectedCreator, () => {
    fetchLinks();
});

watch(globalTableViewMode, (mode) => {
    viewMode.value = mode === 'list' ? 'list' : 'grid';
}, { immediate: true });

const filteredLinks = computed(() => {
    if (!searchQuery.value) return links.value;
    const query = searchQuery.value.toLowerCase();
    return links.value.filter(link => 
        link.name.toLowerCase().includes(query) || 
        (link.folder_name && link.folder_name.toLowerCase().includes(query))
    );
});

const getFileIcon = (ext) => {
    const safeExt = String(ext || '').toLowerCase();
    const extMap = {
        'pdf': 'file-text',
        'png': 'file',
        'jpg': 'file',
        'jpeg': 'file',
        'docx': 'file-text',
        'xlsx': 'file-text',
        'mp4': 'file',
        'zip': 'archiveFill',
        'rar': 'archiveFill',
        'folder': 'folder-open',
    };
    return extMap[safeExt] || 'file';
};

const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('es-ES', { day: '2-digit', month: 'short' });
};

const setLocalViewMode = (mode) => {
    const normalized = mode === 'list' ? 'list' : 'grid';
    viewMode.value = normalized;
    setViewMode(normalized, true);
};

const copyPublicLink = (link) => {
    const publicUrl = buildPublicShareUrl(link?.token || link?.public_url || '');
    if (!publicUrl) {
        alert.toast.error('Error', 'No se pudo resolver la URL pública del enlace.');
        return;
    }

    navigator.clipboard.writeText(publicUrl);
    alert.toast.success('¡Copiado!', 'El enlace público se ha copiado al portapapeles.');
};

const openLink = (link) => {
    const publicUrl = buildPublicShareUrl(link?.token || link?.public_url || '');
    if (!publicUrl) {
        alert.toast.error('Error', 'No se pudo abrir la URL pública del enlace.');
        return;
    }

    window.open(publicUrl, '_blank');
};

const openEditModal = (link) => {
    if (!link?.can_edit) {
        alert.toast.warning('Acceso restringido', 'Solo puedes editar tus propios enlaces.');
        return;
    }

    editingLink.value = link;
    editForm.value = {
        is_active: !!link.is_active,
        expires_at: link.expires_at ? String(link.expires_at).slice(0, 16) : '',
        passwords: link.passwords ? JSON.parse(JSON.stringify(link.passwords)).map(pw => ({
            ...pw,
            password: '' // Obviamente no recibimos el hash, permitimos poner una nueva
        })) : []
    };
    showEditModal.value = true;
};

const addEditPassword = () => {
    editForm.value.passwords.push({ password: '', usage_limit: null });
};

const removeEditPassword = (index) => {
    editForm.value.passwords.splice(index, 1);
};

const closeEditModal = () => {
    showEditModal.value = false;
    editingLink.value = null;
    editForm.value = { is_active: true, expires_at: '', passwords: [] };
};

const saveEditModal = async () => {
    if (!editingLink.value) return;

    savingEdit.value = true;
    try {
        const payload = {
            is_active: !!editForm.value.is_active,
            expires_at: editForm.value.expires_at || null,
            passwords: editForm.value.passwords.filter(pw => pw.id || pw.password.trim() !== '')
        };

        await sharedLinksApi.update(editingLink.value.token || editingLink.value.uuid, payload);

        alert.toast.success('Actualizado', 'Enlace actualizado correctamente.');
        closeEditModal();
        fetchLinks();
    } catch (error) {
        alert.toast.error('Error', error.response?.data?.message || 'No se pudo actualizar el enlace.');
    } finally {
        savingEdit.value = false;
    }
};

const isLinkToggling = (link) => {
    if (!link?.uuid) return false;
    return !!togglingLinks.value[link.uuid];
};

const canToggleLink = (link) => {
    if (!link) return false;
    if (typeof link.can_toggle !== 'undefined') {
        return !!link.can_toggle;
    }
    return !!link.can_edit;
};

const toggleLinkActive = async (link) => {
    if (!canToggleLink(link)) {
        alert.toast.warning('Acceso restringido', 'No tienes permisos para activar o desactivar este enlace.');
        return;
    }

    const key = link.uuid;
    const prevState = !!link.is_active;
    const nextState = !prevState;

    togglingLinks.value = { ...togglingLinks.value, [key]: true };
    link.is_active = nextState;

    try {
        await sharedLinksApi.update(link.token || link.uuid, {
            is_active: nextState,
        });

        alert.toast.success('Actualizado', nextState ? 'Enlace activado.' : 'Enlace desactivado.');
    } catch (error) {
        link.is_active = prevState;
        alert.toast.error('Error', error.response?.data?.message || 'No se pudo actualizar el estado del enlace.');
    } finally {
        const updated = { ...togglingLinks.value };
        delete updated[key];
        togglingLinks.value = updated;
    }
};

const deleteLink = async (link) => {
    if (!link?.can_edit) {
        alert.toast.warning('Acceso restringido', 'Solo puedes editar o eliminar tus propios enlaces.');
        return;
    }

    const confirmed = await alert.fire({
        title: '¿Eliminar enlace público?',
        text: `¿Estás seguro de que deseas eliminar el enlace para "${link.name}"? Los usuarios externos ya no podrán acceder a él.`,
        type: 'warning',
        showCancel: true,
        confirmText: 'Sí, eliminar',
        cancelText: 'Cancelar'
    });

    if (confirmed) {
        try {
            await sharedLinksApi.delete(link.token || link.uuid);
            alert.toast.success('Eliminado', 'Enlace eliminado correctamente.');
            fetchLinks();
        } catch (error) {
            alert.toast.error('Error', error.response?.data?.message || 'No se pudo eliminar el enlace.');
        }
    }
};
</script>

