from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableView, QHeaderView, QLineEdit, QComboBox, QFrame,
    QMessageBox, QMenu, QDialog, QFormLayout, QDialogButtonBox,
    QAbstractItemView, QSplitter, QToolBar, QStatusBar, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal, QSortFilterProxyModel, QThread, QSize
from PyQt6.QtGui import QIcon, QAction, QStandardItemModel, QStandardItem, QFont, QColor
from utils.theme import Theme

class ClientListView(QWidget):
    """Vista de listado de clientes para ERP Pirelli"""

    # Señales
    client_selected = pyqtSignal(int)  # Emitida cuando se selecciona un cliente

    def __init__(self, api_client):
        super().__init__()
        from utils.theme import Theme
        Theme.apply_window_light_theme(self)

        self.api_client = api_client

        # Conectar señales del cliente API
        self.api_client.data_received.connect(self.on_data_loaded)
        self.api_client.request_error.connect(self.on_request_error)

        # Modelo para la tabla
        self.client_model = QStandardItemModel()
        self.client_model.setHorizontalHeaderLabels([
            "ID", "Nombre", "Contacto", "Teléfono", "Email", "Tipo", "Tipo Valor", "Dirección"
        ])

        # Modelo proxy para filtrado avanzado
        self.proxy_model = QSortFilterProxyModel()
        self.proxy_model.setSourceModel(self.client_model)
        self.proxy_model.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.proxy_model.setFilterKeyColumn(-1)  # Buscar en todas las columnas
        self.setup_filter_proxy()

        # Colores corporativos Pirelli
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
        title_label = QLabel("Gestión de Clientes")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        main_layout.addWidget(title_label)

        # Barra de herramientas
        toolbar_layout = QHBoxLayout()

        # Filtro de tipo de cliente
        self.type_filter = QComboBox()
        self.type_filter.addItem("Todos los tipos", "")
        self.type_filter.addItem("Distribuidor", "distribuidor")
        self.type_filter.addItem("Mayorista", "mayorista")
        self.type_filter.addItem("Minorista", "minorista")
        self.type_filter.addItem("OEM", "OEM")
        self.type_filter.currentIndexChanged.connect(self.on_type_changed)

        # Campo de búsqueda
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Buscar por nombre o email...")
        self.search_input.textChanged.connect(self.on_search_changed)

        # Botón de búsqueda
        search_btn = QPushButton("Buscar")
        search_btn.clicked.connect(self._on_filters_changed)

        # Botón para añadir
        self.add_btn = QPushButton("Nuevo Cliente")
        self.add_btn.setIcon(QIcon("resources/icons/add.png"))
        self.add_btn.clicked.connect(self.on_add_client)

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

        # Tabla de clientes
        self.client_table = QTableView()
        self.client_table.setModel(self.proxy_model)
        self.client_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.client_table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.client_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.client_table.setAlternatingRowColors(True)
        self.client_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.client_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)  # ID
        self.client_table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)  # Tipo
        self.client_table.verticalHeader().setVisible(False)
        self.client_table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.client_table.customContextMenuRequested.connect(self.show_context_menu)
        self.client_table.doubleClicked.connect(self.on_row_double_clicked)
        
        main_layout.addWidget(self.client_table)

        # Labels de totales
        summary_layout = QHBoxLayout()
        self.total_label = QLabel("Total de clientes: <b>0</b>")
        self.distributor_label = QLabel("Distribuidores: <b>0</b>")
        self.wholesaler_label = QLabel("Mayoristas: <b>0</b>")
        self.retailer_label = QLabel("Minoristas: <b>0</b>")
        self.oem_label = QLabel("OEM: <b>0</b>")

        summary_layout.addWidget(self.total_label)
        summary_layout.addSpacing(20)
        summary_layout.addWidget(self.distributor_label)
        summary_layout.addSpacing(20)
        summary_layout.addWidget(self.wholesaler_label)
        summary_layout.addSpacing(20)
        summary_layout.addWidget(self.retailer_label)
        summary_layout.addSpacing(20)
        summary_layout.addWidget(self.oem_label)
        summary_layout.addStretch()
        main_layout.addLayout(summary_layout)

        # Barra de estado
        self.status_bar = QStatusBar()
        self.status_bar.showMessage("Sistema ERP Pirelli - Módulo de Gestión de Clientes v2.1")
        main_layout.addWidget(self.status_bar)

    def setup_filter_proxy(self):
        """Configura el modelo proxy para filtrado avanzado"""
        # Sobrescribe el método filterAcceptsRow del proxy model
        self.proxy_model.filterAcceptsRow = self._filter_accepts_row
    
    def _filter_accepts_row(self, source_row, source_parent):
        """Método personalizado para determinar si una fila cumple con los filtros"""
        model = self.client_model
        
        # Obtener valores de los filtros
        search_text = self.search_input.text().strip().lower()
        client_type = self.type_filter.currentData()
        
        # Si no hay filtros activos, mostrar todas las filas
        if not search_text and not client_type:
            return True
            
        # Obtener valores de la fila actual
        try:
            nombre = model.item(source_row, 1).text().lower()
            email = model.item(source_row, 4).text().lower()
            tipo_valor = model.item(source_row, 6).text().lower()  # columna oculta con valor interno
            
            # Filtro de búsqueda (nombre o email)
            if search_text and not (search_text in nombre or search_text in email):
                return False
                
            # Filtro de tipo (compara valor interno exacto)
            if client_type and client_type != tipo_valor:
                return False
                
            return True
        except (AttributeError, IndexError):
            # En caso de error, mostrar la fila
            return True

    def on_search_changed(self, text):
        """Maneja el cambio en el campo de búsqueda"""
        self.proxy_model.setFilterWildcard(text)
        self.proxy_model.invalidateFilter()
        self.status_bar.showMessage(f"Filtrando clientes por: {text}" if text else "Sistema ERP Pirelli - Módulo de Gestión de Clientes v2.1")

    def on_type_changed(self, index):
        """Maneja el cambio en el filtro de tipo de cliente"""
        self._on_filters_changed()

    def _on_filters_changed(self):
        """Se llama cuando cambia el tipo de cliente, para actualizar el filtrado"""
        self.proxy_model.invalidateFilter()
        client_type = self.type_filter.currentData()
        
        msg = "Mostrando clientes"
        if client_type:
            msg += f" del tipo: {self.type_filter.currentText()}"
        else:
            msg = "Sistema ERP Pirelli - Módulo de Gestión de Clientes v2.1"
            
        self.status_bar.showMessage(msg)

    def clear_filters(self):
        """Limpia todos los filtros aplicados"""
        self.search_input.clear()
        self.type_filter.setCurrentIndex(0)
        self.proxy_model.invalidateFilter()
        self.status_bar.showMessage("Filtros eliminados")

    def refresh_data(self):
        """Actualiza los datos de la tabla desde la API"""
        self.status_bar.showMessage("Actualizando datos de clientes...")
        self.api_client.get_clients()

    def load_clients(self, clients):
        """Carga los clientes recibidos en la tabla y actualiza estadísticas"""
        # Limpiar modelo actual
        self.client_model.removeRows(0, self.client_model.rowCount())
        count_distributor = count_wholesaler = count_retailer = count_oem = 0

        for client in clients:
            row = []

            # ID
            id_item = QStandardItem(str(client.id_cliente))
            id_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            row.append(id_item)

            # Nombre
            name_item = QStandardItem(client.nombre)
            font = QFont()
            font.setBold(True)
            name_item.setFont(font)
            row.append(name_item)

            # Contacto
            contact_item = QStandardItem(client.contacto_display)
            row.append(contact_item)

            # Teléfono
            phone_item = QStandardItem(client.telefono if client.telefono else "N/A")
            row.append(phone_item)

            # Email
            email_item = QStandardItem(client.email)
            row.append(email_item)

            # Tipo (display)
            type_item = QStandardItem(client.get_tipo_display())
            row.append(type_item)

            # Tipo (valor interno, columna oculta)
            type_value_item = QStandardItem(client.tipo)
            row.append(type_value_item)
            
            # Dirección (columna oculta)
            address_item = QStandardItem(client.direccion if client.direccion else "Sin dirección")
            row.append(address_item)

            # Contar por tipo
            if client.tipo == "distribuidor":
                count_distributor += 1
            elif client.tipo == "mayorista":
                count_wholesaler += 1
            elif client.tipo == "minorista":
                count_retailer += 1
            elif client.tipo == "OEM":
                count_oem += 1

            self.client_model.appendRow(row)
            
        # Oculta la columna de valor interno de tipo (índice 6) y dirección (índice 7)
        self.client_table.setColumnHidden(6, True)
        self.client_table.setColumnHidden(7, True)

        total = len(clients)
        self.total_label.setText(f"Total de clientes: <b>{total}</b>")
        self.distributor_label.setText(f"Distribuidores: <b>{count_distributor}</b>")
        self.wholesaler_label.setText(f"Mayoristas: <b>{count_wholesaler}</b>")
        self.retailer_label.setText(f"Minoristas: <b>{count_retailer}</b>")
        self.oem_label.setText(f"OEM: <b>{count_oem}</b>")
        self.status_bar.showMessage(f"Se han cargado {total} clientes")

    def on_data_loaded(self, data):
        """Maneja los datos cargados desde la API directa"""
        if data.get("type") == "clients":
            # Convertir datos API a objetos cliente
            from models.client_model import Client
            clients = [Client.from_dict(item) for item in data.get("data", [])]
            self.load_clients(clients)
        elif data.get("type") == "client_created":
            QMessageBox.information(self, "Éxito", "Cliente creado correctamente")
            self.refresh_data()
        elif data.get("type") == "client_updated":
            QMessageBox.information(self, "Éxito", "Cliente actualizado correctamente")
            self.refresh_data()
        elif data.get("type") == "client_deleted":
            QMessageBox.information(self, "Éxito", "Cliente eliminado correctamente")
            self.refresh_data()

    def on_request_error(self, error_message):
        """Maneja errores de la API"""
        QMessageBox.critical(self, "Error", f"Error al cargar clientes: {error_message}")
        self.status_bar.showMessage(f"Error: {error_message}")

    def on_row_double_clicked(self, index):
        """Maneja el doble clic en una fila"""
        mapped_index = self.proxy_model.mapToSource(index)
        row = mapped_index.row()
        client_id = int(self.client_model.item(row, 0).text())
        self.client_selected.emit(client_id)
        self.on_view_client(client_id)

    def show_context_menu(self, position):
        """Muestra menú contextual para una fila"""
        index = self.client_table.indexAt(position)
        if not index.isValid():
            return

        context_menu = QMenu(self)
        # Acciones principales
        view_action = QAction(QIcon("resources/icons/view.png"), "Ver detalles", self)
        edit_action = QAction(QIcon("resources/icons/edit.png"), "Editar", self)
        delete_action = QAction(QIcon("resources/icons/delete.png"), "Eliminar", self)
        # Extra
        sales_action = QAction(QIcon("resources/icons/sales.png"), "Historial de compras", self)
        notes_action = QAction(QIcon("resources/icons/notes.png"), "Agregar nota", self)

        context_menu.addAction(view_action)
        context_menu.addAction(edit_action)
        context_menu.addSeparator()
        context_menu.addAction(sales_action)
        context_menu.addAction(notes_action)
        context_menu.addSeparator()
        context_menu.addAction(delete_action)

        mapped_index = self.proxy_model.mapToSource(index)
        row = mapped_index.row()
        client_id = int(self.client_model.item(row, 0).text())

        view_action.triggered.connect(lambda: self.on_view_client(client_id))
        edit_action.triggered.connect(lambda: self.on_edit_client(client_id))
        delete_action.triggered.connect(lambda: self.on_delete_client(client_id))
        sales_action.triggered.connect(lambda: self.status_bar.showMessage(f"Mostrando historial de compras del cliente ID: {client_id}"))
        notes_action.triggered.connect(lambda: self.status_bar.showMessage(f"Agregando nota al cliente ID: {client_id}"))

        context_menu.exec(self.client_table.viewport().mapToGlobal(position))

    def _get_selected_client_id(self, callback_func):
        """Obtiene el ID del cliente seleccionado y llama al callback"""
        indexes = self.client_table.selectionModel().selectedRows()
        if not indexes:
            QMessageBox.information(self, "Selección", "Por favor, seleccione un cliente primero")
            return
        # Obtener el ID del cliente seleccionado (columna 0)
        mapped_index = self.proxy_model.mapToSource(indexes[0])
        row = mapped_index.row()
        client_id = int(self.client_model.item(row, 0).text())
        # Llamar al callback con el ID
        callback_func(client_id)

    def on_view_client(self, client_id):
        """Muestra detalles de un cliente, incluyendo la dirección"""
        # Buscar la fila en el modelo
        for row in range(self.client_model.rowCount()):
            if int(self.client_model.item(row, 0).text()) == client_id:
                nombre = self.client_model.item(row, 1).text()
                contacto = self.client_model.item(row, 2).text()
                telefono = self.client_model.item(row, 3).text()
                email = self.client_model.item(row, 4).text()
                tipo = self.client_model.item(row, 5).text()
                
                # Obtener dirección de forma segura y robusta
                direccion_item = self.client_model.item(row, 7)
                direccion = ""
                if direccion_item is not None:
                    direccion = direccion_item.text() or ""
                if not direccion.strip():
                    direccion = "Sin dirección disponible"
                break
        else:
            QMessageBox.warning(self, "Error", "No se encontró el cliente seleccionado")
            return

        self.status_bar.showMessage(f"Cargando detalles del cliente ID: {client_id}...")
        
        # Crear un mensaje detallado con HTML para mejor formato
        mensaje = f"""
        <h2>{nombre}</h2>
        <p><b>Contacto:</b> {contacto}</p>
        <p><b>Teléfono:</b> {telefono}</p>
        <p><b>Email:</b> {email}</p>
        <p><b>Tipo:</b> {tipo}</p>
        <p><b>Dirección:</b><br>{direccion}</p>
        """
        
        QMessageBox.information(self, "Detalles del Cliente", mensaje)
        self.status_bar.showMessage(f"Visualizando cliente ID: {client_id}")

    def on_add_client(self):
        """Muestra el diálogo para añadir un nuevo cliente"""
        self.status_bar.showMessage("Abriendo formulario para nuevo cliente...")
        from .client_form import ClientForm
        dialog = ClientForm(self.api_client)
        dialog.client_saved.connect(self._handle_client_save)
        dialog.exec()

    def on_edit_client(self, client_id):
        """Abre el formulario de edición de un cliente"""
        self.status_bar.showMessage(f"Cargando formulario de edición para cliente ID: {client_id}...")
        # Cargar datos del cliente desde el modelo actual
        client = self._get_client_by_id(client_id)
        if client:
            self._show_edit_form(client)
        else:
            QMessageBox.warning(self, "Error", "No se pudo cargar el cliente")

    def _get_client_by_id(self, client_id):
        """Busca un cliente por su ID en el modelo actual"""
        for row in range(self.client_model.rowCount()):
            if int(self.client_model.item(row, 0).text()) == client_id:
                from models.client_model import Client
                
                # Obtener dirección de forma segura y robusta
                direccion_item = self.client_model.item(row, 7)
                direccion = ""
                if direccion_item is not None:
                    direccion = direccion_item.text() or ""
                if not direccion.strip():
                    direccion = "Sin dirección disponible"
                
                client_data = {
                    "id_cliente": self.client_model.item(row, 0).text(),
                    "nombre": self.client_model.item(row, 1).text(),
                    "contacto": self.client_model.item(row, 2).text(),
                    "telefono": self.client_model.item(row, 3).text(),
                    "email": self.client_model.item(row, 4).text(),
                    "tipo": self.client_model.item(row, 6).text(),  # Usamos el valor interno de tipo
                    "direccion": direccion
                }
                return Client.from_dict(client_data)
        return None

    def _show_edit_form(self, client):
        """Muestra el formulario de edición con los datos del cliente"""
        from .client_form import ClientForm
        if client:
            dialog = ClientForm(self.api_client, client.to_dict())
            dialog.client_saved.connect(self._handle_client_save)
            dialog.exec()
        else:
            QMessageBox.warning(self, "Error", "No se pudo cargar el cliente")

    def _handle_client_save(self, client_data):
        """Maneja el guardado de un cliente (nuevo o editado)"""
        if "id_cliente" in client_data and client_data["id_cliente"]:
            # Actualizar cliente
            self.api_client.update_client(client_data["id_cliente"], client_data)
            self.status_bar.showMessage(f"Actualizando cliente ID: {client_data['id_cliente']}...")
        else:
            # Crear cliente
            self.api_client.create_client(client_data)
            self.status_bar.showMessage("Creando nuevo cliente...")

    def on_delete_client(self, client_id):
        """Elimina un cliente"""
        reply = QMessageBox.question(
            self,
            "Confirmar eliminación",
            f"¿Está seguro que desea eliminar el cliente ID: {client_id}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.api_client.delete_client(client_id)
            self.status_bar.showMessage(f"Eliminando cliente ID: {client_id}...")