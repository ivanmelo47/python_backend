<template>
    <ModalForm
        :isVisible="isOpen"
        title="Crear Enlace Público"
        :loading="isSubmitting"
        submitLabel="Generar Enlace"
        size="md"
        @close="$emit('close')"
        @submit="handleSubmit"
    >
        <template #header-icon>
            <Icon name="link" :size="20" />
        </template>

        <div class="share-header">
            <Icon :name="isFolder ? 'folder' : 'file'" :size="32" class="item-icon" />
            <div class="item-info">
                <div class="item-name">{{ item?.name || 'Cargando...' }}</div>
                <div class="item-type">{{ isFolder ? 'Carpeta' : 'Archivo' }}</div>
            </div>
        </div>

        <ModalField label="Fecha de Caducidad (Opcional)" span="full">
            <input
                v-model="form.expires_at"
                type="datetime-local"
                class="form-input"
            />
        </ModalField>

        <div class="section-divider"></div>

        <div class="passwords-section">
            <div class="section-header">
                <div class="section-title">
                    <Icon name="lock" :size="18" />
                    <span>Contraseñas de Acceso</span>
                </div>
                <button type="button" class="btn-add-password" @click="addPassword">
                    <Icon name="plus" :size="14" />
                    Añadir Contraseña
                </button>
            </div>

            <div v-if="form.passwords.length === 0" class="empty-passwords">
                Este enlace será público y accesible por cualquiera que tenga la URL.
            </div>

            <div class="password-list" v-else>
                <div v-for="(pw, index) in form.passwords" :key="index" class="password-item">
                    <div class="pwd-inputs">
                        <input
                            v-model="pw.password"
                            type="text"
                            placeholder="Introduce la contraseña"
                            class="form-input pwd-field"
                            required
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
                    <button type="button" class="btn-remove" @click="removePassword(index)" title="Eliminar">
                        <Icon name="trash-2" :size="16" />
                    </button>
                </div>
            </div>
        </div>

        <template v-if="isFolder">
            <div class="section-divider"></div>
            
            <div class="visibility-warning">
                <Icon name="shield-off" :size="16" />
                <span>Las <strong>carpetas privadas</strong> ("Solo yo") dentro de esta carpeta se pueden excluir de la vista pública.</span>
            </div>

            <div class="cascade-container">
                <div class="cascade-logic-wrapper">
                    <div v-if="isFetchingTree" class="cascade-loading">
                        <div class="spinner-small"></div>
                        <span>Cargando estructura...</span>
                    </div>

                    <template v-else-if="descendantsTree.length > 0">
                        <div class="cascade-header">
                            <Icon name="eye-off" :size="18" />
                            <span>Excluir Subcarpetas</span>
                            <div class="tree-badge">{{ selectedDescendantUuids.length }} excluidas</div>
                        </div>

                        <div class="tree-wrapper visible">
                            <div class="tree-actions">
                                <button type="button" class="btn-action" @click="selectAll">Excluir Todas</button>
                                <button type="button" class="btn-action" @click="selectedDescendantUuids = []">Incluir Todas</button>
                                <button type="button" class="btn-action primary" @click="selectOnlyPrivate">Excluir Privadas</button>
                            </div>
                            <!-- Reutilizamos el selector de árbol que ya existe para ModalFolderForm -->
                            <FolderTreeSelector
                                :tree="descendantsTree"
                                v-model:selected-uuids="selectedDescendantUuids"
                            />
                        </div>
                    </template>

                    <div v-else class="cascade-empty">
                        <Icon name="info" :size="16" />
                        <span v-if="!isFetchingTree">Esta carpeta no tiene subcarpetas.</span>
                    </div>
                </div>
            </div>
        </template>
    </ModalForm>
</template>

