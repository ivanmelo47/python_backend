<template>
    <div class="dashboard-module">
        <Table 
            title="Cuentas de Ahorro y Efectivo"
            :rows="accounts"
            :columns="columns"
            :loading="loading"
            :pagination="pagination"
            :search-query="searchQuery"
            :sort-options="sortOptions"
            module-id="finanzas-ahorros"
            v-model:items-per-page="itemsPerPage"
            @update:searchQuery="searchQuery = $event"
            @request-data="fetchData"
            @toggle-status="handleToggleStatus"
            @row-click="handleViewInfo"
            pagination-mode="server"
            :show-refresh="true"
        >
            <template #cell-nombre="{ value, row }">
                <div class="flex items-center gap-3">
                    <div class="account-icon-wrapper">
                        <DynamicIcon 
                            v-if="row.icon_data"
                            :name="`db:${row.icon_data.name}`" 
                            :databaseData="row.icon_data" 
                            :size="18" 
                        />
                        <Icon v-else :name="row.icon || 'credit-card'" :size="18" />
                    </div>
                    <div class="flex flex-col">
                        <span class="font-bold">{{ value }}</span>
                        <div v-if="row.secciones_count > 0" class="flex items-center gap-1 mt-1">
                            <div class="flex -space-x-2 overflow-hidden">
                                <div 
                                    v-for="s in row.secciones.slice(0, 3)" 
                                    :key="s.id"
                                    class="inline-block h-3 w-3 rounded-full border border-white"
                                    :style="{ backgroundColor: s.color || 'var(--primary)' }"
                                    :title="s.nombre"
                                ></div>
                            </div>
                            <span class="text-[10px] text-tertiary font-medium">
                                {{ row.secciones_count }} {{ row.secciones_count === 1 ? 'sección' : 'secciones' }}
                            </span>
                        </div>
                    </div>
                </div>
            </template>
            <template #cell-saldo_apertura="{ value }">
                <span class="balance-text text-muted">
                    {{ formatCurrency(value) }}
                </span>
            </template>

            <template #cell-saldo_actual="{ value }">
                <span class="balance-text fw-bold" :class="value >= 0 ? 'text-success' : 'text-danger'">
                    {{ formatCurrency(value) }}
                </span>
            </template>

            <template #cell-actions="{ row }">
                <button 
                    class="dropdown-item" 
                    @click.stop="handleViewInfo(row)"
                >
                    <Icon name="info" :size="16" />
                    <span>Ver detalles</span>
                </button>

                <button 
                    class="dropdown-item" 
                    @click.stop="handleViewMovements(row)"
                >
                    <Icon name="list" :size="16" />
                    <span>Ver movimientos</span>
                </button>
                
                <button 
                    class="dropdown-item" 
                    @click.stop="handleViewProjection(row)"
                >
                    <Icon name="trendingUp" :size="16" />
                    <span>Proyección de Saldo</span>
                </button>

                <button 
                    v-if="row.genera_rendimiento"
                    class="dropdown-item" 
                    @click.stop="handleViewAccount(row)"
                >
                    <Icon name="eye" :size="16" />
                    <span>Ver rendimiento</span>
                </button>

                <button 
                    class="dropdown-item" 
                    @click.stop="openEditModal(row)"
                >
                    <Icon name="pencil" :size="16" />
                    <span>Editar cuenta</span>
                </button>

                <button 
                    class="dropdown-item" 
                    @click.stop="handleManageSections(row)"
                >
                    <Icon name="layers" :size="16" />
                    <span>Gestionar Secciones</span>
                </button>

                <button 
                    v-if="row.genera_rendimiento"
                    class="dropdown-item" 
                    @click.stop="openTasasHistory(row)"
                >
                    <Icon name="history" :size="16" />
                    <span>Historial de Tasas</span>
                </button>

                <button 
                    v-if="row.genera_rendimiento"
                    class="dropdown-item" 
                    @click.stop="handleManualYield(row)"
                    :disabled="isCalculatingYield === row.id"
                >
                    <Icon name="wand" :size="16" />
                    <span>{{ isCalculatingYield === row.id ? 'Calculando...' : 'Calcular rendimiento' }}</span>
                </button>

                <div class="dropdown-divider"></div>

                <button 
                    class="dropdown-item danger" 
                    @click.stop="handleDeleteAccount(row)"
                >
                    <Icon name="trash" :size="16" />
                    <span>Eliminar</span>
                </button>
            </template>

            <template #header-actions>
                <div class="header-actions-wrapper">
                    <button class="header-dropdown-trigger" :class="{ 'active': showFabMenu }" @click="showFabMenu = !showFabMenu">
                        <Icon :name="showFabMenu ? 'x' : 'plus'" :size="16" /> NUEVO / REGISTRAR
                    </button>
                    <div v-if="showFabMenu" class="header-actions-menu">
                        <button class="dropdown-item item-income" @click="openMovementModal('ingreso'); showFabMenu = false">
                            <Icon name="arrowDown" :size="16" class="text-success" /> 
                            <span>Registrar Ingreso</span>
                        </button>
                        <button class="dropdown-item item-expense" @click="openMovementModal('gasto'); showFabMenu = false">
                            <Icon name="arrowUp" :size="16" class="text-danger" /> 
                            <span>Registrar Gasto</span>
                        </button>
                        <div class="menu-divider"></div>
                        <button class="dropdown-item item-primary" @click="openCreateModal(); showFabMenu = false">
                            <Icon name="plus" :size="16" class="text-primary" /> 
                            <span>Nueva Cuenta</span>
                        </button>
                        <div class="menu-divider"></div>
                        <button class="dropdown-item item-tertiary" @click="handleViewGlobalProjection(); showFabMenu = false">
                            <Icon name="trendingUp" :size="16" class="text-tertiary" /> 
                            <span>Proyección Global</span>
                        </button>
                    </div>
                    <div v-if="showFabMenu" class="menu-overlay-transparent" @click="showFabMenu = false"></div>
                </div>
            </template>
        </Table>

        <!-- Account Form Modal -->
        <AccountFormModal
            :isVisible="showCreateModal || showEditModal"
            :editingAccount="editingAccount"
            @close="handleCloseAccountModal"
            @saved="handleAccountSaved"
        />

        <!-- View Yield Modal -->
        <ModalForm
            :isVisible="showViewModal"
            :title="`Rendimientos: ${selectedAccount?.nombre || ''}`"
            size="lg"
            @close="showViewModal = false"
            :showFooter="false"
        >
            <template #header-icon>
                <Icon name="eye" :size="20" />
            </template>
            
            <div class="yield-view-content">
                <div class="yield-summary mb-4">
                    <div class="yield-stat">
                        <span class="label">Balance Actual</span>
                        <h4 class="value">{{ formatCurrency(selectedAccount?.saldo_actual || 0) }}</h4>
                    </div>
                    <div class="yield-stat">
                        <span class="label">Tasa Anual</span>
                        <h4 class="value text-warning">{{ selectedAccount?.tasa_rendimiento_anual }}%</h4>
                    </div>
                </div>

                <div class="chart-container mb-4" style="height: 250px; position: relative;">
                    <Line v-if="chartData" :data="chartData" :options="chartOptions" />
                    <div v-else-if="isLoadingHistory" class="loading-overlay">
                        <span>Cargando historial...</span>
                    </div>
                    <div v-else class="empty-yield-text">
                        No hay historial de rendimientos todavía.
                    </div>
                </div>

                <!-- Projection Simulator -->
                <div class="projection-simulator glass-panel mt-4">
                    <div class="simulator-header">
                        <Icon name="trendingUp" :size="18" />
                        <span>Simulador de Proyección</span>
                    </div>
                    <div class="simulator-body">
                        <div class="input-group">
                            <label>Proyectar hasta:</label>
                            <input type="date" v-model="projectionDate" class="form-control" :min="today">
                        </div>
                        <div class="projection-results" v-if="projection">
                            <div class="projection-item">
                                <span class="label">Ganancia Estimada</span>
                                <span class="value text-success">+{{ formatCurrency(projection.profit) }}</span>
                            </div>
                            <div class="projection-item main">
                                <span class="label">Saldo Final Estimado</span>
                                <span class="value">{{ formatCurrency(projection.total) }}</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </ModalForm>

        <!-- Account Movements Modal -->
        <ModalForm
            :isVisible="showMovementsModal"
            :title="`Movimientos: ${movementsAccount?.nombre || ''}`"
            size="lg"
            @close="showMovementsModal = false"
            :showFooter="false"
        >
            <template #header-icon>
                <Icon name="list" :size="20" />
            </template>

            <div v-if="isLoadingMovements" class="loading-overlay py-6">
                <span>Cargando movimientos...</span>
            </div>

            <div v-else class="movements-view">
                <!-- Summary Stats -->
                <div class="movements-summary mb-4">
                    <div class="mov-stat income">
                        <span class="label">Total Ingresos</span>
                        <span class="value">+{{ formatCurrency(movementsSummary.totalIncome) }}</span>
                    </div>
                    <div class="mov-stat expense">
                        <span class="label">Total Egresos</span>
                        <span class="value">-{{ formatCurrency(movementsSummary.totalExpense) }}</span>
                    </div>
                    <div class="mov-stat yield">
                        <span class="label">Total Rendimientos</span>
                        <span class="value">+{{ formatCurrency(movementsSummary.totalYield) }}</span>
                    </div>
                    <div class="mov-stat net">
                        <span class="label">Balance Neto</span>
                        <span class="value" :style="{ color: movementsSummary.net >= 0 ? '#10b981' : '#ef4444' }">
                            {{ movementsSummary.net >= 0 ? '+' : '' }}{{ formatCurrency(movementsSummary.net) }}
                        </span>
                    </div>
                </div>

                <!-- Movements List -->
                <div class="movements-list">
                    <div v-if="accountMovements.length === 0" class="empty-state py-4 text-center text-tertiary">
                        No hay movimientos registrados en esta cuenta.
                    </div>
                    <div 
                        v-for="mov in accountMovements" 
                        :key="mov.id" 
                        class="movement-row cursor-pointer hover:bg-white/5 transition-colors"
                        @click="openMovementDetail(mov)"
                    >
                        <div class="movement-icon" :class="mov.tipo">
                            <Icon 
                                :name="mov.tipo === 'ingreso' ? 'trendingUp' : mov.tipo === 'rendimiento' ? 'star' : 'trendingDown'" 
                                :size="16" 
                            />
                        </div>
                        <div class="movement-info">
                            <span class="movement-desc flex items-center gap-1">
                                {{ mov.descripcion }}
                                <Icon v-if="mov.adjuntos_count > 0" name="paperclip" :size="12" class="text-primary opacity-60" />
                            </span>
                            <span class="movement-date">{{ formatDate(mov.fecha) }}</span>
                        </div>
                        <div class="movement-amount" :style="{ color: (mov.tipo === 'ingreso' || mov.tipo === 'rendimiento') ? '#10b981' : '#ef4444' }">
                            {{ (mov.tipo === 'ingreso' || mov.tipo === 'rendimiento') ? '+' : '-' }}{{ formatCurrency(mov.monto) }}
                        </div>
                    </div>
                </div>
            </div>
        </ModalForm>
        <!-- Tasas History Modal -->
        <ModalForm
            :isVisible="showTasasModal"
            :title="`Historial de Tasas: ${selectedAccount?.nombre || ''}`"
            size="md"
            @close="showTasasModal = false"
            :showFooter="false"
        >
            <template #header-icon>
                <Icon name="history" :size="20" />
            </template>
            
            <div class="tasas-history-content">
                <div class="tasas-form d-flex gap-2 mb-4 align-items-end">
                    <ModalField label="Fecha de Aplicación" span="1" class="flex-grow-1">
                        <input type="date" v-model="newTasaForm.fecha_inicio" :max="today">
                    </ModalField>
                    
                    <ModalField label="Tasa Anual (%)" span="1" class="flex-grow-1">
                        <div class="input-group">
                            <input type="number" step="0.01" v-model="newTasaForm.tasa_anual" placeholder="Ej. 15.00">
                            <span class="input-group-text">%</span>
                        </div>
                    </ModalField>
                    
                    <button class="btn btn-primary mb-1" @click="handleAddTasa" :disabled="isAddingTasa || !newTasaForm.fecha_inicio || !newTasaForm.tasa_anual" style="height: 46px;">
                        <Icon name="plus" :size="16" /> Añadir
                    </button>
                </div>

                <div class="movements-list">
                    <div v-if="accountTasas.length === 0 && !isLoadingTasas" class="empty-state py-4 text-center text-tertiary">
                        No hay tasas registradas.
                    </div>
                    <div v-else-if="isLoadingTasas" class="empty-state py-4 text-center text-tertiary">
                        Cargando tasas...
                    </div>
                    <div 
                        v-else
                        v-for="(tasa, index) in accountTasas" 
                        :key="tasa.id" 
                        class="movement-row d-flex justify-content-between align-items-center"
                    >
                        <div class="d-flex align-items-center gap-3">
                            <div class="movement-icon yield">
                                <Icon name="star" :size="16" />
                            </div>
                            <div class="movement-info">
                                <span class="movement-desc">Tasa Activa</span>
                                <span class="movement-date">Desde: {{ formatDate(tasa.fecha_inicio).split(' ')[0] }}</span>
                            </div>
                        </div>
                        <div class="d-flex align-items-center gap-3">
                            <div class="movement-amount text-warning">
                                {{ parseFloat(tasa.tasa_anual).toFixed(2) }}%
                            </div>
                            <button 
                                v-if="accountTasas.length > 1"
                                class="btn btn-icon text-danger p-1" 
                                @click="handleDeleteTasa(tasa.id)"
                                :disabled="isDeletingTasa === tasa.id"
                                title="Eliminar"
                            >
                                <Icon name="trash" :size="16" />
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </ModalForm>

        <!-- New Movement Modal -->
        <ModalForm
            :isVisible="showMovementModal"
            :title="movementModalTitle"
            :loading="isCreatingMovement"
            size="md"
            @close="showMovementModal = false"
            @submit="handleCreateMovement"
            :fields="movementFormFields"
            :modelValue="movementForm"
            :errors="movementErrors"
        >
            <template #header-icon>
                <Icon :name="movementForm.tipo === 'ingreso' ? 'trendingUp' : 'trendingDown'" :size="20" />
            </template>

            <!-- Custom Amount Input -->
            <template #field-monto="{ field, modelValue }">
                <div class="relative flex items-center">
                    <input 
                        type="number" 
                        v-model="modelValue.monto" 
                        :placeholder="field.placeholder"
                        class="form-control"
                    >
                </div>
            </template>

            <template #field-categoria_uuid="{ field, modelValue }">
                <div class="flex gap-2">
                    <select
                        v-model="modelValue.categoria_uuid"
                        class="flex-1"
                        :disabled="field.options.length === 0"
                    >
                        <option value="" disabled>
                            {{ field.options.length === 0 ? 'Sin categorías disponibles' : 'Selecciona una categoría' }}
                        </option>
                        <option v-for="option in field.options" :key="option.id" :value="option.id">
                            {{ option.name }}
                        </option>
                    </select>
                    <button 
                        type="button" 
                        class="btn-icon-square" 
                        title="Nueva Categoría"
                        @click="openQuickCategoryModal"
                    >
                        <Icon name="plus" :size="16" />
                    </button>
                </div>
            </template>

            <!-- Custom Field: Attachments Upload -->
            <template #field-files>
                <div class="premium-upload-container">
                    <label class="premium-upload-label">
                        <Icon name="paperclip" :size="14" />
                        <span>Comprobantes y Recibos</span>
                    </label>
                    
                    <div 
                        class="premium-drop-zone" 
                        :class="{ 'is-dragging': isDraggingFiles }"
                        @dragover.prevent="isDraggingFiles = true"
                        @dragleave.prevent="isDraggingFiles = false"
                        @drop.prevent="handleFilesDrop"
                    >
                        <input 
                            type="file" 
                            multiple 
                            class="premium-hidden-input" 
                            id="movement-files" 
                            @change="handleFilesSelect"
                            accept="image/*,.pdf"
                        >
                        <div class="drop-zone-overlay">
                            <div class="icon-circle">
                                <Icon :name="isDraggingFiles ? 'cloudUpload' : 'plus'" :size="24" />
                            </div>
                            <div class="drop-text">
                                <span class="main-text">Arrastra tus archivos aquí</span>
                                <span class="sub-text">o haz clic para explorar (PDF, PNG, JPG)</span>
                            </div>
                            <div class="limit-badge">Máx. 10MB</div>
                        </div>
                    </div>

                    <!-- Selected Files List -->
                    <TransitionGroup name="list" tag="div" v-if="selectedFiles.length > 0" class="premium-file-list mt-3">
                        <div v-for="(file, idx) in selectedFiles" :key="idx + file.name" class="premium-file-card">
                            <div class="file-type-icon" :class="getFileClass(file.name.split('.').pop())">
                                <Icon :name="getFileIcon(file.name)" :size="18" />
                            </div>
                            <div class="file-details">
                                <span class="file-name truncate">{{ file.name }}</span>
                                <span class="file-size">{{ formatSize(file.size) }}</span>
                            </div>
                            <button type="button" class="btn-remove-file" @click="removeSelectedFile(idx)" title="Quitar archivo">
                                <Icon name="trash" :size="14" />
                            </button>
                        </div>
                    </TransitionGroup>
                </div>
            </template>
        </ModalForm>

        <!-- Quick Create Category Modal -->
        <ModalForm
            :is-visible="showQuickCategoryModal"
            title="Nueva Categoría Rápida"
            :loading="isCreatingQuickCategory"
            :fields="quickCategoryFields"
            v-model="quickCategoryForm"
            @submit="handleQuickCategoryCreate"
            @close="showQuickCategoryModal = false"
        >
            <template #header-icon>
                <Icon name="tag" :size="20" />
            </template>
        </ModalForm>

        <ModalInformation
            v-if="infoAccount"
            :is-open="showInfoModal"
            title="Detalles de la Cuenta"
            icon="bank"
            :data="infoAccount"
            :columns="infoColumns"
            show-edit-button
            @edit="showInfoModal = false; openEditModal(infoAccount)"
            @close="showInfoModal = false"
        >
            <template #top-header>
                <div class="account-detail-hero">
                    <div class="account-hero-icon">
                        <DynamicIcon 
                            v-if="infoAccount.icon_data"
                            :name="`db:${infoAccount.icon_data.name}`" 
                            :databaseData="infoAccount.icon_data" 
                            :size="32" 
                        />
                        <Icon v-else :name="infoAccount.icon || 'credit-card'" :size="32" />
                    </div>
                    <div class="account-hero-info">
                        <h4>{{ infoAccount.nombre }}</h4>
                        <p>{{ infoAccount.banco || 'Institución no especificada' }}</p>
                    </div>
                    <div class="account-hero-badge">
                        <span class="status-badge" :class="infoAccount.status === 'activa' ? 'active' : 'archived'">
                            {{ infoAccount.status === 'activa' ? 'Cuenta Activa' : 'Archivada' }}
                        </span>
                    </div>
                </div>
            </template>

            <template #value-saldo_apertura>
                {{ formatCurrency(infoAccount.saldo_apertura) }}
            </template>

            <template #value-saldo_actual>
                <span class="font-bold" :class="infoAccount.saldo_actual >= 0 ? 'text-success' : 'text-error'">
                    {{ formatCurrency(infoAccount.saldo_actual) }}
                </span>
            </template>

            <template #value-moneda>
                <span class="badge info">{{ infoAccount.moneda }}</span>
            </template>

            <template #value-genera_rendimiento>
                <div class="flex items-center gap-2">
                    <Icon 
                        :name="infoAccount.genera_rendimiento ? 'checkCircle' : 'xCircle'" 
                        :size="16" 
                        :class="infoAccount.genera_rendimiento ? 'text-success' : 'text-tertiary'"
                    />
                    <span>{{ infoAccount.genera_rendimiento ? 'Genera rendimientos automáticos' : 'No genera rendimientos' }}</span>
                </div>
            </template>

            <template #value-tasa_rendimiento_anual>
                <span v-if="infoAccount.genera_rendimiento" class="text-warning font-bold">
                    {{ infoAccount.tasa_rendimiento_anual }}% Anual
                </span>
                <span v-else class="text-tertiary">N/A</span>
            </template>

            <template #value-hora_rendimiento>
                <span v-if="infoAccount.genera_rendimiento">{{ infoAccount.hora_rendimiento }}</span>
                <span v-else class="text-tertiary">N/A</span>
            </template>
        </ModalInformation>

        <!-- Proyección de Saldo Fullscreen Overlay -->
        <ProjectionOverlay
            :show="showProyeccionModal"
            :loading="loadingProjection"
            :title="isGlobalProjection ? 'Proyección Global de Patrimonio' : 'Proyección de Balance'"
            :subtitle="isGlobalProjection ? 'Consolidado de todas las cuentas activas' : `${selectedAccount?.nombre} • ${selectedAccount?.banco || 'Institución'}`"
            tableTitle="Cronograma de Crecimiento"
            chartTitle="Evolución del Patrimonio"
            chartSubtitle="Proyección considerando ingresos, gastos planeados e interés compuesto"
            v-model:viewMode="projectionViewMode"
            @close="showProyeccionModal = false"
            @export="generatePDF"
        >
            <template #header-icon>
                <Icon v-if="isGlobalProjection" name="trendingUp" :size="20" />
                <template v-else>
                    <DynamicIcon v-if="selectedAccount?.icon_data" :name="`db:${selectedAccount.icon_data.name}`" :databaseData="selectedAccount.icon_data" :size="20" />
                    <Icon v-else name="bank" :size="20" />
                </template>
            </template>

            <template #extra-controls>
                <div v-if="isGlobalProjection" class="flex items-center gap-2 mr-4">
                    <span class="text-sm font-semibold" style="color: var(--text-secondary); font-size: 0.85rem;">Incluir Tarjetas de Crédito</span>
                    <label class="switch">
                        <input type="checkbox" v-model="includeCreditCards" :disabled="loadingProjection">
                        <span class="slider round"></span>
                    </label>
                </div>
            </template>

            <template #metrics>
                <div class="metric-card">
                    <span class="label">SALDO ACTUAL</span>
                    <span class="value">{{ formatCurrency(selectedAccount?.saldo_actual || 0) }}</span>
                </div>
                <div class="metric-card highlight">
                    <span class="label">PROYECCIÓN A 24 MESES</span>
                    <span class="value text-success">{{ projectionData.length > 0 ? formatCurrency(projectionData[projectionData.length - 1].saldo_final) : '$0.00' }}</span>
                </div>
            </template>

            <template #table>
                <table class="mini-table">
                    <thead>
                        <tr>
                            <th>Mes</th>
                            <th class="text-right">Ingresos</th>
                            <th class="text-right">Gastos</th>
                            <th class="text-right">Balance</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="item in projectionData" :key="item.key" :class="{ 'current': item.is_current }" @click="handleViewMonthDetails(item)">
                            <td>{{ item.label }}</td>
                            <td class="text-right text-success">+{{ formatCurrency(item.ingresos + item.intereses) }}</td>
                            <td class="text-right text-danger">-{{ formatCurrency(item.gastos) }}</td>
                            <td class="text-right fw-bold">{{ formatCurrency(item.saldo_final) }}</td>
                        </tr>
                    </tbody>
                </table>
            </template>

            <template #chart>
                <canvas ref="projectionChartRef"></canvas>
            </template>

            <template #details-header>
                <h4>Detalles de {{ selectedMonthDetails?.label }}</h4>
                <p>Desglose de movimientos proyectados para este periodo</p>
            </template>

            <template #details-content>
                <div v-if="selectedMonthDetails" class="details-content-wrapper">
                    <div class="month-summary-cards">
                        <div class="s-card">
                            <span class="label">Saldo Inicial</span>
                            <span class="value">{{ formatCurrency(selectedMonthDetails.saldo_inicial) }}</span>
                        </div>
                        <div class="s-card income">
                            <span class="label">Total Ingresos</span>
                            <span class="value text-success">+{{ formatCurrency(selectedMonthDetails.ingresos) }}</span>
                        </div>
                        <div class="s-card expense">
                            <span class="label">Total Gastos</span>
                            <span class="value text-danger">-{{ formatCurrency(selectedMonthDetails.gastos) }}</span>
                        </div>
                        <div class="s-card yield" v-if="selectedMonthDetails.intereses > 0">
                            <span class="label">Rendimientos</span>
                            <span class="value text-warning">+{{ formatCurrency(selectedMonthDetails.intereses) }}</span>
                        </div>
                        <div class="s-card total">
                            <span class="label">Saldo Final</span>
                            <span class="value">{{ formatCurrency(selectedMonthDetails.saldo_final) }}</span>
                        </div>
                    </div>

                    <div class="movements-drilldown">
                        <h5>MOVIMIENTOS EN ESTE MES</h5>
                        <div class="drilldown-list">
                            <div 
                                v-for="(item, idx) in selectedMonthDetails.detalles" 
                                :key="idx" 
                                class="drilldown-wrapper"
                            >
                                <div 
                                    class="drilldown-item" 
                                    :class="{ 'has-expansion': item.ocurrencias > 1, 'is-expanded': expandedItems.has(`${selectedMonthDetails.key}-${idx}`) }"
                                    @click="toggleItemExpansion(selectedMonthDetails.key, idx, item.ocurrencias)"
                                >
                                    <div class="item-left">
                                        <div class="item-icon" :class="item.tipo">
                                            <Icon :name="item.tipo === 'ingreso' ? 'arrowUp' : item.tipo === 'rendimiento' ? 'zap' : 'arrowDown'" :size="18" />
                                        </div>
                                        <div class="item-info">
                                            <span class="item-name">{{ item.descripcion }}</span>
                                            <div class="item-meta">
                                                <span v-if="isGlobalProjection && item.cuenta" class="projection-account-badge">{{ item.cuenta }}</span>
                                                <span class="installment">
                                                    {{ item.tipo === 'rendimiento' ? 'Interés Compuesto' : (item.ocurrencias > 1 ? `${item.ocurrencias} ejecuciones` : 'Ejecución única') }}
                                                </span>
                                                <Icon v-if="item.ocurrencias > 1" :name="expandedItems.has(`${selectedMonthDetails.key}-${idx}`) ? 'chevronUp' : 'chevronDown'" :size="12" class="ms-1 opacity-50" />
                                            </div>
                                        </div>
                                    </div>
                                    <div class="item-right">
                                        <div class="amount-bubble" :class="item.tipo">
                                            {{ (item.tipo === 'ingreso' || item.tipo === 'rendimiento') ? '+' : '-' }}{{ formatCurrency(item.monto_total) }}
                                        </div>
                                    </div>
                                </div>

                                <!-- Sub-list expansion -->
                                <div 
                                    v-if="expandedItems.has(`${selectedMonthDetails.key}-${idx}`)" 
                                    class="item-expansion-content animate-slide-down"
                                >
                                    <div v-for="(fecha, fIdx) in item.fechas" :key="fIdx" class="expansion-row">
                                        <div class="row-date">
                                            <Icon name="clock" :size="14" />
                                            <span>{{ formatDate(fecha) }}</span>
                                        </div>
                                        <div class="row-amount">{{ formatCurrency(item.monto_unitario) }}</div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </template>
        </ProjectionOverlay>

        <!-- Sections Manager Modal -->
        <AccountSectionsModal
            :show="showSectionsModal"
            :account="sectionsAccount"
            @close="showSectionsModal = false"
            @updated="fetchData"
        />

        <!-- Movement Details Modal -->
        <MovementDetailModal
            :isVisible="showDetailModal"
            :movimiento="selectedMovement"
            @close="showDetailModal = false"
            @updated="fetchData"
        />
    </div>
