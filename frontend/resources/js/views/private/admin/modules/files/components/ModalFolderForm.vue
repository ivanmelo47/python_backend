<template>
    <component
        :is="embedded ? 'div' : ModalForm"
        v-bind="modalProps"
        class="folder-form-shell"
        :class="{ 'folder-form-embedded': embedded }"
        @close="$emit('close')"
        @submit="handleSubmit"
    >
        <template v-if="!embedded" #header-icon>
            <Icon :name="isEdit ? 'edit' : 'folder-plus'" :size="20" />
        </template>

        <ModalField
            label="Nombre de la carpeta"
            required
            span="full"
        >
            <input
                v-model="form.name"
                type="text"
                placeholder="Ej: Documentos de Marketing"
                required
                autofocus
            />
        </ModalField>

        <ModalField
            label="Icono Personalizado"
            span="full"
        >
            <IconSelect
                v-model="form.icon_uuid"
                :selected-icon-data="initialIconData"
            />
        </ModalField>


        <div class="visibility-section" v-if="!!props.parentPublic">
            <div class="visibility-title">Visibilidad de la Carpeta</div>

            <div class="visibility-options">
                <label
                    class="visibility-option"
                    :class="{ active: visibilityMode === 'private' }"
                >
                    <input
                        type="radio"
                        name="visibility"
                        value="private"
                        v-model="visibilityMode"
                    >
                    <Icon name="lock" :size="20" />
                    <div class="option-content">
                        <span class="option-title">Privada</span>
                        <span class="option-description">Solo yo</span>
                    </div>
                </label>

                <label
                    class="visibility-option"
                    :class="{ active: visibilityMode === 'public' }"
                >
                    <input
                        type="radio"
                        name="visibility"
                        value="public"
                        v-model="visibilityMode"
                    >
                    <Icon name="unlock" :size="20" />
                    <div class="option-content">
                        <span class="option-title">Pública</span>
                        <span class="option-description">Todos los usuarios</span>
                    </div>
                </label>

                <label
                    class="visibility-option"
                    :class="{ active: visibilityMode === 'shared' }"
                >
                    <input
                        type="radio"
                        name="visibility"
                        value="shared"
                        v-model="visibilityMode"
                    >
                    <Icon name="users" :size="20" />
                    <div class="option-content">
                        <span class="option-title">Compartida</span>
                        <span class="option-description">Usuarios específicos</span>
                    </div>
                </label>
            </div>
        </div>

        <!-- User Selector for Shared Mode -->
        <transition name="dropdown-fade">
            <div v-if="visibilityMode === 'shared'" class="shared-users-section">
                <UserSelector v-model="form.shared_users" />
            </div>
        </transition>

        <div class="visibility-warning" v-if="visibilityMode === 'public'">
            <Icon name="shield" :size="16" />
            <span>Los usuarios subordinados podrán ver el contenido de esta carpeta.</span>
        </div>
        <div class="visibility-warning private" v-else-if="visibilityMode === 'private'">
            <Icon name="lock" :size="16" />
            <span v-if="!parentPublic">Esta carpeta será <strong>Privada</strong> (Heredado de carpeta superior).</span>
            <span v-else>Solo tú podrás ver esta carpeta. Ni siquiera tus superiores tienen acceso.</span>
        </div>
        <div class="visibility-warning shared" v-else-if="visibilityMode === 'shared'">
            <Icon name="users" :size="16" />
            <span>Solo los usuarios seleccionados y tú podrán acceder a esta carpeta.</span>
        </div>

        <!-- Automatic Private Cascade Warning -->
        <transition name="dropdown-fade">
            <div class="visibility-warning private cascade" v-if="isEdit && visibilityMode === 'private' && props.folder.is_public">
                <Icon name="info" :size="16" />
                <span><strong>Efecto Cascada Automático:</strong> Todas las subcarpetas públicas se convertirán en <strong>privadas</strong> automáticamente para mantener la integridad de acceso.</span>
            </div>
        </transition>

        <!-- Interactive Cascade Section -->
        <transition name="dropdown-fade">
            <div class="cascade-container" v-if="isEdit && visibilityMode === 'public'">
                <!-- Step 1: Explicit Question -->
                <div class="cascade-question">
                    <label class="checkbox-container small">
                        <input type="checkbox" v-model="applyCascade">
                        <span class="checkmark"></span>
                        <div class="checkbox-label">
                            <span class="title">¿Aplicar visibilidad a subcarpetas?</span>
                            <span class="description">Permite elegir qué carpetas hijas también serán públicas.</span>
                        </div>
                    </label>
                </div>

                <!-- Step 2: Display Tree/Loading/Empty based on answer -->
                <div v-if="applyCascade" class="cascade-logic-wrapper">
                    <div v-if="isFetchingTree" class="cascade-loading">
                        <div class="spinner-small"></div>
                        <span>Cargando estructura...</span>
                    </div>

                    <template v-else-if="descendantsTree.length > 0">
                        <div class="cascade-header">
                            <Icon name="folder-plus" :size="18" />
                            <span>Selecciona carpetas adicionales</span>
                            <div class="tree-badge">{{ selectedDescendantUuids.length }} seleccionadas</div>
                        </div>

                        <div class="tree-wrapper visible">
                            <div class="tree-actions">
                                <button class="btn-action" @click.prevent="selectAll">Seleccionar Todas</button>
                                <button class="btn-action" @click.prevent="selectedDescendantUuids = []">Desmarcar Todas</button>
                            </div>
                            <FolderTreeSelector
                                :tree="descendantsTree"
                                v-model:selected-uuids="selectedDescendantUuids"
                            />
                        </div>
                    </template>

                    <div v-else class="cascade-empty">
                        <Icon name="info" :size="16" />
                        <span v-if="!isFetchingTree">Esta carpeta no tiene subcarpetas para procesar.</span>
                    </div>
                </div>
            </div>
        </transition>
    </component>
