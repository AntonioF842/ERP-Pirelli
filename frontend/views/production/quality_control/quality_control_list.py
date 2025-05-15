from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableView, QHeaderView, QLineEdit, QComboBox, QFrame,
    QMessageBox, QMenu, QDialog, QFormLayout, QDialogButtonBox,
    QAbstractItemView, QSplitter, QToolBar, QStatusBar, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal, QSortFilterProxyModel, QThread, QSize
from PyQt6.QtGui import QIcon, QAction, QStandardItemModel, QStandardItem, QFont, QColor
from utils.theme import Theme

class QualityControlListView(QWidget):
    """Vista de listado de controles de calidad para ERP Pirelli"""

    # Señales
    control_selected = pyqtSignal(int)  # Emitida cuando se selecciona un control

    def __init__(self, api_client):
        super().__init__()
        from utils.theme import Theme
        Theme.apply_window_light_theme(self)

        self.api_client = api_client

        # Conectar señales del cliente API
        self.api_client.data_received.connect(self.on_data_loaded)
        self.api_client.request_error.connect(self.on_request_error)

        # Modelo para la tabla
        self.control_model = QStandardItemModel()
        self.control_model.setHorizontalHeaderLabels([
            "ID", "Orden Producción", "Fecha", "Resultado", "Observaciones", "Usuario"
        ])

        # Modelo proxy para filtrado avanzado
        self.proxy_model = QSortFilterProxyModel()
        self.proxy_model.setSourceModel(self.control_model)
        self.proxy_model.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.proxy_model.setFilterKeyColumn(-1)  # Buscar en todas las columnas
        self.setup_filter_proxy()

        # Colores corporativos Pirelli (ahora tomados del tema)
        self.pirelli_red = Theme.SECONDARY_COLOR
        self.pirelli_yellow = Theme.ACCENT_COLOR
        self.pirelli_dark = Theme.PRIMARY_COLOR
        self.pirelli_light = Theme.LIGHT_BG

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
        title_label = QLabel("Gestión de Control de Calidad")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        main_layout.addWidget(title_label)

        # Barra de herramientas
        toolbar_layout = QHBoxLayout()

        # Filtro de resultado
        self.result_filter = QComboBox()
        self.result_filter.addItem("Todos los resultados", "")
        self.result_filter.addItem("Aprobado", "aprobado")
        self.result_filter.addItem("Rechazado", "rechazado")
        self.result_filter.addItem("Requiere Reparación", "reparacion")
        self.result_filter.currentIndexChanged.connect(self.on_result_changed)

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
        toolbar_layout.addWidget(QLabel("Filtrar por resultado:"))
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
        self.control_table.verticalHeader().setVisible(False)
        self.control_table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.control_table.customContextMenuRequested.connect(self.show_context_menu)
        self.control_table.doubleClicked.connect(self.on_row_double_clicked)
        
        main_layout.addWidget(self.control_table)

        # --- Agregar labels de totales debajo de la tabla ---
        summary_layout = QHBoxLayout()
        self.total_label = QLabel("Total de controles: <b>0</b>")
        self.approved_label = QLabel("Aprobados: <b>0</b>")
        self.rejected_label = QLabel("Rechazados: <b>0</b>")
        self.repair_label = QLabel("Reparación: <b>0</b>")

        # Un poco de espacio entre textos
        summary_layout.addWidget(self.total_label)
        summary_layout.addSpacing(30)
        summary_layout.addWidget(self.approved_label)
        summary_layout.addSpacing(30)
        summary_layout.addWidget(self.rejected_label)
        summary_layout.addSpacing(30)
        summary_layout.addWidget(self.repair_label)
        summary_layout.addStretch()
        main_layout.addLayout(summary_layout)
        # --- Fin de la inserción ---

        # Barra de estado
        self.status_bar = QStatusBar()
        self.status_bar.showMessage("Sistema ERP Pirelli - Módulo de Control de Calidad v1.0")
        main_layout.addWidget(self.status_bar)

    def setup_filter_proxy(self):
        """Configura el modelo proxy para filtrado avanzado"""
        # Sobrescribe el método filterAcceptsRow del proxy model
        self.proxy_model.filterAcceptsRow = self._filter_accepts_row
    
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
            resultado = model.item(source_row, 3).text().lower()
            
            # Filtro de búsqueda (orden de producción)
            if search_text and search_text not in orden_produccion:
                return False
                
            # Filtro de resultado
            if result and result != resultado:
                return False
                
            return True
        except (AttributeError, IndexError):
            # En caso de error, mostrar la fila
            return True

    def on_search_changed(self, text):
        """Maneja el cambio en el campo de búsqueda"""
        self.proxy_model.setFilterWildcard(text)
        self.proxy_model.invalidateFilter()
        self.status_bar.showMessage(f"Filtrando controles por: {text}" if text else "Sistema ERP Pirelli - Módulo de Control de Calidad v1.0")

    def on_result_changed(self, index):
        """Maneja el cambio en el filtro de resultado"""
        self._on_filters_changed()

    def _on_filters_changed(self):
        """Se llama cuando cambia resultado, para actualizar el filtrado sobre la tabla"""
        self.proxy_model.invalidateFilter()
        result = self.result_filter.currentData()
        
        msg = "Mostrando controles"
        if result:
            msg += f" con resultado: {self.result_filter.currentText()}"
        else:
            msg = "Sistema ERP Pirelli - Módulo de Control de Calidad v1.0"
            
        self.status_bar.showMessage(msg)

    def clear_filters(self):
        """Limpia todos los filtros aplicados"""
        self.search_input.clear()
        self.result_filter.setCurrentIndex(0)
        self.proxy_model.invalidateFilter()
        self.status_bar.showMessage("Filtros eliminados")

    def refresh_data(self):
        """Actualiza los datos de la tabla desde la API"""
        self.status_bar.showMessage("Actualizando datos de controles de calidad...")
        self.api_client.get_quality_controls()

    def load_controls(self, controls):
        """Carga los controles recibidos en la tabla y actualiza estadísticas"""
        # Limpiar modelo actual
        self.control_model.removeRows(0, self.control_model.rowCount())
        count_aprobados = count_rechazados = count_reparacion = 0

        for control in controls:
            row = []

            # ID
            id_item = QStandardItem(str(control.id_control))
            id_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            row.append(id_item)

            # Orden Producción
            op_item = QStandardItem(str(control.id_orden_produccion))
            op_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            row.append(op_item)

            # Fecha
            fecha_item = QStandardItem(control.fecha)
            fecha_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            row.append(fecha_item)

            # Resultado
            resultado = control.get_resultado_display()
            resultado_item = QStandardItem(resultado)
            
            # Colorear según resultado
            if control.resultado == "aprobado":
                resultado_item.setForeground(QColor(Theme.SUCCESS_COLOR))
                count_aprobados += 1
            elif control.resultado == "rechazado":
                resultado_item.setForeground(QColor(Theme.DANGER_COLOR))
                count_rechazados += 1
            elif control.resultado == "reparacion":
                resultado_item.setForeground(QColor(Theme.WARNING_COLOR))
                count_reparacion += 1
                
            resultado_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            row.append(resultado_item)

            # Observaciones
            obs_item = QStandardItem(control.observaciones_display)
            obs_item.setToolTip(control.observaciones_display)
            row.append(obs_item)

            # Usuario
            user_item = QStandardItem(str(control.id_usuario))
            user_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            row.append(user_item)

            self.control_model.appendRow(row)
            
        total = len(controls)
        self.total_label.setText(f"Total de controles: <b>{total}</b>")
        self.approved_label.setText(f"Aprobados: <b>{count_aprobados}</b>")
        self.rejected_label.setText(f"Rechazados: <b>{count_rechazados}</b>")
        self.repair_label.setText(f"Reparación: <b>{count_reparacion}</b>")
        self.status_bar.showMessage(f"Se han cargado {total} controles de calidad")

    def on_data_loaded(self, data):
        """Maneja los datos cargados desde la API directa"""
        if data.get("type") == "quality_controls":
            # Convertir datos API a objetos control
            from models.quality_control_model import QualityControl
            controls = [QualityControl.from_dict(item) for item in data.get("data", [])]
            self.load_controls(controls)
        elif data.get("type") == "quality_control_created":
            QMessageBox.information(self, "Éxito", "Control de calidad creado correctamente")
            self.refresh_data()
        elif data.get("type") == "quality_control_updated":
            QMessageBox.information(self, "Éxito", "Control de calidad actualizado correctamente")
            self.refresh_data()
        elif data.get("type") == "quality_control_deleted":
            QMessageBox.information(self, "Éxito", "Control de calidad eliminado correctamente")
            self.refresh_data()

    def on_request_error(self, error_message):
        """Maneja errores de la API"""
        QMessageBox.critical(self, "Error", f"Error al cargar controles de calidad: {error_message}")
        self.status_bar.showMessage(f"Error: {error_message}")

    def on_row_double_clicked(self, index):
        """Maneja el doble clic en una fila"""
        mapped_index = self.proxy_model.mapToSource(index)
        row = mapped_index.row()
        control_id = int(self.control_model.item(row, 0).text())
        self.control_selected.emit(control_id)
        self.on_view_control(control_id)

    def show_context_menu(self, position):
        """Muestra menú contextual para una fila"""
        index = self.control_table.indexAt(position)
        if not index.isValid():
            return

        context_menu = QMenu(self)
        # Acciones principales
        view_action = QAction(QIcon("resources/icons/view.png"), "Ver detalles", self)
        edit_action = QAction(QIcon("resources/icons/edit.png"), "Editar", self)
        delete_action = QAction(QIcon("resources/icons/delete.png"), "Eliminar", self)
        # Extra
        report_action = QAction(QIcon("resources/icons/report.png"), "Generar reporte", self)
        attach_action = QAction(QIcon("resources/icons/attach.png"), "Adjuntar evidencia", self)

        context_menu.addAction(view_action)
        context_menu.addAction(edit_action)
        context_menu.addSeparator()
        context_menu.addAction(report_action)
        context_menu.addAction(attach_action)
        context_menu.addSeparator()
        context_menu.addAction(delete_action)

        mapped_index = self.proxy_model.mapToSource(index)
        row = mapped_index.row()
        control_id = int(self.control_model.item(row, 0).text())

        view_action.triggered.connect(lambda: self.on_view_control(control_id))
        edit_action.triggered.connect(lambda: self.on_edit_control(control_id))
        delete_action.triggered.connect(lambda: self.on_delete_control(control_id))
        report_action.triggered.connect(lambda: self.status_bar.showMessage(f"Generando reporte para control ID: {control_id}"))
        attach_action.triggered.connect(lambda: self.status_bar.showMessage(f"Adjuntando evidencia para control ID: {control_id}"))

        context_menu.exec(self.control_table.viewport().mapToGlobal(position))

    def _get_selected_control_id(self, callback_func):
        """Obtiene el ID del control seleccionado y llama al callback"""
        indexes = self.control_table.selectionModel().selectedRows()
        if not indexes:
            QMessageBox.information(self, "Selección", "Por favor, seleccione un control primero")
            return
        # Obtener el ID del control seleccionado (columna 0)
        mapped_index = self.proxy_model.mapToSource(indexes[0])
        row = mapped_index.row()
        control_id = int(self.control_model.item(row, 0).text())
        # Llamar al callback con el ID
        callback_func(control_id)

    def on_view_control(self, control_id):
        """Muestra detalles de un control de calidad"""
        # Buscar la fila en el modelo
        for row in range(self.control_model.rowCount()):
            if int(self.control_model.item(row, 0).text()) == control_id:
                orden_produccion = self.control_model.item(row, 1).text()
                fecha = self.control_model.item(row, 2).text()
                resultado = self.control_model.item(row, 3).text()
                observaciones = self.control_model.item(row, 4).text()
                usuario = self.control_model.item(row, 5).text()
                break
        else:
            QMessageBox.warning(self, "Error", "No se encontró el control seleccionado")
            return

        self.status_bar.showMessage(f"Cargando detalles del control ID: {control_id}...")
        
        # Crear un mensaje detallado con HTML para mejor formato
        mensaje = f"""
        <h2>Control de Calidad #{control_id}</h2>
        <p><b>Orden de Producción:</b> {orden_produccion}</p>
        <p><b>Fecha:</b> {fecha}</p>
        <p><b>Resultado:</b> {resultado}</p>
        <p><b>Usuario:</b> {usuario}</p>
        <p><b>Observaciones:</b><br>{observaciones}</p>
        """
        
        QMessageBox.information(self, "Detalles del Control", mensaje)
        self.status_bar.showMessage(f"Visualizando control ID: {control_id}")

    def on_add_control(self):
        """Muestra el diálogo para añadir un nuevo control"""
        self.status_bar.showMessage("Abriendo formulario para nuevo control...")
        from .quality_control_form import QualityControlForm
        dialog = QualityControlForm(self.api_client)
        dialog.control_saved.connect(self._handle_control_save)
        dialog.exec()

    def on_edit_control(self, control_id):
        """Abre el formulario de edición de un control"""
        self.status_bar.showMessage(f"Cargando formulario de edición para control ID: {control_id}...")
        # Cargar datos del control desde el modelo actual
        control = self._get_control_by_id(control_id)
        if control:
            self._show_edit_form(control)
        else:
            QMessageBox.warning(self, "Error", "No se pudo cargar el control")

    def _get_control_by_id(self, control_id):
        """Busca un control por su ID en el modelo actual"""
        for row in range(self.control_model.rowCount()):
            if int(self.control_model.item(row, 0).text()) == control_id:
                from models.quality_control_model import QualityControl
                
                control_data = {
                    "id_control": self.control_model.item(row, 0).text(),
                    "id_orden_produccion": self.control_model.item(row, 1).text(),
                    "fecha": self.control_model.item(row, 2).text(),
                    "resultado": self.control_model.item(row, 3).text().lower(),
                    "observaciones": self.control_model.item(row, 4).text(),
                    "id_usuario": self.control_model.item(row, 5).text()
                }
                return QualityControl.from_dict(control_data)
        return None

    def _show_edit_form(self, control):
        """Muestra el formulario de edición con los datos del control"""
        from .quality_control_form import QualityControlForm
        if control:
            dialog = QualityControlForm(self.api_client, control.to_dict())
            dialog.control_saved.connect(self._handle_control_save)
            dialog.exec()
        else:
            QMessageBox.warning(self, "Error", "No se pudo cargar el control")

    def _handle_control_save(self, control_data):
        """Maneja el guardado de un control (nuevo o editado)"""
        if "id_control" in control_data and control_data["id_control"]:
            # Actualizar control
            self.api_client.update_quality_control(control_data["id_control"], control_data)
            self.status_bar.showMessage(f"Actualizando control ID: {control_data['id_control']}...")
        else:
            # Crear control
            self.api_client.create_quality_control(control_data)
            self.status_bar.showMessage("Creando nuevo control...")

    def on_delete_control(self, control_id):
        """Elimina un control de calidad"""
        reply = QMessageBox.question(
            self,
            "Confirmar eliminación",
            f"¿Está seguro que desea eliminar el control ID: {control_id}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.api_client.delete_quality_control(control_id)
            self.status_bar.showMessage(f"Eliminando control ID: {control_id}...")