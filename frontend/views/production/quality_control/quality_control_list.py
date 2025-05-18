from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableView, QHeaderView, QLineEdit, QComboBox, QFrame,
    QMessageBox, QMenu, QDialog, QFormLayout, QDialogButtonBox,
    QAbstractItemView, QSplitter, QToolBar, QStatusBar, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal, QSortFilterProxyModel, QThread, QSize
from PyQt6.QtGui import QIcon, QAction, QStandardItemModel, QStandardItem, QFont, QColor, QPixmap
from models.quality_control_model import QualityControl
from utils.theme import Theme
import logging

logger = logging.getLogger(__name__)

class QualityControlListView(QWidget):
    """Vista de listado de controles de calidad para ERP"""

    # Señales
    control_selected = pyqtSignal(int)  # Emitida cuando se selecciona un control
    refresh_requested = pyqtSignal()    # Emitida cuando se solicita actualización

    def __init__(self, api_client, parent=None):
        super().__init__(parent)
        Theme.apply_window_light_theme(self)
        
        self.api_client = api_client
        self.current_filters = {}
        
        # Configurar modelo de datos
        self._setup_models()
        self.init_ui()
        self._connect_signals()
        
        # Cargar datos iniciales
        self.refresh_data()

    def _setup_models(self):
        """Configura los modelos de datos para la tabla"""
        self.control_model = QStandardItemModel()
        self.control_model.setHorizontalHeaderLabels([
            "ID", "Orden Producción", "Fecha", "Resultado", "Valor Resultado", 
            "Observaciones", "Usuario"
        ])
        
        # Modelo proxy para filtrado
        self.proxy_model = QSortFilterProxyModel()
        self.proxy_model.setSourceModel(self.control_model)
        self.proxy_model.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.proxy_model.setFilterKeyColumn(-1)  # Buscar en todas las columnas
        self.proxy_model.filterAcceptsRow = self._filter_accepts_row

    def init_ui(self):
        """Inicializa la interfaz de usuario"""
        self.setMinimumSize(800, 600)
        
        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Título de sección
        title_label = QLabel("Gestión de Control de Calidad")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        main_layout.addWidget(title_label)

        # Barra de herramientas
        toolbar_layout = QHBoxLayout()
        
        # Filtro de resultado
        self.result_filter = QComboBox()
        self.result_filter.addItem("Todos los resultados", "")
        for value, display in QualityControl.get_resultados_lista():
            self.result_filter.addItem(display, value)
        
        # Campo de búsqueda
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Buscar por orden de producción...")
        self.search_input.textChanged.connect(self.on_search_changed)

        # Botón de búsqueda
        search_btn = QPushButton("Buscar")
        search_btn.clicked.connect(self._on_filters_changed)

        # Botón para añadir
        self.add_btn = QPushButton("Nuevo Control")
        self.add_btn.setIcon(QIcon("resources/icons/add.png"))
        self.add_btn.clicked.connect(self.on_add_control)

        # Botón de actualizar
        self.refresh_btn = QPushButton("Actualizar")
        self.refresh_btn.setIcon(QIcon("resources/icons/refresh.png"))
        self.refresh_btn.clicked.connect(self.refresh_data)

        # Agregar widgets a la barra de herramientas
        toolbar_layout.addWidget(QLabel("Resultado:"))
        toolbar_layout.addWidget(self.result_filter)
        toolbar_layout.addWidget(self.search_input)
        toolbar_layout.addWidget(search_btn)
        toolbar_layout.addStretch()
        toolbar_layout.addWidget(self.add_btn)
        toolbar_layout.addWidget(self.refresh_btn)

        main_layout.addLayout(toolbar_layout)

        # Tabla de controles
        self.control_table = QTableView()
        self.control_table.setModel(self.proxy_model)
        self.control_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.control_table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.control_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.control_table.setAlternatingRowColors(True)
        self.control_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.control_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)  # ID
        self.control_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)  # Fecha
        self.control_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)  # Resultado
        self.control_table.verticalHeader().setVisible(False)
        self.control_table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.control_table.customContextMenuRequested.connect(self.show_context_menu)
        self.control_table.doubleClicked.connect(self.on_row_double_clicked)
        
        # Ocultar columnas internas
        self.control_table.setColumnHidden(4, True)  # Valor resultado
        
        main_layout.addWidget(self.control_table)

        # Labels de totales
        summary_layout = QHBoxLayout()
        self.total_label = QLabel("Total de controles: <b>0</b>")
        self.approved_label = QLabel("Aprobados: <b>0</b>")
        self.rejected_label = QLabel("Rechazados: <b>0</b>")
        self.repair_label = QLabel("Reparación: <b>0</b>")

        summary_layout.addWidget(self.total_label)
        summary_layout.addSpacing(30)
        summary_layout.addWidget(self.approved_label)
        summary_layout.addSpacing(30)
        summary_layout.addWidget(self.rejected_label)
        summary_layout.addSpacing(30)
        summary_layout.addWidget(self.repair_label)
        summary_layout.addStretch()
        main_layout.addLayout(summary_layout)

        # Barra de estado
        self.status_bar = QStatusBar()
        self.status_bar.showMessage("Sistema ERP - Módulo de Control de Calidad")
        main_layout.addWidget(self.status_bar)

    def _filter_accepts_row(self, source_row, source_parent):
        """Método personalizado para determinar si una fila cumple con los filtros"""
        model = self.control_model
        
        # Obtener valores de los filtros
        search_text = self.search_input.text().strip().lower()
        result = self.result_filter.currentData()
        
        # Si no hay filtros activos, mostrar todas las filas
        if not search_text and not result:
            return True
            
        # Obtener valores de la fila actual
        try:
            orden_produccion = model.item(source_row, 1).text().lower()
            resultado_valor = model.item(source_row, 4).text().lower()
            
            # Filtro de búsqueda (orden de producción)
            if search_text and search_text not in orden_produccion:
                return False
                
            # Filtro de resultado
            if result and result != resultado_valor:
                return False
                
            return True
        except (AttributeError, IndexError):
            return True

    def on_search_changed(self, text):
        """Maneja el cambio en el campo de búsqueda"""
        self.proxy_model.setFilterWildcard(text)
        self.proxy_model.invalidateFilter()
        self.status_bar.showMessage(f"Filtrando controles por: {text}" if text else "Sistema ERP - Módulo de Control de Calidad")

    def on_result_changed(self, index):
        """Maneja el cambio en el filtro de resultado"""
        self._on_filters_changed()

    def _on_filters_changed(self):
        """Se llama cuando cambia estado, para actualizar el filtrado"""
        self.proxy_model.invalidateFilter()
        result = self.result_filter.currentData()
        
        msg = "Mostrando controles"
        if result:
            msg += f" con resultado: {self.result_filter.currentText()}"
        else:
            msg = "Sistema ERP - Módulo de Control de Calidad"
            
        self.status_bar.showMessage(msg)

    def _connect_signals(self):
        """Conecta todas las señales y slots"""
        # Conectar botones
        self.add_btn.clicked.connect(self.on_add_control)
        self.refresh_btn.clicked.connect(self.refresh_data)
        
        # Conectar filtros
        self.search_input.textChanged.connect(self.on_search_changed)
        self.result_filter.currentIndexChanged.connect(self.on_result_changed)
        
        # Conectar eventos de tabla
        self.control_table.doubleClicked.connect(self.on_row_double_clicked)
        self.control_table.customContextMenuRequested.connect(self.show_context_menu)
        
        # Señales del API Client
        self.api_client.data_received.connect(self.on_data_loaded)
        self.api_client.request_error.connect(self.on_request_error)
        self.api_client.request_success.connect(self.on_request_success)

    def refresh_data(self):
        """Solicita controles filtrados al API"""
        self.status_bar.showMessage("Cargando controles de calidad...")
        
        # Prepara los filtros para la API
        api_filters = {
            'resultado': self.current_filters.get('resultado'),
            'search': self.search_input.text().strip() or None
        }
        
        # Elimina filtros vacíos/None
        api_filters = {k: v for k, v in api_filters.items() if v is not None}
        
        self.api_client.get_quality_controls()

    def load_controls(self, controls):
        """Carga los controles en la tabla"""
        self.control_model.removeRows(0, self.control_model.rowCount())
        
        if not controls:
            self.status_bar.showMessage("No se encontraron controles")
            return
            
        count_aprobados = count_rechazados = count_reparacion = 0
        
        for control in controls:
            if not isinstance(control, QualityControl):
                control = QualityControl.from_dict(control)
                
            # Contar por resultado
            if control.resultado == 'aprobado':
                count_aprobados += 1
            elif control.resultado == 'rechazado':
                count_rechazados += 1
            elif control.resultado == 'reparacion':
                count_reparacion += 1
                
            # Crear fila
            row = [
                QStandardItem(str(control.id_control)),
                QStandardItem(str(control.id_orden_produccion)),
                QStandardItem(control.fecha),
                QStandardItem(control.get_resultado_display()),
                QStandardItem(control.resultado),
                QStandardItem(control.observaciones_display),
                QStandardItem(str(control.id_usuario))
            ]
            
            # Formatear celdas
            row[0].setTextAlignment(Qt.AlignmentFlag.AlignCenter)  # ID
            row[1].setTextAlignment(Qt.AlignmentFlag.AlignCenter)  # Orden Producción
            row[2].setTextAlignment(Qt.AlignmentFlag.AlignCenter)  # Fecha
            row[3].setTextAlignment(Qt.AlignmentFlag.AlignCenter)  # Resultado
            row[6].setTextAlignment(Qt.AlignmentFlag.AlignCenter)  # Usuario
            
            # Color por resultado
            if control.resultado == 'rechazado':
                row[3].setForeground(QColor(Theme.DANGER_COLOR))
            elif control.resultado == 'reparacion':
                row[3].setForeground(QColor(Theme.WARNING_COLOR))
            else:
                row[3].setForeground(QColor(Theme.SUCCESS_COLOR))
            
            self.control_model.appendRow(row)
        
        # Actualizar resumen
        total = len(controls)
        self.total_label.setText(f"Total: <b>{total}</b>")
        self.approved_label.setText(f"Aprobados: <b>{count_aprobados}</b>")
        self.rejected_label.setText(f"Rechazados: <b>{count_rechazados}</b>")
        self.repair_label.setText(f"Reparación: <b>{count_reparacion}</b>")
        
        self.status_bar.showMessage(f"Cargados {total} controles de calidad")

    def show_context_menu(self, position):
        """Muestra el menú contextual para un control"""
        index = self.control_table.indexAt(position)
        if not index.isValid():
            return
            
        # Obtener el control seleccionado
        mapped_index = self.proxy_model.mapToSource(index)
        control_id = int(self.control_model.item(mapped_index.row(), 0).text())
        
        menu = QMenu(self)
        
        # Acciones principales
        view_action = menu.addAction(QIcon("resources/icons/view.png"), "Ver detalles")
        edit_action = menu.addAction(QIcon("resources/icons/edit.png"), "Editar")
        delete_action = menu.addAction(QIcon("resources/icons/delete.png"), "Eliminar")
        menu.addSeparator()
        
        # Conectar acciones
        view_action.triggered.connect(lambda: self.on_view_control(control_id))
        edit_action.triggered.connect(lambda: self.on_edit_control(control_id))
        delete_action.triggered.connect(lambda: self.on_delete_control(control_id))
        
        menu.exec(self.control_table.viewport().mapToGlobal(position))

    def on_add_control(self):
        """Abre el formulario para añadir nuevo control"""
        from .quality_control_form import QualityControlForm
        dialog = QualityControlForm(self.api_client, parent=self)
        dialog.control_saved.connect(self._handle_control_save)
        dialog.exec()

    def on_edit_control(self, control_id):
        """Abre el formulario para editar un control existente"""
        from .quality_control_form import QualityControlForm
        
        # Buscar el control en el modelo
        for row in range(self.control_model.rowCount()):
            if int(self.control_model.item(row, 0).text()) == control_id:
                control_data = {
                    "id_control": control_id,
                    "id_orden_produccion": self.control_model.item(row, 1).text(),
                    "fecha": self.control_model.item(row, 2).text(),
                    "resultado": self.control_model.item(row, 4).text(),
                    "observaciones": self.control_model.item(row, 5).text(),
                    "id_usuario": self.control_model.item(row, 6).text()
                }
                break
        else:
            QMessageBox.warning(self, "Error", "No se pudo cargar el control")
            return
            
        dialog = QualityControlForm(self.api_client, control_data, parent=self)
        dialog.control_saved.connect(self._handle_control_save)
        dialog.exec()

    def on_view_control(self, control_id):
        """Muestra los detalles completos del control"""
        from .quality_control_detail import QualityControlDetailView
        
        # Obtener datos del control desde el modelo
        for row in range(self.control_model.rowCount()):
            if int(self.control_model.item(row, 0).text()) == control_id:
                control_data = {
                    "id_control": control_id,
                    "id_orden_produccion": self.control_model.item(row, 1).text(),
                    "fecha": self.control_model.item(row, 2).text(),
                    "resultado": self.control_model.item(row, 4).text(),
                    "observaciones": self.control_model.item(row, 5).text(),
                    "id_usuario": self.control_model.item(row, 6).text()
                }
                break
        else:
            QMessageBox.warning(self, "Error", "Control no encontrado")
            return
            
        dialog = QualityControlDetailView(self.api_client, control_data, parent=self)
        dialog.edit_requested.connect(self.on_edit_control)
        dialog.delete_requested.connect(self.on_delete_control)
        dialog.exec()

    def on_delete_control(self, control_id):
        """Elimina un control con confirmación"""
        reply = QMessageBox.question(
            self,
            "Confirmar eliminación",
            f"¿Está seguro que desea eliminar el control ID: {control_id}?\n\n"
            "Esta acción no se puede deshacer.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.api_client.delete_quality_control(control_id)
            self.status_bar.showMessage(f"Eliminando control ID: {control_id}...")

    def on_row_double_clicked(self, index):
        """Maneja el doble clic en una fila"""
        mapped_index = self.proxy_model.mapToSource(index)
        control_id = int(self.control_model.item(mapped_index.row(), 0).text())
        self.on_view_control(control_id)

    def _handle_control_save(self, control_data):
        """Maneja el guardado de un control"""
        if 'id_control' in control_data and control_data['id_control']:
            self.api_client.update_quality_control(control_data['id_control'], control_data)
        else:
            self.api_client.create_quality_control(control_data)

    def on_data_loaded(self, data):
        """Maneja los datos cargados desde la API"""
        if data.get('type') == 'quality_controls':
            controls = [QualityControl.from_dict(item) for item in data.get('data', [])]
            self.load_controls(controls)

    def on_request_success(self, endpoint, data):
        """Maneja operaciones exitosas"""
        if endpoint in ['create_quality_control', 'update_quality_control', 'delete_quality_control']:
            self.refresh_data()
            msg = {
                'create_quality_control': "Control creado exitosamente",
                'update_quality_control': "Control actualizado exitosamente",
                'delete_quality_control': "Control eliminado exitosamente"
            }.get(endpoint, "Operación completada")
            QMessageBox.information(self, "Éxito", msg)

    def on_request_error(self, error_msg):
        """Maneja errores de la API"""
        QMessageBox.critical(self, "Error", error_msg)
        self.status_bar.showMessage(f"Error: {error_msg}")