from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QTableView, QHeaderView, QLineEdit, QComboBox, QFrame,
    QMessageBox, QMenu, QDialog, QFormLayout, QDialogButtonBox,
    QAbstractItemView
)
from PyQt6.QtCore import Qt, pyqtSignal, QSortFilterProxyModel, QThread
from PyQt6.QtGui import QIcon, QAction, QStandardItemModel, QStandardItem

class ProductListView(QWidget):
    """Vista de listado de productos"""
    
    # Señales
    product_selected = pyqtSignal(int)  # Emitida cuando se selecciona un producto
    
    def __init__(self, api_client, product_controller=None):
        super().__init__()
        
        self.api_client = api_client
        self.product_controller = product_controller
        
        # Conectar señales del cliente API
        self.api_client.data_received.connect(self.on_data_loaded)
        self.api_client.request_error.connect(self.on_request_error)
        
        # Modelo para la tabla
        self.product_model = QStandardItemModel()
        self.product_model.setHorizontalHeaderLabels([
            "ID", "Código", "Nombre", "Categoría", "Precio", "Acciones"
        ])
        
        # Modelo proxy para filtrado
        self.proxy_model = QSortFilterProxyModel()
        self.proxy_model.setSourceModel(self.product_model)
        self.proxy_model.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        
        self.init_ui()
        
        # Cargar datos iniciales
        self.refresh_data()
    
    def init_ui(self):
        """Inicializa la interfaz de usuario"""
        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Cabecera
        header_layout = QHBoxLayout()
        
        # Título
        title_label = QLabel("Productos")
        font = self.font()
        font.setPointSize(16)
        title_label.setFont(font)
        header_layout.addWidget(title_label)
        
        # Botón para agregar nuevo producto
        add_button = QPushButton("Nuevo Producto")
        add_button.setIcon(QIcon("resources/icons/add.png"))
        add_button.clicked.connect(self.on_add_product)
        header_layout.addWidget(add_button, alignment=Qt.AlignmentFlag.AlignRight)
        
        main_layout.addLayout(header_layout)
        
        # Panel de filtros
        filter_frame = QFrame()
        filter_frame.setFrameShape(QFrame.Shape.StyledPanel)
        filter_frame.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border-radius: 5px;
            }
        """)
        
        filter_layout = QHBoxLayout(filter_frame)
        
        # Búsqueda
        search_label = QLabel("Buscar:")
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Filtrar por nombre o código...")
        self.search_input.textChanged.connect(self.on_search_changed)
        
        # Filtro de categoría
        category_label = QLabel("Categoría:")
        self.category_filter = QComboBox()
        self.category_filter.addItem("Todas", "")
        self.category_filter.addItem("Automóvil", "automovil")
        self.category_filter.addItem("Motocicleta", "motocicleta")
        self.category_filter.addItem("Camión", "camion")
        self.category_filter.addItem("Industrial", "industrial")
        self.category_filter.currentIndexChanged.connect(self.on_category_changed)
        
        # Botón para limpiar filtros
        clear_button = QPushButton("Limpiar")
        clear_button.clicked.connect(self.clear_filters)
        
        # Agregar widgets al layout de filtros
        filter_layout.addWidget(search_label)
        filter_layout.addWidget(self.search_input, 3)
        filter_layout.addWidget(category_label)
        filter_layout.addWidget(self.category_filter, 1)
        filter_layout.addWidget(clear_button)
        
        main_layout.addWidget(filter_frame)
        
        # Tabla de productos
        self.product_table = QTableView()
        self.product_table.setModel(self.proxy_model)
        self.product_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.product_table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.product_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.product_table.setAlternatingRowColors(True)
        self.product_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.product_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)  # ID
        self.product_table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)  # Acciones
        self.product_table.verticalHeader().setVisible(False)
        self.product_table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.product_table.customContextMenuRequested.connect(self.show_context_menu)
        self.product_table.doubleClicked.connect(self.on_row_double_clicked)
        
        main_layout.addWidget(self.product_table)
    
    def on_search_changed(self, text):
        """Maneja el cambio en el campo de búsqueda"""
        self.proxy_model.setFilterKeyColumn(2)  # Columna de nombre
        self.proxy_model.setFilterFixedString(text)
    
    def on_category_changed(self, index):
        """Maneja el cambio en el filtro de categoría"""
        category = self.category_filter.currentData()
        # En una implementación real, aquí podríamos actualizar los filtros
        # en el proxy_model o volver a cargar los datos con un filtro
    
    def clear_filters(self):
        """Limpia todos los filtros aplicados"""
        self.search_input.clear()
        self.category_filter.setCurrentIndex(0)
    
    def refresh_data(self):
        """Actualiza los datos de la tabla desde la API"""
        if self.product_controller:
            # Ejecutar en un hilo separado para no bloquear la UI
            self._get_products_async()
        else:
            # Usar el cliente API directamente como fallback
            self.api_client.get_products()
    
    def _get_products_async(self):
        """Obtiene productos usando el controlador de manera asíncrona"""
        class ProductLoaderThread(QThread):
            products_loaded = pyqtSignal(list)
            error_occurred = pyqtSignal(str)
            
            def __init__(self, product_controller):
                super().__init__()
                self.product_controller = product_controller
            
            def run(self):
                try:
                    # Llamada asíncrona al controlador
                    products = self.product_controller.get_products({})
                    self.products_loaded.emit(products)
                except Exception as e:
                    self.error_occurred.emit(str(e))
        
        # Crear y configurar el hilo
        self.loader_thread = ProductLoaderThread(self.product_controller)
        self.loader_thread.products_loaded.connect(self.load_products)
        self.loader_thread.error_occurred.connect(self.on_request_error)
        self.loader_thread.start()
    
    def load_products(self, products):
        """Carga los productos recibidos en la tabla"""
        # Limpiar modelo actual
        self.product_model.removeRows(0, self.product_model.rowCount())
        
        # Llenar modelo con datos
        for product in products:
            row = []
            
            # ID
            row.append(QStandardItem(str(product.id_producto)))
            
            # Código
            row.append(QStandardItem(product.codigo))
            
            # Nombre
            row.append(QStandardItem(product.nombre))
            
            # Categoría
            row.append(QStandardItem(product.get_categoria_display()))
            
            # Precio
            precio = f"${float(product.precio):.2f}"
            row.append(QStandardItem(precio))
            
            # Acciones (vacío, se manejan con el menú contextual)
            row.append(QStandardItem(""))
            
            self.product_model.appendRow(row)
    
    def on_data_loaded(self, data):
        """Maneja los datos cargados desde la API directa"""
        if data.get("type") != "products":
            return
            
        # Convertir datos API a objetos producto
        from models.product_model import Product
        products = [Product.from_dict(item) for item in data.get("data", [])]
        
        # Usar el mismo método para cargar los datos
        self.load_products(products)
    
    def on_request_error(self, error_message):
        """Maneja errores de la API"""
        QMessageBox.critical(self, "Error", f"Error al cargar productos: {error_message}")
    
    def on_row_double_clicked(self, index):
        """Maneja el doble clic en una fila"""
        # Obtener el ID del producto seleccionado (columna 0)
        mapped_index = self.proxy_model.mapToSource(index)
        row = mapped_index.row()
        product_id = int(self.product_model.item(row, 0).text())
        
        # Emitir señal de producto seleccionado
        self.product_selected.emit(product_id)
    
    def show_context_menu(self, position):
        """Muestra menú contextual para una fila"""
        # Obtener índice de la fila seleccionada
        index = self.product_table.indexAt(position)
        if not index.isValid():
            return
        
        # Crear menú contextual
        context_menu = QMenu(self)
        
        # Acciones
        view_action = QAction("Ver detalles", self)
        edit_action = QAction("Editar", self)
        delete_action = QAction("Eliminar", self)
        
        # Agregar acciones al menú
        context_menu.addAction(view_action)
        context_menu.addAction(edit_action)
        context_menu.addSeparator()
        context_menu.addAction(delete_action)
        
        # Conectar acciones
        mapped_index = self.proxy_model.mapToSource(index)
        row = mapped_index.row()
        product_id = int(self.product_model.item(row, 0).text())
        
        view_action.triggered.connect(lambda: self.on_view_product(product_id))
        edit_action.triggered.connect(lambda: self.on_edit_product(product_id))
        delete_action.triggered.connect(lambda: self.on_delete_product(product_id))
        
        # Mostrar menú
        context_menu.exec(self.product_table.viewport().mapToGlobal(position))
    
    def on_view_product(self, product_id):
        """Muestra detalles de un producto"""
        QMessageBox.information(self, "Ver Producto", f"Mostrar detalles del producto ID: {product_id}")
    
    def on_add_product(self):
        """Muestra el diálogo para añadir un nuevo producto"""
        from product_form import ProductForm
        
        dialog = ProductForm(self.api_client)
        dialog.product_saved.connect(self._handle_product_save)
        dialog.exec()
    
    def on_edit_product(self, product_id):
        """Abre el formulario de edición de un producto"""
        if self.product_controller:
            self._load_and_edit_product(product_id)
        else:
            QMessageBox.information(self, "Editar Producto", f"Editar producto ID: {product_id}")
    
    def _load_and_edit_product(self, product_id):
        """Carga un producto y abre el formulario de edición"""
        class ProductDetailThread(QThread):
            product_loaded = pyqtSignal(object)
            error_occurred = pyqtSignal(str)
            
            def __init__(self, product_controller, product_id):
                super().__init__()
                self.product_controller = product_controller
                self.product_id = product_id
            
            def run(self):
                try:
                    product = self.product_controller.get_product(self.product_id)
                    self.product_loaded.emit(product)
                except Exception as e:
                    self.error_occurred.emit(str(e))
        
        # Crear y configurar el hilo
        self.detail_thread = ProductDetailThread(self.product_controller, product_id)
        self.detail_thread.product_loaded.connect(self._show_edit_form)
        self.detail_thread.error_occurred.connect(self.on_request_error)
        self.detail_thread.start()
    
    def _show_edit_form(self, product):
        """Muestra el formulario de edición con los datos del producto"""
        from product_form import ProductForm
        
        if product:
            dialog = ProductForm(self.api_client, product.to_dict())
            dialog.product_saved.connect(self._handle_product_save)
            dialog.exec()
        else:
            QMessageBox.warning(self, "Error", "No se pudo cargar el producto")
    
    def _handle_product_save(self, product_data):
        """Maneja el guardado de un producto (nuevo o editado)"""
        if self.product_controller:
            if "id_producto" in product_data and product_data["id_producto"]:
                # Actualización
                product_id = product_data["id_producto"]
                self._update_product_async(product_id, product_data)
            else:
                # Creación
                self._create_product_async(product_data)
        else:
            if "id_producto" in product_data and product_data["id_producto"]:
                self.api_client.update_product(product_data["id_producto"], product_data)
            else:
                self.api_client.create_product(product_data)
    
    def _create_product_async(self, product_data):
        """Crea un producto usando el controlador de manera asíncrona"""
        class ProductCreateThread(QThread):
            product_created = pyqtSignal(object)
            error_occurred = pyqtSignal(str)
            
            def __init__(self, product_controller, product_data):
                super().__init__()
                self.product_controller = product_controller
                self.product_data = product_data
            
            def run(self):
                try:
                    product = self.product_controller.create_product(self.product_data)
                    self.product_created.emit(product)
                except Exception as e:
                    self.error_occurred.emit(str(e))
        
        # Crear y configurar el hilo
        self.create_thread = ProductCreateThread(self.product_controller, product_data)
        self.create_thread.product_created.connect(lambda _: self.refresh_data())
        self.create_thread.product_created.connect(lambda _: 
            QMessageBox.information(self, "Éxito", "Producto creado correctamente"))
        self.create_thread.error_occurred.connect(self.on_request_error)
        self.create_thread.start()
    
    def _update_product_async(self, product_id, product_data):
        """Actualiza un producto usando el controlador de manera asíncrona"""
        class ProductUpdateThread(QThread):
            product_updated = pyqtSignal(object)
            error_occurred = pyqtSignal(str)
            
            def __init__(self, product_controller, product_id, product_data):
                super().__init__()
                self.product_controller = product_controller
                self.product_id = product_id
                self.product_data = product_data
            
            def run(self):
                try:
                    product = self.product_controller.update_product(self.product_id, self.product_data)
                    self.product_updated.emit(product)
                except Exception as e:
                    self.error_occurred.emit(str(e))
        
        # Crear y configurar el hilo
        self.update_thread = ProductUpdateThread(self.product_controller, product_id, product_data)
        self.update_thread.product_updated.connect(lambda _: self.refresh_data())
        self.update_thread.product_updated.connect(lambda _: 
            QMessageBox.information(self, "Éxito", "Producto actualizado correctamente"))
        self.update_thread.error_occurred.connect(self.on_request_error)
        self.update_thread.start()
    
    def on_delete_product(self, product_id):
        """Elimina un producto"""
        reply = QMessageBox.question(
            self,
            "Confirmar eliminación",
            f"¿Está seguro que desea eliminar el producto ID: {product_id}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            if self.product_controller:
                self._delete_product_async(product_id)
            else:
                self.api_client.delete_product(product_id)
    
    def _delete_product_async(self, product_id):
        """Elimina un producto usando el controlador de manera asíncrona"""
        class ProductDeleteThread(QThread):
            product_deleted = pyqtSignal(bool)
            error_occurred = pyqtSignal(str)
            
            def __init__(self, product_controller, product_id):
                super().__init__()
                self.product_controller = product_controller
                self.product_id = product_id
            
            def run(self):
                try:
                    result = self.product_controller.delete_product(self.product_id)
                    self.product_deleted.emit(result)
                except Exception as e:
                    self.error_occurred.emit(str(e))
        
        # Crear y configurar el hilo
        self.delete_thread = ProductDeleteThread(self.product_controller, product_id)
        self.delete_thread.product_deleted.connect(lambda success: 
            self.refresh_data() if success else None)
        self.delete_thread.product_deleted.connect(lambda success: 
            QMessageBox.information(self, "Éxito", "Producto eliminado correctamente") if success else
            QMessageBox.warning(self, "Error", "No se pudo eliminar el producto"))
        self.delete_thread.error_occurred.connect(self.on_request_error)
        self.delete_thread.start()