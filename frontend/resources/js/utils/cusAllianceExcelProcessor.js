/**
 * Color definitions (ARGB)
 */
const COLORS = {
    HABITACIONES: "FF9CC2E5", // Light Blue
    GENERALES: "FFA5A5A5", // Grey
    ALBERCAS: "FFC65911", // Orange
    RESTAURANTES: "FF548235", // Green
    DEFAULT: "FFFFFFFF", // White
};

/**
 * Areas that should be colored as RESTAURANTES (Green)
 */
const RESTAURANT_AREAS = [
    "RESTAURANTES",
    "TAVOLA",
    "CAFE DEL ANGOLO",
    "IN ROOM DINING",
    "CHULA VISTA",
    "PRINCIPE MIXTECO",
    "COCO LOCO",
    "MATCHA",
    "AZUL, MAR & TIERRA",
    "THE BEACH CLUB",
    "LEUDO",
    "SUSHI MAHÓ",
    "SUSHI MAHO",
    "VALET PARKING",
    "PLAYA",
    "MESTIZO",
];

/**
 * Convert ARGB to CSS Hex (RRGGBB)
 */
function argbToHex(argb) {
    if (!argb || argb.length < 8) return "#ffffff";
    return `#${argb.substring(2)}`;
}

/**
 * Get background color for a given area name
 */
export function getAreaColor(areaName) {
    if (!areaName) return COLORS.DEFAULT;
    const upper = areaName.toString().toUpperCase().trim();

    if (upper.includes("HABITACIONES")) return COLORS.HABITACIONES;
    if (upper.includes("GENERALES")) return COLORS.GENERALES;
    if (upper.includes("ALBERCA")) return COLORS.ALBERCAS;

    if (RESTAURANT_AREAS.some((r) => upper.includes(r))) {
        return COLORS.RESTAURANTES;
    }

    return COLORS.DEFAULT;
}

/**
 * Get CSS style object for a given area
 */
export function getAreaStyle(areaName, isDarkMode = false) {
    const argb = getAreaColor(areaName);

    // If it's the default white, we return an empty object so it uses theme colors
    if (argb === COLORS.DEFAULT) {
        return {};
    }

    const hex = argbToHex(argb);

    // Determine contrast
    let textColor = '#ffffff';
    if (argb === COLORS.HABITACIONES) textColor = '#1e293b'; // Dark blue for light blue bg

    return {
        backgroundColor: hex,
        color: textColor,
        fontWeight: '500'
    };
}

/**
 * Process an Excel File (File object) and return the data structure
 */