</template>

<script setup>
import { ref, reactive, computed, watch, onMounted, nextTick } from 'vue';
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, BarElement, BarController, Title, Tooltip, Legend, Filler } from 'chart.js';
import { Line } from 'vue-chartjs';
import { api } from '@/services/api';
import Icon from '@/components/Icon.vue';
import DynamicIcon from '@/components/DynamicIcon.vue';
import Table from '@/views/private/admin/components/Table.vue';
import ModalForm from '@/views/private/admin/components/ModalForm.vue';
import ModalField from '@/views/private/admin/components/ModalField.vue';
import ModalInformation from '@/views/private/admin/components/ModalInformation.vue';
import ProjectionOverlay from './components/ProjectionOverlay.vue';
import AccountSectionsModal from './components/AccountSectionsModal.vue';
import MovementDetailModal from './components/MovementDetailModal.vue';
import AccountFormModal from './components/AccountFormModal.vue';
import MovementFormModal from './components/MovementFormModal.vue';
import QuickCategoryModal from './components/QuickCategoryModal.vue';
import { useTableData } from '@/composables/useTableData';
import { useAlert } from '@/composables/useAlert';
import { useTheme } from '@/composables/useTheme';
import { formatDate } from '@/utils/format-date';

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, BarElement, BarController, Title, Tooltip, Legend, Filler);

