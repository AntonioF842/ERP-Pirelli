

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableView, QHeaderView, QLineEdit, QComboBox, QFrame,
    QMessageBox, QMenu, QDialog, QFormLayout, QDialogButtonBox,
    QAbstractItemView, QSplitter, QToolBar, QStatusBar, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal, QSortFilterProxyModel, QThread, QSize
from PyQt6.QtGui import QIcon, QAction, QStandardItemModel, QStandardItem, QFont, QColor, QPalette, QPixmap

class ProductListView(QWidget):
    """Vista de listado de productos para ERP Pirelli"""

    # Señales
    product_selected = pyqtSignal(int)  # Emitida cuando se selecciona un producto

    def __init__(self, api_client):
        super().__init__()

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

        # Definir colores corporativos Pirelli
        self.pirelli_red = "#D50000"
        self.pirelli_yellow = "#FFEB3B"
        self.pirelli_dark = "#212121"
        self.pirelli_gray = "#E0E0E0"
        self.pirelli_light = "#F5F5F5"

        self.init_ui()
        self.apply_pirelli_styles()

        # Cargar datos iniciales
        self.refresh_data()

    def init_ui(self):
        """Inicializa la interfaz de usuario"""

        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Toolbar superior
        self.toolbar = QToolBar()
        self.toolbar.setIconSize(QSize(24, 24))
        self.toolbar.setMovable(False)

        # Logo Pirelli
        logo_label = QLabel()
        logo_pixmap = QPixmap("resources/icons/pirelli_logo.png")
        if not logo_pixmap.isNull():
            logo_label.setPixmap(logo_pixmap.scaled(120, 40, Qt.AspectRatioMode.KeepAspectRatio))
        else:
            # Fallback: texto en lugar de imagen
            logo_label = QLabel("PIRELLI ERP")
            font = logo_label.font()
            font.setPointSize(14)
            font.setBold(True)
            logo_label.setFont(font)
        self.toolbar.addWidget(logo_label)
        self.toolbar.addSeparator()

        # Título de sección
        title_label = QLabel("Gestión de Productos")
        font = title_label.font()
        font.setPointSize(14)
        title_label.setFont(font)
        self.toolbar.addWidget(title_label)

        # Añadir espaciador
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.toolbar.addWidget(spacer)

        # Acciones de la barra de herramientas
        refresh_action = QAction(QIcon("resources/icons/refresh.png"), "Actualizar", self)
        refresh_action.triggered.connect(self.refresh_data)
        self.toolbar.addAction(refresh_action)

        add_action = QAction(QIcon("resources/icons/add.png"), "Nuevo Producto", self)
        add_action.triggered.connect(self.on_add_product)
        self.toolbar.addAction(add_action)

        export_action = QAction(QIcon("resources/icons/export.png"), "Exportar", self)
        # TODO: conectar a función de export
        self.toolbar.addAction(export_action)

        settings_action = QAction(QIcon("resources/icons/settings.png"), "Configuración", self)
        # TODO: conectar a función de configuración
        self.toolbar.addAction(settings_action)

        main_layout.addWidget(self.toolbar)

        # Contenedor principal (con margen)
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setSpacing(15)
        content_layout.setContentsMargins(20, 20, 20, 20)

        # Panel de filtros
        filter_frame = QFrame()
        filter_frame.setFrameShape(QFrame.Shape.StyledPanel)
        filter_frame.setObjectName("filterPanel")
        filter_layout = QHBoxLayout(filter_frame)
        filter_layout.setSpacing(15)

        # Búsqueda con icono
        search_container = QFrame()
        search_container.setObjectName("searchContainer")
        search_layout = QHBoxLayout(search_container)
        search_layout.setContentsMargins(10, 0, 10, 0)
        search_icon = QLabel()
        search_icon_pixmap = QPixmap("resources/icons/search.png")
        if not search_icon_pixmap.isNull():
            search_icon.setPixmap(search_icon_pixmap.scaled(16, 16, Qt.AspectRatioMode.KeepAspectRatio))
        else:
            search_icon.setText("🔍")
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Buscar productos por nombre o código...")
        self.search_input.setMinimumHeight(36)
        self.search_input.textChanged.connect(self.on_search_changed)
        search_layout.addWidget(search_icon)
        search_layout.addWidget(self.search_input)

        # Filtros de categoría mejorados
        category_container = QFrame()
        category_container.setObjectName("categoryContainer")
        category_layout = QHBoxLayout(category_container)
        category_layout.setContentsMargins(10, 0, 10, 0)

        category_label = QLabel("Categoría:")
        self.category_filter = QComboBox()
        self.category_filter.setMinimumHeight(36)
        self.category_filter.addItem("Todas las categorías", "")
        self.category_filter.addItem("Automóvil", "automovil")
        self.category_filter.addItem("Motocicleta", "motocicleta")
        self.category_filter.addItem("Camión", "camion")
        self.category_filter.addItem("Industrial", "industrial")
        self.category_filter.addItem("Competición", "competicion")
        self.category_filter.currentIndexChanged.connect(self.on_category_changed)
        category_layout.addWidget(category_label)
        category_layout.addWidget(self.category_filter)

        # Filtro de estado
        status_container = QFrame()
        status_container.setObjectName("statusContainer")
        status_layout = QHBoxLayout(status_container)
        status_layout.setContentsMargins(10, 0, 10, 0)

        status_label = QLabel("Estado:")
        self.status_filter = QComboBox()
        self.status_filter.setMinimumHeight(36)
        self.status_filter.addItem("Todos", "")
        self.status_filter.addItem("Activo", "activo")
        self.status_filter.addItem("Descontinuado", "descontinuado")
        self.status_filter.addItem("En oferta", "oferta")
        self.status_filter.currentIndexChanged.connect(self._on_filters_changed)
        status_layout.addWidget(status_label)
        status_layout.addWidget(self.status_filter)

        # Botón para limpiar filtros
        clear_button = QPushButton("Limpiar filtros")
        clear_button.setMinimumHeight(36)
        clear_button.setObjectName("secondaryButton")
        clear_button.clicked.connect(self.clear_filters)

        # Agregar widgets al layout de filtros
        filter_layout.addWidget(search_container, 4)
        filter_layout.addWidget(category_container, 2)
        filter_layout.addWidget(status_container, 2)
        filter_layout.addWidget(clear_button, 1)

        content_layout.addWidget(filter_frame)

        # Contadores y estadísticas
        stats_frame = QFrame()
        stats_frame.setObjectName("statsPanel")
        stats_layout = QHBoxLayout(stats_frame)
        self.total_label = QLabel("Total de productos: <b>0</b>")
        self.active_label = QLabel("Productos activos: <b>0</b>")
        self.discontinued_label = QLabel("Productos descontinuados: <b>0</b>")
        stats_layout.addWidget(self.total_label)
        stats_layout.addWidget(self.active_label)
        stats_layout.addWidget(self.discontinued_label)
        stats_layout.addStretch()
        content_layout.addWidget(stats_frame)

        # Tabla de productos con estilo mejorado
        self.product_table = QTableView()
        self.product_table.setModel(self.proxy_model)
        self.product_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.product_table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.product_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.product_table.setAlternatingRowColors(True)
        self.product_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.product_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)  # ID
        self.product_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)  # Código
        self.product_table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)  # Estado
        self.product_table.verticalHeader().setVisible(False)
        self.product_table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.product_table.customContextMenuRequested.connect(self.show_context_menu)
        self.product_table.doubleClicked.connect(self.on_row_double_clicked)
        self.product_table.setObjectName("productTable")
        self.product_table.setMinimumHeight(500)
        content_layout.addWidget(self.product_table)

        # Barra de acciones inferior
        action_bar = QFrame()
        action_bar.setObjectName("actionBar")
        action_layout = QHBoxLayout(action_bar)
        # Botones de acción principales
        view_button = QPushButton("Ver seleccionado")
        view_button.setIcon(QIcon("resources/icons/view.png"))
        view_button.setMinimumHeight(40)
        view_button.setObjectName("primaryButton")
        view_button.clicked.connect(lambda: self._get_selected_product_id(self.on_view_product))
        edit_button = QPushButton("Editar")
        edit_button.setIcon(QIcon("resources/icons/edit.png"))
        edit_button.setMinimumHeight(40)
        edit_button.setObjectName("primaryButton")
        edit_button.clicked.connect(lambda: self._get_selected_product_id(self.on_edit_product))
        delete_button = QPushButton("Eliminar")
        delete_button.setIcon(QIcon("resources/icons/delete.png"))
        delete_button.setMinimumHeight(40)
        delete_button.setObjectName("dangerButton")
        delete_button.clicked.connect(lambda: self._get_selected_product_id(self.on_delete_product))
        action_layout.addStretch()
        action_layout.addWidget(view_button)
        action_layout.addWidget(edit_button)
        action_layout.addWidget(delete_button)
        content_layout.addWidget(action_bar)

        main_layout.addWidget(content_widget)

        # Barra de estado inferior
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
    
    def apply_pirelli_styles(self):
        """Aplica estilos corporativos de Pirelli: fondo blanco y textos siempre legibles"""
        self.setStyleSheet(f"""
        QWidget {{
            background: white;
            color: #212121; /* Muy oscuro, máxima legibilidad sobre fondo blanco */
            font-family: 'Segoe UI', Arial, sans-serif;
        }}
        /* Barra de herramientas: fondo blanco, textos oscuros, sin perder íconos */
        QToolBar {{
            background-color: white;
            color: #212121;
            border: none;
            height: 60px;
        }}
        QToolBar QLabel {{
            color: #212121;
            padding: 0 10px;
        }}

        /* TABLA */
        QTableView {{
            background: white;
            color: #212121;
            border: 1px solid #D0D0D0;
            border-radius: 4px;
            selection-background-color: {self.pirelli_red};
            selection-color: white;
            gridline-color: #E0E0E0;
        }}
        QTableView QTableCornerButton::section {{
            background: #f8f8f8;
        }}
        QTableView::item {{
            background: white;
            color: #212121;
            padding: 8px;
            height: 40px;
        }}
        QTableView::item:alternate {{
            background-color: {self.pirelli_light};
            color: #212121;
        }}

        /* CABECERAS DE TABLA: fondo claro, letras negras/negritas */
        QHeaderView::section {{
            background-color: #f5f5f5;
            color: #212121;
            padding: 8px;
            border: none;
            font-weight: bold;
        }}

        /* BOTONES (contraste garantizado, nunca texto blanco sobre blanco o fondo clarísimo) */
        QPushButton#primaryButton {{
            background-color: {self.pirelli_red};
            color: white; /* Siempre sobre rojo fuerte */
            border: none;
            border-radius: 4px;
            padding: 6px 16px;
            font-weight: bold;
        }}
        QPushButton#primaryButton:hover {{
            background-color: #B71C1C;
            color: white;
        }}
        QPushButton#secondaryButton {{
            background-color: {self.pirelli_gray};
            color: {self.pirelli_dark}; /* Gris claro fondo, texto oscuro */
            border: none;
            border-radius: 4px;
            padding: 6px 16px;
        }}
        QPushButton#secondaryButton:hover {{
            background-color: #BDBDBD;
            color: #212121;
        }}
        QPushButton#dangerButton {{
            background-color: white;
            color: {self.pirelli_red};
            border: 1px solid {self.pirelli_red};
            border-radius: 4px;
            padding: 6px 16px;
        }}
        QPushButton#dangerButton:hover {{
            background-color: #FFEBEE;
            color: {self.pirelli_red};
        }}

        QComboBox, QLineEdit {{
            border: 1px solid #BDBDBD;
            border-radius: 4px;
            padding: 6px;
            background-color: white;
            color: #212121;
        }}
        QComboBox:focus, QLineEdit:focus {{
            border: 1.5px solid {self.pirelli_red};
            color: #212121;
        }}

        /* Panel de filtros blanco con textos oscuros */
        QFrame#filterPanel {{
            background-color: white;
            border-radius: 4px;
            padding: 15px;
        }}
        QFrame#statsPanel {{
            background-color: #fcfcfc;
            border-radius: 4px;
            border: 1px solid #eeeeee;
            color: #212121;
            padding: 10px;
        }}
        QFrame#actionBar {{
            margin-top: 10px;
            background: transparent;
        }}

        QStatusBar {{
            background-color: white;
            color: #212121;
            padding: 5px;
        }}

        QMenu {{
            background-color: white;
            color: #212121;
            border: 1px solid #D0D0D0;
        }}
        QMenu::item {{
            background: white;
            color: #212121;
            padding: 6px 25px 6px 20px;
        }}
        QMenu::item:selected {{
            background-color: {self.pirelli_light};
            color: {self.pirelli_red};
        }}

        QFrame#searchContainer, QFrame#categoryContainer, QFrame#statusContainer {{
            background-color: white;
            border-radius: 4px;
            border: 1px solid #D0D0D0;
            color: #212121;
        }}

        QLabel, QCheckBox, QRadioButton, QListView, QTreeView, QTabBar {{
            color: #212121;
        }}
        """)

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
                status_item.setForeground(QColor('#388E3C'))  # Verde
                count_activos += 1
            elif estado == 'descontinuado':
                status_item.setForeground(QColor('#D32F2F'))  # Rojo
                count_descontinuados += 1
            elif estado == 'oferta':
                status_item.setForeground(QColor('#1976D2'))  # Azul
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


