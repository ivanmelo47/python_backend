<template>
    <div class="icon-select" v-click-outside="closeDropdown" ref="selectContainer">
        <div 
            class="selection-display" 
            @click.stop="toggleDropdown" 
            :class="{ 'has-selection': modelValue, 'is-open': isOpen }"
        >
            <div class="selected-icon" v-if="localSelectedIcon">
                <div class="icon-svg">
                    <DynamicIcon :name="`db:${localSelectedIcon.name || 'icon'}`" :databaseData="localSelectedIcon" :size="20" />
                </div>
                <span class="icon-name">{{ localSelectedIcon.name }}</span>
            </div>
            <div class="placeholder" v-else>
                <Icon name="folder" :size="20" />
                <span>Por defecto</span>
            </div>

            <div class="controls">
                <button v-if="modelValue" class="clear-btn" @click.stop="clearSelection" title="Resetear">
                    <Icon name="x" :size="14" />
                </button>
                <Icon :name="isOpen ? 'chevronUp' : 'chevronDown'" :size="16" class="arrow" />
            </div>
        </div>

        <Teleport to="body">
            <transition name="dropdown-fade">
                <div 
                    v-if="isOpen" 
                    class="icon-dropdown teleported-dropdown"
                    :style="dropdownStyle"
                    @click.stop
                >
                    <div class="search-container">
                        <Icon name="search" :size="16" class="search-icon" />
                        <input 
                            v-model="search" 
                            type="text" 
                            placeholder="Buscar icono..." 
                            ref="searchInput"
                            class="search-input"
                        />
                    </div>
                    
                    <div class="icons-list" v-if="!loading">
                        <div 
                            class="icon-item default-item" 
                            :class="{ active: !modelValue }"
                            @click="selectIcon(null)"
                        >
                            <Icon name="folder" :size="20" />
                            <span class="icon-name">Por defecto (Carpeta)</span>
                        </div>
                        
                        <div 
                            v-for="icon in filteredIcons" 
                            :key="icon.uuid" 
                            class="icon-item"
                            :class="{ active: modelValue === icon.uuid }"
                            @click.stop.prevent="selectIcon(icon)"
                        >
                            <div class="icon-svg">
                                <DynamicIcon :name="`db:${icon.name || 'icon'}`" :databaseData="icon" :size="20" />
                            </div>
                            <span class="icon-name">{{ icon.name }}</span>
                        </div>
                    </div>
                    
                    <div v-if="loading" class="loading-state">
                        <div class="spinner-small"></div>
                    </div>
                    
                    <div v-if="!loading && filteredIcons.length === 0" class="empty-state">
                        No se encontraron resultados
                    </div>
                </div>
            </transition>
        </Teleport>
    </div>
</template>

<script setup>
import { ref, computed, watch, nextTick, onUnmounted } from 'vue';
import Icon from '@/components/Icon.vue';
import DynamicIcon from '@/components/DynamicIcon.vue';
import iconsApi from '@/services/api/endpoints/icons';

const props = defineProps({
    modelValue: String,
    selectedIconData: Object,
    category: {
        type: String,
        default: null
    }
});

const emit = defineEmits(['update:modelValue', 'change']);

const isOpen = ref(false);
const search = ref('');
const allIcons = ref([]);
const loading = ref(false);
const searchInput = ref(null);
const selectContainer = ref(null);
const localSelectedIcon = ref(props.selectedIconData);

const dropdownStyle = ref({
    position: 'fixed',
    top: '0px',
    left: '0px',
    width: '0px',
    zIndex: 9999
});

const updateDropdownPosition = () => {
    if (!isOpen.value || !selectContainer.value) return;
    
    const rect = selectContainer.value.getBoundingClientRect();
    const dropdownHeight = 350; // Max height estimate
    const windowHeight = window.innerHeight;
    
    let top = rect.bottom + 5;
    
    // Check if it fits below, otherwise show above
    if (top + dropdownHeight > windowHeight && rect.top > dropdownHeight) {
        top = rect.top - dropdownHeight - 5;
    }

    dropdownStyle.value = {
        position: 'fixed',
        top: `${top}px`,
        left: `${rect.left}px`,
        width: `${rect.width}px`,
        zIndex: 9999
    };
};

const fetchIcons = async () => {
    if (allIcons.value.length > 0) return;
    
    loading.value = true;
    try {
        const params = { per_page: -1 };
        if (props.category) {
            params.category = props.category;
        }
        
        const response = await iconsApi.getAll(params);
        allIcons.value = response.data.data || response.data || [];
    } catch (error) {
        console.error('Error fetching icons for selector:', error);
    } finally {
        loading.value = false;
    }
};

const filteredIcons = computed(() => {
    if (!search.value) return allIcons.value;
    const term = search.value.toLowerCase();
    return allIcons.value.filter(icon => 
        icon.name.toLowerCase().includes(term)
    );
});

const toggleDropdown = () => {
    isOpen.value = !isOpen.value;
    if (isOpen.value) {
        fetchIcons();
        nextTick(() => {
            updateDropdownPosition();
            searchInput.value?.focus();
        });
        
        window.addEventListener('scroll', updateDropdownPosition, true);
        window.addEventListener('resize', updateDropdownPosition);
    } else {
        removeListeners();
    }
};

const closeDropdown = () => {
    isOpen.value = false;
    removeListeners();
};

const removeListeners = () => {
    window.removeEventListener('scroll', updateDropdownPosition, true);
    window.removeEventListener('resize', updateDropdownPosition);
};

