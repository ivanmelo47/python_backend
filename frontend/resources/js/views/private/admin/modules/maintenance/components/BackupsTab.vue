<template>
    <div class="maintenance-backup-tab">
        <section class="maintenance-card">
            <div class="card-heading">
                <div>
                    <span class="section-kicker">Respaldo</span>
                    <h2>Copia de seguridad</h2>
                </div>
            </div>

            <p class="backup-description">
                Genera un ZIP con la base de datos y los archivos persistentes de storage/public y storage/private/files. Cuando termine, se enviará un correo con enlace temporal de descarga de 1 día.
            </p>

            <div class="backup-status-block">
                <div class="backup-status-line">
                    <span class="backup-status-label">Estado actual</span>
                    <span v-if="latestBackup" class="status-chip" :class="`status-chip-${latestBackup.status}`">
                        {{ latestBackup.status }}
                    </span>
                    <span v-else class="status-chip status-chip-muted">Sin historial</span>
                </div>
                <p v-if="latestBackup" class="backup-meta">
                    <span>Creado: {{ formatDateTime(latestBackup.created_at) }}</span>
                    <span>Completado: {{ formatDateTime(latestBackup.completed_at) }}</span>
                    <span>Expira: {{ formatDateTime(latestBackup.expires_at) }}</span>
                </p>
                <p v-else class="backup-meta">Aún no hay respaldos generados.</p>
            </div>

            <div class="flex justify-end gap-3">
                <button
                    v-if="latestBackup && (latestBackup.status === 'queued' || latestBackup.status === 'processing')"
                    @click="$emit('cancel-backup')"
                    class="maintenance-action-btn maintenance-action-btn-danger"
                    :disabled="isLoading || isBackupLoading || backupStatusLoading"
                >
                    <Icon name="x-circle" :size="16" />
                    Cancelar proceso atascado
                </button>
                
                <button
                    @click="$emit('generate-backup')"
                    class="maintenance-action-btn maintenance-action-btn-primary"
                    :disabled="isLoading || isBackupLoading || backupStatusLoading"
                >
                    <Icon v-if="isBackupLoading" name="refresh" :size="16" class="spinning" />
                    {{ isBackupLoading ? 'Encolando respaldo...' : 'Generar respaldo en segundo plano' }}
                </button>
            </div>
        </section>

        <div class="history-card mt-6" v-if="backupHistory.length">
            <div class="history-header">
                <h3>Historial de respaldos</h3>
                <span>Últimos 10</span>
            </div>

            <div class="overflow-x-auto">
                <table class="history-table">
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Estado</th>
                            <th>Creado</th>
                            <th>Completado</th>
                            <th>Expira</th>
                            <th>Archivo</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr
                            v-for="item in backupHistory"
                            :key="item.id"
                        >
                            <td>#{{ item.id }}</td>
                            <td>
                                <span class="status-chip" :class="`status-chip-${item.status}`">
                                    {{ item.status }}
                                </span>
                            </td>
                            <td>{{ formatDateTime(item.created_at) }}</td>
                            <td>{{ formatDateTime(item.completed_at) }}</td>
                            <td>{{ formatDateTime(item.expires_at) }}</td>
                            <td class="truncate max-w-[220px]">{{ item.file_name || '-' }}</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>

        <p v-else class="history-empty mt-6">
            No existe historial de respaldos todavía.
        </p>
    </div>
</template>

<script setup>
import Icon from '@/components/Icon.vue';

defineProps({
    latestBackup: Object,
    backupHistory: Array,
    isLoading: Boolean,
    isBackupLoading: Boolean,
    backupStatusLoading: Boolean
});

defineEmits(['generate-backup', 'cancel-backup']);

const formatDateTime = (value) => {
    if (!value) return '-';
    const date = new Date(value);
    if (Number.isNaN(date.getTime())) return value;
    return date.toLocaleString('es-ES');
};
</script>
