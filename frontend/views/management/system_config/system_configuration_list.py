from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableView, QHeaderView, QLineEdit, QFrame,
    QMessageBox, QMenu, QDialog, QAbstractItemView, QStatusBar
)
from PyQt6.QtCore import Qt, pyqtSignal, QSortFilterProxyModel
from PyQt6.QtGui import QIcon, QAction, QStandardItemModel, QStandardItem, QFont, QColor
from utils.theme import Theme

class SystemConfigurationListView(QWidget):
    """Vista de listado de configuraciones del sistema"""
    
    configuration_selected = pyqtSignal(int)
    
    def __init__(self, api_client):
        super().__init__()
        Theme.apply_window_light_theme(self)

        self.api_client = api_client
        self.api_client.data_received.connect(self.on_data_loaded)
        self.api_client.request_error.connect(self.on_request_error)

        self.config_model = QStandardItemModel()
        self.config_model.setHorizontalHeaderLabels([
            "ID", "Parámetro", "Valor", "Descripción"
        ])

        self.proxy_model = QSortFilterProxyModel()
        self.proxy_model.setSourceModel(self.config_model)
        self.proxy_model.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.proxy_model.setFilterKeyColumn(-1)

        self.init_ui()
        self.refresh_data()

    def init_ui(self):
        """Inicializa la interfaz de usuario"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        title_label = QLabel("Configuraciones del Sistema")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        main_layout.addWidget(title_label)

        toolbar_layout = QHBoxLayout()

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Buscar por parámetro o valor...")
        self.search_input.textChanged.connect(self.on_search_changed)

        self.add_btn = QPushButton("Nueva Configuración")
        self.add_btn.setIcon(QIcon("resources/icons/add.png"))
        self.add_btn.clicked.connect(self.on_add_configuration)

        self.refresh_btn = QPushButton("Actualizar")
        self.refresh_btn.setIcon(QIcon("resources/icons/refresh.png"))
        self.refresh_btn.clicked.connect(self.refresh_data)

        toolbar_layout.addWidget(self.search_input)
        toolbar_layout.addStretch()
        toolbar_layout.addWidget(self.add_btn)
        toolbar_layout.addWidget(self.refresh_btn)

        main_layout.addLayout(toolbar_layout)

        self.config_table = QTableView()
        self.config_table.setModel(self.proxy_model)
        self.config_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.config_table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.config_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.config_table.setAlternatingRowColors(True)
        self.config_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.config_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.config_table.verticalHeader().setVisible(False)
        self.config_table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.config_table.customContextMenuRequested.connect(self.show_context_menu)
        self.config_table.doubleClicked.connect(self.on_row_double_clicked)
        
        main_layout.addWidget(self.config_table)

        self.status_bar = QStatusBar()
        self.status_bar.showMessage("Sistema ERP - Configuraciones del Sistema")
        main_layout.addWidget(self.status_bar)

    def load_configurations(self, configs):
        """Carga las configuraciones en la tabla"""
        self.config_model.removeRows(0, self.config_model.rowCount())

        for config in configs:
            row = [
                QStandardItem(str(config.id_config)),
                QStandardItem(config.parametro),
                QStandardItem(str(config.valor)),
                QStandardItem(config.descripcion_display)
            ]
            self.config_model.appendRow(row)

        self.status_bar.showMessage(f"Se han cargado {len(configs)} configuraciones")

    def on_data_loaded(self, data):
        """Maneja los datos cargados desde la API"""
        if data.get("type") == "system_configurations":
            from models.system_configuration_model import SystemConfiguration
            configs = [SystemConfiguration.from_dict(item) for item in data.get("data", [])]
            self.load_configurations(configs)
        elif data.get("type") == "configuration_created":
            QMessageBox.information(self, "Éxito", "Configuración creada correctamente")
            self.refresh_data()
        elif data.get("type") == "configuration_updated":
            QMessageBox.information(self, "Éxito", "Configuración actualizada correctamente")
            self.refresh_data()
        elif data.get("type") == "configuration_deleted":
            QMessageBox.information(self, "Éxito", "Configuración eliminada correctamente")
            self.refresh_data()

    def on_request_error(self, error_message):
        """Maneja errores de la API"""
        QMessageBox.critical(self, "Error", f"Error al cargar configuraciones: {error_message}")
        self.status_bar.showMessage(f"Error: {error_message}")

    def refresh_data(self):
        """Actualiza los datos de la tabla"""
        self.status_bar.showMessage("Cargando configuraciones del sistema...")
        self.api_client.get_system_configurations()

    def on_search_changed(self, text):
        """Maneja el cambio en el campo de búsqueda"""
        self.proxy_model.setFilterWildcard(text)
        self.status_bar.showMessage(f"Filtrando configuraciones por: {text}" if text else "Sistema ERP - Configuraciones del Sistema")

    def on_row_double_clicked(self, index):
        """Maneja el doble clic en una fila"""
        mapped_index = self.proxy_model.mapToSource(index)
        row = mapped_index.row()
        config_id = int(self.config_model.item(row, 0).text())
        self.configuration_selected.emit(config_id)
        self.on_view_configuration(config_id)

    def show_context_menu(self, position):
        """Muestra menú contextual para una fila"""
        index = self.config_table.indexAt(position)
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
        config_id = int(self.config_model.item(row, 0).text())

        view_action.triggered.connect(lambda: self.on_view_configuration(config_id))
        edit_action.triggered.connect(lambda: self.on_edit_configuration(config_id))
        delete_action.triggered.connect(lambda: self.on_delete_configuration(config_id))

        context_menu.exec(self.config_table.viewport().mapToGlobal(position))

    def on_view_configuration(self, config_id):
        """Muestra detalles de una configuración"""
        from .system_configuration_detail import SystemConfigurationDetailView
        config = self._get_configuration_by_id(config_id)
        if config:
            dialog = SystemConfigurationDetailView(self.api_client, config.to_dict())
            dialog.exec()
        else:
            QMessageBox.warning(self, "Error", "No se pudo cargar la configuración")

    def on_add_configuration(self):
        """Muestra el diálogo para añadir una nueva configuración"""
        from .system_configuration_form import SystemConfigurationForm
        dialog = SystemConfigurationForm(self.api_client)
        dialog.configuration_saved.connect(self._handle_configuration_save)
        dialog.exec()

    def on_edit_configuration(self, config_id):
        """Abre el formulario de edición de una configuración"""
        config = self._get_configuration_by_id(config_id)
        if config:
            self._show_edit_form(config)
        else:
            QMessageBox.warning(self, "Error", "No se pudo cargar la configuración")

    def _get_configuration_by_id(self, config_id):
        """Busca una configuración por su ID en el modelo actual"""
        for row in range(self.config_model.rowCount()):
            if int(self.config_model.item(row, 0).text()) == config_id:
                from models.system_configuration_model import SystemConfiguration
                config_data = {
                    "id_config": self.config_model.item(row, 0).text(),
                    "parametro": self.config_model.item(row, 1).text(),
                    "valor": self.config_model.item(row, 2).text(),
                    "descripcion": self.config_model.item(row, 3).text()
                }
                return SystemConfiguration.from_dict(config_data)
        return None

    def _show_edit_form(self, config):
        """Muestra el formulario de edición con los datos de la configuración"""
        from .system_configuration_form import SystemConfigurationForm
        if config:
            dialog = SystemConfigurationForm(self.api_client, config.to_dict())
            dialog.configuration_saved.connect(self._handle_configuration_save)
            dialog.exec()
        else:
            QMessageBox.warning(self, "Error", "No se pudo cargar la configuración")

    def _handle_configuration_save(self, config_data):
        """Maneja el guardado de una configuración (nueva o editada)"""
        if "id_config" in config_data and config_data["id_config"]:
            self.api_client.update_system_configuration(config_data["id_config"], config_data)
            self.status_bar.showMessage(f"Actualizando configuración ID: {config_data['id_config']}...")
        else:
            self.api_client.create_system_configuration(config_data)
            self.status_bar.showMessage("Creando nueva configuración...")

    def on_delete_configuration(self, config_id):
        """Elimina una configuración"""
        reply = QMessageBox.question(
            self,
            "Confirmar eliminación",
            f"¿Está seguro que desea eliminar la configuración ID: {config_id}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.api_client.delete_system_configuration(config_id)
            self.status_bar.showMessage(f"Eliminando configuración ID: {config_id}...")