from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableView, QHeaderView, QLineEdit, QComboBox, QFrame,
    QMessageBox, QMenu, QDialog, QFormLayout, QDialogButtonBox,
    QAbstractItemView, QSplitter, QToolBar, QStatusBar, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal, QSortFilterProxyModel, QThread, QSize
from PyQt6.QtGui import QIcon, QAction, QStandardItemModel, QStandardItem, QFont, QColor
from utils.theme import Theme

class ProductionAssetListView(QWidget):
    """Vista de listado de activos de producción para ERP Pirelli"""

    # Señales
    asset_selected = pyqtSignal(int)  # Emitida cuando se selecciona un activo

    def __init__(self, api_client):
        super().__init__()
        from utils.theme import Theme
        Theme.apply_window_light_theme(self)

        self.api_client = api_client

        # Conectar señals del cliente API
        self.api_client.data_received.connect(self.on_data_loaded)
        self.api_client.request_error.connect(self.on_request_error)

        # Modelo para la tabla
        self.asset_model = QStandardItemModel()
        self.asset_model.setHorizontalHeaderLabels([
            "ID", "Nombre", "Tipo", "Área", "Fecha Adquisición", "Estado"
        ])

        # Modelo proxy para filtrado avanzado
        self.proxy_model = QSortFilterProxyModel()
        self.proxy_model.setSourceModel(self.asset_model)
        self.proxy_model.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.proxy_model.setFilterKeyColumn(-1)  # Buscar en todas las columnas
        self.setup_filter_proxy()

        self.init_ui()
        self.refresh_data()

    def init_ui(self):
        """Inicializa la interfaz de usuario"""
        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # Título de sección
        title_label = QLabel("Gestión de Activos de Producción")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        main_layout.addWidget(title_label)

        # Barra de herramientas
        toolbar_layout = QHBoxLayout()

        # Filtro de tipo
        self.type_filter = QComboBox()
        self.type_filter.addItem("Todos los tipos", "")
        self.type_filter.addItem("Maquinaria", "maquinaria")
        self.type_filter.addItem("Herramienta", "herramienta")
        self.type_filter.addItem("Equipo", "equipo")
        self.type_filter.currentIndexChanged.connect(self.on_type_changed)

        # Filtro de estado
        self.status_filter = QComboBox()
        self.status_filter.addItem("Todos", "")
        self.status_filter.addItem("Operativo", "operativo")
        self.status_filter.addItem("En Mantenimiento", "mantenimiento")
        self.status_filter.addItem("Dado de Baja", "baja")
        self.status_filter.currentIndexChanged.connect(self._on_filters_changed)

        # Campo de búsqueda
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Buscar por nombre...")
        self.search_input.textChanged.connect(self.on_search_changed)

        # Botón de búsqueda
        search_btn = QPushButton("Buscar")
        search_btn.clicked.connect(self._on_filters_changed)

        # Botón para añadir
        self.add_btn = QPushButton("Nuevo Activo")
        self.add_btn.setIcon(QIcon("resources/icons/add.png"))
        self.add_btn.clicked.connect(self.on_add_asset)

        # Botón de actualizar
        self.refresh_btn = QPushButton("Actualizar")
        self.refresh_btn.setIcon(QIcon("resources/icons/refresh.png"))
        self.refresh_btn.clicked.connect(self.refresh_data)

        # Agregar widgets a la barra de herramientas
        toolbar_layout.addWidget(QLabel("Filtrar por tipo:"))
        toolbar_layout.addWidget(self.type_filter)
        toolbar_layout.addWidget(QLabel("Estado:"))
        toolbar_layout.addWidget(self.status_filter)
        toolbar_layout.addWidget(self.search_input)
        toolbar_layout.addWidget(search_btn)
        toolbar_layout.addStretch()
        toolbar_layout.addWidget(self.add_btn)
        toolbar_layout.addWidget(self.refresh_btn)

        main_layout.addLayout(toolbar_layout)

        # Tabla de activos
        self.asset_table = QTableView()
        self.asset_table.setModel(self.proxy_model)
        self.asset_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.asset_table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.asset_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.asset_table.setAlternatingRowColors(True)
        self.asset_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.asset_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)  # ID
        self.asset_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)  # Fecha
        self.asset_table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)  # Estado
        self.asset_table.verticalHeader().setVisible(False)
        self.asset_table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.asset_table.customContextMenuRequested.connect(self.show_context_menu)
        self.asset_table.doubleClicked.connect(self.on_row_double_clicked)
        
        main_layout.addWidget(self.asset_table)

        # Labels de totales
        summary_layout = QHBoxLayout()
        self.total_label = QLabel("Total de activos: <b>0</b>")
        self.operational_label = QLabel("Activos operativos: <b>0</b>")
        self.maintenance_label = QLabel("En mantenimiento: <b>0</b>")

        summary_layout.addWidget(self.total_label)
        summary_layout.addSpacing(30)
        summary_layout.addWidget(self.operational_label)
        summary_layout.addSpacing(30)
        summary_layout.addWidget(self.maintenance_label)
        summary_layout.addStretch()
        main_layout.addLayout(summary_layout)

        # Barra de estado
        self.status_bar = QStatusBar()
        self.status_bar.showMessage("Sistema ERP Pirelli - Módulo de Activos de Producción v1.0")
        main_layout.addWidget(self.status_bar)

    def setup_filter_proxy(self):
        """Configura el modelo proxy para filtrado avanzado"""
        self.proxy_model.filterAcceptsRow = self._filter_accepts_row
    
    def _filter_accepts_row(self, source_row, source_parent):
        """Método personalizado para determinar si una fila cumple con los filtros"""
        model = self.asset_model
        
        # Obtener valores de los filtros
        search_text = self.search_input.text().strip().lower()
        asset_type = self.type_filter.currentData()
        status = self.status_filter.currentData()
        
        # Si no hay filtros activos, mostrar todas las filas
        if not search_text and not asset_type and not status:
            return True
            
        # Obtener valores de la fila actual
        try:
            nombre = model.item(source_row, 1).text().lower()
            tipo = model.item(source_row, 2).text().lower()
            estado = model.item(source_row, 5).text().lower()
            
            # Filtro de búsqueda (nombre)
            if search_text and search_text not in nombre:
                return False
                
            # Filtro de tipo
            if asset_type and asset_type != tipo:
                return False
                
            # Filtro de estado
            if status and status not in estado.lower():
                return False
                
            return True
        except (AttributeError, IndexError):
            return True

    def on_search_changed(self, text):
        """Maneja el cambio en el campo de búsqueda"""
        self.proxy_model.setFilterWildcard(text)
        self.proxy_model.invalidateFilter()
        self.status_bar.showMessage(f"Filtrando activos por: {text}" if text else "Sistema ERP Pirelli - Módulo de Activos de Producción v1.0")

    def on_type_changed(self, index):
        """Maneja el cambio en el filtro de tipo"""
        self._on_filters_changed()

    def _on_filters_changed(self):
        """Se llama cuando cambia tipo o estado, para actualizar el filtrado"""
        self.proxy_model.invalidateFilter()
        asset_type = self.type_filter.currentData()
        status = self.status_filter.currentData()
        
        msg = "Mostrando activos"
        if asset_type:
            msg += f" de tipo: {self.type_filter.currentText()}"
        if status:
            msg += f" con estado: {self.status_filter.currentText()}"
        if not asset_type and not status:
            msg = "Sistema ERP Pirelli - Módulo de Activos de Producción v1.0"
            
        self.status_bar.showMessage(msg)

    def clear_filters(self):
        """Limpia todos los filtros aplicados"""
        self.search_input.clear()
        self.type_filter.setCurrentIndex(0)
        self.status_filter.setCurrentIndex(0)
        self.proxy_model.invalidateFilter()
        self.status_bar.showMessage("Filtros eliminados")

    def refresh_data(self):
        """Actualiza los datos de la tabla desde la API"""
        self.status_bar.showMessage("Actualizando datos de activos...")
        self.api_client.get_production_assets()

    def load_assets(self, assets):
        """Carga los activos recibidos en la tabla y actualiza estadísticas"""
        self.asset_model.removeRows(0, self.asset_model.rowCount())
        count_operational = count_maintenance = 0

        for asset in assets:
            row = [
                QStandardItem(str(asset.get('id_activo'))),
                QStandardItem(asset.get('nombre', '')),
                QStandardItem(asset.get('tipo', '')),
                QStandardItem(asset.get('area_name', '')),
                QStandardItem(asset.get('fecha_adquisicion', '')),
                QStandardItem(asset.get('estado', ''))
            ]

            # Establecer alineación para ID y fecha
            row[0].setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            row[4].setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            
            # Establecer color para estado
            estado = asset.get('estado', '').lower()
            if estado == 'operativo':
                row[5].setForeground(QColor(Theme.SUCCESS_COLOR))
                count_operational += 1
            elif estado == 'mantenimiento':
                row[5].setForeground(QColor(Theme.WARNING_COLOR))
                count_maintenance += 1
            elif estado == 'baja':
                row[5].setForeground(QColor(Theme.DANGER_COLOR))
            
            row[5].setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            
            self.asset_model.appendRow(row)

        total = len(assets)
        self.total_label.setText(f"Total de activos: <b>{total}</b>")
        self.operational_label.setText(f"Activos operativos: <b>{count_operational}</b>")
        self.maintenance_label.setText(f"En mantenimiento: <b>{count_maintenance}</b>")
        self.status_bar.showMessage(f"Se han cargado {total} activos")

    def on_data_loaded(self, data):
        """Maneja los datos cargados desde la API"""
        if data.get("type") == "production_assets":
            self.load_assets(data.get("data", []))
        elif data.get("type") == "asset_created":
            QMessageBox.information(self, "Éxito", "Activo creado correctamente")
            self.refresh_data()
        elif data.get("type") == "asset_updated":
            QMessageBox.information(self, "Éxito", "Activo actualizado correctamente")
            self.refresh_data()
        elif data.get("type") == "asset_deleted":
            QMessageBox.information(self, "Éxito", "Activo eliminado correctamente")
            self.refresh_data()

    def on_request_error(self, error_message):
        """Maneja errores de la API"""
        QMessageBox.critical(self, "Error", f"Error al cargar activos: {error_message}")
        self.status_bar.showMessage(f"Error: {error_message}")

    def on_row_double_clicked(self, index):
        """Maneja el doble clic en una fila"""
        mapped_index = self.proxy_model.mapToSource(index)
        row = mapped_index.row()
        asset_id = int(self.asset_model.item(row, 0).text())
        self.asset_selected.emit(asset_id)
        self.on_view_asset(asset_id)

    def show_context_menu(self, position):
        """Muestra menú contextual para una fila"""
        index = self.asset_table.indexAt(position)
        if not index.isValid():
            return

        context_menu = QMenu(self)
        view_action = QAction(QIcon("resources/icons/view.png"), "Ver detalles", self)
        edit_action = QAction(QIcon("resources/icons/edit.png"), "Editar", self)
        delete_action = QAction(QIcon("resources/icons/delete.png"), "Eliminar", self)
        maintenance_action = QAction(QIcon("resources/icons/maintenance.png"), "Registrar mantenimiento", self)
        history_action = QAction(QIcon("resources/icons/history.png"), "Historial", self)

        context_menu.addAction(view_action)
        context_menu.addAction(edit_action)
        context_menu.addSeparator()
        context_menu.addAction(maintenance_action)
        context_menu.addSeparator()
        context_menu.addAction(history_action)
        context_menu.addSeparator()
        context_menu.addAction(delete_action)

        mapped_index = self.proxy_model.mapToSource(index)
        row = mapped_index.row()
        asset_id = int(self.asset_model.item(row, 0).text())

        view_action.triggered.connect(lambda: self.on_view_asset(asset_id))
        edit_action.triggered.connect(lambda: self.on_edit_asset(asset_id))
        delete_action.triggered.connect(lambda: self.on_delete_asset(asset_id))
        maintenance_action.triggered.connect(lambda: self.status_bar.showMessage(f"Registrando mantenimiento para activo ID: {asset_id}"))
        history_action.triggered.connect(lambda: self.status_bar.showMessage(f"Mostrando historial del activo ID: {asset_id}"))

        context_menu.exec(self.asset_table.viewport().mapToGlobal(position))

    def on_view_asset(self, asset_id):
        """Muestra detalles de un activo"""
        from .production_assets_detail import ProductionAssetDetailView
        
        # Show loading indicator in status bar
        self.status_bar.showMessage(f"Cargando detalles del activo ID: {asset_id}...")
        
        # Obtener los datos del activo directamente
        asset_data = self.api_client.get_production_asset(asset_id)
        if asset_data:
            dialog = ProductionAssetDetailView(self.api_client, asset_data, self)
            dialog.edit_requested.connect(lambda data: self.on_edit_asset(data.get("id_activo")))
            dialog.delete_requested.connect(self.on_delete_asset)
            dialog.exec()
            self.status_bar.showMessage("Sistema ERP Pirelli - Módulo de Activos de Producción v1.0", 3000)
        else:
            QMessageBox.warning(self, "Error", "No se pudieron cargar los datos del activo")
            self.status_bar.showMessage("Error al cargar detalles del activo", 3000)


    def on_add_asset(self):
        """Muestra el diálogo para añadir un nuevo activo"""
        from .production_assets_form import ProductionAssetForm
        dialog = ProductionAssetForm(self.api_client)
        dialog.asset_saved.connect(self.handle_new_asset)
        dialog.exec()

    def on_edit_asset(self, asset_id):
        """Abre el formulario de edición de un activo"""
        from .production_assets_form import ProductionAssetForm
        
        # Obtener los datos del activo directamente
        asset_data = self.api_client.get_production_asset(asset_id)
        if asset_data:
            dialog = ProductionAssetForm(self.api_client, asset_data, self)
            dialog.asset_saved.connect(self.handle_updated_asset)
            dialog.exec()
        else:
            QMessageBox.warning(self, "Error", "No se pudieron cargar los datos del activo para edición")

    def handle_new_asset(self, asset_data):
        """Maneja la creación de un nuevo activo"""
        result = self.api_client.create_production_asset(asset_data)
        if result:
            QMessageBox.information(self, "Éxito", "Activo creado correctamente")
            self.refresh_data()
        else:
            QMessageBox.warning(self, "Error", "No se pudo crear el activo")

    def handle_updated_asset(self, asset_data):
        """Maneja la actualización de un activo existente"""
        if "id_activo" in asset_data:
            result = self.api_client.update_production_asset(asset_data["id_activo"], asset_data)
            if result:
                QMessageBox.information(self, "Éxito", "Activo actualizado correctamente")
                self.refresh_data()
            else:
                QMessageBox.warning(self, "Error", "No se pudo actualizar el activo")

    def on_delete_asset(self, asset_id):
        """Elimina un activo"""
        reply = QMessageBox.question(
            self,
            "Confirmar eliminación",
            f"¿Está seguro que desea eliminar el activo ID: {asset_id}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            result = self.api_client.delete_production_asset(asset_id)
            if result:
                QMessageBox.information(self, "Éxito", "Activo eliminado correctamente")
                self.refresh_data()
            else:
                QMessageBox.warning(self, "Error", "No se pudo eliminar el activo")