const showFabMenu = ref(false);

const alert = useAlert();
const { theme } = useTheme();

// Sort Options
const sortOptions = [
    { key: 'nombre', label: 'Nombre de Cuenta' },
    { key: 'banco', label: 'Institución' },
    { key: 'tasa_rendimiento_anual', label: 'Tasa Anual' },
    { key: 'saldo_actual', label: 'Balance Actual' }
];

// Data & Table
const itemsPerPage = ref(10);
const searchQuery = ref('');

const { 
    data: accounts, 
    loading, 
    pagination, 
    fetchData 
} = useTableData(api.finanzas.getCuentasAhorro, {
    mode: 'server',
    itemsPerPage: itemsPerPage,
    searchQuery: searchQuery,
    onError: (err) => console.error("Error cargando cuentas", err)
});

const columns = [
    { key: 'nombre', label: 'NOMBRE CUENTA' },
    { key: 'banco', label: 'INSTITUCIÓN' },
    { key: 'saldo_apertura', label: 'S. INICIAL', cellClass: 'text-right' },
    { key: 'saldo_actual', label: 'S. ACTUAL', cellClass: 'text-right font-bold' },
    { key: 'status', label: 'ESTADO', type: 'switch', activeLabel: 'Activa', inactiveLabel: 'Inactiva', headerClass: 'text-center', cellClass: 'text-center' },
    { key: 'actions', label: '', headerClass: 'compact', cellClass: 'compact' },
];


