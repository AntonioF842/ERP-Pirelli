from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableView, QHeaderView, QLineEdit, QComboBox, QFrame,
    QMessageBox, QMenu, QDialog, QFormLayout, QDialogButtonBox,
    QAbstractItemView, QSplitter, QToolBar, QStatusBar, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal, QSortFilterProxyModel, QThread, QSize
from PyQt6.QtGui import QIcon, QAction, QStandardItemModel, QStandardItem, QFont, QColor
from utils.theme import Theme

class LegalRegulationListView(QWidget):
    """Vista de listado de normativas legales para ERP Pirelli"""

    # Señales
    regulation_selected = pyqtSignal(int)  # Emitida cuando se selecciona una normativa

    def __init__(self, api_client):
        super().__init__()
        from utils.theme import Theme
        Theme.apply_window_light_theme(self)

        self.api_client = api_client

        # Conectar señales del cliente API
        self.api_client.data_received.connect(self.on_data_loaded)
        self.api_client.request_error.connect(self.on_request_error)

        # Modelo para la tabla
        self.regulation_model = QStandardItemModel()
        self.regulation_model.setHorizontalHeaderLabels([
            "ID", "Nombre", "Tipo", "Tipo Valor", "Descripción", "Fecha Actualización", "Aplicable a"
        ])

        # Modelo proxy para filtrado avanzado
        self.proxy_model = QSortFilterProxyModel()
        self.proxy_model.setSourceModel(self.regulation_model)
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
        title_label = QLabel("Gestión de Normativas Legales")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        main_layout.addWidget(title_label)

        # Barra de herramientas
        toolbar_layout = QHBoxLayout()

        # Filtro de tipo
        self.type_filter = QComboBox()
        self.type_filter.addItem("Todos los tipos", "")
        self.type_filter.addItem("Ambiental", "ambiental")
        self.type_filter.addItem("Seguridad", "seguridad")
        self.type_filter.addItem("Laboral", "laboral")
        self.type_filter.addItem("Calidad", "calidad")
        self.type_filter.currentIndexChanged.connect(self.on_type_changed)

        # Campo de búsqueda
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Buscar por nombre o descripción...")
        self.search_input.textChanged.connect(self.on_search_changed)

        # Botón de búsqueda
        search_btn = QPushButton("Buscar")
        search_btn.clicked.connect(self._on_filters_changed)

        # Botón para añadir
        self.add_btn = QPushButton("Nueva Normativa")
        self.add_btn.setIcon(QIcon("resources/icons/add.png"))
        self.add_btn.clicked.connect(self.on_add_regulation)

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

        # Tabla de normativas
        self.regulation_table = QTableView()
        self.regulation_table.setModel(self.proxy_model)
        self.regulation_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.regulation_table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.regulation_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.regulation_table.setAlternatingRowColors(True)
        self.regulation_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.regulation_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)  # ID
        self.regulation_table.verticalHeader().setVisible(False)
        self.regulation_table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.regulation_table.customContextMenuRequested.connect(self.show_context_menu)
        self.regulation_table.doubleClicked.connect(self.on_row_double_clicked)
        
        main_layout.addWidget(self.regulation_table)

        # Labels de totales
        summary_layout = QHBoxLayout()
        self.total_label = QLabel("Total de normativas: <b>0</b>")

        summary_layout.addWidget(self.total_label)
        summary_layout.addStretch()
        main_layout.addLayout(summary_layout)

        # Barra de estado
        self.status_bar = QStatusBar()
        self.status_bar.showMessage("Sistema ERP Pirelli - Módulo de Normativas Legales v1.0")
        main_layout.addWidget(self.status_bar)

    def setup_filter_proxy(self):
        """Configura el modelo proxy para filtrado avanzado"""
        self.proxy_model.filterAcceptsRow = self._filter_accepts_row
    
    def _filter_accepts_row(self, source_row, source_parent):
        """Método personalizado para determinar si una fila cumple con los filtros"""
        model = self.regulation_model
        
        # Obtener valores de los filtros
        search_text = self.search_input.text().strip().lower()
        type_filter = self.type_filter.currentData()
        
        # Si no hay filtros activos, mostrar todas las filas
        if not search_text and not type_filter:
            return True
            
        # Obtener valores de la fila actual
        try:
            nombre = model.item(source_row, 1).text().lower()
            tipo_valor = model.item(source_row, 3).text().lower()  # columna oculta con valor interno
            descripcion = model.item(source_row, 4).text().lower()
            
            # Filtro de búsqueda (nombre o descripción)
            if search_text and not (search_text in nombre or search_text in descripcion):
                return False
                
            # Filtro de tipo (compara valor interno exacto)
            if type_filter and type_filter != tipo_valor:
                return False
                
            return True
        except (AttributeError, IndexError):
            # En caso de error, mostrar la fila
            return True

    def on_search_changed(self, text):
        """Maneja el cambio en el campo de búsqueda"""
        self.proxy_model.setFilterWildcard(text)
        self.proxy_model.invalidateFilter()
        self.status_bar.showMessage(f"Filtrando normativas por: {text}" if text else "Sistema ERP Pirelli - Módulo de Normativas Legales v1.0")

    def on_type_changed(self, index):
        """Maneja el cambio en el filtro de tipo"""
        self._on_filters_changed()

    def _on_filters_changed(self):
        """Se llama cuando cambia tipo, para actualizar el filtrado sobre la tabla"""
        self.proxy_model.invalidateFilter()
        type_filter = self.type_filter.currentData()
        
        msg = "Mostrando normativas"
        if type_filter:
            msg += f" del tipo: {self.type_filter.currentText()}"
        if not type_filter:
            msg = "Sistema ERP Pirelli - Módulo de Normativas Legales v1.0"
            
        self.status_bar.showMessage(msg)

    def clear_filters(self):
        """Limpia todos los filtros aplicados"""
        self.search_input.clear()
        self.type_filter.setCurrentIndex(0)
        self.proxy_model.invalidateFilter()
        self.status_bar.showMessage("Filtros eliminados")

    def refresh_data(self):
        """Actualiza los datos de la tabla desde la API"""
        self.status_bar.showMessage("Actualizando datos de normativas legales...")
        self.api_client.get_legal_regulations()

    def load_regulations(self, regulations):
        """Carga las normativas recibidas en la tabla y actualiza estadísticas"""
        # Limpiar modelo actual
        self.regulation_model.removeRows(0, self.regulation_model.rowCount())

        for regulation in regulations:
            row = []

            # ID
            id_item = QStandardItem(str(regulation.id_normativa))
            id_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            row.append(id_item)

            # Nombre
            name_item = QStandardItem(regulation.nombre)
            font = QFont()
            font.setBold(True)
            name_item.setFont(font)
            row.append(name_item)

            # Tipo (display)
            type_item = QStandardItem(regulation.get_type_display())
            row.append(type_item)

            # Tipo (valor interno, columna oculta)
            type_value_item = QStandardItem(regulation.tipo)
            row.append(type_value_item)
            
            # Descripción
            desc_item = QStandardItem(regulation.descripcion_display)
            row.append(desc_item)

            # Fecha Actualización
            date_item = QStandardItem(regulation.fecha_actualizacion if regulation.fecha_actualizacion else "N/A")
            date_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            row.append(date_item)

            # Aplicable a
            aplicable_item = QStandardItem(regulation.aplicable_a if regulation.aplicable_a else "N/A")
            row.append(aplicable_item)

            self.regulation_model.appendRow(row)
            
        # Oculta la columna de valor interno de tipo (índice 3)
        self.regulation_table.setColumnHidden(3, True)

        total = len(regulations)
        self.total_label.setText(f"Total de normativas: <b>{total}</b>")
        self.status_bar.showMessage(f"Se han cargado {total} normativas")

    def on_data_loaded(self, data):
        """Maneja los datos cargados desde la API directa"""
        if data.get("type") == "legal_regulations":
            # Convertir datos API a objetos normativa
            from models.legal_regulation_model import LegalRegulation
            regulations = [LegalRegulation.from_dict(item) for item in data.get("data", [])]
            self.load_regulations(regulations)
        elif data.get("type") == "legal_regulation_created":
            QMessageBox.information(self, "Éxito", "Normativa creada correctamente")
            self.refresh_data()
        elif data.get("type") == "legal_regulation_updated":
            QMessageBox.information(self, "Éxito", "Normativa actualizada correctamente")
            self.refresh_data()
        elif data.get("type") == "legal_regulation_deleted":
            QMessageBox.information(self, "Éxito", "Normativa eliminada correctamente")
            self.refresh_data()

    def on_request_error(self, error_message):
        """Maneja errores de la API"""
        QMessageBox.critical(self, "Error", f"Error al cargar normativas: {error_message}")
        self.status_bar.showMessage(f"Error: {error_message}")

    def on_row_double_clicked(self, index):
        """Maneja el doble clic en una fila"""
        mapped_index = self.proxy_model.mapToSource(index)
        row = mapped_index.row()
        regulation_id = int(self.regulation_model.item(row, 0).text())
        self.regulation_selected.emit(regulation_id)
        self.on_view_regulation(regulation_id)

    def show_context_menu(self, position):
        """Muestra menú contextual para una fila"""
        index = self.regulation_table.indexAt(position)
        if not index.isValid():
            return

        context_menu = QMenu(self)
        # Acciones principales
        view_action = QAction(QIcon("resources/icons/view.png"), "Ver detalles", self)
        edit_action = QAction(QIcon("resources/icons/edit.png"), "Editar", self)
        delete_action = QAction(QIcon("resources/icons/delete.png"), "Eliminar", self)
        # Extra
        history_action = QAction(QIcon("resources/icons/history.png"), "Historial", self)

        context_menu.addAction(view_action)
        context_menu.addAction(edit_action)
        context_menu.addSeparator()
        context_menu.addAction(history_action)
        context_menu.addSeparator()
        context_menu.addAction(delete_action)

        mapped_index = self.proxy_model.mapToSource(index)
        row = mapped_index.row()
        regulation_id = int(self.regulation_model.item(row, 0).text())

        view_action.triggered.connect(lambda: self.on_view_regulation(regulation_id))
        edit_action.triggered.connect(lambda: self.on_edit_regulation(regulation_id))
        delete_action.triggered.connect(lambda: self.on_delete_regulation(regulation_id))
        history_action.triggered.connect(lambda: self.status_bar.showMessage(f"Mostrando historial de la normativa ID: {regulation_id}"))

        context_menu.exec(self.regulation_table.viewport().mapToGlobal(position))

    def _get_selected_regulation_id(self, callback_func):
        """Obtiene el ID de la normativa seleccionada y llama al callback"""
        indexes = self.regulation_table.selectionModel().selectedRows()
        if not indexes:
            QMessageBox.information(self, "Selección", "Por favor, seleccione una normativa primero")
            return
        # Obtener el ID de la normativa seleccionada (columna 0)
        mapped_index = self.proxy_model.mapToSource(indexes[0])
        row = mapped_index.row()
        regulation_id = int(self.regulation_model.item(row, 0).text())
        # Llamar al callback con el ID
        callback_func(regulation_id)

    def on_view_regulation(self, regulation_id):
        """Muestra detalles de una normativa"""
        # Buscar la fila en el modelo
        for row in range(self.regulation_model.rowCount()):
            if int(self.regulation_model.item(row, 0).text()) == regulation_id:
                nombre = self.regulation_model.item(row, 1).text()
                tipo = self.regulation_model.item(row, 2).text()
                descripcion = self.regulation_model.item(row, 4).text()
                fecha_actualizacion = self.regulation_model.item(row, 5).text()
                aplicable_a = self.regulation_model.item(row, 6).text()
                break
        else:
            QMessageBox.warning(self, "Error", "No se encontró la normativa seleccionada")
            return

        self.status_bar.showMessage(f"Cargando detalles de la normativa ID: {regulation_id}...")
        
        # Crear un mensaje detallado con HTML para mejor formato
        mensaje = f"""
        <h2>{nombre}</h2>
        <p><b>Tipo:</b> {tipo}</p>
        <p><b>Fecha Actualización:</b> {fecha_actualizacion}</p>
        <p><b>Aplicable a:</b> {aplicable_a}</p>
        <p><b>Descripción:</b><br>{descripcion}</p>
        """
        
        QMessageBox.information(self, "Detalles de la Normativa", mensaje)
        self.status_bar.showMessage(f"Visualizando normativa ID: {regulation_id}")

    def on_add_regulation(self):
        """Muestra el diálogo para añadir una nueva normativa"""
        self.status_bar.showMessage("Abriendo formulario para nueva normativa...")
        from .legal_regulation_form import LegalRegulationForm
        dialog = LegalRegulationForm(self.api_client)
        dialog.regulation_saved.connect(self._handle_regulation_save)
        dialog.exec()

    def on_edit_regulation(self, regulation_id):
        """Abre el formulario de edición de una normativa"""
        self.status_bar.showMessage(f"Cargando formulario de edición para normativa ID: {regulation_id}...")
        # Cargar datos de la normativa desde el modelo actual
        regulation = self._get_regulation_by_id(regulation_id)
        if regulation:
            self._show_edit_form(regulation)
        else:
            QMessageBox.warning(self, "Error", "No se pudo cargar la normativa")

    def _get_regulation_by_id(self, regulation_id):
        """Busca una normativa por su ID en el modelo actual"""
        for row in range(self.regulation_model.rowCount()):
            if int(self.regulation_model.item(row, 0).text()) == regulation_id:
                from models.legal_regulation_model import LegalRegulation
                
                regulation_data = {
                    "id_normativa": self.regulation_model.item(row, 0).text(),
                    "nombre": self.regulation_model.item(row, 1).text(),
                    "tipo": self.regulation_model.item(row, 3).text(),  # Usamos el valor interno de tipo
                    "descripcion": self.regulation_model.item(row, 4).text(),
                    "fecha_actualizacion": self.regulation_model.item(row, 5).text(),
                    "aplicable_a": self.regulation_model.item(row, 6).text()
                }
                return LegalRegulation.from_dict(regulation_data)
        return None

    def _show_edit_form(self, regulation):
        """Muestra el formulario de edición con los datos de la normativa"""
        from .legal_regulation_form import LegalRegulationForm
        if regulation:
            dialog = LegalRegulationForm(self.api_client, regulation.to_dict())
            dialog.regulation_saved.connect(self._handle_regulation_save)
            dialog.exec()
        else:
            QMessageBox.warning(self, "Error", "No se pudo cargar la normativa")

    def _handle_regulation_save(self, regulation_data):
        """Maneja el guardado de una normativa (nueva o editada)"""
        if "id_normativa" in regulation_data and regulation_data["id_normativa"]:
            # Actualizar normativa
            self.api_client.update_legal_regulation(regulation_data["id_normativa"], regulation_data)
            self.status_bar.showMessage(f"Actualizando normativa ID: {regulation_data['id_normativa']}...")
        else:
            # Crear normativa
            self.api_client.create_legal_regulation(regulation_data)
            self.status_bar.showMessage("Creando nueva normativa...")

    def on_delete_regulation(self, regulation_id):
        """Elimina una normativa"""
        reply = QMessageBox.question(
            self,
            "Confirmar eliminación",
            f"¿Está seguro que desea eliminar la normativa ID: {regulation_id}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.api_client.delete_legal_regulation(regulation_id)
            self.status_bar.showMessage(f"Eliminando normativa ID: {regulation_id}...")