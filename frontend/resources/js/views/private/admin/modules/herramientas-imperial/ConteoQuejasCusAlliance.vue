<template>
    <div class="cus-alliance-container">
        <Table title="Conteo de Quejas Cus Alliance" :columns="columns" :rows="reports" :loading="loading"
            :pagination="pagination" :searchQuery="searchQuery" @update:searchQuery="searchQuery = $event"
            searchPlaceholder="Buscar reporte por nombre o periodo..." paginationMode="server"
            @request-data="fetchReports" @row-click="viewReport">

            <!-- Header Actions -->
            <template #header-actions>
                <button class="btn-solid" @click="openCreateModal">
                    <Icon name="plus" :size="18" />
                    <span>Nuevo Reporte</span>
                </button>
            </template>

            <!-- Custom Cell: Date -->
            <template #cell-mes_año="{ row }">
                <span class="period-badge">
                    <Icon name="calendar" :size="14" />
                    {{ formatPeriod(row.mes_año) }}
                </span>
            </template>

            <!-- Custom Cell: Total Complaints -->
            <template #cell-total="{ row }">
                <span class="count-badge">
                    {{ getTotalComplaints(row.contenido_json) }}
                </span>
            </template>

            <!-- Actions Dropdown -->
            <template #cell-actions="{ row }">
                <button @click.stop="viewReport(row)" class="dropdown-item">
                    <Icon name="eye" :size="16" />
                    <span>Ver Detalles</span>
                </button>
                <button @click.stop="exportToExcel(row)" class="dropdown-item">
                    <Icon name="download" :size="16" />
                    <span>Descargar Excel</span>
                </button>
                <button @click.stop="editReport(row)" class="dropdown-item">
                    <Icon name="edit" :size="16" />
                    <span>Editar</span>
                </button>
                <button @click.stop="confirmDelete(row)" class="dropdown-item delete">
                    <Icon name="trash" :size="16" />
                    <span>Eliminar</span>
                </button>
            </template>
        </Table>

        <!-- Modal Form for Create/Edit -->
        <ModalForm :isVisible="showFormModal" :title="editingReport ? 'Editar Reporte' : 'Nuevo Reporte'"
            :loading="formLoading" submitLabel="Guardar Reporte" size="xl" :columns="2" @close="closeFormModal"
            @submit="submitForm">

            <template #header-icon>
                <Icon name="file-text" :size="18" />
            </template>

            <!-- Name -->
            <ModalField label="Nombre del Reporte" :required="true" :span="1" :error="errors.nombre?.[0]">
                <input v-model="formData.nombre" type="text" placeholder="Ej: Reporte Mensual Casitas" />
            </ModalField>

            <!-- Period (Month/Year) -->
            <ModalField label="Periodo (Mes/Año)" :required="true" :span="1" :error="errors.mes_año?.[0]">
                <input v-model="formData.mes_año" type="month" />
            </ModalField>

            <!-- File Upload (Only for New or if re-uploading) -->
            <ModalField label="Archivo Excel (.xlsx)" :span="2" :required="!editingReport && !processedData"
                :error="errors.file?.[0]">
                <div class="file-upload-wrapper" :class="{ 'has-file': selectedFileName }">
                    <input ref="fileInput" type="file" accept=".xlsx" @change="handleFileUpload" id="excel-file-input"
                        class="file-input-hidden" />
                    <label for="excel-file-input" class="file-upload-label">
                        <div class="file-upload-content">
                            <Icon :name="selectedFileName ? 'check-circle' : 'upload'" :size="32"
                                :class="{ 'success-icon': selectedFileName }" />
                            <span class="file-upload-text">
                                {{ selectedFileName || 'Selecciona el archivo Excel de Customer Alliance' }}
                            </span>
                            <span class="file-upload-hint">Debe contener la columna "Criterios"</span>
                        </div>
                    </label>
                    <button v-if="selectedFileName" type="button" class="btn-text btn-sm mt-1" @click.stop="resetFile">
                        Cambiar archivo
                    </button>
                </div>
            </ModalField>

            <!-- Preview Section -->
            <ModalField v-if="processedData" label="Vista Previa de Datos Extraídos" :span="2">
                <div class="preview-container">
                    <div class="preview-stats">
                        <span class="badge info">{{ processedData.length }} filas detectadas</span>
                        <span class="badge success">Total: {{ getTotalComplaints(processedData) }}</span>
                    </div>
                    <div class="preview-table-wrapper">
                        <table class="preview-table">
                            <thead>
                                <tr>
                                    <th>Área</th>
                                    <th>Criterio</th>
                                    <th>Cantidad</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr v-for="(item, idx) in processedData.filter(i => !i.area.toUpperCase().includes('TOTAL GENERAL')).slice(0, 10)"
                                    :key="idx" :style="getAreaStyle(item.area, isDarkMode)">
                                    <td class="font-bold">{{ item.area }}</td>
                                    <td>{{ item.criteria }}</td>
                                    <td class="text-right font-bold">{{ item.count }}</td>
                                </tr>
                                <tr v-if="processedData.length > 10">
                                    <td colspan="3" class="text-center text-muted">
                                        ... y {{ processedData.length - 10 }} filas más ...
                                    </td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            </ModalField>
        </ModalForm>
 
        <!-- Modal Information for View -->
        <ModalInformation 
            v-if="selectedReport"
            :is-open="showInfoModal" 
            :title="selectedReport.nombre || 'Detalles del Reporte'"
            icon="file-text" 
            size="xl" 
            :data="selectedReport"
            :columns="[
                { key: 'nombre', label: 'Nombre Reporte' },
                { key: 'mes_año', label: 'Periodo' },
                { key: 'total', label: 'Total de Quejas' }
            ]"
            show-edit-button
            @edit="showInfoModal = false; handleEdit(selectedReport)"
            @close="closeInfoModal"
        >
            <template #top-header>
                <div class="report-summary-hero">
                    <div class="report-hero-icon">
                        <Icon name="file-text" :size="24" />
                    </div>
                    <div class="report-hero-text">
                        <h4>{{ selectedReport.nombre }}</h4>
                        <span class="badge info">{{ formatPeriod(selectedReport.mes_año) }}</span>
                    </div>
                </div>
            </template>
            <template #value-mes_año>
                {{ formatPeriod(selectedReport.mes_año) }}
            </template>

            <template #value-total>
                <span class="count-badge font-bold">{{ getTotalComplaints(selectedReport.contenido_json) }}</span>
            </template>

            <!-- Table breakdown in the default slot -->
            <div class="data-section mt-4">
                <label class="row-label mb-3 d-block">Desglose Detallado de Datos</label>
                <div class="details-table-wrapper">
                    <table class="details-table">
                        <thead>
                            <tr>
                                <th>Área</th>
                                 <th>Criterio</th>
                                 <th class="text-right">Cantidad</th>
                             </tr>
                         </thead>
                         <tbody>
                             <tr v-for="(item, idx) in selectedReport.contenido_json.filter(i => !i.area.toUpperCase().includes('TOTAL GENERAL'))"
                                 :key="idx" :style="getAreaStyle(item.area, isDarkMode)">
                                 <td class="font-bold">{{ item.area }}</td>
                                 <td>{{ item.criteria }}</td>
                                 <td class="text-right font-bold">{{ item.count }}</td>
                             </tr>
                         </tbody>
                     </table>
                 </div>
             </div>
            <div class="actions-section mt-6 flex justify-end gap-3 px-4 pb-2">
                <button class="btn-solid" @click="exportToExcel(selectedReport)">
                    <Icon name="download" :size="16" />
                    <span>Descargar Reporte Excel</span>
                </button>
            </div>
        </ModalInformation>
    </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { useAlert } from '@/composables/useAlert';
