from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableView, QHeaderView, QLineEdit, QComboBox, QFrame,
    QMessageBox, QMenu, QDialog, QFormLayout, QDialogButtonBox,
    QAbstractItemView, QSplitter, QToolBar, QStatusBar, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal, QSortFilterProxyModel, QThread, QSize
from PyQt6.QtGui import QIcon, QAction, QStandardItemModel, QStandardItem, QFont, QColor, QPixmap
from models.product_model import Product
from utils.theme import Theme
import logging

logger = logging.getLogger(__name__)

class ProductListView(QWidget):
    """Vista de listado de productos para ERP"""

    # Señales
    product_selected = pyqtSignal(int)  # Emitida cuando se selecciona un producto
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
        self.product_model = QStandardItemModel()
        self.product_model.setHorizontalHeaderLabels([
            "ID", "Código", "Nombre", "Categoría", "Valor Categoría", 
            "Descripción", "Precio", "Estado", "Valor Estado"
        ])
        
        # Modelo proxy para filtrado
        self.proxy_model = QSortFilterProxyModel()
        self.proxy_model.setSourceModel(self.product_model)
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
        title_label = QLabel("Gestión de Productos")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        main_layout.addWidget(title_label)

        # Barra de herramientas
        toolbar_layout = QHBoxLayout()
        
        # Filtro de categoría
        self.category_filter = QComboBox()
        self.category_filter.addItem("Todas las categorías", "")
        for value, display in Product.get_categorias_lista():
            self.category_filter.addItem(display, value)
        
        # Filtro de estado
        self.status_filter = QComboBox()
        self.status_filter.addItem("Todos los estados", "")
        for value, display in Product.get_estados_lista():
            self.status_filter.addItem(display, value)
        
        # Campo de búsqueda
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Buscar por nombre o código...")
        self.search_input.textChanged.connect(self.on_search_changed)

        # Botón de búsqueda
        search_btn = QPushButton("Buscar")
        search_btn.clicked.connect(self._on_filters_changed)

        # Botón para añadir
        self.add_btn = QPushButton("Nuevo Producto")
        self.add_btn.setIcon(QIcon("resources/icons/add.png"))
        self.add_btn.clicked.connect(self.on_add_product)

        # Botón de actualizar
        self.refresh_btn = QPushButton("Actualizar")
        self.refresh_btn.setIcon(QIcon("resources/icons/refresh.png"))
        self.refresh_btn.clicked.connect(self.refresh_data)

        # Agregar widgets a la barra de herramientas
        toolbar_layout.addWidget(QLabel("Categoría:"))
        toolbar_layout.addWidget(self.category_filter)
        toolbar_layout.addWidget(QLabel("Estado:"))
        toolbar_layout.addWidget(self.status_filter)
        toolbar_layout.addWidget(self.search_input)
        toolbar_layout.addWidget(search_btn)
        toolbar_layout.addStretch()
        toolbar_layout.addWidget(self.add_btn)
        toolbar_layout.addWidget(self.refresh_btn)

        main_layout.addLayout(toolbar_layout)

        # Tabla de productos
        self.product_table = QTableView()
        self.product_table.setModel(self.proxy_model)
        self.product_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.product_table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.product_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.product_table.setAlternatingRowColors(True)
        self.product_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.product_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)  # ID
        self.product_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)  # Código
        self.product_table.horizontalHeader().setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)  # Precio
        self.product_table.horizontalHeader().setSectionResizeMode(7, QHeaderView.ResizeMode.ResizeToContents)  # Estado
        self.product_table.verticalHeader().setVisible(False)
        self.product_table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.product_table.customContextMenuRequested.connect(self.show_context_menu)
        self.product_table.doubleClicked.connect(self.on_row_double_clicked)
        
        # Ocultar columnas internas
        self.product_table.setColumnHidden(4, True)  # Valor categoría
        self.product_table.setColumnHidden(5, True)  # Descripción
        self.product_table.setColumnHidden(8, True)  # Valor estado
        
        main_layout.addWidget(self.product_table)

        # Labels de totales
        summary_layout = QHBoxLayout()
        self.total_label = QLabel("Total de productos: <b>0</b>")
        self.active_label = QLabel("Activos: <b>0</b>")
        self.discontinued_label = QLabel("Descontinuados: <b>0</b>")
        self.oferta_label = QLabel("En oferta: <b>0</b>")

        summary_layout.addWidget(self.total_label)
        summary_layout.addSpacing(30)
        summary_layout.addWidget(self.active_label)
        summary_layout.addSpacing(30)
        summary_layout.addWidget(self.discontinued_label)
        summary_layout.addSpacing(30)
        summary_layout.addWidget(self.oferta_label)
        summary_layout.addStretch()
        main_layout.addLayout(summary_layout)

        # Barra de estado
        self.status_bar = QStatusBar()
        self.status_bar.showMessage("Sistema ERP - Módulo de Productos")
        main_layout.addWidget(self.status_bar)

    def setup_filter_proxy(self):
        """Configura el modelo proxy para filtrado avanzado"""
        self.proxy_model.filterAcceptsRow = self._filter_accepts_row
    
    def _filter_accepts_row(self, source_row, source_parent):
        """Método personalizado para determinar si una fila cumple con los filtros"""
        model = self.product_model
        
        # Obtener valores de los filtros
        search_text = self.search_input.text().strip().lower()
        category = self.category_filter.currentData()
        status = self.status_filter.currentData()
        
        # Si no hay filtros activos, mostrar todas las filas
        if not search_text and not category and not status:
            return True
            
        # Obtener valores de la fila actual
        try:
            codigo = model.item(source_row, 1).text().lower()
            nombre = model.item(source_row, 2).text().lower()
            categoria_valor = model.item(source_row, 4).text().lower()
            estado_valor = model.item(source_row, 8).text().lower()
            
            # Filtro de búsqueda (nombre o código)
            if search_text and not (search_text in nombre or search_text in codigo):
                return False
                
            # Filtro de categoría
            if category and category != categoria_valor:
                return False
                
            # Filtro de estado
            if status and status != estado_valor:
                return False
                
            return True
        except (AttributeError, IndexError):
            return True

    def on_search_changed(self, text):
        """Maneja el cambio en el campo de búsqueda"""
        self.proxy_model.setFilterWildcard(text)
        self.proxy_model.invalidateFilter()
        self.status_bar.showMessage(f"Filtrando productos por: {text}" if text else "Sistema ERP - Módulo de Productos")

    def on_category_changed(self, index):
        """Maneja el cambio en el filtro de categoría"""
        self._on_filters_changed()

    def on_status_changed(self, index):
        """Maneja el cambio en el filtro de estado"""
        self._on_filters_changed()

    def _on_filters_changed(self):
        """Se llama cuando cambia estado, para actualizar el filtrado"""
        self.proxy_model.invalidateFilter()
        category = self.category_filter.currentData()
        status = self.status_filter.currentData()
        
        msg = "Mostrando productos"
        if category:
            msg += f" de categoría: {self.category_filter.currentText()}"
        if status:
            msg += f" con estado: {self.status_filter.currentText()}"
            
        if not category and not status:
            msg = "Sistema ERP - Módulo de Productos"
            
        self.status_bar.showMessage(msg)

    def _connect_signals(self):
        """Conecta todas las señales y slots"""
        # Conectar botones
        self.add_btn.clicked.connect(self.on_add_product)
        self.refresh_btn.clicked.connect(self.refresh_data)
        
        # Conectar filtros
        self.search_input.textChanged.connect(self.on_search_changed)
        self.category_filter.currentIndexChanged.connect(self.on_category_changed)
        self.status_filter.currentIndexChanged.connect(self.on_status_changed)
        
        # Conectar eventos de tabla
        self.product_table.doubleClicked.connect(self.on_row_double_clicked)
        self.product_table.customContextMenuRequested.connect(self.show_context_menu)
        
        # Señales del API Client
        self.api_client.data_received.connect(self.on_data_loaded)
        self.api_client.request_error.connect(self.on_request_error)
        self.api_client.request_success.connect(self.on_request_success)

    def refresh_data(self):
        """Solicita productos filtrados al API"""
        self.status_bar.showMessage("Cargando productos...")
        
        # Prepara los filtros para la API
        api_filters = {
            'categoria': self.current_filters.get('categoria'),
            'estado': self.current_filters.get('estado'),
            'search': self.search_input.text().strip() or None
        }
        
        # Elimina filtros vacíos/None
        api_filters = {k: v for k, v in api_filters.items() if v is not None}
        
        self.api_client.get_products(filters=api_filters)

    def load_products(self, products):
        """Carga los productos en la tabla"""
        self.product_model.removeRows(0, self.product_model.rowCount())
        
        if not products:
            self.status_bar.showMessage("No se encontraron productos")
            return
            
        count_activos = count_descontinuados = count_oferta = 0
        
        for product in products:
            if not isinstance(product, Product):
                product = Product.from_dict(product)
                
            # Contar por estado
            if product.estado == 'activo':
                count_activos += 1
            elif product.estado == 'descontinuado':
                count_descontinuados += 1
            elif product.estado == 'oferta':
                count_oferta += 1
                
            # Crear fila
            row = [
                QStandardItem(str(product.id_producto)),
                QStandardItem(product.codigo),
                QStandardItem(product.nombre),
                QStandardItem(product.get_categoria_display()),
                QStandardItem(product.categoria),
                QStandardItem(product.descripcion_display),
                QStandardItem(f"${product.precio:,.2f}"),
                QStandardItem(product.get_estado_display()),
                QStandardItem(product.estado)
            ]
            
            # Formatear celdas
            row[0].setTextAlignment(Qt.AlignmentFlag.AlignCenter)  # ID
            row[6].setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)  # Precio
            row[7].setTextAlignment(Qt.AlignmentFlag.AlignCenter)  # Estado
            
            # Color por estado
            if product.estado == 'descontinuado':
                row[7].setForeground(QColor(Theme.DANGER_COLOR))
            elif product.estado == 'oferta':
                row[7].setForeground(QColor(Theme.INFO_COLOR))
            else:
                row[7].setForeground(QColor(Theme.SUCCESS_COLOR))
            
            self.product_model.appendRow(row)
        
        # Actualizar resumen
        total = len(products)
        self.total_label.setText(f"Total: <b>{total}</b>")
        self.active_label.setText(f"Activos: <b>{count_activos}</b>")
        self.discontinued_label.setText(f"Descontinuados: <b>{count_descontinuados}</b>")
        self.oferta_label.setText(f"En oferta: <b>{count_oferta}</b>")
        
        self.status_bar.showMessage(f"Cargados {total} productos")

    def show_context_menu(self, position):
        """Muestra el menú contextual para un producto"""
        index = self.product_table.indexAt(position)
        if not index.isValid():
            return
            
        # Obtener el producto seleccionado
        mapped_index = self.proxy_model.mapToSource(index)
        product_id = int(self.product_model.item(mapped_index.row(), 0).text())
        
        menu = QMenu(self)
        
        # Acciones principales
        view_action = menu.addAction(QIcon("resources/icons/view.png"), "Ver detalles")
        edit_action = menu.addAction(QIcon("resources/icons/edit.png"), "Editar")
        delete_action = menu.addAction(QIcon("resources/icons/delete.png"), "Eliminar")
        menu.addSeparator()
        
        # Conectar acciones
        view_action.triggered.connect(lambda: self.on_view_product(product_id))
        edit_action.triggered.connect(lambda: self.on_edit_product(product_id))
        delete_action.triggered.connect(lambda: self.on_delete_product(product_id))
        
        menu.exec(self.product_table.viewport().mapToGlobal(position))

    def on_add_product(self):
        """Abre el formulario para añadir nuevo producto"""
        from .product_form import ProductForm
        dialog = ProductForm(self.api_client, parent=self)
        dialog.product_saved.connect(self._handle_product_save)
        dialog.exec()

    def on_edit_product(self, product_id):
        """Abre el formulario para editar un producto existente"""
        from .product_form import ProductForm
        
        # Buscar el producto en el modelo
        for row in range(self.product_model.rowCount()):
            if int(self.product_model.item(row, 0).text()) == product_id:
                product_data = {
                    "id_producto": product_id,
                    "codigo": self.product_model.item(row, 1).text(),
                    "nombre": self.product_model.item(row, 2).text(),
                    "descripcion": self.product_model.item(row, 5).text(),
                    "precio": float(self.product_model.item(row, 6).text().replace("$", "").replace(",", "")),
                    "categoria": self.product_model.item(row, 4).text(),
                    "estado": self.product_model.item(row, 8).text()
                }
                break
        else:
            QMessageBox.warning(self, "Error", "No se pudo cargar el producto")
            return
            
        dialog = ProductForm(self.api_client, product_data, parent=self)
        dialog.product_saved.connect(self._handle_product_save)
        dialog.exec()

    def on_view_product(self, product_id):
        """Muestra los detalles completos del producto"""
        from .product_detail import ProductDetailView
        
        # Obtener datos del producto desde el modelo
        for row in range(self.product_model.rowCount()):
            if int(self.product_model.item(row, 0).text()) == product_id:
                product_data = {
                    "id_producto": product_id,
                    "codigo": self.product_model.item(row, 1).text(),
                    "nombre": self.product_model.item(row, 2).text(),
                    "descripcion": self.product_model.item(row, 5).text(),
                    "precio": float(self.product_model.item(row, 6).text().replace("$", "").replace(",", "")),
                    "categoria": self.product_model.item(row, 4).text(),
                    "estado": self.product_model.item(row, 8).text()
                }
                break
        else:
            QMessageBox.warning(self, "Error", "Producto no encontrado")
            return
            
        dialog = ProductDetailView(self.api_client, product_data, parent=self)
        dialog.edit_requested.connect(self.on_edit_product)
        dialog.delete_requested.connect(self.on_delete_product)
        dialog.exec()

    def on_delete_product(self, product_id):
        """Elimina un producto con confirmación"""
        reply = QMessageBox.question(
            self,
            "Confirmar eliminación",
            f"¿Está seguro que desea eliminar el producto ID: {product_id}?\n\n"
            "Esta acción no se puede deshacer.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.api_client.delete_product(product_id)
            self.status_bar.showMessage(f"Eliminando producto ID: {product_id}...")

    def on_row_double_clicked(self, index):
        """Maneja el doble clic en una fila"""
        mapped_index = self.proxy_model.mapToSource(index)
        product_id = int(self.product_model.item(mapped_index.row(), 0).text())
        self.on_view_product(product_id)

    def _handle_product_save(self, product_data):
        """Maneja el guardado de un producto"""
        if 'id_producto' in product_data and product_data['id_producto']:
            self.api_client.update_product(product_data['id_producto'], product_data)
        else:
            self.api_client.create_product(product_data)

    def on_data_loaded(self, data):
        """Maneja los datos cargados desde la API"""
        if data.get('type') == 'products':
            products = [Product.from_dict(item) for item in data.get('data', [])]
            self.load_products(products)

    def on_request_success(self, endpoint, data):
        """Maneja operaciones exitosas"""
        if endpoint in ['create_product', 'update_product', 'delete_product']:
            self.refresh_data()
            msg = {
                'create_product': "Producto creado exitosamente",
                'update_product': "Producto actualizado exitosamente",
                'delete_product': "Producto eliminado exitosamente"
            }.get(endpoint, "Operación completada")
            QMessageBox.information(self, "Éxito", msg)

    def on_request_error(self, error_msg):
        """Maneja errores de la API"""
        QMessageBox.critical(self, "Error", error_msg)
        self.status_bar.showMessage(f"Error: {error_msg}")