const selectIcon = (icon) => {
    if (icon) {
        emit('update:modelValue', icon.uuid);
        localSelectedIcon.value = icon;
        emit('change', icon);
    } else {
        clearSelection();
    }
    closeDropdown();
};

const clearSelection = () => {
    emit('update:modelValue', null);
    localSelectedIcon.value = null;
    emit('change', null);
};

watch(() => props.modelValue, (newVal) => {
    if (!newVal) {
        localSelectedIcon.value = null;
    }
});

watch(() => props.selectedIconData, (newVal) => {
    localSelectedIcon.value = newVal;
}, { immediate: true });

onUnmounted(() => {
    removeListeners();
});
</script>

<style lang="scss">
@use "../../sass/shared/variables" as *;
@use "../../sass/shared/mixins" as *;

.icon-select {
    position: relative;
    width: 100%;
    
    .selection-display {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 0.75rem;
        padding: 0.85rem 1.1rem;
        background: var(--bg-primary);
        border: 1px solid var(--border-color);
        border-radius: 0.85rem;
        cursor: pointer;
        transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
        width: 100%;
        box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.05);

        &:hover {
            border-color: var(--primary);
            background: var(--bg-secondary);
        }

        &.is-open {
            border-color: var(--primary);
            box-shadow: 0 0 0 4px rgba(var(--primary-rgb), 0.12),
                        inset 0 2px 4px rgba(0, 0, 0, 0.05);
            background: var(--bg-secondary);
        }

        .selected-icon, .placeholder {
            display: flex;
            align-items: center;
            gap: 0.75rem;
            flex: 1;
            font-size: 0.95rem;
            font-weight: 500;
            color: var(--text-primary);
            overflow: hidden;

            .icon-svg {
                width: 20px;
                height: 20px;
                display: flex;
                align-items: center;
                justify-content: center;
                flex-shrink: 0;
                color: var(--primary);
                
                svg {
                    width: 100%;
                    height: 100%;
                }
            }

            .icon-name {
                white-space: nowrap;
                overflow: hidden;
                text-overflow: ellipsis;
            }
        }

        .placeholder {
            color: var(--text-tertiary);
            font-weight: 400;
        }

        .controls {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            
            .arrow {
                color: var(--text-tertiary);
                transition: transform 0.2s ease;
            }

            .clear-btn {
                background: var(--bg-tertiary);
                border: none;
                border-radius: 6px;
                width: 24px;
                height: 24px;
                display: flex;
                align-items: center;
                justify-content: center;
                cursor: pointer;
                color: var(--text-secondary);
                transition: all 0.2s ease;
                
                &:hover {
                    background: #ef4444;
                    color: white;
                }
            }
        }
    }
}

/* Teleported Dropdown (Global Scope) */
.icon-dropdown.teleported-dropdown {
    position: fixed;
    background: var(--bg-primary);
    border: 1px solid var(--border-color);
    border-radius: 1rem;
    box-shadow: 0 20px 50px rgba(0, 0, 0, 0.5);
    z-index: 10000;
    padding: 0.65rem;
    max-height: 350px;
    display: flex;
    flex-direction: column;
    backdrop-filter: blur(12px);
    border: 1px solid rgba(255, 255, 255, 0.08);

    [data-theme='light'] & {
        background: #ffffff;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.15);
    }

    .search-container {
        position: sticky;
        top: 0;
        background: inherit;
        padding-bottom: 0.5rem;
        margin-bottom: 0.25rem;
        border-bottom: 1px solid var(--border-color);
        z-index: 2;

        .search-icon {
            position: absolute;
            left: 14px;
            top: 14px;
            color: var(--text-tertiary);
            pointer-events: none;
        }

        .search-input {
            width: 100%;
            padding: 0.65rem 1rem 0.65rem 2.4rem;
            background: var(--bg-secondary);
            border: 1px solid var(--border-color);
            border-radius: 0.65rem;
            color: var(--text-primary);
            font-size: 0.9rem;
            font-weight: 500;

            &:focus {
                outline: none;
                border-color: var(--primary);
                background: var(--bg-primary);
            }
        }
    }

    .icons-list {
        overflow-y: auto;
        flex: 1;
        padding: 0.25rem;

        &::-webkit-scrollbar {
            width: 5px;
        }
        &::-webkit-scrollbar-thumb {
            background: var(--border-color);
            border-radius: 10px;
        }

        .icon-item {
            display: flex;
            align-items: center;
            gap: 0.85rem;
            padding: 0.75rem 1rem;
            border-radius: 0.65rem;
            cursor: pointer;
            transition: all 0.15s ease;
            color: var(--text-secondary);
            font-size: 0.92rem;
            font-weight: 500;

            &:hover {
                background: var(--bg-tertiary);
                color: var(--text-primary);
                transform: translateX(4px);
            }

            &.active {
                background: rgba(var(--primary-rgb), 0.12);
                color: var(--primary);
                font-weight: 600;
            }

            .icon-svg {
                width: 20px;
                height: 20px;
                display: flex;
                align-items: center;
                justify-content: center;
                flex-shrink: 0;
                
                svg {
                    width: 100%;
                    height: 100%;
                }
            }

            .icon-name {
                white-space: nowrap;
                overflow: hidden;
                text-overflow: ellipsis;
            }
        }
    }

    .loading-state, .empty-state {
        padding: 2.5rem 1rem;
        text-align: center;
        color: var(--text-tertiary);
        font-size: 0.9rem;
    }
}

.dropdown-fade-enter-active, .dropdown-fade-leave-active {
    transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
}
.dropdown-fade-enter-from, .dropdown-fade-leave-to {
    opacity: 0;
    transform: translateY(-8px) scale(0.98);
}
</style>