const formatCurrency = (val) => {
    return new Intl.NumberFormat('es-MX', { style: 'currency', currency: 'MXN' }).format(val);
};

// Logic for account modals
const showCreateModal = ref(false);
const showEditModal = ref(false);
const editingAccount = ref(null);

const handleCloseAccountModal = () => {
    showCreateModal.value = false;
    showEditModal.value = false;
    editingAccount.value = null;
};

const handleAccountSaved = () => {
    fetchData();
};

// --- MOVEMENT CREATION MIGRATION ---
const showMovementModal = ref(false);
const isCreatingMovement = ref(false);
const movementErrors = ref({});
const accountsForMovement = ref([]);
const categorias = ref([]);
const sectionsForMovement = ref([]);
const isLoadingSections = ref(false);

const showSectionsModal = ref(false);
const sectionsAccount = ref(null);
const isDraggingFiles = ref(false);
const selectedFiles = ref([]);
const movementForm = reactive({
    cuenta_uuid: '', 
    tipo: 'ingreso',
    monto: '',
    descripcion: '',
    fecha: new Date().toISOString().split('T')[0],
    categoria_uuid: '',
    notas: '',
    a_meses: false,
    es_msi: true,
    monto_final: '',
    plazo: 12,
    fuente_fondos_uuid: 'externo',
    seccion_uuid: ''
});

const selectedAccountBalance = computed(() => {
    if (!movementForm.cuenta_uuid) return 0;
    const uuid = movementForm.cuenta_uuid.replace('cuenta_', '');
    const account = accountsForMovement.value.find(a => a.uuid === uuid);
    return account ? parseFloat(account.saldo_actual) : 0;
});

const insufficientFundsError = computed(() => {
    if (movementForm.tipo !== 'gasto') return null;
    if (!movementForm.cuenta_uuid || !movementForm.monto) return null;
    const montoNum = parseFloat(movementForm.monto);
    if (isNaN(montoNum)) return null;
    if (montoNum > selectedAccountBalance.value) {
        return `Saldo insuficiente. Disponible: ${formatCurrency(selectedAccountBalance.value)}`;
    }
    return null;
});

watch(insufficientFundsError, (newError) => {
    if (newError) {
        movementErrors.value = {
            ...movementErrors.value,
            monto: [newError]
        };
    } else if (movementErrors.value.monto && movementErrors.value.monto[0]?.includes('Saldo insuficiente')) {
        const newErrors = { ...movementErrors.value };
        delete newErrors.monto;
        movementErrors.value = newErrors;
    }
});

// Movement Detail State
const showDetailModal = ref(false);
const selectedMovement = ref(null);

const openMovementDetail = (mov) => {
    selectedMovement.value = mov;
    showDetailModal.value = true;
};

// Projection State
const showProyeccionModal = ref(false);
const loadingProjection = ref(false);
const projectionData = ref([]);
const projectionViewMode = ref('chart'); // 'chart' or 'details'
const selectedMonthDetails = ref(null);
const projectionChartRef = ref(null);
let projectionChartInstance = null;
const includeCreditCards = ref(false);

const movementModalTitle = computed(() => {
    return movementForm.tipo === 'ingreso' ? 'Registrar Ingreso' : 'Registrar Gasto';
});


