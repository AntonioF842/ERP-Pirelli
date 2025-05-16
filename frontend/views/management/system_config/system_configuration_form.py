from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QLineEdit, QPushButton, QTextEdit, QFormLayout, 
                            QMessageBox, QDialog)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from utils.theme import Theme

class SystemConfigurationForm(QDialog):
    """Formulario para crear o editar configuraciones del sistema"""
    
    # Señal emitida cuando se guarda una configuración
    configuration_saved = pyqtSignal(dict)
    
    def __init__(self, api_client, config_data=None, parent=None):
        super().__init__(parent)
        Theme.apply_window_light_theme(self)
        
        self.api_client = api_client
        self.config_data = config_data
        self.edit_mode = config_data is not None
        
        self.init_ui()
        
        if self.edit_mode:
            self.fill_form()
    
    def init_ui(self):
        """Inicializa la interfaz de usuario"""
        self.setWindowTitle("Nueva Configuración" if not self.edit_mode else "Editar Configuración")
        self.setMinimumWidth(500)
        self.setModal(True)
        
        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        title_label = QLabel("Nueva Configuración" if not self.edit_mode else "Editar Configuración")
        title_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        title_label.setProperty("heading", True)
        
        form_layout = QFormLayout()
        form_layout.setVerticalSpacing(10)
        form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        
        self.parametro_input = QLineEdit()
        self.parametro_input.setPlaceholderText("Nombre del parámetro")
        form_layout.addRow("Parámetro:", self.parametro_input)
        
        self.valor_input = QLineEdit()
        self.valor_input.setPlaceholderText("Valor del parámetro")
        form_layout.addRow("Valor:", self.valor_input)
        
        self.descripcion_input = QTextEdit()
        self.descripcion_input.setPlaceholderText("Descripción del parámetro")
        self.descripcion_input.setMaximumHeight(100)
        form_layout.addRow("Descripción:", self.descripcion_input)
        
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
        
        self.save_button.clicked.connect(self.save_configuration)
        self.cancel_button.clicked.connect(self.reject)
        
        main_layout.addWidget(title_label)
        main_layout.addLayout(form_layout)
        main_layout.addStretch()
        main_layout.addLayout(buttons_layout)
        
        self.setLayout(main_layout)
    
    def fill_form(self):
        """Rellena el formulario con los datos de la configuración"""
        if not self.config_data:
            return
            
        self.parametro_input.setText(self.config_data.get("parametro", ""))
        self.valor_input.setText(str(self.config_data.get("valor", "")))
        self.descripcion_input.setText(self.config_data.get("descripcion", ""))
    
    def save_configuration(self):
        """Valida y guarda la configuración"""
        parametro = self.parametro_input.text().strip()
        valor = self.valor_input.text().strip()
        descripcion = self.descripcion_input.toPlainText().strip()
        
        if not parametro:
            QMessageBox.warning(self, "Error de validación", "El parámetro es obligatorio")
            return
            
        if not valor:
            QMessageBox.warning(self, "Error de validación", "El valor es obligatorio")
            return
        
        config_data = {
            "parametro": parametro,
            "valor": valor,
            "descripcion": descripcion
        }
        
        if self.edit_mode and "id_config" in self.config_data:
            config_data["id_config"] = self.config_data["id_config"]
        
        self.configuration_saved.emit(config_data)
        self.accept()