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
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(15)
        
        # Barra de herramientas
        self._setup_toolbar(main_layout)
        
        # Barra de filtros
        self._setup_filter_bar(main_layout)
        
        # Tabla de productos
        self._setup_product_table(main_layout)
        
        # Barra de resumen
        self._setup_summary_bar(main_layout)
        
        # Barra de estado
        self._setup_status_bar(main_layout)

    def _setup_toolbar(self, parent_layout):
        """Configura la barra de herramientas superior"""
        toolbar = QToolBar()
        toolbar.setIconSize(QSize(24, 24))
        
        # Acciones
        self.add_action = QAction(QIcon("resources/icons/add.png"), "Nuevo Producto", self)
        self.refresh_action = QAction(QIcon("resources/icons/refresh.png"), "Actualizar", self)
        self.export_action = QAction(QIcon("resources/icons/export.png"), "Exportar", self)
        self.print_action = QAction(QIcon("resources/icons/print.png"), "Imprimir", self)
        
        # Agregar acciones
        toolbar.addAction(self.add_action)
        toolbar.addAction(self.refresh_action)
        toolbar.addSeparator()
        toolbar.addAction(self.export_action)
        toolbar.addAction(self.print_action)
        
        parent_layout.addWidget(toolbar)

    def _setup_filter_bar(self, parent_layout):
        """Configura la barra de filtros"""
        filter_layout = QHBoxLayout()
        
        # Filtro de búsqueda
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Buscar productos...")
        self.search_input.setClearButtonEnabled(True)
        self.search_input.setMaximumWidth(300)
        
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
        
        # Botón limpiar filtros
        clear_btn = QPushButton("Limpiar")
        clear_btn.setIcon(QIcon("resources/icons/clear.png"))
        
        # Organizar widgets
        filter_layout.addWidget(QLabel("Buscar:"))
        filter_layout.addWidget(self.search_input)
        filter_layout.addWidget(QLabel("Categoría:"))
        filter_layout.addWidget(self.category_filter)
        filter_layout.addWidget(QLabel("Estado:"))
        filter_layout.addWidget(self.status_filter)
        filter_layout.addWidget(clear_btn)
        filter_layout.addStretch()
        
        parent_layout.addLayout(filter_layout)

    def _setup_product_table(self, parent_layout):
        """Configura la tabla de productos"""
        self.product_table = QTableView()
        self.product_table.setModel(self.proxy_model)
        
        # Configuración de la tabla
        self.product_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.product_table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.product_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.product_table.setAlternatingRowColors(True)
        self.product_table.setSortingEnabled(True)
        self.product_table.verticalHeader().setVisible(False)
        self.product_table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        
        # Configurar columnas
        header = self.product_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)  # ID
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)  # Código
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)          # Nombre
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents) # Categoría
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents) # Precio
        header.setSectionResizeMode(7, QHeaderView.ResizeMode.ResizeToContents) # Estado
        
        # Ocultar columnas internas
        self.product_table.setColumnHidden(4, True)  # Valor categoría
        self.product_table.setColumnHidden(5, True)  # Descripción
        self.product_table.setColumnHidden(8, True)  # Valor estado
        
        parent_layout.addWidget(self.product_table)

    def _setup_summary_bar(self, parent_layout):
        """Configura la barra de resumen estadístico"""
        summary_frame = QFrame()
        summary_frame.setFrameShape(QFrame.Shape.StyledPanel)
        
        summary_layout = QHBoxLayout(summary_frame)
        summary_layout.setContentsMargins(10, 5, 10, 5)
        
        self.total_label = QLabel("Total: <b>0</b>")
        self.active_label = QLabel("Activos: <b>0</b>")
        self.discontinued_label = QLabel("Descontinuados: <b>0</b>")
        self.oferta_label = QLabel("En oferta: <b>0</b>")
        
        # Añadir widgets
        summary_layout.addWidget(self.total_label)
        summary_layout.addWidget(QLabel("|"))
        summary_layout.addWidget(self.active_label)
        summary_layout.addWidget(QLabel("|"))
        summary_layout.addWidget(self.discontinued_label)
        summary_layout.addWidget(QLabel("|"))
        summary_layout.addWidget(self.oferta_label)
        summary_layout.addStretch()
        
        parent_layout.addWidget(summary_frame)

    def _setup_status_bar(self, parent_layout):
        """Configura la barra de estado"""
        self.status_bar = QStatusBar()
        self.status_bar.showMessage("Listo")
        parent_layout.addWidget(self.status_bar)

    def _connect_signals(self):
        """Conecta todas las señales y slots"""
        # Señales de UI
        self.add_action.triggered.connect(self.on_add_product)
        self.refresh_action.triggered.connect(self.refresh_data)
        self.search_input.textChanged.connect(self.on_search_changed)
        self.category_filter.currentIndexChanged.connect(self.on_category_changed)
        self.status_filter.currentIndexChanged.connect(self.on_status_changed)
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
        
        self.api_client.get_products(api_filters)

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

    def _filter_accepts_row(self, source_row, source_parent):
        """Filtrado personalizado para el proxy model"""
        model = self.product_model
        search_text = self.search_input.text().lower()
        
        # Obtener valores de la fila
        codigo = model.item(source_row, 1).text().lower()
        nombre = model.item(source_row, 2).text().lower()
        categoria = model.item(source_row, 4).text().lower()
        estado = model.item(source_row, 8).text().lower()
        descripcion = model.item(source_row, 5).text().lower()
        
        # Aplicar filtros
        if search_text and not (search_text in codigo or search_text in nombre or search_text in descripcion):
            return False
            
        selected_category = self.category_filter.currentData()
        if selected_category and selected_category != categoria:
            return False
            
        selected_status = self.status_filter.currentData()
        if selected_status and selected_status != estado:
            return False
            
        return True

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


    def on_view_history(self, product_id):
        """Muestra el historial de un producto"""
        # Implementar lógica de historial
        QMessageBox.information(self, "Historial", f"Mostrando historial del producto ID: {product_id}")

    def on_search_changed(self, text):
        """Actualiza el filtro de búsqueda"""
        self.proxy_model.invalidateFilter()
        if text:
            self.status_bar.showMessage(f"Filtrando por: '{text}'")
        else:
            self.status_bar.showMessage("Listo")

    def on_category_changed(self, index):
        """Actualiza el filtro de categoría"""
        category = self.category_filter.currentData()
        self.current_filters['categoria'] = category if category else None
        self.proxy_model.invalidateFilter()
        self.refresh_data()

    def on_status_changed(self, index):
        """Actualiza el filtro de estado"""
        status = self.status_filter.currentData()
        self.current_filters['estado'] = status if status else None
        self.proxy_model.invalidateFilter()
        self.refresh_data()

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