const movementFormFields = computed(() => {
    const fields = [
        { key: 'fecha', label: 'Fecha', type: 'date', required: true, span: 2 },
        {
            key: 'cuenta_uuid',
            label: 'Cuenta de Ahorro',
            type: 'select',
            required: true,
            span: 2,
            options: accountsForMovement.value
                .filter(a => a.status === true || a.status === 1 || a.status === 'activa')
                .map(a => ({
                    id: `cuenta_${a.uuid}`,
                    name: `🏦 ${a.nombre} (${a.banco || 'N/A'})`
                }))
        },
        { key: 'descripcion', label: 'Concepto', type: 'text', placeholder: 'Ej. Compra Súper, Pago Nómina', required: true, span: 2 },
        { 
            key: 'monto', 
            label: 'Monto ($)', 
            type: 'number', 
            placeholder: '0.00', 
            required: true, 
            span: 2,
            help: (movementForm.tipo === 'gasto' && movementForm.cuenta_uuid) ? `Saldo Disponible: ${formatCurrency(selectedAccountBalance.value)}` : ''
        },
    ];

    fields.push({
        key: 'fuente_fondos_uuid',
        label: movementForm.tipo === 'ingreso' ? '¿De dónde viene el dinero? (Fuente)' : '¿A dónde va el dinero? (Destino)',
        type: 'select',
        required: true,
        span: 4,
        options: [
            { id: 'externo', name: '💸 Externo (Efectivo / Terceros)' },
            ...accountsForMovement.value
                .filter(a => a.status === true || a.status === 1 || a.status === 'activa')
                .map(a => ({
                    id: `cuenta_${a.uuid}`,
                    name: `🏦 ${a.nombre} (${a.banco})`
                }))
        ]
    });

    fields.push(
        {
            key: 'categoria_uuid',
            label: 'Categoría',
            type: 'select',
            span: 4,
            options: categorias.value
                .filter(c => c.tipo === movementForm.tipo || c.tipo === 'mixto')
                .map(c => ({ id: c.uuid, name: c.nombre }))
        },
        { key: 'notas', label: 'Notas', type: 'textarea', span: 4 },
        { key: 'files', label: 'Archivos Adjuntos', type: 'custom', span: 4 },
    );

    if (sectionsForMovement.value.length > 0) {
        fields.push({
            key: 'seccion_uuid',
            label: 'Sección / Apartado (Opcional)',
            type: 'select',
            span: 4,
            options: [
                { id: '', name: '💰 Saldo Principal (Sin sección)' },
                ...sectionsForMovement.value.map(s => ({
                    id: s.uuid,
                    name: `${s.nombre} (${formatCurrency(s.saldo_actual)})`
                }))
            ]
        });
    }

    return fields;
});

const fetchMovementData = async () => {
    try {
        const response = await api.finanzas.getCuentasAhorro({ per_page: 100 });
        accountsForMovement.value = (response.data.data || []);
        
        const catRes = await api.finanzas.getCategorias();
        categorias.value = catRes.data || [];
    } catch (e) {
        console.error("Error loading movement dependencies", e);
    }
};

const openMovementModal = (type = 'ingreso') => {
    Object.assign(movementForm, {
        cuenta_uuid: accountsForMovement.value[0] ? `cuenta_${accountsForMovement.value[0].uuid}` : '',
        tipo: type,
        monto: '',
        descripcion: '',
        fecha: new Date().toISOString().split('T')[0],
        categoria_uuid: '',
        notas: '',
        fuente_fondos_uuid: 'externo',
        seccion_uuid: ''
    });
    selectedFiles.value = [];
    sectionsForMovement.value = [];
    movementErrors.value = {};
    showMovementModal.value = true;
};

const handleCreateMovement = async () => {
    isCreatingMovement.value = true;
    movementErrors.value = {};
    try {
        const payload = { ...movementForm };
        
        if (payload.cuenta_uuid.startsWith('cuenta_')) {
            payload.cuenta_uuid = payload.cuenta_uuid.replace('cuenta_', '');
        }

        if (payload.fuente_fondos_uuid?.startsWith('cuenta_')) {
            payload.cuenta_cargo_uuid = payload.fuente_fondos_uuid.replace('cuenta_', '');
        }
        delete payload.fuente_fondos_uuid;

        // Validation: Expense cannot exceed balance
        if (payload.tipo === 'gasto' && payload.cuenta_uuid) {
            const selectedAccount = accountsForMovement.value.find(a => a.uuid === payload.cuenta_uuid);
            if (selectedAccount && parseFloat(payload.monto) > parseFloat(selectedAccount.saldo_actual)) {
                movementErrors.value = {
                    monto: [`Saldo insuficiente en la cuenta seleccionada. Saldo actual: ${formatCurrency(selectedAccount.saldo_actual)}`]
                };
                isCreatingMovement.value = false;
                return;
            }
        }

        const response = await api.finanzas.storeMovimiento(payload);
        const movementUuid = response.data.uuid;

        // 2. Upload files if any
        if (selectedFiles.value.length > 0) {
            alert.showLoading('Subiendo comprobantes...', `Enviando ${selectedFiles.value.length} archivo(s)`);
            for (const file of selectedFiles.value) {
                try {
                    await api.finanzas.uploadAdjunto(movementUuid, file);
                } catch (uploadErr) {
                    console.error("Error uploading file", file.name, uploadErr);
                    alert.toast.error('Error de subida', `No se pudo subir: ${file.name}`);
                }
            }
            alert.closeLoading();
        }

        alert.toast.success('¡Éxito!', `Movimiento registrado${selectedFiles.value.length > 0 ? ' con adjuntos' : ''}.`);
        fetchData();
        showMovementModal.value = false;
    } catch (error) {
        if (error.response?.data?.errors) {
            movementErrors.value = error.response.data.errors;
        }
    } finally {
        isCreatingMovement.value = false;
    }
};

// --- FILE HANDLING FOR NEW MOVEMENT ---
const handleFilesSelect = (e) => {
    const files = Array.from(e.target.files);
    addFiles(files);
};

const handleFilesDrop = (e) => {
    isDraggingFiles.value = false;
    const files = Array.from(e.dataTransfer.files);
    addFiles(files);
};

const addFiles = (files) => {
    const validFiles = files.filter(f => {
        const isTooLarge = f.size > 10 * 1024 * 1024;
        if (isTooLarge) alert.toast.warning('Archivo muy grande', `${f.name} excede los 10MB`);
        return !isTooLarge;
    });
    selectedFiles.value = [...selectedFiles.value, ...validFiles];
};

const removeSelectedFile = (idx) => {
    selectedFiles.value.splice(idx, 1);
};

const getFileIcon = (filename) => {
    const ext = (filename || '').split('.').pop().toLowerCase();
    if (['jpg', 'jpeg', 'png', 'gif', 'webp'].includes(ext)) return 'image';
    if (ext === 'pdf') return 'filePdf';
    return 'file';
};

const getFileClass = (ext) => {
    const e = (ext || '').toLowerCase();
    if (['jpg', 'jpeg', 'png', 'gif', 'webp'].includes(e)) return 'is-image';
    if (e === 'pdf') return 'is-pdf';
    return 'is-generic';
};

const formatSize = (bytes) => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};

// --- QUICK CATEGORY CREATION ---
const showQuickCategoryModal = ref(false);
const isCreatingQuickCategory = ref(false);
const quickCategoryForm = reactive({
    nombre: '', tipo: 'gasto', icon: null, color: '#3b82f6', status: true
});

const quickCategoryFields = computed(() => [
    { key: 'nombre', label: 'Nombre de la Categoría', type: 'text', placeholder: 'Ej. Supermercado', required: true },
    { key: 'icon', label: 'Icono', type: 'icon-select' },
    { key: 'color', label: 'Color', type: 'color' }
]);

const openQuickCategoryModal = () => {
    quickCategoryForm.nombre = '';
    quickCategoryForm.tipo = movementForm.tipo;
    quickCategoryForm.icon = null;
    quickCategoryForm.color = movementForm.tipo === 'ingreso' ? '#10b981' : '#3b82f6';
    showQuickCategoryModal.value = true;
};

const handleQuickCategoryCreate = async () => {
    isCreatingQuickCategory.value = true;
    try {
        const response = await api.finanzas.storeCategoria(quickCategoryForm);
        const catRes = await api.finanzas.getCategorias();
        categorias.value = catRes.data || [];
        movementForm.categoria_uuid = response.data.uuid;
        alert.toast.success('¡Listo!', 'Categoría añadida.');
        showQuickCategoryModal.value = false;
    } catch (e) {
        alert.toast.error('Error', 'No se pudo crear la categoría.');
    } finally {
        isCreatingQuickCategory.value = false;
    }
};

onMounted(() => {
    fetchMovementData();
});

watch(() => movementForm.cuenta_uuid, async (newVal) => {
    if (newVal && newVal.startsWith('cuenta_')) {
        const uuid = newVal.replace('cuenta_', '');
        isLoadingSections.value = true;
        try {
            const response = await api.finanzas.getSecciones(uuid);
            sectionsForMovement.value = response.data || response;
        } catch (e) {
            console.error("Error loading sections", e);
            sectionsForMovement.value = [];
        } finally {
            isLoadingSections.value = false;
        }
    } else {
        sectionsForMovement.value = [];
    }
});