import Table from '@/views/private/admin/components/Table.vue';
import ModalForm from '@/views/private/admin/components/ModalForm.vue';
import ModalField from '@/views/private/admin/components/ModalField.vue';
import ModalInformation from '@/views/private/admin/components/ModalInformation.vue';
import Icon from '@/components/Icon.vue';
import { useTheme } from '@/composables/useTheme';
import complaintsApi from '@/services/api/endpoints/cus-alliance-complaints';
import { processExcelFile, downloadExcel, getAreaStyle } from '@/utils/cusAllianceExcelProcessor';

// Auth & Alerts
const alert = useAlert();
const { theme } = useTheme();
const isDarkMode = computed(() => theme.value === 'dark');

// Table Data
const reports = ref([]);
const loading = ref(false);
const pagination = ref(null);
const searchQuery = ref('');

const columns = [
    { key: 'actions', label: 'ACCIONES', headerClass: 'compact', cellClass: 'compact' },
    { key: 'nombre', label: 'Nombre del Reporte' },
    { key: 'mes_año', label: 'Periodo', cellClass: 'text-center' },
    { key: 'total', label: 'Total Quejas', cellClass: 'text-right' },
    { key: 'created_at', label: 'Fecha de Creación', format: 'date' }
];

// Form Modal
const showFormModal = ref(false);
const formLoading = ref(false);
const editingReport = ref(null);
const formData = ref({
    nombre: '',
    mes_año: '',
    contenido_json: null
});
const errors = ref({});
const selectedFileName = ref('');
const fileInput = ref(null);
const processedData = ref(null);

