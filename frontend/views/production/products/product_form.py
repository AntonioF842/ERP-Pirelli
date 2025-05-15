from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QLineEdit, QPushButton, QComboBox, QSpinBox,
                            QDoubleSpinBox, QTextEdit, QFormLayout, 
                            QMessageBox, QDialog)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from utils.theme import Theme

class ProductForm(QDialog):
    """Formulario para crear o editar productos"""
    
    # Señal emitida cuando se guarda un producto
    product_saved = pyqtSignal(dict)
    
    def __init__(self, api_client, product_data=None, parent=None):
        super().__init__(parent)
        from utils.theme import Theme
        Theme.apply_window_light_theme(self)
        
        self.api_client = api_client
        self.product_data = product_data  # None para nuevo producto, dict para edición
        self.edit_mode = product_data is not None
        
        self.init_ui()
        
        # Si estamos en modo edición, rellenar el formulario
        if self.edit_mode:
            self.fill_form()
    
    def init_ui(self):
        """Inicializa la interfaz de usuario"""
        # Configuración de la ventana
        self.setWindowTitle("Nuevo Producto" if not self.edit_mode else "Editar Producto")
        self.setMinimumWidth(500)
        self.setModal(True)
        
        # Layout principal
        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Título
        title = "Nuevo Producto" if not self.edit_mode else "Editar Producto"
        title_label = QLabel(title)
        title_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        title_label.setProperty("heading", True)  # Usar propiedad de estilo del tema
        
        # Formulario
        form_layout = QFormLayout()
        form_layout.setVerticalSpacing(10)
        form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        
        # Código del producto
        self.codigo_input = QLineEdit()
        self.codigo_input.setPlaceholderText("Código único del producto")
        form_layout.addRow("Código:", self.codigo_input)
        
        # Nombre del producto
        self.nombre_input = QLineEdit()
        self.nombre_input.setPlaceholderText("Nombre del producto")
        form_layout.addRow("Nombre:", self.nombre_input)
        
        # Descripción
        self.descripcion_input = QTextEdit()
        self.descripcion_input.setPlaceholderText("Descripción detallada del producto")
        self.descripcion_input.setMaximumHeight(100)
        form_layout.addRow("Descripción:", self.descripcion_input)
        
        # Precio
        self.precio_input = QDoubleSpinBox()
        self.precio_input.setRange(0.01, 999999.99)
        self.precio_input.setDecimals(2)
        self.precio_input.setSingleStep(0.01)
        self.precio_input.setPrefix("$ ")
        form_layout.addRow("Precio:", self.precio_input)
        
        # Categoría
        self.categoria_combo = QComboBox()
        self.categoria_combo.addItems(["automovil", "motocicleta", "camion", "industrial"])
        form_layout.addRow("Categoría:", self.categoria_combo)
        
        # Botones
        buttons_layout = QHBoxLayout()
        
        # Usar propiedades de tema para los botones
        self.save_button = QPushButton("Guardar")
        self.save_button.setFixedHeight(40)
        self.save_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.save_button.setProperty("secondary", True)  # Usar propiedad de estilo del tema
        
        self.cancel_button = QPushButton("Cancelar")
        self.cancel_button.setFixedHeight(40)
        self.cancel_button.setCursor(Qt.CursorShape.PointingHandCursor)
        
        buttons_layout.addWidget(self.save_button)
        buttons_layout.addWidget(self.cancel_button)
        
        # Conectar eventos
        self.save_button.clicked.connect(self.save_product)
        self.cancel_button.clicked.connect(self.reject)
        
        # Agregar widgets al layout principal
        main_layout.addWidget(title_label)
        main_layout.addLayout(form_layout)
        main_layout.addStretch()
        main_layout.addLayout(buttons_layout)
        
        # Establecer el layout
        self.setLayout(main_layout)
    
    def fill_form(self):
        """Rellena el formulario con los datos del producto"""
        if not self.product_data:
            return
            
        self.codigo_input.setText(self.product_data.get("codigo", ""))
        self.nombre_input.setText(self.product_data.get("nombre", ""))
        self.descripcion_input.setText(self.product_data.get("descripcion", ""))
        self.precio_input.setValue(float(self.product_data.get("precio", 0)))
        
        # Establecer la categoría
        categoria = self.product_data.get("categoria", "")
        index = self.categoria_combo.findText(categoria)
        if index >= 0:
            self.categoria_combo.setCurrentIndex(index)
    
    def save_product(self):
        """Valida y guarda el producto"""
        # Obtener datos
        codigo = self.codigo_input.text().strip()
        nombre = self.nombre_input.text().strip()
        descripcion = self.descripcion_input.toPlainText().strip()
        precio = self.precio_input.value()
        categoria = self.categoria_combo.currentText()
        
        # Validar campos obligatorios
        if not codigo:
            QMessageBox.warning(self, "Error de validación", "El código es obligatorio")
            return
            
        if not nombre:
            QMessageBox.warning(self, "Error de validación", "El nombre es obligatorio")
            return
        
        # Crear diccionario de datos
        product_data = {
            "codigo": codigo,
            "nombre": nombre,
            "descripcion": descripcion,
            "precio": str(precio),
            "categoria": categoria
        }
        
        # Si estamos editando, incluir el ID
        if self.edit_mode and "id_producto" in self.product_data:
            product_data["id_producto"] = self.product_data["id_producto"]
        
        # Emitir señal
        self.product_saved.emit(product_data)
        self.accept()