</template>

<script setup>
import { ref, reactive, computed, watch } from 'vue';
import Icon from '@/components/Icon.vue';
import ModalForm from '@/views/private/admin/components/ModalForm.vue';
import ModalField from '@/views/private/admin/components/ModalField.vue';
import FolderTreeSelector from './FolderTreeSelector.vue';
import UserSelector from './UserSelector.vue';
import IconSelect from '@/components/IconSelect.vue';
import folderApi from '@/services/api/endpoints/folders';
import { useAlert } from '@/composables/useAlert';
import { useAuth } from '@/composables/useAuth';

const props = defineProps({
    isOpen: Boolean,
    embedded: {
        type: Boolean,
        default: false,
    },
    parentUuid: String,
    parentPublic: {
        type: Boolean,
        default: true
    },
    folder: {
        type: Object,
        default: null
    }
});

const emit = defineEmits(['close', 'created', 'updated']);
const alert = useAlert();
const { user } = useAuth();
const isSubmitting = ref(false);

const isEdit = computed(() => !!props.folder);

const embedded = computed(() => props.embedded);

const modalProps = computed(() => {
    if (embedded.value) return {};

    return {
        isVisible: props.isOpen,
        title: isEdit.value ? 'Editar Carpeta' : 'Nueva Carpeta',
        loading: isSubmitting.value,
        submitLabel: isEdit.value ? 'Guardar Cambios' : 'Crear Carpeta',
        size: 'md',
    };
});

// Cascade state
const applyCascade = ref(false);
const descendantsTree = ref([]);
const selectedDescendantUuids = ref([]);
const isFetchingTree = ref(false);

const visibilityMode = ref('private');

const form = reactive({
    name: '',
    is_public: false,
    parent_uuid: props.parentUuid,
    icon_uuid: null,
    shared_users: []
});

const initialIconData = ref(null);

const fetchDescendants = async () => {
    if (!props.folder?.uuid) return;

    isFetchingTree.value = true;
    try {
        const response = await folderApi.getDescendants(props.folder.uuid);
        // Correct path: response.data (Axios) -> data (App Envelope) -> tree
        descendantsTree.value = response.data.data?.tree || [];
        selectedDescendantUuids.value = [];
    } catch (error) {
        console.error('Error fetching descendants:', error);
        alert.toast.error('Error', 'No se pudo cargar la estructura de carpetas.');
    } finally {
        isFetchingTree.value = false;
    }
};

const selectAll = () => {
    const uuids = [];
    const traverse = (nodes) => {
        nodes.forEach(node => {
            uuids.push(node.uuid);
            if (node.children) traverse(node.children);
        });
    };
    traverse(descendantsTree.value);
    selectedDescendantUuids.value = uuids;
};

