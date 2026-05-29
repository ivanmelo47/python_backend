<template>
    <div class="user-selector">
        <div class="search-wrapper">
            <Icon name="search" :size="16" />
            <input 
                v-model="searchQuery"
                type="text"
                placeholder="Buscar usuarios..."
                @input="handleSearch"
                @focus="showDropdown = true"
            />
        </div>

        <!-- Selected Users (Tags) -->
        <div v-if="selectedUsers.length > 0" class="selected-users">
            <div 
                v-for="user in selectedUsers" 
                :key="user.uuid"
                class="user-tag"
            >
                <span>{{ user.name }}</span>
                <button 
                    type="button"
                    @click="removeUser(user.uuid)"
                    class="remove-btn"
                    title="Quitar usuario"
                >
                    <Icon name="x" :size="14" />
                </button>
            </div>
        </div>

        <!-- Dropdown with search results -->
        <transition name="dropdown-fade">
            <div 
                v-if="showDropdown && filteredUsers.length > 0" 
                class="users-dropdown"
                v-click-outside="closeDropdown"
            >
                <div 
                    v-for="user in filteredUsers" 
                    :key="user.uuid"
                    class="user-item"
                    :class="{ selected: isSelected(user.uuid) }"
                    @click="toggleUser(user)"
                >
                    <div class="user-info">
                        <span class="user-name">{{ user.name }}</span>
                        <span class="user-email">{{ user.email }}</span>
                    </div>
                    <Icon 
                        v-if="isSelected(user.uuid)" 
                        name="check" 
                        :size="16" 
                        class="check-icon"
                    />
                </div>
            </div>
        </transition>

        <div v-if="loading" class="loading-state">
            <div class="spinner-small"></div>
            <span>Cargando usuarios...</span>
        </div>

        <div v-if="!loading && searchQuery && filteredUsers.length === 0" class="empty-state">
            <Icon name="userX" :size="20" />
            <span>No se encontraron usuarios</span>
        </div>
    </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import Icon from '@/components/Icon.vue';
import folderApi from '@/services/api/endpoints/folders';

const props = defineProps({
    modelValue: {
        type: Array,
        default: () => []
    }
});

const emit = defineEmits(['update:modelValue']);

const searchQuery = ref('');
const showDropdown = ref(false);
const loading = ref(false);
const availableUsers = ref([]);
const selectedUsers = ref([]);

// Initialize selected users from modelValue
onMounted(async () => {
    await fetchUsers();
    
    // Map modelValue (array of UUIDs) to full user objects
    if (props.modelValue && props.modelValue.length > 0) {
        selectedUsers.value = availableUsers.value.filter(u => 
            props.modelValue.includes(u.uuid)
        );
    }
});

const fetchUsers = async () => {
    loading.value = true;
    try {
        const response = await folderApi.getShareableUsers();
        availableUsers.value = response.data.data || response.data || [];
    } catch (error) {
        console.error('Error fetching users:', error);
    } finally {
        loading.value = false;
    }
};

const filteredUsers = computed(() => {
    // Exclude already selected users
    const unselectedUsers = availableUsers.value.filter(user => 
        !isSelected(user.uuid)
    );
    
    if (!searchQuery.value) return unselectedUsers;
    
    const query = searchQuery.value.toLowerCase();
    return unselectedUsers.filter(user => 
        user.name.toLowerCase().includes(query) ||
        user.email.toLowerCase().includes(query)
    );
});

const isSelected = (uuid) => {
    return selectedUsers.value.some(u => u.uuid === uuid);
};

const toggleUser = (user) => {
    if (isSelected(user.uuid)) {
        removeUser(user.uuid);
    } else {
        selectedUsers.value.push(user);
        searchQuery.value = ''; // Clear search after adding
        emitUpdate();
    }
};

const removeUser = (userUuid) => {
    selectedUsers.value = selectedUsers.value.filter(u => u.uuid !== userUuid);
    emitUpdate();
};

const emitUpdate = () => {
    emit('update:modelValue', selectedUsers.value.map(u => u.uuid));
};

const handleSearch = () => {
    if (searchQuery.value.length > 0) {
        showDropdown.value = true;
    }
};

const closeDropdown = () => {
    showDropdown.value = false;
};
</script>

<style lang="scss" scoped>
.user-selector {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
    position: relative;

    .search-wrapper {
        position: relative;
        display: flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.75rem 1rem;
        background: var(--bg-tertiary);
        border: 1px solid var(--border-color);
        border-radius: 8px;
        transition: all 0.2s ease;

        &:focus-within {
            border-color: var(--primary);
            background: var(--bg-primary);
        }

        input {
            flex: 1;
            background: transparent;
            border: none;
            outline: none;
            color: var(--text-primary);
            font-size: 0.9rem;

            &::placeholder {
                color: var(--text-tertiary);
            }
        }
    }

    .selected-users {
        display: flex;
        flex-wrap: wrap;
        gap: 0.5rem;

        .user-tag {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            padding: 0.4rem 0.75rem;
            background: var(--primary);
            color: white;
            border-radius: 20px;
            font-size: 0.85rem;
            font-weight: 500;

            .remove-btn {
                background: none;
                border: none;
                padding: 0;
                cursor: pointer;
                display: flex;
                align-items: center;
                color: white;
                opacity: 0.8;
                transition: opacity 0.2s;

                &:hover {
                    opacity: 1;
                }
            }
        }
    }

    .users-dropdown {
        position: absolute;
        top: calc(100% + 0.5rem);
        left: 0;
        right: 0;
        max-height: 250px;
        overflow-y: auto;
        background: var(--bg-primary);
        border: 1px solid var(--border-color);
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        z-index: 100;

        .user-item {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0.75rem 1rem;
            cursor: pointer;
            transition: background 0.2s;

            &:hover {
                background: var(--bg-secondary);
            }

            &.selected {
                background: rgba(var(--primary-rgb), 0.1);
            }

            .user-info {
                display: flex;
                flex-direction: column;
                gap: 0.2rem;

                .user-name {
                    font-weight: 500;
                    color: var(--text-primary);
                    font-size: 0.9rem;
                }

                .user-email {
                    font-size: 0.8rem;
                    color: var(--text-tertiary);
                }
            }

            .check-icon {
                color: var(--primary);
            }
        }
    }

    .loading-state,
    .empty-state {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.75rem;
        font-size: 0.85rem;
        color: var(--text-tertiary);
        justify-content: center;

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

.dropdown-fade-enter-active,
.dropdown-fade-leave-active {
    transition: all 0.2s ease;
}

.dropdown-fade-enter-from,
.dropdown-fade-leave-to {
    opacity: 0;
    transform: translateY(-10px);
}
</style>