const handleManageSections = (row) => {
    sectionsAccount.value = row;
    showSectionsModal.value = true;
};

const openCreateModal = () => {
    editingAccount.value = null;
    showCreateModal.value = true;
};

const openEditModal = (row) => {
    editingAccount.value = row;
    showEditModal.value = true;
};

const handleToggleStatus = async ({ row }) => {
    try {
        const isActive = row.status === true || row.status === 'activa' || row.status === 1;
        const newStatus = !isActive;
        
        await api.finanzas.updateCuentaAhorro(row.uuid, { 
            ...row, 
            status: newStatus 
        });
        
        row.status = newStatus ? 'activa' : 'archivada'; // Sync with backend string representation
        alert.toast.success(
            newStatus ? 'Cuenta activada' : 'Cuenta desactivada', 
            `La cuenta "${row.nombre}" ha sido ${newStatus ? 'habilitada' : 'archivada'}.`
        );
    } catch (error) {
        alert.toast.error('Error', 'No se pudo cambiar el estado de la cuenta.');
        console.error(error);
    }
};

const handleDeleteAccount = async (row) => {
    const confirmed = await alert.fire({
        title: '¿Eliminar cuenta?',
        text: `Se eliminará "${row.nombre}" junto con TODOS sus movimientos (ingresos, egresos y rendimientos). Esta acción no se puede deshacer.`,
        type: 'warning',
        showCancel: true,
        confirmText: 'Sí, eliminar todo',
        cancelText: 'Cancelar'
    });

    if (confirmed) {
        try {
            const response = await api.finanzas.deleteCuentaAhorro(row.uuid);
            const count = response?.data?.movements_deleted ?? 0;
            alert.toast.success(
                'Cuenta eliminada',
                count > 0
                    ? `Se borraron también ${count} movimiento(s) asociado(s).`
                    : 'La cuenta ha sido eliminada.'
            );
            fetchData();
        } catch (error) {
            alert.toast.error('Error', 'No se pudo eliminar la cuenta.');
        }
    }
};

// Movements Modal Logic
const showMovementsModal = ref(false);
const isLoadingMovements = ref(false);
const movementsAccount = ref(null);
const accountMovements = ref([]);

const movementsSummary = computed(() => {
    const totalIncome = accountMovements.value
        .filter(m => m.tipo === 'ingreso')
        .reduce((sum, m) => sum + parseFloat(m.monto), 0);
    const totalExpense = accountMovements.value
        .filter(m => m.tipo === 'gasto')
        .reduce((sum, m) => sum + parseFloat(m.monto), 0);
    const totalYield = accountMovements.value
        .filter(m => m.tipo === 'rendimiento')
        .reduce((sum, m) => sum + parseFloat(m.monto), 0);
    return {
        totalIncome,
        totalExpense,
        totalYield,
        net: totalIncome + totalYield - totalExpense
    };
});

const handleViewMovements = async (row) => {
    movementsAccount.value = row;
    showMovementsModal.value = true;
    isLoadingMovements.value = true;
    accountMovements.value = [];
    try {
        const response = await api.finanzas.getAccountMovements(row.uuid);
        accountMovements.value = response.data.data || [];
    } catch (error) {
        alert.toast.error('Error', 'No se pudo cargar el historial de movimientos');
    } finally {
        isLoadingMovements.value = false;
    }
};

// View Logic
const showViewModal = ref(false);
const isLoadingHistory = ref(false);
const selectedAccount = ref(null);
const yieldHistory = ref([]);

const handleViewAccount = async (row) => {
    selectedAccount.value = row;
    showViewModal.value = true;
    isLoadingHistory.value = true;
    yieldHistory.value = [];
    
    try {
        const response = await api.finanzas.showCuentaAhorro(row.uuid);
        yieldHistory.value = response.data.movimientos || [];
    } catch (error) {
        alert.toast.error('Error', 'No se pudo cargar el historial');
    } finally {
        isLoadingHistory.value = false;
    }
};

// Info Modal Logic
const showInfoModal = ref(false);
const infoAccount = ref(null);
const infoColumns = [
    { key: 'nombre', label: 'Nombre de la Cuenta' },
    { key: 'banco', label: 'Institución' },
    { key: 'tipo', label: 'Tipo de Cuenta' },
    { key: 'saldo_apertura', label: 'Saldo Inicial' },
    { key: 'saldo_actual', label: 'Saldo Actual' },
    { key: 'moneda', label: 'Divisa' },
    { key: 'genera_rendimiento', label: 'Rendimientos', isNote: true },
    { key: 'tasa_rendimiento_anual', label: 'Tasa Anual' },
    { key: 'hora_rendimiento', label: 'Hora de Aplicación' },
    { key: 'notas', label: 'Notas', fullWidth: true, isNote: true }
];

const handleViewInfo = (row) => {
    infoAccount.value = row;
    showInfoModal.value = true;
};

const chartData = computed(() => {
    if (!yieldHistory.value.length) return null;
    
    // Sort chronologically (API returns desc)
    const sorted = [...yieldHistory.value].reverse();
    
    const labels = sorted.map(m => {
        // formatDate might return "25/04/2026, 12:00 a.m.", we just want "25/04/2026"
        return formatDate(m.fecha).split(',')[0].trim();
    });
    const data = sorted.map(m => parseFloat(m.monto));
    
    const datasets = [{
        label: 'Rendimiento Histórico',
        data: [...data],
        borderColor: '#10b981',
        backgroundColor: 'rgba(16, 185, 129, 0.1)',
        fill: true,
        tension: 0.4,
        pointRadius: 4,
        pointBackgroundColor: '#10b981'
    }];
    
    // Add Projection Data if valid
    if (projection.value && projection.value.days > 0) {
        const balance = parseFloat(selectedAccount.value.saldo_actual);
        const annualRate = parseFloat(selectedAccount.value.tasa_rendimiento_anual);
        const dailyRate = (annualRate / 100) / 365;
        
        const projData = new Array(labels.length).fill(null);
        
        // Connect the projection line from the last historical point
        const lastHistoricalValue = data[data.length - 1];
        projData[labels.length - 1] = lastHistoricalValue;
        
        // Plot every consecutive day for the projection
        for (let currentDays = 1; currentDays <= projection.value.days; currentDays++) {
            const futureDate = new Date();
            futureDate.setDate(futureDate.getDate() + currentDays);
            
            // Format to DD/MM/YYYY to match historical
            const day = String(futureDate.getDate()).padStart(2, '0');
            const month = String(futureDate.getMonth() + 1).padStart(2, '0');
            const year = futureDate.getFullYear();
            labels.push(`${day}/${month}/${year}`);
            
            // Calculate the daily yield at this future point
            // Balance at day N = P * (1 + r)^N
            // Yield for day N = Balance at day N * r
            const futureBalance = balance * Math.pow(1 + dailyRate, currentDays);
            const futureDailyYield = futureBalance * dailyRate;
            
            data.push(null); // Keep historical data null for future points
            projData.push(futureDailyYield);
        }
        
        datasets.push({
            label: 'Proyección Diaria',
            data: projData,
            borderColor: '#6366f1',
            backgroundColor: 'rgba(99, 102, 241, 0.1)',
            borderDash: [5, 5],
            fill: true,
            tension: 0.4,
            pointRadius: 4,
            pointBackgroundColor: '#6366f1'
        });
    }
    
    return { labels, datasets };
});

const chartOptions = computed(() => {
    const textColor = getCssVar('--text-secondary') || '#94a3b8';
    const gridColor = theme.value === 'dark' ? 'rgba(255,255,255,0.05)' : 'rgba(0,0,0,0.05)';

    return {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: { display: false },
            tooltip: {
                callbacks: {
                    label: (context) => `Rendimiento: ${formatCurrency(context.parsed.y)}`
                }
            }
        },
        scales: {
            x: {
                grid: { display: false },
                ticks: { color: textColor, maxRotation: 45, minRotation: 45 }
            },
            y: {
                grid: { color: gridColor },
                ticks: { color: textColor }
            }
        }
    };
});

const getCssVar = (name) => {
    return typeof window !== 'undefined' ? getComputedStyle(document.documentElement).getPropertyValue(name).trim() : '';
};

// Projection Logic
const today = new Date().toISOString().split('T')[0];
const projectionDate = ref(today);
const isGlobalProjection = ref(false);