// Initialize form for edit or create
watch(() => props.isOpen, (isOpen) => {
    if (isOpen) {
        if (props.folder) {
            form.name = props.folder.name;
            form.is_public = !!props.folder.is_public;

            // Determine visibility mode based on folder state
            if (props.folder.is_public) {
                visibilityMode.value = 'public';
            } else if (props.folder.shared_users && props.folder.shared_users.length > 0) {
                visibilityMode.value = 'shared';
                form.shared_users = props.folder.shared_users.map(u => u.uuid);
            } else {
                visibilityMode.value = 'private';
            }

            form.icon_uuid = props.folder.icon?.uuid || null;
            initialIconData.value = props.folder.icon || null;

            applyCascade.value = false;
            descendantsTree.value = [];
            selectedDescendantUuids.value = [];
        } else {
            form.name = '';
            form.is_public = false;
            form.shared_users = [];
            form.icon_uuid = null;
            initialIconData.value = null;
            visibilityMode.value = 'private';
            if (!props.parentPublic) {
                form.is_public = false;
            }
        }
    }
}, { immediate: true });

// Watch visibility mode and update form data accordingly
watch(visibilityMode, (newMode) => {
    if (newMode === 'public') {
        form.is_public = true;
        form.shared_users = [];
    } else if (newMode === 'shared') {
        form.is_public = false;
        // shared_users managed by UserSelector
    } else { // private
        form.is_public = false;
        form.shared_users = [];
    }
});

// Fetch tree when user says "YES" to cascade
watch(applyCascade, async (val) => {
    if (val && descendantsTree.value.length === 0) {
        await fetchDescendants();
    }
});

const handleSubmit = async () => {
    isSubmitting.value = true;
    try {
        if (isEdit.value) {
            // Bulk update only if cascade is toggled ON and we have selections
            if (applyCascade.value && selectedDescendantUuids.value.length > 0) {
                await folderApi.bulkUpdatePrivacy({
                    uuids: selectedDescendantUuids.value,
                    is_public: true
                });
            }

            await folderApi.updateFolder(props.folder.uuid, {
                name: form.name,
                is_public: form.is_public,
                shared_users: form.shared_users,
                icon_uuid: form.icon_uuid
            });
            alert.toast.success('Éxito', 'Carpeta actualizada correctamente.');
            emit('updated');
        } else {
            await folderApi.createFolder(form);
            alert.toast.success('Éxito', 'Carpeta creada correctamente.');
            emit('created');
        }
    } catch (error) {
        console.error('Error handling folder:', error);
        alert.toast.error('Error', error.response?.data?.message || 'No se pudo procesar la solicitud.');
    } finally {
        isSubmitting.value = false;
    }
};

defineExpose({
    submitForm: handleSubmit,
    isSubmitting,
    isEdit,
});
</script>

<style lang="scss" scoped>
.folder-form-embedded {
    display: grid;
    grid-template-columns: repeat(1, minmax(0, 1fr));
    gap: 1.5rem;
}

.form-row {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 1rem;
    grid-column: 1 / -1;
}

.visibility-section {
    grid-column: 1 / -1;
    margin-top: 0.5rem;

    .visibility-title {
        font-weight: 600;
        color: var(--text-primary);
        margin-bottom: 0.75rem;
        font-size: 0.95rem;
    }

    .visibility-options {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 0.75rem;

        .visibility-option {
            position: relative;
            cursor: pointer;
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 0.5rem;
            padding: 1rem;
            background: var(--bg-primary);
            border: 2px solid var(--border-color);
            border-radius: 12px;
            transition: all 0.2s ease;

            input[type="radio"] {
                position: absolute;
                opacity: 0;
                width: 0;
                height: 0;
            }

            &:hover {
                border-color: var(--primary);
                background: rgba(var(--primary-rgb), 0.02);
            }

            &.active {
                border-color: var(--primary);
                background: rgba(var(--primary-rgb), 0.08);

                .option-title {
                    color: var(--primary);
                }
            }

            .option-content {
                text-align: center;

                .option-title {
                    display: block;
                    font-weight: 600;
                    color: var(--text-primary);
                    font-size: 0.9rem;
                    margin-bottom: 0.2rem;
                }

                .option-description {
                    display: block;
                    font-size: 0.75rem;
                    color: var(--text-tertiary);
                }
            }
        }
    }

    .checkbox-container {
        display: flex;
        align-items: flex-start;
        gap: 1rem;
        cursor: pointer;
        position: relative;
        padding: 1rem;
        background: var(--bg-primary);
        border: 1px solid var(--border-color);
        border-radius: 12px;
        transition: all 0.2s ease;

        &:hover {
            border-color: var(--primary);
            background: rgba(var(--primary-rgb), 0.02);
        }

        input {
            position: absolute;
            opacity: 0;
            cursor: pointer;
            height: 0;
            width: 0;
        }

        .checkmark {
            flex-shrink: 0;
            height: 22px;
            width: 22px;
            background-color: var(--bg-tertiary);
            border: 1px solid var(--border-color);
            border-radius: 6px;
            position: relative;
            margin-top: 2px;

            &:after {
                content: "";
                position: absolute;
                display: none;
                left: 7px;
                top: 3px;
                width: 6px;
                height: 11px;
                border: solid white;
                border-width: 0 2px 2px 0;
                transform: rotate(45deg);
            }
        }

        input:checked ~ .checkmark {
            background-color: var(--primary);
            border-color: var(--primary);
            &:after { display: block; }
        }

        .checkbox-label {
            .title {
                display: block;
                font-weight: 600;
                color: var(--text-primary);
                font-size: 0.95rem;
            }
            .description {
                font-size: 0.8rem;
                color: var(--text-tertiary);
            }
        }

        &.small {
            background: transparent;
            border-color: transparent;
            padding: 0.5rem;

            &:hover {
                border-color: var(--primary-rgb);
            }
        }
    }
}