<script setup>
import { ref, reactive, computed, watch } from 'vue';
import Icon from '@/components/Icon.vue';
import ModalForm from '@/views/private/admin/components/ModalForm.vue';
import ModalField from '@/views/private/admin/components/ModalField.vue';
import FolderTreeSelector from './FolderTreeSelector.vue';
import folderApi from '@/services/api/endpoints/folders';
import sharedLinksApi from '@/services/api/endpoints/sharedLinks';
import { useAlert } from '@/composables/useAlert';

const props = defineProps({
    isOpen: Boolean,
    item: {
        type: Object,
        default: null
    },
    isFolder: {
        type: Boolean,
        default: false
    }
});

const emit = defineEmits(['close', 'created']);
const alert = useAlert();
const isSubmitting = ref(false);

const descendantsTree = ref([]);
const selectedDescendantUuids = ref([]);
const isFetchingTree = ref(false);

const form = reactive({
    expires_at: '',
    passwords: [],
    excluded_folders: [] // se mapearán luego a IDs numéricos si el backend así lo espera, o mantendremos UUIDs
});

const addPassword = () => {
    form.passwords.push({ password: '', usage_limit: null });
};

const removePassword = (index) => {
    form.passwords.splice(index, 1);
};

const fetchDescendants = async () => {
    if (!props.isFolder || !props.item?.uuid) return;

    isFetchingTree.value = true;
    try {
        const response = await folderApi.getDescendants(props.item.uuid);
        descendantsTree.value = response.data.data?.tree || [];
        selectedDescendantUuids.value = [];
        
        // Auto select private folders by default to prevent accidental leaks
        selectOnlyPrivate();
        
    } catch (error) {
        console.error('Error fetching descendants:', error);
        alert.toast.error('Error', 'No se pudo cargar la estructura de subcarpetas.');
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

const selectOnlyPrivate = () => {
    const uuids = [];
    const traverse = (nodes) => {
        nodes.forEach(node => {
            if (!node.is_public) {
                uuids.push(node.uuid);
            }
            if (node.children) traverse(node.children);
        });
    };
    traverse(descendantsTree.value);
    selectedDescendantUuids.value = uuids;
};

// Flatten tree to easily map UUIDs back to IDs
const flattenTree = (nodes, flatArray = []) => {
    nodes.forEach(node => {
        flatArray.push(node);
        if (node.children) flattenTree(node.children, flatArray);
    });
    return flatArray;
};

watch(() => props.isOpen, async (isOpen) => {
    if (isOpen) {
        form.expires_at = '';
        form.passwords = [];
        form.excluded_folders = [];
        
        descendantsTree.value = [];
        selectedDescendantUuids.value = [];
        
        if (props.isFolder) {
            await fetchDescendants();
        }
    }
}, { immediate: true });

const handleSubmit = async () => {
    isSubmitting.value = true;
    try {
        const shareable_type = props.isFolder ? 'folder' : 'file';

        // Cleanup empty passwords string
        const cleanedPasswords = form.passwords.filter(pw => pw.password.trim() !== '');

        const payload = {
            shareable_id: props.item.uuid,
            shareable_type: shareable_type,
            expires_at: form.expires_at || null,
            passwords: cleanedPasswords,
            excluded_folders: selectedDescendantUuids.value.length > 0 ? selectedDescendantUuids.value : null,
        };

        const res = await sharedLinksApi.create(payload);
        alert.toast.success('¡Enlace Creado!', 'El enlace público está listo para ser compartido.');
        emit('created', res.data.link);
        emit('close');
        
    } catch (error) {
        console.error('Error creating link:', error);
        alert.toast.error('Error', error.response?.data?.message || 'No se pudo crear el enlace.');
    } finally {
        isSubmitting.value = false;
    }
};

</script>

<style lang="scss" scoped>
.share-header {
    display: flex;
    align-items: center;
    gap: 1rem;
    padding: 1rem;
    background: var(--bg-secondary);
    border-radius: 8px;
    margin-bottom: 1.5rem;
    border: 1px solid var(--border-color);

    .item-icon {
        color: var(--primary);
        opacity: 0.8;
    }

    .item-info {
        display: flex;
        flex-direction: column;

        .item-name {
            font-weight: 600;
            color: var(--text-primary);
            font-size: 1.05rem;
            word-break: break-all;
        }

        .item-type {
            font-size: 0.8rem;
            color: var(--text-tertiary);
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-top: 2px;
        }
    }
}

.section-divider {
    height: 1px;
    background: var(--border-color);
    margin: 1.5rem 0;
}

.passwords-section {
    .section-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1rem;

        .section-title {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            font-weight: 600;
            color: var(--text-primary);
        }

        .btn-add-password {
            display: flex;
            align-items: center;
            gap: 0.25rem;
            background: rgba(var(--primary-rgb), 0.1);
            color: var(--primary);
            border: 1px dashed var(--primary);
            padding: 0.4rem 0.75rem;
            border-radius: 6px;
            font-size: 0.8rem;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.2s;

            &:hover {
                background: var(--primary);
                color: white;
            }
        }
    }

    .empty-passwords {
        padding: 1rem;
        text-align: center;
        background: var(--bg-secondary);
        border: 1px dashed var(--border-color);
        border-radius: 8px;
        color: var(--text-tertiary);
        font-size: 0.85rem;
    }

    .password-list {
        display: flex;
        flex-direction: column;
        gap: 0.75rem;

        .password-item {
            display: flex;
            gap: 0.5rem;
            align-items: flex-start;

            .pwd-inputs {
                flex: 1;
                display: flex;
                gap: 0.5rem;

                .pwd-field {
                    flex: 2;
                }

                .limit-input {
                    flex: 1;
                    position: relative;
                    display: flex;
                    align-items: center;

                    input {
                        padding-right: 4.5rem;
                    }

                    .limit-label {
                        position: absolute;
                        right: 0.75rem;
                        font-size: 0.7rem;
                        color: var(--text-tertiary);
                        pointer-events: none;
                    }
                }
            }

            .btn-remove {
                background: rgba(239, 68, 68, 0.1);
                color: #ef4444;
                border: none;
                width: 38px;
                height: 38px;
                border-radius: 8px;
                display: flex;
                align-items: center;
                justify-content: center;
                cursor: pointer;
                transition: all 0.2s;
                flex-shrink: 0;

                &:hover {
                    background: #ef4444;
                    color: white;
                }
            }
        }
    }
}

.form-input {
    width: 100%;
    padding: 0.5rem 0.75rem;
    border: 1px solid var(--border-color);
    border-radius: 6px;
    background: var(--bg-primary);
    color: var(--text-primary);
    font-size: 0.9rem;
    height: 38px;
    box-sizing: border-box;

    &:focus {
        outline: none;
        border-color: var(--primary);
        box-shadow: 0 0 0 2px rgba(var(--primary-rgb), 0.1);
    }
}

/* Reusing cascade logic styles from ModalFolderForm */
.visibility-warning {
    padding: 0.85rem 1.25rem;
    border-radius: 10px;
    background: rgba(245, 158, 11, 0.1);
    border: 1px solid #f59e0b;
    color: #f59e0b;
    font-size: 0.85rem;
    display: flex;
    align-items: center;
    gap: 0.75rem;
}

.cascade-container {
    margin-top: 1.25rem;
    padding: 1.25rem;
    background: var(--bg-secondary);
    border: 1px dashed var(--border-color);
    border-radius: 12px;

    .cascade-header {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        margin-bottom: 0.75rem;
        color: var(--text-primary);
        font-weight: 600;

        .tree-badge {
            margin-left: auto;
            background: var(--text-tertiary);
            color: white;
            padding: 0.2rem 0.6rem;
            border-radius: 20px;
            font-size: 0.7rem;
        }
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
                color: var(--text-secondary);
                background: none;
                border: none;
                padding: 0;
                cursor: pointer;
                font-weight: 500;

                &:hover {
                    text-decoration: underline;
                }
                
                &.primary {
                    color: var(--primary);
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

:deep(.modal-container) {
    max-height: 85vh;
}
</style>
