from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QPushButton, QComboBox, QSpinBox,
    QDoubleSpinBox, QTextEdit, QFormLayout, 
    QMessageBox, QDialog
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from utils.theme import Theme

class ProductionRecipeForm(QDialog):
    """Formulario para crear o editar recetas de producción"""
    
    recipe_saved = pyqtSignal(dict)
    
    def __init__(self, api_client, recipe_data=None, parent=None):
        super().__init__(parent)
        Theme.apply_window_light_theme(self)
        
        self.api_client = api_client
        self.recipe_data = recipe_data
        self.edit_mode = recipe_data is not None
        
        self.products = []
        self.materials = []
        
        self.init_ui()
        
        # Cargar datos asincrónicamente
        self.load_products()
        self.load_materials()
        
        if self.edit_mode:
            self.fill_form()
    
    def init_ui(self):
        """Inicializa la interfaz de usuario"""
        self.setWindowTitle("Nueva Receta" if not self.edit_mode else "Editar Receta")
        self.setMinimumWidth(500)
        self.setModal(True)
        
        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        title = "Nueva Receta de Producción" if not self.edit_mode else "Editar Receta de Producción"
        title_label = QLabel(title)
        title_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        title_label.setProperty("heading", True)
        
        form_layout = QFormLayout()
        form_layout.setVerticalSpacing(10)
        form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        
        # Producto
        self.product_combo = QComboBox()
        self.product_combo.setPlaceholderText("Cargando productos...")
        form_layout.addRow("Producto:", self.product_combo)
        
        # Material
        self.material_combo = QComboBox()
        self.material_combo.setPlaceholderText("Cargando materiales...")
        form_layout.addRow("Material:", self.material_combo)
        
        # Cantidad
        self.cantidad_input = QDoubleSpinBox()
        self.cantidad_input.setRange(0.01, 999999.99)
        self.cantidad_input.setDecimals(2)
        self.cantidad_input.setSingleStep(0.01)
        form_layout.addRow("Cantidad:", self.cantidad_input)
        
        buttons_layout = QHBoxLayout()
        
        self.save_button = QPushButton("Guardar")
        self.save_button.setFixedHeight(40)
        self.save_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.save_button.setProperty("secondary", True)
        
        self.cancel_button = QPushButton("Cancelar")
        self.cancel_button.setFixedHeight(40)
        self.cancel_button.setCursor(Qt.CursorShape.PointingHandCursor)
        
        buttons_layout.addWidget(self.save_button)
        buttons_layout.addWidget(self.cancel_button)
        
        self.save_button.clicked.connect(self.save_recipe)
        self.cancel_button.clicked.connect(self.reject)
        
        main_layout.addWidget(title_label)
        main_layout.addLayout(form_layout)
        main_layout.addStretch()
        main_layout.addLayout(buttons_layout)
        
        self.setLayout(main_layout)
    
    def load_products(self):
        """Carga los productos desde la API"""
        self.api_client.get_products()
        self.api_client.data_received.connect(self._on_products_loaded)
    
    def _on_products_loaded(self, data):
        """Maneja la carga de productos"""
        if data.get("type") == "products":
            self.api_client.data_received.disconnect(self._on_products_loaded)
            self.products = data.get("data", [])
            
            self.product_combo.clear()
            self.product_combo.addItem("Seleccione un producto", None)
            
            for product in self.products:
                self.product_combo.addItem(
                    f"{product.get('nombre')} ({product.get('codigo')})",
                    product.get('id_producto')
                )
    
    def load_materials(self):
        """Carga los materiales desde la API"""
        self.api_client.get_materials()
        self.api_client.data_received.connect(self._on_materials_loaded)
    
    def _on_materials_loaded(self, data):
        """Maneja la carga de materiales"""
        if data.get("type") == "materials":
            self.api_client.data_received.disconnect(self._on_materials_loaded)
            self.materials = data.get("data", [])
            
            self.material_combo.clear()
            self.material_combo.addItem("Seleccione un material", None)
            
            for material in self.materials:
                self.material_combo.addItem(
                    material.get('nombre', 'Material sin nombre'),
                    material.get('id_material')
                )
    
    def fill_form(self):
        """Rellena el formulario con los datos de la receta"""
        if not self.recipe_data:
            return
            
        # Establecer producto seleccionado
        product_id = self.recipe_data.get("id_producto")
        if product_id:
            index = self.product_combo.findData(product_id)
            if index >= 0:
                self.product_combo.setCurrentIndex(index)
        
        # Establecer material seleccionado
        material_id = self.recipe_data.get("id_material")
        if material_id:
            index = self.material_combo.findData(material_id)
            if index >= 0:
                self.material_combo.setCurrentIndex(index)
        
        # Establecer cantidad
        self.cantidad_input.setValue(float(self.recipe_data.get("cantidad", 0)))
    
    def save_recipe(self):
        """Valida y guarda la receta"""
        product_id = self.product_combo.currentData()
        material_id = self.material_combo.currentData()
        cantidad = self.cantidad_input.value()
        
        if not product_id:
            QMessageBox.warning(self, "Error de validación", "Debe seleccionar un producto")
            return
            
        if not material_id:
            QMessageBox.warning(self, "Error de validación", "Debe seleccionar un material")
            return
        
        if cantidad <= 0:
            QMessageBox.warning(self, "Error de validación", "La cantidad debe ser mayor que cero")
            return
        
        # Obtener nombres para mostrar
        product_name = self.product_combo.currentText()
        material_name = self.material_combo.currentText()
        
        recipe_data = {
            "id_producto": product_id,
            "producto_nombre": product_name,
            "id_material": material_id,
            "material_nombre": material_name,
            "cantidad": str(cantidad)
        }
        
        if self.edit_mode and "id_receta" in self.recipe_data:
            recipe_data["id_receta"] = self.recipe_data["id_receta"]
        
        self.recipe_saved.emit(recipe_data)
        self.accept()