.shared-users-section {
    grid-column: 1 / -1;
    margin-top: 0.75rem;
}

.visibility-warning {
    grid-column: 1 / -1;
    padding: 0.85rem 1.25rem;
    border-radius: 10px;
    background: rgba(var(--primary-rgb), 0.1);
    border: 1px solid var(--primary);
    color: var(--primary);
    font-size: 0.85rem;
    display: flex;
    align-items: center;
    gap: 0.75rem;
    margin-top: 0.5rem;

    &.private {
        background: rgba(245, 158, 11, 0.1);
        border-color: #f59e0b;
        color: #f59e0b;
    }

    &.shared {
        background: rgba(59, 130, 246, 0.1);
        border-color: #3b82f6;
        color: #3b82f6;
    }

    span {
        line-height: 1.4;
    }
}

.cascade-container {
    grid-column: 1 / -1;
    margin-top: 1.25rem;
    padding: 1.25rem;
    background: var(--bg-secondary);
    border: 1px dashed var(--primary);
    border-radius: 12px;

    .cascade-question {
        margin-bottom: 0.75rem;
    }

    .cascade-logic-wrapper {
        border-top: 1px solid var(--border-color);
        padding-top: 1rem;
        margin-top: 0.5rem;
    }

    .cascade-header {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        margin-bottom: 0.75rem;
        color: var(--primary);
        font-weight: 600;

        .tree-badge {
            margin-left: auto;
            background: var(--primary);
            color: white;
            padding: 0.2rem 0.6rem;
            border-radius: 20px;
            font-size: 0.7rem;
        }
    }

    .cascade-info {
        font-size: 0.85rem;
        color: var(--text-secondary);
        line-height: 1.5;
        margin-bottom: 1rem;
    }

    .tree-wrapper {
        background: var(--bg-primary);
        border: 1px solid var(--border-color);
        border-radius: 8px;
        max-height: 250px;
        overflow-y: auto;

        .tree-actions {
            display: flex;
            gap: 1rem;
            padding: 0.75rem;
            border-bottom: 1px solid var(--border-color);
            position: sticky;
            top: 0;
            background: var(--bg-primary);
            z-index: 10;

            .btn-action {
                font-size: 0.75rem;
                color: var(--primary);
                background: none;
                border: none;
                padding: 0;
                cursor: pointer;
                font-weight: 500;

                &:hover {
                    text-decoration: underline;
                }
            }
        }
    }

    .cascade-loading, .cascade-empty {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        padding: 0.5rem;
        font-size: 0.85rem;
        color: var(--text-tertiary);
    }

    .cascade-loading {
        color: var(--primary);

        .spinner-small {
            width: 16px;
            height: 16px;
            border: 2px solid rgba(var(--primary-rgb), 0.1);
            border-top-color: var(--primary);
            border-radius: 50%;
            animation: spin 0.8s linear infinite;
        }
    }
}

@keyframes spin {
    to { transform: rotate(360deg); }
}

// Dynamic size with max limit and internal scroll for this form
:deep(.modal-container) {
    max-height: 600px;
}
</style>