const projection = computed(() => {
    if (!selectedAccount.value) return null;
    
    const balance = parseFloat(selectedAccount.value.saldo_actual);
    const annualRate = parseFloat(selectedAccount.value.tasa_rendimiento_anual);
    
    if (!balance || !annualRate) return null;

    const start = new Date();
    const end = new Date(projectionDate.value);
    const diffTime = Math.max(0, end - start);
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    
    // Compound interest formula (Daily)
    // A = P(1 + r/n)^nt
    // Here n = 365, t = diffDays/365 -> nt = diffDays
    const dailyRate = (annualRate / 100) / 365;
    const futureValue = balance * Math.pow(1 + dailyRate, diffDays);
    
    return {
        days: diffDays,
        total: futureValue,
        profit: futureValue - balance
    };
});

// Tasas History Logic
const showTasasModal = ref(false);
const accountTasas = ref([]);
const isLoadingTasas = ref(false);
const isAddingTasa = ref(false);
const isDeletingTasa = ref(null);
const newTasaForm = reactive({
    tasa_anual: null,
    fecha_inicio: ''
});

const openTasasHistory = async (row) => {
    selectedAccount.value = row;
    showTasasModal.value = true;
    newTasaForm.tasa_anual = null;
    newTasaForm.fecha_inicio = today;
    await fetchTasasHistory();
};

const fetchTasasHistory = async () => {
    if (!selectedAccount.value) return;
    isLoadingTasas.value = true;
    try {
        const response = await api.finanzas.getTasas(selectedAccount.value.uuid);
        accountTasas.value = response.data;
    } catch (error) {
        console.error('Error fetching tasas:', error);
        alert.toast.error('Error', 'No se pudo cargar el historial de tasas');
    } finally {
        isLoadingTasas.value = false;
    }
};

const handleAddTasa = async () => {
    if (!newTasaForm.tasa_anual || !newTasaForm.fecha_inicio) return;
    
    isAddingTasa.value = true;
    try {
        const response = await api.finanzas.storeTasa(selectedAccount.value.uuid, {
            tasa_anual: newTasaForm.tasa_anual,
            fecha_inicio: newTasaForm.fecha_inicio
        });
        
        const rb = response.data.rebalance;
        const rbMsg = rb && rb.corrections_count > 0 
            ? `. Se aplicaron ${rb.corrections_count} ajustes retroactivos (${rb.total_correction >= 0 ? '+' : ''}${formatCurrency(rb.total_correction)})`
            : '';
            
        alert.toast.success('Tasa registrada', `El historial se ha actualizado${rbMsg}`);
        newTasaForm.tasa_anual = null;
        await fetchTasasHistory();
        fetchData();
    } catch (error) {
        console.error('Error adding tasa:', error);
        alert.toast.error('Error', error.response?.data?.message || 'No se pudo añadir la tasa');
    } finally {
        isAddingTasa.value = false;
    }
};

const handleDeleteTasa = async (tasaId) => {
    if (!confirm('¿Estás seguro de eliminar esta tasa histórica? Se recalcularán los rendimientos de forma automática.')) return;
    
    isDeletingTasa.value = tasaId;
    try {
        const response = await api.finanzas.deleteTasa(selectedAccount.value.uuid, tasaId);
        
        const rb = response.data.rebalance;
        const rbMsg = rb && rb.corrections_count > 0 
            ? `. Se aplicaron ${rb.corrections_count} correcciones (${rb.total_correction >= 0 ? '+' : ''}${formatCurrency(rb.total_correction)})`
            : '';

        alert.toast.success('Tasa eliminada', `El historial se ha actualizado${rbMsg}`);
        await fetchTasasHistory();
        fetchData();
    } catch (error) {
        console.error('Error deleting tasa:', error);
        alert.toast.error('Error', error.response?.data?.message || 'No se pudo eliminar la tasa');
    } finally {
        isDeletingTasa.value = null;
    }
};

// Actions
const isCalculatingYield = ref(null);

const handleManualYield = async (row) => {
    isCalculatingYield.value = row.uuid;
    try {
        // Step 1: Silently rebalance past yields (corrects backdated movements)
        let rebalanceCorrections = 0;
        let rebalanceTotal = 0;
        try {
            const rbRes = await api.finanzas.rebalanceYields(row.uuid);
            rebalanceCorrections = rbRes.data.corrections_count ?? 0;
            rebalanceTotal = rbRes.data.total_correction ?? 0;
        } catch (_) {
            // Rebalance errors are non-critical; continue to yield calculation
        }

        // Step 2: Calculate today's yield
        try {
            const response = await api.finanzas.calculateYield(row.uuid);
            const sign = rebalanceTotal >= 0 ? '+' : '';
            const rebalanceMsg = rebalanceCorrections > 0
                ? ` | Ajuste histórico: ${sign}${formatCurrency(rebalanceTotal)}`
                : '';
            alert.toast.success(
                'Rendimiento Aplicado',
                `+${formatCurrency(response.data.yield)} añadido a tu cuenta.${rebalanceMsg}`
            );
        } catch (yieldError) {
            // calculateYield returns 400 when yield is already covered for today.
            // If rebalance made corrections, that IS the good news — show it.
            if (rebalanceCorrections > 0) {
                const sign = rebalanceTotal >= 0 ? '+' : '';
                alert.toast.success(
                    'Ajuste Histórico Aplicado',
                    `${rebalanceCorrections} corrección(es) de rendimiento: ${sign}${formatCurrency(rebalanceTotal)}`
                );
            } else {
                const message = yieldError.response?.data?.message || 'No se pudo calcular el rendimiento';
                alert.toast.info('Info', message);
            }
        }

        fetchData();
    } finally {
        isCalculatingYield.value = null;
    }
};

const handleViewGlobalProjection = () => {
    handleViewProjection(null);
};

const handleViewProjection = async (row) => {
    if (row) {
        selectedAccount.value = row;
        isGlobalProjection.value = false;
    } else {
        isGlobalProjection.value = true;
        // Current total sum
        const totalBalance = (accounts.value || []).reduce((acc, c) => acc + parseFloat(c.saldo_actual), 0);
        selectedAccount.value = {
            nombre: 'Patrimonio Global',
            banco: 'Consolidado de cuentas',
            saldo_actual: totalBalance
        };
    }

    showProyeccionModal.value = true;
    loadingProjection.value = true;
    projectionViewMode.value = 'chart';
    projectionData.value = [];

    try {
        const response = isGlobalProjection.value 
            ? await api.finanzas.getProyeccionGeneralAhorro({ include_credit_cards: includeCreditCards.value ? 1 : 0 })
            : await api.finanzas.getCuentaProyeccion(selectedAccount.value.uuid);
            
        projectionData.value = response.data || [];
        loadingProjection.value = false;
        
        await nextTick();
        setTimeout(() => {
            renderProjectionChart();
        }, 100);
    } catch (e) {
        console.error('Error in projection:', e);
        alert.toast.error('Error', 'No se pudo cargar la proyección.');
        loadingProjection.value = false;
    }
};

const handleViewMonthDetails = (data) => {
    selectedMonthDetails.value = data;
    projectionViewMode.value = 'details';
};

const expandedItems = ref(new Set());
const toggleItemExpansion = (monthKey, itemIdx, occurrences) => {
    if (occurrences <= 1) return;
    const key = `${monthKey}-${itemIdx}`;
    if (expandedItems.value.has(key)) {
        expandedItems.value.delete(key);
    } else {
        expandedItems.value.add(key);
    }
};

// Re-render chart when switching back from details to chart view
watch(projectionViewMode, async (newVal) => {
    if (newVal === 'chart') {
        await nextTick();
        renderProjectionChart();
    }
});

watch(includeCreditCards, () => {
    if (showProyeccionModal.value && isGlobalProjection.value) {
        handleViewProjection(null);
    }
});