export async function processExcelFile(file, sheetName = null) {
    const ExcelJS = (await import('exceljs')).default || (await import('exceljs'));
    const workbook = new ExcelJS.Workbook();
    const arrayBuffer = await file.arrayBuffer();
    await workbook.xlsx.load(arrayBuffer);

    // If no sheetName provided, we could take the first one or ask (the UI will handle selection)
    const sheet = sheetName ? workbook.getWorksheet(sheetName) : workbook.worksheets[0];

    if (!sheet) throw new Error('No se encontró la hoja especificada');

    const complaints = [];
    let currentArea = null;
    let headerFound = false;
    let startRow = 1;

    // Find header row
    sheet.eachRow((row, rowNumber) => {
        if (headerFound) return;
        const cellB = row.getCell(2).value;
        if (cellB && cellB.toString().trim() === "Criterios") {
            headerFound = true;
            startRow = rowNumber + 1;
        }
    });

    if (!headerFound) {
        startRow = 1;
    }

    const rowCount = sheet.rowCount;

    for (let i = startRow; i <= rowCount; i++) {
        const row = sheet.getRow(i);

        // Handle Area (Column A)
        let cellA = row.getCell(1);
        let areaValue = cellA.value;

        if (cellA.isMerged && cellA.master !== cellA) {
            // Merged cell, use currentArea (implicitly)
        } else if (areaValue) {
            if (typeof areaValue === "object" && areaValue.richText) {
                currentArea = areaValue.richText.map((t) => t.text).join("");
            } else {
                currentArea = areaValue.toString();
            }
        }

        if (!currentArea && !areaValue && !row.getCell(2).value) {
            continue;
        }

        // Get Criteria (Column B)
        let cellB = row.getCell(2);
        let criteriaValue = cellB.value;
        if (!criteriaValue) continue;

        let criteria = "";
        if (typeof criteriaValue === "object" && criteriaValue.richText) {
            criteria = criteriaValue.richText.map((t) => t.text).join("");
        } else {
            criteria = criteriaValue.toString();
        }

        if (criteria.trim().toLowerCase() === "criterios") continue;

        // Calculate Count (Sum C onwards)
        let count = 0;
        row.eachCell((cell, colNum) => {
            if (colNum > 2) {
                const val = cell.value;
                if (typeof val === "number") {
                    count += val;
                } else if (val && !isNaN(parseInt(val))) {
                    count += parseInt(val);
                }
            }
        });

        if (count === 0) continue;

        const areaStr = (currentArea || "").toString();
        const criteriaStr = (criteria || "").toString();

        // Skip summary rows
        if (areaStr.toUpperCase().includes("TOTAL GENERAL") || criteriaStr.toUpperCase().includes("TOTAL GENERAL")) {
            continue;
        }

        complaints.push({
            area: areaStr || "Sin Area",
            criteria: criteriaStr,
            count: count,
        });
    }

    complaints.sort((a, b) => b.count - a.count);

    return {
        sheetName: sheet.name,
        data: complaints,
        availableSheets: workbook.worksheets.map(ws => ws.name)
    };
}

/**
 * Generate and download an Excel file from the complaint data
 */
export async function downloadExcel(complaints, filename = 'Reporte_Quejas.xlsx') {
    const ExcelJS = (await import('exceljs')).default || (await import('exceljs'));
    const workbook = new ExcelJS.Workbook();
    const sheet = workbook.addWorksheet("Reporte");

    sheet.columns = [
        { header: "Área", key: "area", width: 20 },
        { header: "Criterio", key: "criteria", width: 50 },
        { header: "Cantidad", key: "count", width: 15 },
    ];

    complaints.forEach((item) => {
        const addedRow = sheet.addRow(item);
        const bgColor = getAreaColor(item.area);

        addedRow.eachCell({ includeEmpty: true }, (cell) => {
            cell.fill = {
                type: "pattern",
                pattern: "solid",
                fgColor: { argb: bgColor },
            };
            cell.border = {
                top: { style: "thin" },
                left: { style: "thin" },
                bottom: { style: "thin" },
                right: { style: "thin" },
            };
        });
    });

    const totalCount = complaints.reduce((sum, item) => sum + item.count, 0);
    const totalRow = sheet.addRow({
        area: "TOTAL GENERAL",
        criteria: "",
        count: totalCount,
    });

    totalRow.eachCell((cell) => {
        cell.font = { bold: true, size: 12 };
        cell.fill = {
            type: "pattern",
            pattern: "solid",
            fgColor: { argb: "FFFFFF00" }, // Yellow
        };
        cell.border = {
            top: { style: "double" },
            bottom: { style: "thick" },
        };
    });
    sheet.mergeCells(`A${totalRow.number}:B${totalRow.number}`);

    sheet.getRow(1).eachCell((cell) => {
        cell.font = { bold: true, color: { argb: "FFFFFFFF" } };
        cell.fill = {
            type: "pattern",
            pattern: "solid",
            fgColor: { argb: "FF4472C4" },
        };
        cell.alignment = { horizontal: "center" };
    });

    const buffer = await workbook.xlsx.writeBuffer();
    const blob = new Blob([buffer], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' });
    const url = window.URL.createObjectURL(blob);
    const anchor = document.createElement('a');
    anchor.href = url;
    anchor.download = filename;
    anchor.click();
    window.URL.revokeObjectURL(url);
}