// Info Modal
const showInfoModal = ref(false);
const selectedReport = ref(null);

/**
 * Fetch Reports from API
 */
const fetchReports = async (params = {}) => {
    loading.value = true;
    try {
        const response = await complaintsApi.getAll(params);
        if (response.data.success) {
            reports.value = response.data.data.data;
            pagination.value = {
                current_page: response.data.data.current_page,
                last_page: response.data.data.last_page,
                from: response.data.data.from,
                to: response.data.data.to,
                total: response.data.data.total
            };
        }
    } catch (error) {
        alert.toast.error('Error', 'No se pudieron cargar los reportes');
        console.error(error);
    } finally {
        loading.value = false;
    }
};

/**
 * Handle File Upload and Processing
 */
const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    selectedFileName.value = file.name;
    formLoading.value = true;

    try {
        const result = await processExcelFile(file);
        processedData.value = result.data;
        formData.value.contenido_json = result.data;

        // Suggest name if empty
        if (!formData.value.nombre) {
            formData.value.nombre = file.name.replace('.xlsx', '');
        }

        alert.toast.success('Excel Procesado', `${result.data.length} criterios encontrados`);
    } catch (error) {
        alert.toast.error('Error', 'No se pudo procesar el archivo Excel. Verifica el formato.');
        console.error(error);
        resetFile();
    } finally {
        formLoading.value = false;
    }
};

const resetFile = () => {
    selectedFileName.value = '';
    processedData.value = null;
    formData.value.contenido_json = null;
    if (fileInput.value) fileInput.value.value = '';
};

/**
 * Open Create Modal
 */
const openCreateModal = () => {
    editingReport.value = null;
    resetForm();
    showFormModal.value = true;
};

/**
 * Edit existing report
 */
const editReport = (report) => {
    editingReport.value = report;
    formData.value = {
        nombre: report.nombre,
        mes_año: report.mes_año,
        contenido_json: [...report.contenido_json]
    };
    processedData.value = report.contenido_json;
    selectedFileName.value = 'Datos ya cargados (Sube uno nuevo para reemplazar)';
    errors.value = {};
    showFormModal.value = true;
};

/**
 * Reset Form State
 */
const resetForm = () => {
    formData.value = {
        nombre: '',
        mes_año: '',
        contenido_json: null
    };
    errors.value = {};
    processedData.value = null;
    selectedFileName.value = '';
    if (fileInput.value) fileInput.value.value = '';
};

/**
 * Close Form Modal
 */
const closeFormModal = () => {
    showFormModal.value = false;
    resetForm();
};

/**
 * Submit Create/Edit Form
 */
const submitForm = async () => {
    if (!formData.value.contenido_json) {
        alert.toast.warning('Archivo requerido', 'Por favor sube un archivo Excel válido');
        return;
    }

    formLoading.value = true;
    errors.value = {};

    try {
        if (editingReport.value) {
            await complaintsApi.update(editingReport.value.uuid, formData.value);
            alert.toast.success('Éxito', 'Reporte actualizado correctamente');
        } else {
            await complaintsApi.create(formData.value);
            alert.toast.success('Éxito', 'Reporte guardado correctamente');
        }
        closeFormModal();
        fetchReports({ page: pagination.value?.current_page || 1 });
    } catch (error) {
        if (error.response?.data?.errors) {
            errors.value = error.response.data.errors;
        }
        alert.toast.error('Error', error.response?.data?.message || 'Error al guardar el reporte');
    } finally {
        formLoading.value = false;
    }
};

/**
 * View Report Details
 */
const viewReport = (report) => {
    selectedReport.value = report;
    showInfoModal.value = true;
};

const closeInfoModal = () => {
    showInfoModal.value = false;
    selectedReport.value = null;
};

/**
 * Confirm and Delete
 */
const confirmDelete = async (report) => {
    const confirmed = await alert.fire({
        title: '¿Eliminar reporte?',
        text: `Esta acción no se puede deshacer. Se eliminará "${report.nombre}".`,
        type: 'warning',
        showCancel: true,
        confirmText: 'Sí, eliminar',
        cancelText: 'Cancelar'
    });

    if (confirmed) {
        try {
            await complaintsApi.delete(report.uuid);
            alert.toast.success('Eliminado', 'El reporte ha sido eliminado');
            fetchReports({ page: pagination.value?.current_page || 1 });
        } catch (error) {
            alert.toast.error('Error', 'No se pudo eliminar el reporte');
        }
    }
};

/**
 * Export to Excel (Using processor)
 */
