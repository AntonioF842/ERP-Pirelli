from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableView, QHeaderView, QLineEdit, QComboBox, QFrame,
    QMessageBox, QMenu, QDialog, QFormLayout, QDialogButtonBox,
    QAbstractItemView, QSplitter, QToolBar, QStatusBar, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal, QSortFilterProxyModel, QThread, QSize
from PyQt6.QtGui import QIcon, QAction, QStandardItemModel, QStandardItem, QFont, QColor
from utils.theme import Theme

class ProductionRecipeListView(QWidget):
    """Vista de listado de recetas de producción para ERP Pirelli"""

    # Señales
    recipe_selected = pyqtSignal(int)  # Emitida cuando se selecciona una receta

    def __init__(self, api_client):
        super().__init__()
        from utils.theme import Theme
        Theme.apply_window_light_theme(self)

        self.api_client = api_client

        # Conectar señales del cliente API
        self.api_client.data_received.connect(self.on_data_loaded)
        self.api_client.request_error.connect(self.on_request_error)

        # Modelo para la tabla
        self.recipe_model = QStandardItemModel()
        self.recipe_model.setHorizontalHeaderLabels([
            "ID", "Producto", "Material", "Cantidad"
        ])

        # Modelo proxy para filtrado avanzado
        self.proxy_model = QSortFilterProxyModel()
        self.proxy_model.setSourceModel(self.recipe_model)
        self.proxy_model.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.proxy_model.setFilterKeyColumn(-1)  # Buscar en todas las columnas
        self.setup_filter_proxy()

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
        title_label = QLabel("Gestión de Recetas de Producción")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        main_layout.addWidget(title_label)

        # Barra de herramientas
        toolbar_layout = QHBoxLayout()

        # Campo de búsqueda
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Buscar por producto o material...")
        self.search_input.textChanged.connect(self.on_search_changed)

        # Botón de búsqueda
        search_btn = QPushButton("Buscar")
        search_btn.clicked.connect(self._on_filters_changed)

        # Botón para añadir
        self.add_btn = QPushButton("Nueva Receta")
        self.add_btn.setIcon(QIcon("resources/icons/add.png"))
        self.add_btn.clicked.connect(self.on_add_recipe)

        # Botón de actualizar
        self.refresh_btn = QPushButton("Actualizar")
        self.refresh_btn.setIcon(QIcon("resources/icons/refresh.png"))
        self.refresh_btn.clicked.connect(self.refresh_data)

        # Agregar widgets a la barra de herramientas
        toolbar_layout.addWidget(self.search_input)
        toolbar_layout.addWidget(search_btn)
        toolbar_layout.addStretch()
        toolbar_layout.addWidget(self.add_btn)
        toolbar_layout.addWidget(self.refresh_btn)

        main_layout.addLayout(toolbar_layout)

        # Tabla de recetas
        self.recipe_table = QTableView()
        self.recipe_table.setModel(self.proxy_model)
        self.recipe_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.recipe_table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.recipe_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.recipe_table.setAlternatingRowColors(True)
        self.recipe_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.recipe_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)  # ID
        self.recipe_table.verticalHeader().setVisible(False)
        self.recipe_table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.recipe_table.customContextMenuRequested.connect(self.show_context_menu)
        self.recipe_table.doubleClicked.connect(self.on_row_double_clicked)
        
        main_layout.addWidget(self.recipe_table)

        # Barra de resumen
        summary_layout = QHBoxLayout()
        self.total_label = QLabel("Total de recetas: <b>0</b>")
        
        summary_layout.addWidget(self.total_label)
        summary_layout.addStretch()
        main_layout.addLayout(summary_layout)

        # Barra de estado
        self.status_bar = QStatusBar()
        self.status_bar.showMessage("Sistema ERP Pirelli - Módulo de Recetas de Producción")
        main_layout.addWidget(self.status_bar)

    def setup_filter_proxy(self):
        """Configura el modelo proxy para filtrado avanzado"""
        self.proxy_model.filterAcceptsRow = self._filter_accepts_row
    
    def _filter_accepts_row(self, source_row, source_parent):
        """Método personalizado para determinar si una fila cumple con los filtros"""
        model = self.recipe_model
        search_text = self.search_input.text().lower()
        
        # Si no hay filtros activos, mostrar todas las filas
        if not search_text:
            return True
            
        # Obtener valores de la fila actual
        try:
            producto = model.item(source_row, 1).text().lower()
            material = model.item(source_row, 2).text().lower()
            
            # Filtro de búsqueda (producto o material)
            if search_text and not (search_text in producto or search_text in material):
                return False
                
            return True
        except (AttributeError, IndexError):
            return True

    def on_search_changed(self, text):
        """Maneja el cambio en el campo de búsqueda"""
        self.proxy_model.setFilterWildcard(text)
        self.proxy_model.invalidateFilter()
        self.status_bar.showMessage(f"Filtrando recetas por: {text}" if text else "Sistema ERP Pirelli - Módulo de Recetas de Producción")

    def _on_filters_changed(self):
        """Actualiza el filtrado sobre la tabla"""
        self.proxy_model.invalidateFilter()

    def refresh_data(self):
        """Actualiza los datos de la tabla desde la API"""
        self.status_bar.showMessage("Actualizando datos de recetas...")
        self.api_client.get_production_recipes()

    def load_recipes(self, recipes):
        """Carga las recetas recibidas en la tabla"""
        self.recipe_model.removeRows(0, self.recipe_model.rowCount())

        for recipe in recipes:
            row = []

            # ID
            id_item = QStandardItem(str(recipe.id_receta))
            id_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            row.append(id_item)

            # Producto
            product_item = QStandardItem(recipe.producto_nombre)
            font = QFont()
            font.setBold(True)
            product_item.setFont(font)
            row.append(product_item)

            # Material
            material_item = QStandardItem(recipe.material_nombre)
            row.append(material_item)

            # Cantidad
            cantidad = f"{float(recipe.cantidad):.2f}"
            cantidad_item = QStandardItem(cantidad)
            cantidad_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            row.append(cantidad_item)

            self.recipe_model.appendRow(row)

        total = len(recipes)
        self.total_label.setText(f"Total de recetas: <b>{total}</b>")
        self.status_bar.showMessage(f"Se han cargado {total} recetas")

    def on_data_loaded(self, data):
        """Maneja los datos cargados desde la API"""
        if data.get("type") == "production_recipes":
            from models.production_recipe_model import ProductionRecipe
            recipes = [ProductionRecipe.from_dict(item) for item in data.get("data", [])]
            self.load_recipes(recipes)
        elif data.get("type") == "production_recipe_created":
            QMessageBox.information(self, "Éxito", "Receta creada correctamente")
            self.refresh_data()
        elif data.get("type") == "production_recipe_updated":
            QMessageBox.information(self, "Éxito", "Receta actualizada correctamente")
            self.refresh_data()
        elif data.get("type") == "production_recipe_deleted":
            QMessageBox.information(self, "Éxito", "Receta eliminada correctamente")
            self.refresh_data()

    def on_request_error(self, error_message):
        """Maneja errores de la API"""
        QMessageBox.critical(self, "Error", f"Error al cargar recetas: {error_message}")
        self.status_bar.showMessage(f"Error: {error_message}")

    def on_row_double_clicked(self, index):
        """Maneja el doble clic en una fila"""
        mapped_index = self.proxy_model.mapToSource(index)
        row = mapped_index.row()
        recipe_id = int(self.recipe_model.item(row, 0).text())
        self.recipe_selected.emit(recipe_id)
        self.on_view_recipe(recipe_id)

    def show_context_menu(self, position):
        """Muestra menú contextual para una fila"""
        index = self.recipe_table.indexAt(position)
        if not index.isValid():
            return

        context_menu = QMenu(self)
        view_action = QAction(QIcon("resources/icons/view.png"), "Ver detalles", self)
        edit_action = QAction(QIcon("resources/icons/edit.png"), "Editar", self)
        delete_action = QAction(QIcon("resources/icons/delete.png"), "Eliminar", self)

        context_menu.addAction(view_action)
        context_menu.addAction(edit_action)
        context_menu.addSeparator()
        context_menu.addAction(delete_action)

        mapped_index = self.proxy_model.mapToSource(index)
        row = mapped_index.row()
        recipe_id = int(self.recipe_model.item(row, 0).text())

        view_action.triggered.connect(lambda: self.on_view_recipe(recipe_id))
        edit_action.triggered.connect(lambda: self.on_edit_recipe(recipe_id))
        delete_action.triggered.connect(lambda: self.on_delete_recipe(recipe_id))

        context_menu.exec(self.recipe_table.viewport().mapToGlobal(position))

    def on_view_recipe(self, recipe_id):
        """Muestra detalles de una receta"""
        from .production_recipe_detail import ProductionRecipeDetailView
        recipe = self._get_recipe_by_id(recipe_id)
        if recipe:
            dialog = ProductionRecipeDetailView(self.api_client, recipe.to_dict())
            dialog.exec()
        else:
            QMessageBox.warning(self, "Error", "No se pudo cargar la receta")

    def on_add_recipe(self):
        """Muestra el diálogo para añadir una nueva receta"""
        from .production_recipe_form import ProductionRecipeForm
        dialog = ProductionRecipeForm(self.api_client)
        dialog.recipe_saved.connect(self._handle_recipe_save)
        dialog.exec()

    def on_edit_recipe(self, recipe_id):
        """Abre el formulario de edición de una receta"""
        recipe = self._get_recipe_by_id(recipe_id)
        if recipe:
            self._show_edit_form(recipe)
        else:
            QMessageBox.warning(self, "Error", "No se pudo cargar la receta")

    def _get_recipe_by_id(self, recipe_id):
        """Busca una receta por su ID en el modelo actual"""
        for row in range(self.recipe_model.rowCount()):
            if int(self.recipe_model.item(row, 0).text()) == recipe_id:
                from models.production_recipe_model import ProductionRecipe
                
                recipe_data = {
                    "id_receta": self.recipe_model.item(row, 0).text(),
                    "producto_nombre": self.recipe_model.item(row, 1).text(),
                    "material_nombre": self.recipe_model.item(row, 2).text(),
                    "cantidad": self.recipe_model.item(row, 3).text()
                }
                return ProductionRecipe.from_dict(recipe_data)
        return None

    def _show_edit_form(self, recipe):
        """Muestra el formulario de edición con los datos de la receta"""
        from .production_recipe_form import ProductionRecipeForm
        if recipe:
            dialog = ProductionRecipeForm(self.api_client, recipe.to_dict())
            dialog.recipe_saved.connect(self._handle_recipe_save)
            dialog.exec()
        else:
            QMessageBox.warning(self, "Error", "No se pudo cargar la receta")

    def _handle_recipe_save(self, recipe_data):
        """Maneja el guardado de una receta (nueva o editada)"""
        if "id_receta" in recipe_data and recipe_data["id_receta"]:
            # Actualizar receta
            self.api_client.update_production_recipe(recipe_data["id_receta"], {
                "id_producto": recipe_data["id_producto"],
                "id_material": recipe_data["id_material"],
                "cantidad": recipe_data["cantidad"]
            })
            self.status_bar.showMessage(f"Actualizando receta ID: {recipe_data['id_receta']}...")
        else:
            # Crear receta
            self.api_client.create_production_recipe({
                "id_producto": recipe_data["id_producto"],
                "id_material": recipe_data["id_material"],
                "cantidad": recipe_data["cantidad"]
            })
            self.status_bar.showMessage("Creando nueva receta...")

    def on_delete_recipe(self, recipe_id):
        """Elimina una receta"""
        reply = QMessageBox.question(
            self,
            "Confirmar eliminación",
            f"¿Está seguro que desea eliminar la receta ID: {recipe_id}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.api_client.delete_production_recipe(recipe_id)
            self.status_bar.showMessage(f"Eliminando receta ID: {recipe_id}...")