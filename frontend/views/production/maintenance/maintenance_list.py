from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableView, QHeaderView, QLineEdit, QComboBox, QFrame,
    QMessageBox, QMenu, QDialog, QFormLayout, QDialogButtonBox,
    QAbstractItemView, QSplitter, QToolBar, QStatusBar, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal, QSortFilterProxyModel, QThread, QSize
from PyQt6.QtGui import QIcon, QAction, QStandardItemModel, QStandardItem, QFont, QColor
from utils.theme import Theme

class MaintenanceListView(QWidget):
    """Vista de listado de registros de mantenimiento"""

    # Señales
    maintenance_selected = pyqtSignal(int)  # Emitida cuando se selecciona un registro

    def __init__(self, api_client):
        super().__init__()
        from utils.theme import Theme
        Theme.apply_window_light_theme(self)

        self.api_client = api_client

        # Conectar señales del cliente API
        self.api_client.data_received.connect(self.on_data_loaded)
        self.api_client.request_error.connect(self.on_request_error)

        # Modelo para la tabla
        self.maintenance_model = QStandardItemModel()
        self.maintenance_model.setHorizontalHeaderLabels([
            "ID", "Activo", "Tipo", "Fecha", "Descripción", "Costo", "Técnico", "ID Activo", "ID Empleado"
        ])

        # Modelo proxy para filtrado
        self.proxy_model = QSortFilterProxyModel()
        self.proxy_model.setSourceModel(self.maintenance_model)
        self.proxy_model.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.proxy_model.setFilterKeyColumn(-1)  # Buscar en todas las columnas

        self.init_ui()

        # Cargar datos iniciales
        self.refresh_data()

    def init_ui(self):
        """Inicializa la interfaz de usuario"""
        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # Título de sección
        title_label = QLabel("Gestión de Mantenimiento")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        main_layout.addWidget(title_label)

        # Barra de herramientas
        toolbar_layout = QHBoxLayout()

        # Filtro de tipo
        self.type_filter = QComboBox()
        self.type_filter.addItem("Todos los tipos", "")
        self.type_filter.addItem("Preventivo", "preventivo")
        self.type_filter.addItem("Correctivo", "correctivo")
        self.type_filter.currentIndexChanged.connect(self.on_filter_changed)

        # Campo de búsqueda
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Buscar por activo o descripción...")
        self.search_input.textChanged.connect(self.on_search_changed)

        # Botón de búsqueda
        search_btn = QPushButton("Buscar")
        search_btn.clicked.connect(self.on_filter_changed)

        # Botón para añadir
        self.add_btn = QPushButton("Nuevo Registro")
        self.add_btn.setIcon(QIcon("resources/icons/add.png"))
        self.add_btn.clicked.connect(self.on_add_maintenance)

        # Botón de actualizar
        self.refresh_btn = QPushButton("Actualizar")
        self.refresh_btn.setIcon(QIcon("resources/icons/refresh.png"))
        self.refresh_btn.clicked.connect(self.refresh_data)

        # Agregar widgets a la barra de herramientas
        toolbar_layout.addWidget(QLabel("Filtrar por tipo:"))
        toolbar_layout.addWidget(self.type_filter)
        toolbar_layout.addWidget(self.search_input)
        toolbar_layout.addWidget(search_btn)
        toolbar_layout.addStretch()
        toolbar_layout.addWidget(self.add_btn)
        toolbar_layout.addWidget(self.refresh_btn)

        main_layout.addLayout(toolbar_layout)

        # Tabla de mantenimiento
        self.maintenance_table = QTableView()
        self.maintenance_table.setModel(self.proxy_model)
        self.maintenance_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.maintenance_table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.maintenance_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.maintenance_table.setAlternatingRowColors(True)
        self.maintenance_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.maintenance_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)  # ID
        self.maintenance_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)  # Tipo
        self.maintenance_table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)  # Costo
        self.maintenance_table.verticalHeader().setVisible(False)
        self.maintenance_table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.maintenance_table.customContextMenuRequested.connect(self.show_context_menu)
        self.maintenance_table.doubleClicked.connect(self.on_row_double_clicked)
        
        main_layout.addWidget(self.maintenance_table)

        # Estadísticas
        stats_layout = QHBoxLayout()
        self.total_label = QLabel("Total registros: <b>0</b>")
        self.preventive_label = QLabel("Preventivos: <b>0</b>")
        self.corrective_label = QLabel("Correctivos: <b>0</b>")
        self.cost_label = QLabel("Costo total: <b>$0.00</b>")

        stats_layout.addWidget(self.total_label)
        stats_layout.addWidget(self.preventive_label)
        stats_layout.addWidget(self.corrective_label)
        stats_layout.addWidget(self.cost_label)
        stats_layout.addStretch()
        main_layout.addLayout(stats_layout)

        # Barra de estado
        self.status_bar = QStatusBar()
        self.status_bar.showMessage("Sistema ERP Pirelli - Módulo de Mantenimiento v1.0")
        main_layout.addWidget(self.status_bar)

        # Ocultar columnas de IDs
        self.maintenance_table.setColumnHidden(7, True)  # ID Activo
        self.maintenance_table.setColumnHidden(8, True)  # ID Empleado

    def on_search_changed(self, text):
        """Maneja el cambio en el campo de búsqueda"""
        self.proxy_model.setFilterWildcard(text)
        self.status_bar.showMessage(f"Filtrando registros por: {text}" if text else "Listo")

    def on_filter_changed(self):
        """Maneja el cambio en los filtros"""
        filter_text = self.type_filter.currentData()
        if filter_text:
            self.proxy_model.setFilterRegularExpression(filter_text)
            self.proxy_model.setFilterKeyColumn(2)  # Columna de Tipo
        else:
            self.proxy_model.setFilterRegularExpression("")
        
        self.status_bar.showMessage(f"Filtrando por tipo: {self.type_filter.currentText()}")

    def refresh_data(self):
        """Actualiza los datos de la tabla desde la API"""
        self.status_bar.showMessage("Cargando registros de mantenimiento...")
        self.api_client.get_maintenance()

    def load_maintenance(self, maintenance_records):
        """Carga los registros de mantenimiento en la tabla"""
        from models.maintenance_model import Maintenance
        
        # Limpiar modelo actual
        self.maintenance_model.removeRows(0, self.maintenance_model.rowCount())
        
        total_cost = 0
        preventive_count = 0
        corrective_count = 0

        for record in maintenance_records:
            row = []

            # ID
            id_item = QStandardItem(str(record.id_mantenimiento))
            id_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            row.append(id_item)

            # Activo
            activo_item = QStandardItem(record.activo_nombre)
            row.append(activo_item)

            # Tipo
            tipo_item = QStandardItem(record.get_tipo_display())
            if record.tipo == "preventivo":
                tipo_item.setForeground(QColor(Theme.INFO_COLOR))
                preventive_count += 1
            else:
                tipo_item.setForeground(QColor(Theme.WARNING_COLOR))
                corrective_count += 1
            row.append(tipo_item)

            # Fecha
            fecha_item = QStandardItem(record.fecha)
            fecha_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            row.append(fecha_item)

            # Descripción
            desc_item = QStandardItem(record.descripcion_display)
            row.append(desc_item)

            # Costo
            costo_item = QStandardItem(record.get_costo_display())
            costo_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            total_cost += record.costo
            row.append(costo_item)

            # Técnico
            tecnico_item = QStandardItem(record.empleado_nombre or "No asignado")
            row.append(tecnico_item)

            # IDs ocultos
            id_activo_item = QStandardItem(str(record.id_activo))
            row.append(id_activo_item)

            id_empleado_item = QStandardItem(str(record.id_empleado) if record.id_empleado else "")
            row.append(id_empleado_item)

            self.maintenance_model.appendRow(row)

        # Actualizar estadísticas
        total = len(maintenance_records)
        self.total_label.setText(f"Total registros: <b>{total}</b>")
        self.preventive_label.setText(f"Preventivos: <b>{preventive_count}</b>")
        self.corrective_label.setText(f"Correctivos: <b>{corrective_count}</b>")
        self.cost_label.setText(f"Costo total: <b>${total_cost:,.2f}</b>")
        self.status_bar.showMessage(f"Cargados {total} registros de mantenimiento")

    def on_data_loaded(self, data):
        """Maneja los datos cargados desde la API"""
        if data.get("type") == "maintenance":
            from models.maintenance_model import Maintenance
            records = [Maintenance.from_dict(item) for item in data.get("data", [])]
            self.load_maintenance(records)
        elif data.get("type") == "maintenance_created":
            QMessageBox.information(self, "Éxito", "Registro de mantenimiento creado correctamente")
            self.refresh_data()
        elif data.get("type") == "maintenance_updated":
            QMessageBox.information(self, "Éxito", "Registro de mantenimiento actualizado correctamente")
            self.refresh_data()
        elif data.get("type") == "maintenance_deleted":
            QMessageBox.information(self, "Éxito", "Registro de mantenimiento eliminado correctamente")
            self.refresh_data()

    def on_request_error(self, error_message):
        """Maneja errores de la API"""
        QMessageBox.critical(self, "Error", f"Error al cargar registros: {error_message}")
        self.status_bar.showMessage(f"Error: {error_message}")

    def on_row_double_clicked(self, index):
        """Maneja el doble clic en una fila"""
        mapped_index = self.proxy_model.mapToSource(index)
        row = mapped_index.row()
        record_id = int(self.maintenance_model.item(row, 0).text())
        self.maintenance_selected.emit(record_id)
        self.on_view_maintenance(record_id)

    def show_context_menu(self, position):
        """Muestra menú contextual para una fila"""
        index = self.maintenance_table.indexAt(position)
        if not index.isValid():
            return

        context_menu = QMenu(self)
        view_action = QAction(QIcon("resources/icons/view.png"), "Ver detalles", self)
        edit_action = QAction(QIcon("resources/icons/edit.png"), "Editar", self)
        delete_action = QAction(QIcon("resources/icons/delete.png"), "Eliminar", self)
        report_action = QAction(QIcon("resources/icons/report.png"), "Generar reporte", self)

        context_menu.addAction(view_action)
        context_menu.addAction(edit_action)
        context_menu.addSeparator()
        context_menu.addAction(report_action)
        context_menu.addSeparator()
        context_menu.addAction(delete_action)

        mapped_index = self.proxy_model.mapToSource(index)
        row = mapped_index.row()
        record_id = int(self.maintenance_model.item(row, 0).text())

        view_action.triggered.connect(lambda: self.on_view_maintenance(record_id))
        edit_action.triggered.connect(lambda: self.on_edit_maintenance(record_id))
        delete_action.triggered.connect(lambda: self.on_delete_maintenance(record_id))
        report_action.triggered.connect(lambda: self.on_generate_report(record_id))

        context_menu.exec(self.maintenance_table.viewport().mapToGlobal(position))

    def on_view_maintenance(self, record_id):
        """Muestra detalles de un registro de mantenimiento"""
        from .maintenance_detail import MaintenanceDetailView
        
        # Buscar el registro en el modelo
        record = self._get_record_by_id(record_id)
        if record:
            dialog = MaintenanceDetailView(self.api_client, record.to_dict())
            dialog.exec()
        else:
            QMessageBox.warning(self, "Error", "No se encontró el registro seleccionado")

    def on_add_maintenance(self):
        """Abre el formulario para añadir un nuevo registro"""
        from .maintenance_form import MaintenanceForm
        dialog = MaintenanceForm(self.api_client)
        dialog.maintenance_saved.connect(self._handle_maintenance_save)
        dialog.exec()

    def on_edit_maintenance(self, record_id):
        """Abre el formulario de edición de un registro"""
        record = self._get_record_by_id(record_id)
        if record:
            self._show_edit_form(record)
        else:
            QMessageBox.warning(self, "Error", "No se pudo cargar el registro")

    def _get_record_by_id(self, record_id):
        """Busca un registro por su ID en el modelo actual"""
        for row in range(self.maintenance_model.rowCount()):
            if int(self.maintenance_model.item(row, 0).text()) == record_id:
                from models.maintenance_model import Maintenance
                
                record_data = {
                    "id_mantenimiento": self.maintenance_model.item(row, 0).text(),
                    "id_activo": self.maintenance_model.item(row, 7).text(),
                    "activo_nombre": self.maintenance_model.item(row, 1).text(),
                    "tipo": self.maintenance_model.item(row, 2).text().lower(),
                    "fecha": self.maintenance_model.item(row, 3).text(),
                    "descripcion": self.maintenance_model.item(row, 4).text(),
                    "costo": self.maintenance_model.item(row, 5).text().replace("$", "").replace(",", ""),
                    "id_empleado": self.maintenance_model.item(row, 8).text(),
                    "empleado_nombre": self.maintenance_model.item(row, 6).text()
                }
                return Maintenance.from_dict(record_data)
        return None

    def _show_edit_form(self, record):
        """Muestra el formulario de edición con los datos del registro"""
        from .maintenance_form import MaintenanceForm
        if record:
            dialog = MaintenanceForm(self.api_client, record.to_dict())
            dialog.maintenance_saved.connect(self._handle_maintenance_save)
            dialog.exec()
        else:
            QMessageBox.warning(self, "Error", "No se pudo cargar el registro")

    def _handle_maintenance_save(self, maintenance_data):
        """Maneja el guardado de un registro (nuevo o editado)"""
        if "id_mantenimiento" in maintenance_data and maintenance_data["id_mantenimiento"]:
            # Actualizar registro
            self.api_client.update_maintenance(maintenance_data["id_mantenimiento"], maintenance_data)
            self.status_bar.showMessage(f"Actualizando registro ID: {maintenance_data['id_mantenimiento']}...")
        else:
            # Crear registro
            self.api_client.create_maintenance(maintenance_data)
            self.status_bar.showMessage("Creando nuevo registro de mantenimiento...")

    def on_delete_maintenance(self, record_id):
        """Elimina un registro de mantenimiento"""
        reply = QMessageBox.question(
            self,
            "Confirmar eliminación",
            f"¿Está seguro que desea eliminar el registro ID: {record_id}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.api_client.delete_maintenance(record_id)
            self.status_bar.showMessage(f"Eliminando registro ID: {record_id}...")

    def on_generate_report(self, record_id):
        """Genera un reporte del registro de mantenimiento"""
        record = self._get_record_by_id(record_id)
        if record:
            self.status_bar.showMessage(f"Generando reporte para registro ID: {record_id}...")
            # Aquí iría la lógica para generar el reporte
            QMessageBox.information(self, "Reporte", f"Reporte generado para el registro {record_id}")