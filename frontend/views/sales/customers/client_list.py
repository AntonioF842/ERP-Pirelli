from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableView, QHeaderView, QLineEdit, QComboBox, QFrame,
    QMessageBox, QMenu, QDialog, QFormLayout, QDialogButtonBox,
    QAbstractItemView, QSplitter, QToolBar, QStatusBar, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal, QSortFilterProxyModel, QThread, QSize
from PyQt6.QtGui import QIcon, QAction, QStandardItemModel, QStandardItem, QFont, QColor
from utils.theme import Theme
from models.client_model import Client
import logging

logger = logging.getLogger(__name__)

class ClientListView(QWidget):
    """Vista de listado de clientes para ERP Pirelli"""

    # Señales
    client_selected = pyqtSignal(int)  # Emitida cuando se selecciona un cliente
    refresh_requested = pyqtSignal()   # Emitida cuando se solicita actualización

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
        self.client_model = QStandardItemModel()
        self.client_model.setHorizontalHeaderLabels([
            "ID", "Nombre", "Contacto", "Teléfono", "Email", 
            "Tipo", "Tipo Valor", "Dirección"
        ])
        
        # Modelo proxy para filtrado
        self.proxy_model = QSortFilterProxyModel()
        self.proxy_model.setSourceModel(self.client_model)
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
        title_label = QLabel("Gestión de Clientes")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        main_layout.addWidget(title_label)

        # Barra de herramientas
        toolbar_layout = QHBoxLayout()
        
        # Filtro de tipo de cliente
        self.type_filter = QComboBox()
        self.type_filter.addItem("Todos los tipos", "")
        for value, display in Client.get_tipos_lista():
            self.type_filter.addItem(display, value)
        
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
        toolbar_layout.addWidget(QLabel("Tipo:"))
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
        
        # Ocultar columnas internas
        self.client_table.setColumnHidden(6, True)  # Tipo Valor
        self.client_table.setColumnHidden(7, True)  # Dirección
        
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
        self.status_bar.showMessage("Sistema ERP Pirelli - Módulo de Gestión de Clientes")
        main_layout.addWidget(self.status_bar)

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
            tipo_valor = model.item(source_row, 6).text().lower()
            
            # Filtro de búsqueda (nombre o email)
            if search_text and not (search_text in nombre or search_text in email):
                return False
                
            # Filtro de tipo
            if client_type and client_type != tipo_valor:
                return False
                
            return True
        except (AttributeError, IndexError):
            return True

    def _connect_signals(self):
        """Conecta todas las señales y slots"""
        # Conectar botones
        self.add_btn.clicked.connect(self.on_add_client)
        self.refresh_btn.clicked.connect(self.refresh_data)
        
        # Conectar filtros
        self.search_input.textChanged.connect(self.on_search_changed)
        self.type_filter.currentIndexChanged.connect(self.on_type_changed)
        
        # Conectar eventos de tabla
        self.client_table.doubleClicked.connect(self.on_row_double_clicked)
        self.client_table.customContextMenuRequested.connect(self.show_context_menu)
        
        # Señales del API Client
        self.api_client.data_received.connect(self.on_data_loaded)
        self.api_client.request_error.connect(self.on_request_error)
        self.api_client.request_success.connect(self.on_request_success)

    def refresh_data(self):
        """Solicita clientes al API"""
        self.status_bar.showMessage("Cargando clientes...")
        
        # Prepara los filtros para la API
        api_filters = {
            'tipo': self.current_filters.get('tipo'),
            'search': self.search_input.text().strip() or None
        }
        
        # Elimina filtros vacíos/None
        api_filters = {k: v for k, v in api_filters.items() if v is not None}
        
        self.api_client.get_clients()

    def load_clients(self, clients):
        """Carga los clientes en la tabla"""
        self.client_model.removeRows(0, self.client_model.rowCount())
        
        if not clients:
            self.status_bar.showMessage("No se encontraron clientes")
            return
            
        count_distributor = count_wholesaler = count_retailer = count_oem = 0
        
        for client in clients:
            if not isinstance(client, Client):
                client = Client.from_dict(client)
                
            # Contar por tipo
            if client.tipo == 'distribuidor':
                count_distributor += 1
            elif client.tipo == 'mayorista':
                count_wholesaler += 1
            elif client.tipo == 'minorista':
                count_retailer += 1
            elif client.tipo == 'OEM':
                count_oem += 1
                
            # Crear fila
            row = [
                QStandardItem(str(client.id_cliente)),
                QStandardItem(client.nombre),
                QStandardItem(client.contacto_display),
                QStandardItem(client.telefono if client.telefono else "N/A"),
                QStandardItem(client.email),
                QStandardItem(client.get_tipo_display()),
                QStandardItem(client.tipo),
                QStandardItem(client.direccion if client.direccion else "Sin dirección")
            ]
            
            # Formatear celdas
            row[0].setTextAlignment(Qt.AlignmentFlag.AlignCenter)  # ID
            
            # Estilo para nombre
            font = QFont()
            font.setBold(True)
            row[1].setFont(font)
            
            self.client_model.appendRow(row)
        
        # Actualizar resumen
        total = len(clients)
        self.total_label.setText(f"Total: <b>{total}</b>")
        self.distributor_label.setText(f"Distribuidores: <b>{count_distributor}</b>")
        self.wholesaler_label.setText(f"Mayoristas: <b>{count_wholesaler}</b>")
        self.retailer_label.setText(f"Minoristas: <b>{count_retailer}</b>")
        self.oem_label.setText(f"OEM: <b>{count_oem}</b>")
        
        self.status_bar.showMessage(f"Cargados {total} clientes")

    def show_context_menu(self, position):
        """Muestra el menú contextual para un cliente"""
        index = self.client_table.indexAt(position)
        if not index.isValid():
            return
            
        # Obtener el cliente seleccionado
        mapped_index = self.proxy_model.mapToSource(index)
        client_id = int(self.client_model.item(mapped_index.row(), 0).text())
        
        menu = QMenu(self)
        
        # Acciones principales
        view_action = menu.addAction(QIcon("resources/icons/view.png"), "Ver detalles")
        edit_action = menu.addAction(QIcon("resources/icons/edit.png"), "Editar")
        delete_action = menu.addAction(QIcon("resources/icons/delete.png"), "Eliminar")
        menu.addSeparator()
        
        # Acciones adicionales
        sales_action = menu.addAction(QIcon("resources/icons/sales.png"), "Historial de compras")
        notes_action = menu.addAction(QIcon("resources/icons/notes.png"), "Agregar nota")
        
        # Conectar acciones
        view_action.triggered.connect(lambda: self.on_view_client(client_id))
        edit_action.triggered.connect(lambda: self.on_edit_client(client_id))
        delete_action.triggered.connect(lambda: self.on_delete_client(client_id))
        sales_action.triggered.connect(lambda: self.status_bar.showMessage(f"Mostrando historial de compras del cliente ID: {client_id}"))
        notes_action.triggered.connect(lambda: self.status_bar.showMessage(f"Agregando nota al cliente ID: {client_id}"))
        
        menu.exec(self.client_table.viewport().mapToGlobal(position))

    def on_add_client(self):
        """Abre el formulario para añadir nuevo cliente"""
        from .client_form import ClientForm
        dialog = ClientForm(self.api_client, parent=self)
        dialog.client_saved.connect(self._handle_client_save)
        dialog.exec()

    def on_edit_client(self, client_id):
        """Abre el formulario para editar un cliente existente"""
        from .client_form import ClientForm
        
        # Buscar el cliente en el modelo
        for row in range(self.client_model.rowCount()):
            if int(self.client_model.item(row, 0).text()) == client_id:
                client_data = {
                    "id_cliente": client_id,
                    "nombre": self.client_model.item(row, 1).text(),
                    "contacto": self.client_model.item(row, 2).text(),
                    "telefono": self.client_model.item(row, 3).text(),
                    "email": self.client_model.item(row, 4).text(),
                    "tipo": self.client_model.item(row, 6).text(),
                    "direccion": self.client_model.item(row, 7).text()
                }
                break
        else:
            QMessageBox.warning(self, "Error", "No se pudo cargar el cliente")
            return
            
        dialog = ClientForm(self.api_client, client_data, parent=self)
        dialog.client_saved.connect(self._handle_client_save)
        dialog.exec()

    def on_view_client(self, client_id):
        """Muestra los detalles completos del cliente"""
        # Buscar el cliente en el modelo
        for row in range(self.client_model.rowCount()):
            if int(self.client_model.item(row, 0).text()) == client_id:
                nombre = self.client_model.item(row, 1).text()
                contacto = self.client_model.item(row, 2).text()
                telefono = self.client_model.item(row, 3).text()
                email = self.client_model.item(row, 4).text()
                tipo = self.client_model.item(row, 5).text()
                direccion = self.client_model.item(row, 7).text()
                break
        else:
            QMessageBox.warning(self, "Error", "Cliente no encontrado")
            return
            
        # Crear mensaje con HTML para mejor formato
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

    def on_delete_client(self, client_id):
        """Elimina un cliente con confirmación"""
        reply = QMessageBox.question(
            self,
            "Confirmar eliminación",
            f"¿Está seguro que desea eliminar el cliente ID: {client_id}?\n\n"
            "Esta acción no se puede deshacer.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.api_client.delete_client(client_id)
            self.status_bar.showMessage(f"Eliminando cliente ID: {client_id}...")

    def on_row_double_clicked(self, index):
        """Maneja el doble clic en una fila"""
        mapped_index = self.proxy_model.mapToSource(index)
        client_id = int(self.client_model.item(mapped_index.row(), 0).text())
        self.on_view_client(client_id)

    def _handle_client_save(self, client_data):
        """Maneja el guardado de un cliente"""
        if 'id_cliente' in client_data and client_data['id_cliente']:
            self.api_client.update_client(client_data['id_cliente'], client_data)
        else:
            self.api_client.create_client(client_data)

    def on_search_changed(self, text):
        """Maneja el cambio en el campo de búsqueda"""
        self.proxy_model.setFilterWildcard(text)
        self.proxy_model.invalidateFilter()
        self.status_bar.showMessage(f"Filtrando clientes por: {text}" if text else "Sistema ERP Pirelli - Módulo de Gestión de Clientes")

    def on_type_changed(self, index):
        """Maneja el cambio en el filtro de tipo de cliente"""
        self._on_filters_changed()

    def _on_filters_changed(self):
        """Se llama cuando cambian los filtros"""
        self.proxy_model.invalidateFilter()
        client_type = self.type_filter.currentData()
        
        msg = "Mostrando clientes"
        if client_type:
            msg += f" del tipo: {self.type_filter.currentText()}"
        else:
            msg = "Sistema ERP Pirelli - Módulo de Gestión de Clientes"
            
        self.status_bar.showMessage(msg)

    def on_data_loaded(self, data):
        """Maneja los datos cargados desde la API"""
        if data.get('type') == 'clients':
            clients = [Client.from_dict(item) for item in data.get('data', [])]
            self.load_clients(clients)

    def on_request_success(self, endpoint, data):
        """Maneja operaciones exitosas"""
        if endpoint in ['create_client', 'update_client', 'delete_client']:
            self.refresh_data()
            msg = {
                'create_client': "Cliente creado exitosamente",
                'update_client': "Cliente actualizado exitosamente",
                'delete_client': "Cliente eliminado exitosamente"
            }.get(endpoint, "Operación completada")
            QMessageBox.information(self, "Éxito", msg)

    def on_request_error(self, error_msg):
        """Maneja errores de la API"""
        QMessageBox.critical(self, "Error", error_msg)
        self.status_bar.showMessage(f"Error: {error_msg}")