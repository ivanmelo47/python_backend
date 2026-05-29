<template>
    <div class="folder-tree-selector">
        <ul class="tree-list">
            <li v-for="node in tree" :key="node.uuid" class="tree-item">
                <div class="item-content" :style="{ paddingLeft: depth * 1.5 + 'rem' }">
                    <label class="custom-checkbox">
                        <input 
                            type="checkbox" 
                            :checked="selectedUuids.includes(node.uuid)"
                            @change="toggleNode(node.uuid, $event.target.checked)"
                        >
                        <span class="checkmark"></span>
                    </label>
                    
                    <div class="folder-info">
                        <Icon name="folder" :size="18" class="folder-icon" />
                        <span class="folder-name">{{ node.name }}</span>
                        <span class="current-status" :class="{ 'is-public': node.is_public }">
                            ({{ node.is_public ? 'Pública' : 'Privada' }})
                        </span>
                    </div>
                </div>
                
                <!-- Recursive Children -->
                <transition name="fade">
                    <FolderTreeSelector 
                        v-if="node.children && node.children.length > 0"
                        :tree="node.children"
                        :selected-uuids="selectedUuids"
                        :depth="depth + 1"
                        @update:selected-uuids="$emit('update:selected-uuids', $event)"
                    />
                </transition>
            </li>
        </ul>
    </div>
</template>

<script setup>
import Icon from '@/components/Icon.vue';

const props = defineProps({
    tree: {
        type: Array,
        required: true
    },
    selectedUuids: {
        type: Array,
        default: () => []
    },
    depth: {
        type: Number,
        default: 0
    }
});

const emit = defineEmits(['update:selected-uuids']);

const toggleNode = (uuid, isChecked) => {
    let newSelected = [...props.selectedUuids];
    
    if (isChecked) {
        if (!newSelected.includes(uuid)) {
            newSelected.push(uuid);
        }
    } else {
        newSelected = newSelected.filter(id => id !== uuid);
    }
    
    emit('update:selected-uuids', newSelected);
};
</script>

<style lang="scss" scoped>
.folder-tree-selector {
    .tree-list {
        list-style: none;
        padding: 0;
        margin: 0;
    }

    .tree-item {
        border-bottom: 1px solid var(--border-color);
        
        &:last-child {
            border-bottom: none;
        }

        .item-content {
            display: flex;
            align-items: center;
            gap: 1rem;
            padding: 0.75rem 1rem;
            transition: background 0.2s ease;

            &:hover {
                background: rgba(var(--primary-rgb), 0.03);
            }
        }

        .custom-checkbox {
            position: relative;
            cursor: pointer;
            height: 20px;
            width: 20px;
            
            input {
                position: absolute;
                opacity: 0;
                cursor: pointer;
                height: 0;
                width: 0;
            }

            .checkmark {
                position: absolute;
                top: 0;
                left: 0;
                height: 20px;
                width: 20px;
                background-color: var(--bg-tertiary);
                border: 1px solid var(--border-color);
                border-radius: 5px;
                transition: all 0.2s ease;

                &:after {
                    content: "";
                    position: absolute;
                    display: none;
                    left: 6px;
                    top: 2px;
                    width: 5px;
                    height: 10px;
                    border: solid white;
                    border-width: 0 2px 2px 0;
                    transform: rotate(45deg);
                }
            }

            input:checked ~ .checkmark {
                background-color: var(--primary);
                border-color: var(--primary);
                &:after {
                    display: block;
                }
            }
        }

        .folder-info {
            display: flex;
            align-items: center;
            gap: 0.75rem;
            flex: 1;

            .folder-icon {
                color: var(--primary);
            }

            .folder-name {
                font-size: 0.9rem;
                font-weight: 500;
                color: var(--text-primary);
            }

            .current-status {
                font-size: 0.75rem;
                color: var(--text-tertiary);
                
                &.is-public {
                    color: var(--primary);
                }
            }
        }
    }
}

.fade-enter-active, .fade-leave-active {
    transition: opacity 0.3s ease;
}
.fade-enter-from, .fade-leave-to {
    opacity: 0;
}
</style>
