from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableView, QHeaderView, QLineEdit, QComboBox, QFrame,
    QMessageBox, QMenu, QDialog, QFormLayout, QDialogButtonBox,
    QAbstractItemView, QSplitter, QToolBar, QStatusBar, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal, QSortFilterProxyModel, QThread, QSize
from PyQt6.QtGui import QIcon, QAction, QStandardItemModel, QStandardItem, QFont, QColor
from utils.theme import Theme

class ProductListView(QWidget):
    """Vista de listado de productos para ERP Pirelli"""

    # Señales
    product_selected = pyqtSignal(int)  # Emitida cuando se selecciona un producto

    def __init__(self, api_client):
        super().__init__()
        from utils.theme import Theme
        Theme.apply_window_light_theme(self)

        self.api_client = api_client

        # Conectar señales del cliente API
        self.api_client.data_received.connect(self.on_data_loaded)
        self.api_client.request_error.connect(self.on_request_error)

        # Modelo para la tabla
        self.product_model = QStandardItemModel()
        self.product_model.setHorizontalHeaderLabels([
            "ID", "Código", "Nombre", "Categoría", "Categoría Valor", "Descripción", "Precio", "Estado"
        ])

        # Modelo proxy para filtrado avanzado
        self.proxy_model = QSortFilterProxyModel()
        self.proxy_model.setSourceModel(self.product_model)
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
        title_label = QLabel("Gestión de Productos")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        main_layout.addWidget(title_label)

        # Barra de herramientas (similar a sales_list.py)
        toolbar_layout = QHBoxLayout()

        # Filtro de categoría
        self.category_filter = QComboBox()
        self.category_filter.addItem("Todas las categorías", "")
        self.category_filter.addItem("Automóvil", "automovil")
        self.category_filter.addItem("Motocicleta", "motocicleta")
        self.category_filter.addItem("Camión", "camion")
        self.category_filter.addItem("Industrial", "industrial")
        self.category_filter.addItem("Competición", "competicion")
        self.category_filter.currentIndexChanged.connect(self.on_category_changed)

        # Filtro de estado
        self.status_filter = QComboBox()
        self.status_filter.addItem("Todos", "")
        self.status_filter.addItem("Activo", "activo")
        self.status_filter.addItem("Descontinuado", "descontinuado")
        self.status_filter.addItem("En oferta", "oferta")
        self.status_filter.currentIndexChanged.connect(self._on_filters_changed)

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
        toolbar_layout.addWidget(QLabel("Filtrar por categoría:"))
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
        self.product_table.horizontalHeader().setSectionResizeMode(7, QHeaderView.ResizeMode.ResizeToContents)  # Estado
        self.product_table.verticalHeader().setVisible(False)
        self.product_table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.product_table.customContextMenuRequested.connect(self.show_context_menu)
        self.product_table.doubleClicked.connect(self.on_row_double_clicked)
        
        main_layout.addWidget(self.product_table)

        # --- Agregar labels de totales debajo de la tabla ---
        summary_layout = QHBoxLayout()
        self.total_label = QLabel("Total de productos: <b>0</b>")
        self.active_label = QLabel("Productos activos: <b>0</b>")
        self.discontinued_label = QLabel("Productos descontinuados: <b>0</b>")

        # Un poco de espacio entre textos
        summary_layout.addWidget(self.total_label)
        summary_layout.addSpacing(30)
        summary_layout.addWidget(self.active_label)
        summary_layout.addSpacing(30)
        summary_layout.addWidget(self.discontinued_label)
        summary_layout.addStretch()
        main_layout.addLayout(summary_layout)
        # --- Fin de la inserción ---

        # Barra de estado
        self.status_bar = QStatusBar()
        self.status_bar.showMessage("Sistema ERP Pirelli - Módulo de Gestión de Productos v2.1")
        main_layout.addWidget(self.status_bar)

    def setup_filter_proxy(self):
        """Configura el modelo proxy para filtrado avanzado"""
        # Sobrescribe el método filterAcceptsRow del proxy model
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
            categoria_valor = model.item(source_row, 4).text().lower()  # columna oculta con valor interno
            estado = model.item(source_row, 6).text().lower()  # ahora el estado está en la columna 6
            
            # Filtro de búsqueda (nombre o código)
            if search_text and not (search_text in codigo or search_text in nombre):
                return False
                
            # Filtro de categoría (compara valor interno exacto)
            if category and category != categoria_valor:
                return False
                
            # Filtro de estado
            if status and status not in estado.lower():
                return False
                
            return True
        except (AttributeError, IndexError):
            # En caso de error, mostrar la fila
            return True

    def on_search_changed(self, text):
        """Maneja el cambio en el campo de búsqueda"""
        self.proxy_model.setFilterWildcard(text)
        self.proxy_model.invalidateFilter()
        self.status_bar.showMessage(f"Filtrando productos por: {text}" if text else "Sistema ERP Pirelli - Módulo de Gestión de Productos v2.1")

    def on_category_changed(self, index):
        """Maneja el cambio en el filtro de categoría"""
        self._on_filters_changed()

    def _on_filters_changed(self):
        """Se llama cuando cambia categoría o estado, para actualizar el filtrado sobre la tabla"""
        self.proxy_model.invalidateFilter()
        category = self.category_filter.currentData()
        status = self.status_filter.currentData()
        
        msg = "Mostrando productos"
        if category:
            msg += f" de la categoría: {self.category_filter.currentText()}"
        if status:
            msg += f" con estado: {self.status_filter.currentText()}"
        if not category and not status:
            msg = "Sistema ERP Pirelli - Módulo de Gestión de Productos v2.1"
            
        self.status_bar.showMessage(msg)

    def clear_filters(self):
        """Limpia todos los filtros aplicados"""
        self.search_input.clear()
        self.category_filter.setCurrentIndex(0)
        self.status_filter.setCurrentIndex(0)
        self.proxy_model.invalidateFilter()
        self.status_bar.showMessage("Filtros eliminados")

    def refresh_data(self):
        """Actualiza los datos de la tabla desde la API"""
        self.status_bar.showMessage("Actualizando datos de productos...")
        self.api_client.get_products()

    def load_products(self, products):
        """Carga los productos recibidos en la tabla y actualiza estadísticas"""
        # Limpiar modelo actual
        self.product_model.removeRows(0, self.product_model.rowCount())
        count_activos = count_descontinuados = 0

        for product in products:
            row = []

            # ID
            id_item = QStandardItem(str(product.id_producto))
            id_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            row.append(id_item)

            # Código
            code_item = QStandardItem(product.codigo)
            code_item.setFont(QFont("Consolas", 9))
            row.append(code_item)

            # Nombre
            name_item = QStandardItem(product.nombre)
            font = QFont()
            font.setBold(True)
            name_item.setFont(font)
            row.append(name_item)

            # Categoría (display)
            category_item = QStandardItem(product.get_categoria_display())
            row.append(category_item)

            # Categoría (valor interno, columna oculta)
            category_value_item = QStandardItem(product.categoria)
            row.append(category_value_item)
            
            # Descripción (columna oculta)
            descripcion = getattr(product, 'descripcion', None)
            if descripcion is None or not str(descripcion).strip():
                descripcion = "Sin descripción disponible"
            desc_item = QStandardItem(descripcion)
            row.append(desc_item)

            # Precio
            precio = f"${float(product.precio):.2f}"
            price_item = QStandardItem(precio)
            price_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            row.append(price_item)

            # Estado (opcional: si no tiene, se asume 'activo')
            estado = getattr(product, 'estado', 'activo')
            status_item = QStandardItem(estado.capitalize())
            if estado == 'activo':
                status_item.setForeground(QColor(Theme.SUCCESS_COLOR))
                count_activos += 1
            elif estado == 'descontinuado':
                status_item.setForeground(QColor(Theme.DANGER_COLOR))
                count_descontinuados += 1
            elif estado == 'oferta':
                status_item.setForeground(QColor(Theme.INFO_COLOR))
            status_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            row.append(status_item)

            self.product_model.appendRow(row)
            
        # Oculta la columna de valor interno de categoría (índice 4) y descripción (índice 5)
        self.product_table.setColumnHidden(4, True)
        self.product_table.setColumnHidden(5, True)

        total = len(products)
        self.total_label.setText(f"Total de productos: <b>{total}</b>")
        self.active_label.setText(f"Productos activos: <b>{count_activos}</b>")
        self.discontinued_label.setText(f"Productos descontinuados: <b>{count_descontinuados}</b>")
        self.status_bar.showMessage(f"Se han cargado {total} productos")

    def on_data_loaded(self, data):
        """Maneja los datos cargados desde la API directa"""
        if data.get("type") == "products":
            # Convertir datos API a objetos producto
            from models.product_model import Product
            products = [Product.from_dict(item) for item in data.get("data", [])]
            self.load_products(products)
        elif data.get("type") == "product_created":
            QMessageBox.information(self, "Éxito", "Producto creado correctamente")
            self.refresh_data()
        elif data.get("type") == "product_updated":
            QMessageBox.information(self, "Éxito", "Producto actualizado correctamente")
            self.refresh_data()
        elif data.get("type") == "product_deleted":
            QMessageBox.information(self, "Éxito", "Producto eliminado correctamente")
            self.refresh_data()

    def on_request_error(self, error_message):
        """Maneja errores de la API"""
        QMessageBox.critical(self, "Error", f"Error al cargar productos: {error_message}")
        self.status_bar.showMessage(f"Error: {error_message}")

    def on_row_double_clicked(self, index):
        """Maneja el doble clic en una fila"""
        mapped_index = self.proxy_model.mapToSource(index)
        row = mapped_index.row()
        product_id = int(self.product_model.item(row, 0).text())
        self.product_selected.emit(product_id)
        self.on_view_product(product_id)

    def show_context_menu(self, position):
        """Muestra menú contextual para una fila"""
        index = self.product_table.indexAt(position)
        if not index.isValid():
            return

        context_menu = QMenu(self)
        # Acciones principales
        view_action = QAction(QIcon("resources/icons/view.png"), "Ver detalles", self)
        edit_action = QAction(QIcon("resources/icons/edit.png"), "Editar", self)
        delete_action = QAction(QIcon("resources/icons/delete.png"), "Eliminar", self)
        # Extra
        duplicate_action = QAction(QIcon("resources/icons/duplicate.png"), "Duplicar", self)
        price_action = QAction(QIcon("resources/icons/price.png"), "Actualizar precio", self)
        stock_action = QAction(QIcon("resources/icons/stock.png"), "Gestionar stock", self)
        history_action = QAction(QIcon("resources/icons/history.png"), "Historial", self)

        context_menu.addAction(view_action)
        context_menu.addAction(edit_action)
        context_menu.addSeparator()
        context_menu.addAction(duplicate_action)
        context_menu.addAction(price_action)
        context_menu.addAction(stock_action)
        context_menu.addSeparator()
        context_menu.addAction(history_action)
        context_menu.addSeparator()
        context_menu.addAction(delete_action)

        mapped_index = self.proxy_model.mapToSource(index)
        row = mapped_index.row()
        product_id = int(self.product_model.item(row, 0).text())

        view_action.triggered.connect(lambda: self.on_view_product(product_id))
        edit_action.triggered.connect(lambda: self.on_edit_product(product_id))
        delete_action.triggered.connect(lambda: self.on_delete_product(product_id))
        duplicate_action.triggered.connect(lambda: self.status_bar.showMessage(f"Duplicando producto ID: {product_id}"))
        price_action.triggered.connect(lambda: self.status_bar.showMessage(f"Actualización de precio para producto ID: {product_id}"))
        stock_action.triggered.connect(lambda: self.status_bar.showMessage(f"Gestión de stock para producto ID: {product_id}"))
        history_action.triggered.connect(lambda: self.status_bar.showMessage(f"Mostrando historial del producto ID: {product_id}"))

        context_menu.exec(self.product_table.viewport().mapToGlobal(position))

    def _get_selected_product_id(self, callback_func):
        """Obtiene el ID del producto seleccionado y llama al callback"""
        indexes = self.product_table.selectionModel().selectedRows()
        if not indexes:
            QMessageBox.information(self, "Selección", "Por favor, seleccione un producto primero")
            return
        # Obtener el ID del producto seleccionado (columna 0)
        mapped_index = self.proxy_model.mapToSource(indexes[0])
        row = mapped_index.row()
        product_id = int(self.product_model.item(row, 0).text())
        # Llamar al callback con el ID
        callback_func(product_id)

    def on_view_product(self, product_id):
        """Muestra detalles de un producto, incluyendo la descripción"""
        # Buscar la fila en el modelo
        for row in range(self.product_model.rowCount()):
            if int(self.product_model.item(row, 0).text()) == product_id:
                nombre = self.product_model.item(row, 2).text()
                codigo = self.product_model.item(row, 1).text()
                categoria = self.product_model.item(row, 3).text()
                precio = self.product_model.item(row, 6).text()
                estado = self.product_model.item(row, 7).text()
                
                # Obtener descripción de forma segura y robusta
                descripcion_item = self.product_model.item(row, 5)
                descripcion = ""
                if descripcion_item is not None:
                    descripcion = descripcion_item.text() or ""
                if not descripcion.strip():
                    descripcion = "Sin descripción disponible"
                break
        else:
            QMessageBox.warning(self, "Error", "No se encontró el producto seleccionado")
            return

        self.status_bar.showMessage(f"Cargando detalles del producto ID: {product_id}...")
        
        # Crear un mensaje detallado con HTML para mejor formato
        mensaje = f"""
        <h2>{nombre}</h2>
        <p><b>Código:</b> {codigo}</p>
        <p><b>Categoría:</b> {categoria}</p>
        <p><b>Precio:</b> {precio}</p>
        <p><b>Estado:</b> {estado}</p>
        <p><b>Descripción:</b><br>{descripcion}</p>
        """
        
        QMessageBox.information(self, "Detalles del Producto", mensaje)
        self.status_bar.showMessage(f"Visualizando producto ID: {product_id}")

    def on_add_product(self):
        """Muestra el diálogo para añadir un nuevo producto"""
        self.status_bar.showMessage("Abriendo formulario para nuevo producto...")
        from .product_form import ProductForm
        dialog = ProductForm(self.api_client)
        dialog.product_saved.connect(self._handle_product_save)
        dialog.exec()

    def on_edit_product(self, product_id):
        """Abre el formulario de edición de un producto"""
        self.status_bar.showMessage(f"Cargando formulario de edición para producto ID: {product_id}...")
        # Cargar datos del producto desde el modelo actual
        product = self._get_product_by_id(product_id)
        if product:
            self._show_edit_form(product)
        else:
            QMessageBox.warning(self, "Error", "No se pudo cargar el producto")

    def _get_product_by_id(self, product_id):
        """Busca un producto por su ID en el modelo actual"""
        for row in range(self.product_model.rowCount()):
            if int(self.product_model.item(row, 0).text()) == product_id:
                from models.product_model import Product
                
                # Obtener descripción de forma segura y robusta
                descripcion_item = self.product_model.item(row, 5)
                descripcion = ""
                if descripcion_item is not None:
                    descripcion = descripcion_item.text() or ""
                if not descripcion.strip():
                    descripcion = "Sin descripción disponible"
                
                product_data = {
                    "id_producto": self.product_model.item(row, 0).text(),
                    "codigo": self.product_model.item(row, 1).text(),
                    "nombre": self.product_model.item(row, 2).text(),
                    "categoria": self.product_model.item(row, 4).text(),  # Usamos el valor interno de categoría
                    "descripcion": descripcion,
                    "precio": self.product_model.item(row, 6).text().replace("$", "").replace(",", ""),
                    "estado": self.product_model.item(row, 7).text().lower()
                }
                return Product.from_dict(product_data)
        return None

    def _show_edit_form(self, product):
        """Muestra el formulario de edición con los datos del producto"""
        from .product_form import ProductForm
        if product:
            dialog = ProductForm(self.api_client, product.to_dict())
            dialog.product_saved.connect(self._handle_product_save)
            dialog.exec()
        else:
            QMessageBox.warning(self, "Error", "No se pudo cargar el producto")

    def _handle_product_save(self, product_data):
        """Maneja el guardado de un producto (nuevo o editado)"""
        if "id_producto" in product_data and product_data["id_producto"]:
            # Actualizar producto
            self.api_client.update_product(product_data["id_producto"], product_data)
            self.status_bar.showMessage(f"Actualizando producto ID: {product_data['id_producto']}...")
        else:
            # Crear producto
            self.api_client.create_product(product_data)
            self.status_bar.showMessage("Creando nuevo producto...")

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
            self.api_client.delete_product(product_id)
            self.status_bar.showMessage(f"Eliminando producto ID: {product_id}...")
