from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QLineEdit, QPushButton, QComboBox, QTextEdit, 
                            QFormLayout, QMessageBox, QDialog)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from utils.theme import Theme

class ClientForm(QDialog):
    """Formulario para crear o editar clientes"""
    
    # Señal emitida cuando se guarda un cliente
    client_saved = pyqtSignal(dict)
    
    def __init__(self, api_client, client_data=None, parent=None):
        super().__init__(parent)
        from utils.theme import Theme
        Theme.apply_window_light_theme(self)
        
        self.api_client = api_client
        self.client_data = client_data  # None para nuevo cliente, dict para edición
        self.edit_mode = client_data is not None
        
        self.init_ui()
        
        # Si estamos en modo edición, rellenar el formulario
        if self.edit_mode:
            self.fill_form()
    
    def init_ui(self):
        """Inicializa la interfaz de usuario"""
        # Configuración de la ventana
        self.setWindowTitle("Nuevo Cliente" if not self.edit_mode else "Editar Cliente")
        self.setMinimumWidth(500)
        self.setModal(True)
        
        # Layout principal
        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Título
        title = "Nuevo Cliente" if not self.edit_mode else "Editar Cliente"
        title_label = QLabel(title)
        title_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        title_label.setProperty("heading", True)
        
        # Formulario
        form_layout = QFormLayout()
        form_layout.setVerticalSpacing(10)
        form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        
        # Nombre del cliente
        self.nombre_input = QLineEdit()
        self.nombre_input.setPlaceholderText("Nombre completo o razón social")
        form_layout.addRow("Nombre:", self.nombre_input)
        
        # Persona de contacto
        self.contacto_input = QLineEdit()
        self.contacto_input.setPlaceholderText("Persona de contacto principal")
        form_layout.addRow("Contacto:", self.contacto_input)
        
        # Teléfono
        self.telefono_input = QLineEdit()
        self.telefono_input.setPlaceholderText("Teléfono de contacto")
        form_layout.addRow("Teléfono:", self.telefono_input)
        
        # Email
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Correo electrónico")
        form_layout.addRow("Email:", self.email_input)
        
        # Dirección
        self.direccion_input = QTextEdit()
        self.direccion_input.setPlaceholderText("Dirección completa")
        self.direccion_input.setMaximumHeight(100)
        form_layout.addRow("Dirección:", self.direccion_input)
        
        # Tipo de cliente
        self.tipo_combo = QComboBox()
        self.tipo_combo.addItems(["distribuidor", "mayorista", "minorista", "OEM"])
        form_layout.addRow("Tipo:", self.tipo_combo)
        
        # Botones
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
        
        # Conectar eventos
        self.save_button.clicked.connect(self.save_client)
        self.cancel_button.clicked.connect(self.reject)
        
        # Agregar widgets al layout principal
        main_layout.addWidget(title_label)
        main_layout.addLayout(form_layout)
        main_layout.addStretch()
        main_layout.addLayout(buttons_layout)
        
        # Establecer el layout
        self.setLayout(main_layout)
    
    def fill_form(self):
        """Rellena el formulario con los datos del cliente"""
        if not self.client_data:
            return
            
        self.nombre_input.setText(self.client_data.get("nombre", ""))
        self.contacto_input.setText(self.client_data.get("contacto", ""))
        self.telefono_input.setText(self.client_data.get("telefono", ""))
        self.email_input.setText(self.client_data.get("email", ""))
        self.direccion_input.setText(self.client_data.get("direccion", ""))
        
        # Establecer el tipo de cliente
        tipo = self.client_data.get("tipo", "")
        index = self.tipo_combo.findText(tipo)
        if index >= 0:
            self.tipo_combo.setCurrentIndex(index)
    
    def save_client(self):
        """Valida y guarda el cliente"""
        # Obtener datos
        nombre = self.nombre_input.text().strip()
        contacto = self.contacto_input.text().strip()
        telefono = self.telefono_input.text().strip()
        email = self.email_input.text().strip()
        direccion = self.direccion_input.toPlainText().strip()
        tipo = self.tipo_combo.currentText()
        
        # Validar campos obligatorios
        if not nombre:
            QMessageBox.warning(self, "Error de validación", "El nombre es obligatorio")
            return
            
        if not email:
            QMessageBox.warning(self, "Error de validación", "El email es obligatorio")
            return
        
        # Crear diccionario de datos
        client_data = {
            "nombre": nombre,
            "contacto": contacto,
            "telefono": telefono,
            "email": email,
            "direccion": direccion,
            "tipo": tipo
        }
        
        # Si estamos editando, incluir el ID
        if self.edit_mode and "id_cliente" in self.client_data:
            client_data["id_cliente"] = self.client_data["id_cliente"]
        
        # Emitir señal
        self.client_saved.emit(client_data)
        self.accept()