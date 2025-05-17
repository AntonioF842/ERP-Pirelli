from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QPushButton, QComboBox, QDoubleSpinBox,
    QTextEdit, QFormLayout, QMessageBox, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QIcon
from models.product_model import Product
from utils.theme import Theme
import logging

logger = logging.getLogger(__name__)

class ProductForm(QDialog):
    """Formulario para crear o editar productos"""
    
    product_saved = pyqtSignal(dict)  # Señal emitida al guardar
    
    def __init__(self, api_client, product_data=None, parent=None):
        super().__init__(parent)
        Theme.apply_window_light_theme(self)
        
        self.api_client = api_client
        self.product_data = product_data or {}
        self.edit_mode = bool(product_data)
        
        self.setup_ui()
        self.setup_connections()
        
        if self.edit_mode:
            self.load_data()

    def setup_ui(self):
        """Configura la interfaz de usuario"""
        self.setWindowTitle("Editar Producto" if self.edit_mode else "Nuevo Producto")
        self.setMinimumSize(500, 400)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Título
        title = QLabel("Editar Producto" if self.edit_mode else "Crear Nuevo Producto")
        title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {Theme.PRIMARY_COLOR};")
        main_layout.addWidget(title)
        
        # Formulario
        form_frame = QFrame()
        form_frame.setFrameShape(QFrame.Shape.StyledPanel)
        form_layout = QFormLayout(form_frame)
        form_layout.setVerticalSpacing(15)
        form_layout.setContentsMargins(15, 15, 15, 15)
        
        # Código
        self.code_input = QLineEdit()
        self.code_input.setPlaceholderText("Código único del producto")
        self.code_input.setMaxLength(50)
        form_layout.addRow("Código:", self.code_input)
        
        # Nombre
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Nombre del producto")
        self.name_input.setMaxLength(100)
        form_layout.addRow("Nombre:", self.name_input)
        
        # Descripción
        self.desc_input = QTextEdit()
        self.desc_input.setPlaceholderText("Descripción detallada del producto")
        self.desc_input.setMaximumHeight(100)
        form_layout.addRow("Descripción:", self.desc_input)
        
        # Precio
        self.price_input = QDoubleSpinBox()
        self.price_input.setRange(0.01, 999999.99)
        self.price_input.setDecimals(2)
        self.price_input.setPrefix("$ ")
        self.price_input.setSuffix(" MXN")
        form_layout.addRow("Precio:", self.price_input)
        
        # Categoría
        self.category_combo = QComboBox()
        for value, display in Product.get_categorias_lista():
            self.category_combo.addItem(display, value)
        form_layout.addRow("Categoría:", self.category_combo)
        
        # Estado (solo en modo edición)
        if self.edit_mode:
            self.status_combo = QComboBox()
            for value, display in Product.get_estados_lista():
                self.status_combo.addItem(display, value)
            form_layout.addRow("Estado:", self.status_combo)
        
        main_layout.addWidget(form_frame)
        
        # Botones
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)
        
        self.save_btn = QPushButton("Guardar")
        self.save_btn.setIcon(QIcon("resources/icons/save.png"))
        self.save_btn.setFixedHeight(40)
        
        self.cancel_btn = QPushButton("Cancelar")
        self.cancel_btn.setIcon(QIcon("resources/icons/cancel.png"))
        self.cancel_btn.setFixedHeight(40)
        
        button_layout.addWidget(self.save_btn)
        button_layout.addStretch()
        button_layout.addWidget(self.cancel_btn)
        
        main_layout.addLayout(button_layout)

    def setup_connections(self):
        """Conecta señales y slots"""
        self.save_btn.clicked.connect(self.validate_and_save)
        self.cancel_btn.clicked.connect(self.reject)
        
        # Validación en tiempo real
        self.code_input.textChanged.connect(self.validate_code)
        self.name_input.textChanged.connect(self.validate_name)
        self.price_input.valueChanged.connect(self.validate_price)

    def load_data(self):
        """Carga los datos del producto en el formulario"""
        try:
            self.code_input.setText(self.product_data.get('codigo', ''))
            self.name_input.setText(self.product_data.get('nombre', ''))
            self.desc_input.setPlainText(self.product_data.get('descripcion', ''))
            self.price_input.setValue(float(self.product_data.get('precio', 0.01)))
            
            # Establecer categoría
            categoria = self.product_data.get('categoria', 'automovil')
            index = self.category_combo.findData(categoria)
            if index >= 0:
                self.category_combo.setCurrentIndex(index)
            
            # Establecer estado si está en modo edición
            if self.edit_mode and hasattr(self, 'status_combo'):
                estado = self.product_data.get('estado', 'activo')
                index = self.status_combo.findData(estado)
                if index >= 0:
                    self.status_combo.setCurrentIndex(index)
        except Exception as e:
            logger.error(f"Error al cargar datos del producto: {str(e)}")
            QMessageBox.critical(self, "Error", "No se pudieron cargar los datos del producto")

    def validate_code(self):
        """Valida el código del producto"""
        code = self.code_input.text().strip()
        if not code:
            self.code_input.setStyleSheet("border: 1px solid red;")
            return False
        self.code_input.setStyleSheet("")
        return True

    def validate_name(self):
        """Valida el nombre del producto"""
        name = self.name_input.text().strip()
        if not name:
            self.name_input.setStyleSheet("border: 1px solid red;")
            return False
        self.name_input.setStyleSheet("")
        return True

    def validate_price(self):
        """Valida el precio del producto"""
        price = self.price_input.value()
        if price <= 0:
            self.price_input.setStyleSheet("border: 1px solid red;")
            return False
        self.price_input.setStyleSheet("")
        return True

    def validate_and_save(self):
        """Valida y guarda el producto"""
        if not all([self.validate_code(), self.validate_name(), self.validate_price()]):
            QMessageBox.warning(self, "Validación", "Por favor complete todos los campos requeridos")
            return
            
        product_data = {
            'codigo': self.code_input.text().strip(),
            'nombre': self.name_input.text().strip(),
            'descripcion': self.desc_input.toPlainText().strip(),
            'precio': self.price_input.value(),
            'categoria': self.category_combo.currentData()
        }
        
        if self.edit_mode and hasattr(self, 'status_combo'):
            product_data['estado'] = self.status_combo.currentData()
        
        # Validar con el modelo
        product = Product.from_dict(product_data)
        is_valid, errors = product.validate()
        
        if not is_valid:
            error_msg = "Por favor corrija los siguientes errores:\n\n"
            error_msg += "\n".join(f"- {field}: {msg}" for field, msg in errors.items())
            QMessageBox.warning(self, "Error de Validación", error_msg)
            return
            
        # Si estamos editando, añadir el ID
        if self.edit_mode and 'id_producto' in self.product_data:
            product_data['id_producto'] = self.product_data['id_producto']
        
        # Emitir señal con los datos
        self.product_saved.emit(product_data)
        self.accept()