const renderProjectionChart = () => {
    if (!projectionChartRef.value || projectionData.value.length === 0) return;
    
    if (projectionChartInstance) {
        projectionChartInstance.destroy();
        projectionChartInstance = null;
    }

    const style = getComputedStyle(document.documentElement);
    const primaryRGB = style.getPropertyValue('--primary-rgb').trim() || '59, 130, 246';
    const isDark = theme.value === 'dark';
    const textColor = isDark ? '#94a3b8' : '#64748b';
    const gridColor = isDark ? 'rgba(255, 255, 255, 0.05)' : 'rgba(0, 0, 0, 0.05)';

    const canvas = projectionChartRef.value;
    const ctx = canvas.getContext('2d');

    // Gradient for the balance line area
    const gradient = ctx.createLinearGradient(0, 0, 0, 400);
    gradient.addColorStop(0, `rgba(${primaryRGB}, 0.2)`);
    gradient.addColorStop(1, `rgba(${primaryRGB}, 0.0)`);

    const labels = projectionData.value.map(d => d.label);
    const balanceData = projectionData.value.map(d => d.saldo_final);
    const netFlowData = projectionData.value.map(d => d.neto);

    projectionChartInstance = new ChartJS(ctx, {
        type: 'bar',
        plugins: [{
            id: 'topLabels',
            afterDatasetsDraw(chart) {
                const { ctx, data } = chart;
                ctx.save();
                ctx.font = 'bold 11px "Inter", sans-serif';
                ctx.fillStyle = isDark ? 'rgba(255, 255, 255, 0.7)' : 'rgba(15, 23, 42, 0.7)';
                ctx.textAlign = 'left';
                ctx.textBaseline = 'middle';

                const formatCompact = (val) => {
                    if (Math.abs(val) >= 1000000) return (val / 1000000).toFixed(1) + 'M';
                    if (Math.abs(val) >= 1000) return (val / 1000).toFixed(1) + 'k';
                    return Math.round(val);
                };

                // Labels for net flow bars
                chart.getDatasetMeta(1).data.forEach((bar, index) => {
                    const value = data.datasets[1].data[index];
                    if (Math.abs(value) > 10) {
                        const text = (value >= 0 ? '+' : '') + formatCompact(value);
                        ctx.save();
                        ctx.translate(bar.x, (value >= 0 ? bar.y - 10 : bar.y + 10));
                        ctx.rotate(-Math.PI / 2);
                        ctx.fillText(text, 0, 0);
                        ctx.restore();
                    }
                });
                ctx.restore();
            }
        }],
        data: {
            labels,
            datasets: [
                {
                    label: 'Saldo Proyectado',
                    type: 'line',
                    data: balanceData,
                    borderColor: `rgb(${primaryRGB})`,
                    backgroundColor: gradient,
                    fill: true,
                    tension: 0.4,
                    pointRadius: 4,
                    pointHoverRadius: 6,
                    yAxisID: 'y'
                },
                {
                    label: 'Flujo Neto Mensual',
                    type: 'bar',
                    data: netFlowData,
                    backgroundColor: projectionData.value.map(d => d.neto >= 0 ? 'rgba(16, 185, 129, 0.3)' : 'rgba(239, 68, 68, 0.3)'),
                    borderColor: projectionData.value.map(d => d.neto >= 0 ? '#10b981' : '#ef4444'),
                    borderWidth: 1,
                    borderRadius: 4,
                    yAxisID: 'y1'
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            layout: {
                padding: { top: 35, right: 10 }
            },
            interaction: {
                mode: 'index',
                intersect: false,
            },
            plugins: {
                legend: {
                    position: 'top',
                    labels: { color: textColor, font: { weight: '600' } }
                },
                tooltip: {
                    backgroundColor: isDark ? '#1e293b' : '#ffffff',
                    titleColor: isDark ? '#ffffff' : '#1e293b',
                    bodyColor: isDark ? '#cbd5e1' : '#475569',
                    borderColor: isDark ? '#334155' : '#e2e8f0',
                    borderWidth: 1,
                    padding: 12,
                    callbacks: {
                        label: (context) => {
                            let label = context.dataset.label || '';
                            if (label) label += ': ';
                            label += formatCurrency(context.parsed.y);
                            return label;
                        }
                    }
                }
            },
            scales: {
                y: {
                    position: 'left',
                    grid: { color: gridColor },
                    ticks: {
                        color: textColor,
                        callback: (value) => formatCurrency(value)
                    },
                    title: { display: true, text: 'Saldo Total', color: textColor }
                },
                y1: {
                    position: 'right',
                    grid: { drawOnChartArea: false },
                    ticks: {
                        color: textColor,
                        callback: (value) => formatCurrency(value)
                    },
                    title: { display: true, text: 'Flujo Neto', color: textColor }
                },
                x: {
                    grid: { display: false },
                    ticks: { color: textColor, maxRotation: 45, minRotation: 45 }
                }
            },
            onClick: (event, elements) => {
                if (elements.length > 0) {
                    const index = elements[0].index;
                    const data = projectionData.value[index];
                    if (data) {
                        handleViewMonthDetails(data);
                    }
                }
            }
        }
    });
};

const generatePDF = async () => {
    if (!projectionData.value.length) return;

    alert.showLoading('Generando reporte PDF...', 'Por favor espera un momento.');

    try {
        if (projectionViewMode.value !== 'chart') {
            projectionViewMode.value = 'chart';
            await nextTick();
            await new Promise(r => setTimeout(r, 500));
        }

        const { jsPDF } = await import('jspdf');
        const autoTable = (await import('jspdf-autotable')).default || (await import('jspdf-autotable'));
        const doc = new jsPDF('p', 'mm', 'a4');
        const pageWidth = doc.internal.pageSize.getWidth();
        const margin = 15;

        // 1. Header
        doc.setFillColor(15, 23, 42); // Midnight Blue
        doc.rect(0, 0, pageWidth, 40, 'F');
        
        doc.setTextColor(255, 255, 255);
        doc.setFontSize(22);
        doc.setFont('helvetica', 'bold');
        doc.text('REPORTE DE PROYECCIÓN DE SALDO', margin, 20);
        
        doc.setFontSize(10);
        doc.setFont('helvetica', 'normal');
        doc.text(`${selectedAccount.value?.nombre} • ${selectedAccount.value?.banco}`, margin, 28);
        doc.text(`Generado el: ${new Date().toLocaleString('es-MX')}`, margin, 34);

        let currentY = 55;

        // 2. Executive Summary
        doc.setTextColor(15, 23, 42);
        doc.setFontSize(14);
        doc.setFont('helvetica', 'bold');
        doc.text('RESUMEN EJECUTIVO', margin, currentY);
        currentY += 10;

        const summaryData = [
            ['Saldo Inicial:', formatCurrency(selectedAccount.value?.saldo_actual || 0)],
            ['Tasa de Rendimiento:', `${selectedAccount.value?.tasa_rendimiento_anual || 0}% Anual`],
            ['Proyección a 24 Meses:', formatCurrency(projectionData.value[projectionData.value.length - 1]?.saldo_final || 0)],
            ['Crecimiento Neto Estimado:', formatCurrency(projectionData.value[projectionData.value.length - 1]?.saldo_final - selectedAccount.value?.saldo_actual)]
        ];

        autoTable(doc, {
            startY: currentY,
            body: summaryData,
            theme: 'plain',
            styles: { fontSize: 10, cellPadding: 2 },
            columnStyles: { 0: { fontStyle: 'bold', width: 60 } }
        });

        currentY = doc.lastAutoTable.finalY + 15;

        // 3. Chart
        const chartCanvas = projectionChartRef.value;
        const chartImg = chartCanvas.toDataURL('image/png', 1.0);
        
        doc.setFontSize(14);
        doc.text('VISUALIZACIÓN DE CRECIMIENTO', margin, currentY);
        currentY += 5;

        const imgWidth = pageWidth - (margin * 2);
        const imgHeight = (chartCanvas.height * imgWidth) / chartCanvas.width;
        
        doc.setFillColor(15, 23, 42);
        doc.roundedRect(margin, currentY, imgWidth, imgHeight, 3, 3, 'F');
        doc.addImage(chartImg, 'PNG', margin, currentY, imgWidth, imgHeight);
        
        currentY += imgHeight + 20;

        // 4. Detailed Table
        if (currentY > 240) { doc.addPage(); currentY = 20; }
        
        doc.setFontSize(14);
        doc.text('DETALLE MENSUAL PROYECTADO', margin, currentY);
        currentY += 5;

        const tableBody = projectionData.value.map(item => [
            item.label,
            formatCurrency(item.saldo_inicial),
            { content: (item.neto >= 0 ? '+' : '') + formatCurrency(item.neto), styles: { textColor: item.neto >= 0 ? [16, 185, 129] : [239, 68, 68] } },
            formatCurrency(item.saldo_final)
        ]);

        autoTable(doc, {
            startY: currentY,
            head: [['Mes', 'Saldo Inicial', 'Flujo Neto', 'Saldo Final']],
            body: tableBody,
            styles: { fontSize: 8, cellPadding: 3, textColor: [51, 65, 85] },
            headStyles: { fillColor: [15, 23, 42], textColor: 255, fontStyle: 'bold' },
            alternateRowStyles: { fillColor: [248, 250, 252] },
            columnStyles: { 
                1: { halign: 'right' },
                2: { halign: 'right', fontStyle: 'bold' },
                3: { halign: 'right', fontStyle: 'bold' }
            }
        });

        doc.save(`Proyeccion_${selectedAccount.value?.nombre}_${new Date().toISOString().split('T')[0]}.pdf`);
        alert.toast.success('¡Éxito!', 'Reporte generado correctamente.');
    } catch (e) {
        console.error(e);
        alert.toast.error('Error', 'No se pudo generar el PDF.');
    } finally {
        alert.closeLoading();
    }
};

const handleRequestData = (params) => {
    fetchData(params);
};
</script>
