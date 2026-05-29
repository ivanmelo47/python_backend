<template>
    <div class="excel-preview-wrapper">
        <div v-if="loading" class="excel-state">Procesando hoja de cálculo...</div>
        <div v-else-if="error" class="excel-state error">{{ error }}</div>
        <template v-else>
            <div class="excel-sheet-tabs">
                <button
                    v-for="sheet in sheetNames"
                    :key="sheet"
                    type="button"
                    class="sheet-tab"
                    :class="{ active: selectedSheetName === sheet }"
                    @click="selectSheet(sheet)"
                >
                    {{ sheet }}
                </button>
            </div>

            <div class="excel-grid-container">
                <table class="excel-grid">
                    <thead>
                        <tr>
                            <th class="corner-cell"></th>
                            <th v-for="col in columnHeaders" :key="col" class="col-header">
                                {{ col }}
                            </th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="(row, rowIndex) in rows" :key="`row-${rowIndex}`">
                            <th class="row-header">{{ rowIndex + 1 }}</th>
                            <td v-for="(cell, cellIndex) in row" :key="`cell-${rowIndex}-${cellIndex}`">
                                {{ cell }}
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </template>
    </div>
</template>

<script setup>
import { ref, watch } from 'vue';
import * as XLSX from 'xlsx';

const props = defineProps({
    fileUrl: {
        type: String,
        default: '',
    },
});

const loading = ref(false);
const error = ref('');
const sheetNames = ref([]);
const selectedSheetName = ref('');
const rows = ref([]);
const columnHeaders = ref([]);
const workbookRef = ref(null);

const MAX_PREVIEW_ROWS = 120;
const MAX_PREVIEW_COLS = 40;

const toColumnLabel = (index) => {
    let value = index + 1;
    let label = '';
    while (value > 0) {
        const mod = (value - 1) % 26;
        label = String.fromCharCode(65 + mod) + label;
        value = Math.floor((value - mod) / 26);
    }
    return label;
};

const renderSheet = (sheetName) => {
    if (!workbookRef.value || !sheetName) return;

    const worksheet = workbookRef.value.Sheets[sheetName];
    if (!worksheet) {
        rows.value = [];
        columnHeaders.value = [];
        return;
    }

    const range = worksheet['!ref'] ? XLSX.utils.decode_range(worksheet['!ref']) : XLSX.utils.decode_range('A1:A1');
    const endRow = Math.min(range.e.r, MAX_PREVIEW_ROWS - 1);
    const endCol = Math.min(range.e.c, MAX_PREVIEW_COLS - 1);

    const nextRows = [];
    for (let rowIndex = 0; rowIndex <= endRow; rowIndex++) {
        const row = [];
        for (let colIndex = 0; colIndex <= endCol; colIndex++) {
            const addr = XLSX.utils.encode_cell({ r: rowIndex, c: colIndex });
            const cell = worksheet[addr];
            row.push(cell ? String(cell.w ?? cell.v ?? '') : '');
        }
        nextRows.push(row);
    }

    rows.value = nextRows;
    columnHeaders.value = Array.from({ length: endCol + 1 }, (_, i) => toColumnLabel(i));
};

const selectSheet = (sheetName) => {
    selectedSheetName.value = sheetName;
    renderSheet(sheetName);
};

const parseExcel = async () => {
    if (!props.fileUrl) return;

    loading.value = true;
    error.value = '';
    workbookRef.value = null;
    rows.value = [];
    columnHeaders.value = [];
    sheetNames.value = [];
    selectedSheetName.value = '';

    try {
        const response = await fetch(props.fileUrl);
        if (!response.ok) {
            throw new Error('No se pudo leer el archivo Excel para la vista previa.');
        }

        const arrayBuffer = await response.arrayBuffer();
        const workbook = XLSX.read(arrayBuffer, { type: 'array', cellText: true, cellDates: true });

        workbookRef.value = workbook;
        sheetNames.value = workbook.SheetNames || [];

        if (!sheetNames.value.length) {
            throw new Error('El documento no contiene hojas visibles.');
        }

        selectedSheetName.value = sheetNames.value[0];
        renderSheet(selectedSheetName.value);
    } catch (err) {
        error.value = err?.message || 'No se pudo procesar el archivo Excel.';
    } finally {
        loading.value = false;
    }
};

watch(
    () => props.fileUrl,
    () => {
        parseExcel();
    },
    { immediate: true }
);
</script>

<style scoped lang="scss">
.excel-preview-wrapper {
    width: 100%;
    height: 100%;
    display: flex;
    flex-direction: column;
    gap: 0.6rem;
}

.excel-state {
    width: 100%;
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    color: var(--text-secondary);
}

.excel-state.error {
    color: var(--danger, #ff7070);
}

.excel-sheet-tabs {
    display: flex;
    gap: 0.45rem;
    overflow-x: auto;
    padding-bottom: 0.25rem;
}

.sheet-tab {
    height: 32px;
    border-radius: 8px;
    border: 1px solid var(--border-color);
    background: var(--bg-tertiary);
    color: var(--text-primary);
    padding: 0 0.75rem;
    font-size: 0.82rem;
    white-space: nowrap;
    cursor: pointer;
}

.sheet-tab.active {
    border-color: var(--primary);
    color: var(--primary);
}

.excel-grid-container {
    border: 1px solid var(--border-color);
    border-radius: 10px;
    background: var(--bg-primary);
    overflow: auto;
    height: 100%;
}

.excel-grid {
    width: max-content;
    min-width: 100%;
    border-collapse: collapse;
    table-layout: fixed;
}

.excel-grid th,
.excel-grid td {
    border: 1px solid var(--border-color);
    min-width: 120px;
    max-width: 240px;
    padding: 0.35rem 0.5rem;
    font-size: 0.78rem;
    color: var(--text-primary);
    background: transparent;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.excel-grid .col-header,
.excel-grid .row-header,
.excel-grid .corner-cell {
    background: var(--bg-tertiary);
    color: var(--text-secondary);
    font-weight: 600;
    text-align: center;
}

.excel-grid .corner-cell {
    min-width: 44px;
}

.excel-grid .row-header {
    min-width: 44px;
    max-width: 44px;
}
</style>