const exportToExcel = async (report) => {
    try {
        const filename = `${report.nombre}_${report.mes_año}.xlsx`;
        await downloadExcel(report.contenido_json, filename);
        alert.toast.success('Descargado', 'El archivo Excel se ha generado correctamente');
    } catch (error) {
        alert.toast.error('Error', 'No se pudo generar el archivo Excel');
    }
};

/**
 * Helpers
 */
const formatPeriod = (period) => {
    if (!period) return '';
    const [year, month] = period.split('-');
    const months = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'];
    return `${months[parseInt(month) - 1]} ${year}`;
};

const getTotalComplaints = (data) => {
    if (!data || !Array.isArray(data)) return 0;
    return data.reduce((sum, item) => sum + (item.count || 0), 0);
};
</script>

<style lang="scss" scoped>
.cus-alliance-container {
    padding: 1rem;
}

.period-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.25rem 0.75rem;
    background: rgba(var(--primary-rgb), 0.1);
    color: var(--primary);
    border-radius: 20px;
    font-size: 0.85rem;
    font-weight: 500;
}

.count-badge {
    display: inline-block;
    padding: 0.25rem 0.6rem;
    background: #f3f4f6;
    color: #374151;
    border-radius: 6px;
    font-weight: 700;
    min-width: 40px;
    text-align: center;

    &.large {
        font-size: 1.25rem;
        padding: 0.5rem 1rem;
        background: var(--primary);
        color: white;
    }
}

.file-upload-wrapper {
    position: relative;
    border: 2px dashed #d1d5db;
    border-radius: 12px;
    padding: 2rem;
    text-align: center;
    transition: all 0.3s ease;
    background: #f9fafb;

    &:hover {
        border-color: var(--primary);
        background: #f3f4f6;
    }

    &.has-file {
        border-color: #10b981;
        background: #ecfdf5;
    }

    .file-input-hidden {
        position: absolute;
        inset: 0;
        opacity: 0;
        cursor: pointer;
    }

    .file-upload-content {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 0.75rem;

        .success-icon {
            color: #10b981;
        }

        .file-upload-text {
            font-weight: 500;
            color: #4b5563;
        }

        .file-upload-hint {
            font-size: 0.8rem;
            color: #9ca3af;
        }
    }
}

.preview-container {
    background: var(--bg-secondary, #f3f4f6);
    border-radius: 8px;
    padding: 1rem;

    .preview-stats {
        display: flex;
        gap: 0.5rem;
        margin-bottom: 1rem;
    }

    .preview-table-wrapper {
        max-height: 250px;
        overflow-y: auto;
        border: 1px solid var(--border-color, #e5e7eb);
        border-radius: 4px;
        background: var(--bg-primary, white);
    }

    .preview-table {
        width: 100%;
        border-collapse: separate;
        border-spacing: 0;
        font-size: 0.85rem;
        transition: all 0.3s ease;

        th {
            position: sticky;
            top: 0;
            background: var(--bg-secondary, #f9fafb);
            text-align: left;
            padding: 0.75rem;
            border-bottom: 2px solid var(--border-color, #e5e7eb);
            z-index: 10;
        }

        td {
            padding: 0.75rem;
            border-bottom: 1px solid var(--border-color, #f3f4f6);
        }

        tr {
            transition: background-color 0.2s ease;
        }
    }
}

.report-summary-hero {
    display: flex;
    align-items: center;
    gap: 1rem;
    padding: 1.25rem;
    background: var(--bg-tertiary);
    border-radius: 12px;
    border: 1px solid var(--border-color);
    margin-bottom: 0.5rem;

    .report-hero-icon {
        width: 48px;
        height: 48px;
        background: var(--bg-secondary);
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: var(--primary);
        border: 1px solid var(--border-color);
    }

    .report-hero-text {
        flex: 1;
        h4 {
            margin: 0 0 0.25rem;
            font-size: 1.15rem;
            color: var(--text-primary);
        }
    }
}

.report-details {
    .details-table-wrapper {
        max-height: 450px;
        overflow-y: auto;
        border: 1px solid var(--border-color);
        border-radius: 12px;
        background: var(--bg-primary);
    }

    .details-table {
        width: 100%;
        border-collapse: separate;
        border-spacing: 0;

        th {
            position: sticky;
            top: 0;
            background: var(--bg-secondary);
            text-align: left;
            padding: 1rem;
            border-bottom: 2px solid var(--border-color);
            font-weight: 700;
            z-index: 10;
            font-size: 0.75rem;
            text-transform: uppercase;
        }

        td {
            padding: 0.85rem 1rem;
            border-bottom: 1px solid var(--border-color);
            font-size: 0.9rem;
        }

        tr:last-child td {
            border-bottom: none;
        }
    }
}
</style>
