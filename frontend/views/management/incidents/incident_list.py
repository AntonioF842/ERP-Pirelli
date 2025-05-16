from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableView, QHeaderView, QLineEdit, QComboBox, QFrame,
    QMessageBox, QMenu, QDialog, QFormLayout, QDialogButtonBox,
    QAbstractItemView, QSplitter, QToolBar, QStatusBar, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal, QSortFilterProxyModel, QThread, QSize
from PyQt6.QtGui import QIcon, QAction, QStandardItemModel, QStandardItem, QFont, QColor
from utils.theme import Theme

class IncidentListView(QWidget):
    """Vista de listado de incidentes para ERP Pirelli"""

    # Señales
    incident_selected = pyqtSignal(int)  # Emitida cuando se selecciona un incidente

    def __init__(self, api_client):
        super().__init__()
        from utils.theme import Theme
        Theme.apply_window_light_theme(self)

        self.api_client = api_client

        # Conectar señales del cliente API
        self.api_client.data_received.connect(self.on_data_loaded)
        self.api_client.request_error.connect(self.on_request_error)

        # Modelo para la tabla
        self.incident_model = QStandardItemModel()
        self.incident_model.setHorizontalHeaderLabels([
            "ID", "Tipo", "Descripción", "Fecha", "Área", "Reportado por", "Estado"
        ])

        # Modelo proxy para filtrado
        self.proxy_model = QSortFilterProxyModel()
        self.proxy_model.setSourceModel(self.incident_model)
        self.proxy_model.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.proxy_model.setFilterKeyColumn(-1)  # Buscar en todas las columnas

        self.init_ui()
        self.refresh_data()

    def init_ui(self):
        """Inicializa la interfaz de usuario"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # Título
        title_label = QLabel("Gestión de Incidentes")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        main_layout.addWidget(title_label)

        # Barra de herramientas
        toolbar_layout = QHBoxLayout()

        # Filtros
        self.type_filter = QComboBox()
        self.type_filter.addItem("Todos los tipos", "")
        self.type_filter.addItem("Seguridad", "seguridad")
        self.type_filter.addItem("Calidad", "calidad")
        self.type_filter.addItem("Logística", "logistica")
        self.type_filter.currentIndexChanged.connect(self.on_filter_changed)

        self.status_filter = QComboBox()
        self.status_filter.addItem("Todos los estados", "")
        self.status_filter.addItem("Reportado", "reportado")
        self.status_filter.addItem("En investigación", "investigacion")
        self.status_filter.addItem("Resuelto", "resuelto")
        self.status_filter.currentIndexChanged.connect(self.on_filter_changed)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Buscar incidentes...")
        self.search_input.textChanged.connect(self.on_search_changed)

        self.add_btn = QPushButton("Nuevo Incidente")
        self.add_btn.setIcon(QIcon("resources/icons/add.png"))
        self.add_btn.clicked.connect(self.on_add_incident)

        self.refresh_btn = QPushButton("Actualizar")
        self.refresh_btn.setIcon(QIcon("resources/icons/refresh.png"))
        self.refresh_btn.clicked.connect(self.refresh_data)

        toolbar_layout.addWidget(QLabel("Filtrar por tipo:"))
        toolbar_layout.addWidget(self.type_filter)
        toolbar_layout.addWidget(QLabel("Estado:"))
        toolbar_layout.addWidget(self.status_filter)
        toolbar_layout.addWidget(self.search_input)
        toolbar_layout.addStretch()
        toolbar_layout.addWidget(self.add_btn)
        toolbar_layout.addWidget(self.refresh_btn)

        main_layout.addLayout(toolbar_layout)

        # Tabla de incidentes
        self.incident_table = QTableView()
        self.incident_table.setModel(self.proxy_model)
        self.incident_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.incident_table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.incident_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.incident_table.setAlternatingRowColors(True)
        self.incident_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.incident_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)  # ID
        self.incident_table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.incident_table.customContextMenuRequested.connect(self.show_context_menu)
        self.incident_table.doubleClicked.connect(self.on_row_double_clicked)
        
        main_layout.addWidget(self.incident_table)

        # Barra de estado
        self.status_bar = QStatusBar()
        self.status_bar.showMessage("Sistema ERP Pirelli - Módulo de Incidentes")
        main_layout.addWidget(self.status_bar)

    def load_incidents(self, incidents):
        """Carga los incidentes en la tabla"""
        self.incident_model.removeRows(0, self.incident_model.rowCount())
        
        for incident in incidents:
            row = [
                QStandardItem(str(incident.id_incidente)),
                QStandardItem(incident.get_tipo_display()),
                QStandardItem(incident.descripcion),
                QStandardItem(incident.fecha),
                QStandardItem(str(incident.id_area) if incident.id_area else "N/A"),
                QStandardItem(str(incident.id_empleado_reporta) if incident.id_empleado_reporta else "N/A"),
                QStandardItem(incident.get_estado_display())
            ]
            
            # Colorear según estado
            if incident.estado == "reportado":
                row[-1].setForeground(QColor(Theme.DANGER_COLOR))
            elif incident.estado == "investigacion":
                row[-1].setForeground(QColor(Theme.WARNING_COLOR))
            elif incident.estado == "resuelto":
                row[-1].setForeground(QColor(Theme.SUCCESS_COLOR))
            
            self.incident_model.appendRow(row)
        
        self.status_bar.showMessage(f"Se han cargado {len(incidents)} incidentes")

    def on_data_loaded(self, data):
        """Maneja los datos cargados desde la API"""
        if data.get("type") == "incidents":
            from models.incident_model import Incident
            incidents = [Incident.from_dict(item) for item in data.get("data", [])]
            self.load_incidents(incidents)
        elif data.get("type") == "incident_created":
            QMessageBox.information(self, "Éxito", "Incidente creado correctamente")
            self.refresh_data()
        elif data.get("type") == "incident_updated":
            QMessageBox.information(self, "Éxito", "Incidente actualizado correctamente")
            self.refresh_data()
        elif data.get("type") == "incident_deleted":
            QMessageBox.information(self, "Éxito", "Incidente eliminado correctamente")
            self.refresh_data()

    def on_request_error(self, error_message):
        """Maneja errores de la API"""
        QMessageBox.critical(self, "Error", f"Error al cargar incidentes: {error_message}")
        self.status_bar.showMessage(f"Error: {error_message}")

    def refresh_data(self):
        """Actualiza los datos de la tabla"""
        self.status_bar.showMessage("Cargando incidentes...")
        self.api_client.get_incidents()

    def on_row_double_clicked(self, index):
        """Maneja doble clic en una fila"""
        mapped_index = self.proxy_model.mapToSource(index)
        row = mapped_index.row()
        incident_id = int(self.incident_model.item(row, 0).text())
        self.incident_selected.emit(incident_id)
        self.on_view_incident(incident_id)

    def show_context_menu(self, position):
        """Muestra menú contextual"""
        index = self.incident_table.indexAt(position)
        if not index.isValid():
            return

        context_menu = QMenu(self)
        view_action = QAction(QIcon("resources/icons/view.png"), "Ver detalles", self)
        edit_action = QAction(QIcon("resources/icons/edit.png"), "Editar", self)
        delete_action = QAction(QIcon("resources/icons/delete.png"), "Eliminar", self)

        context_menu.addAction(view_action)
        context_menu.addAction(edit_action)
        context_menu.addSeparator()
        context_menu.addAction(delete_action)

        mapped_index = self.proxy_model.mapToSource(index)
        row = mapped_index.row()
        incident_id = int(self.incident_model.item(row, 0).text())

        view_action.triggered.connect(lambda: self.on_view_incident(incident_id))
        edit_action.triggered.connect(lambda: self.on_edit_incident(incident_id))
        delete_action.triggered.connect(lambda: self.on_delete_incident(incident_id))

        context_menu.exec(self.incident_table.viewport().mapToGlobal(position))

    def on_view_incident(self, incident_id):
        """Muestra detalles del incidente"""
        from .incident_detail import IncidentDetailView
        incident = self._get_incident_by_id(incident_id)
        if incident:
            dialog = IncidentDetailView(self.api_client, incident.to_dict())
            dialog.exec()

    def on_add_incident(self):
        """Abre formulario para nuevo incidente"""
        from .incident_form import IncidentForm
        dialog = IncidentForm(self.api_client)
        dialog.incident_saved.connect(self._handle_incident_save)
        dialog.exec()

    def on_edit_incident(self, incident_id):
        """Abre formulario de edición"""
        from .incident_form import IncidentForm
        incident = self._get_incident_by_id(incident_id)
        if incident:
            dialog = IncidentForm(self.api_client, incident.to_dict())
            dialog.incident_saved.connect(self._handle_incident_save)
            dialog.exec()

    def on_delete_incident(self, incident_id):
        """Elimina un incidente"""
        reply = QMessageBox.question(
            self,
            "Confirmar eliminación",
            f"¿Está seguro que desea eliminar el incidente ID: {incident_id}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.api_client.delete_incident(incident_id)
            self.status_bar.showMessage(f"Eliminando incidente ID: {incident_id}...")

    def _get_incident_by_id(self, incident_id):
        """Busca un incidente por ID en el modelo actual"""
        for row in range(self.incident_model.rowCount()):
            if int(self.incident_model.item(row, 0).text()) == incident_id:
                from models.incident_model import Incident
                incident_data = {
                    "id_incidente": self.incident_model.item(row, 0).text(),
                    "tipo": self.type_filter.findText(self.incident_model.item(row, 1).text()),
                    "descripcion": self.incident_model.item(row, 2).text(),
                    "fecha": self.incident_model.item(row, 3).text(),
                    "id_area": self.incident_model.item(row, 4).text(),
                    "id_empleado_reporta": self.incident_model.item(row, 5).text(),
                    "estado": self.status_filter.findText(self.incident_model.item(row, 6).text())
                }
                return Incident.from_dict(incident_data)
        return None

    def _handle_incident_save(self, incident_data):
        """Maneja el guardado de un incidente"""
        if "id_incidente" in incident_data and incident_data["id_incidente"]:
            self.api_client.update_incident(incident_data["id_incidente"], incident_data)
        else:
            self.api_client.create_incident(incident_data)

    def on_search_changed(self, text):
        """Filtra la tabla según texto de búsqueda"""
        self.proxy_model.setFilterWildcard(text)
        self.proxy_model.invalidateFilter()

    def on_filter_changed(self):
        """Aplica filtros de tipo y estado"""
        self.proxy_model.invalidateFilter()