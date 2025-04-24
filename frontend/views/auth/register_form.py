from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                           QLineEdit, QPushButton, QComboBox, QFrame, 
                           QFormLayout, QMessageBox)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

class RegisterForm(QWidget):
    """Formulario de registro de usuario"""
    
    # Señales
    register_requested = pyqtSignal(dict)
    login_requested = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        from utils.theme import Theme
        Theme.apply_window_light_theme(self)
        
        self.init_ui()
    
    def init_ui(self):
        """Inicializa la interfaz de usuario"""
        # Layout principal
        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Título
        title_label = QLabel("Registrar Usuario")
        title_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        
        # Formulario
        form_layout = QFormLayout()
        form_layout.setVerticalSpacing(10)
        form_layout.setHorizontalSpacing(20)
        
        # Nombre
        self.nombre_input = QLineEdit()
        self.nombre_input.setPlaceholderText("Ingrese su nombre completo")
        form_layout.addRow("Nombre:", self.nombre_input)
        
        # Email
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Ingrese su correo electrónico")
        form_layout.addRow("Email:", self.email_input)
        
        # Contraseña
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Ingrese su contraseña")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        form_layout.addRow("Contraseña:", self.password_input)
        
        # Confirmar contraseña
        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setPlaceholderText("Confirme su contraseña")
        self.confirm_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        form_layout.addRow("Confirmar contraseña:", self.confirm_password_input)
        
        # Rol (solo en caso de que sea un formulario administrativo)
        self.rol_combo = QComboBox()
        self.rol_combo.addItems(["empleado", "supervisor", "admin"])
        form_layout.addRow("Rol:", self.rol_combo)
        
        # Botones
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)
        
        self.register_button = QPushButton("Registrar")
        self.register_button.setFixedHeight(40)
        self.register_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.register_button.setStyleSheet("""
            QPushButton {
                background-color: #d60000;
                color: white;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #ff0000;
            }
            QPushButton:pressed {
                background-color: #b80000;
            }
        """)
        
        self.cancel_button = QPushButton("Cancelar")
        self.cancel_button.setFixedHeight(40)
        self.cancel_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #f0f0f0;
                border: 1px solid #ccc;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
            QPushButton:pressed {
                background-color: #d0d0d0;
            }
        """)
        
        buttons_layout.addWidget(self.register_button)
        buttons_layout.addWidget(self.cancel_button)
        
        # Conectar eventos
        self.register_button.clicked.connect(self.validate_and_register)
        self.cancel_button.clicked.connect(self.login_requested.emit)
        
        # Agregar widgets al layout principal
        main_layout.addWidget(title_label)
        main_layout.addLayout(form_layout)
        main_layout.addSpacing(20)
        main_layout.addLayout(buttons_layout)
        
        # Establecer el layout
        self.setLayout(main_layout)
    
    def validate_and_register(self):
        """Valida los datos del formulario y emite la señal de registro"""
        # Obtener datos
        nombre = self.nombre_input.text().strip()
        email = self.email_input.text().strip()
        password = self.password_input.text()
        confirm_password = self.confirm_password_input.text()
        rol = self.rol_combo.currentText()
        
        # Validar campos
        if not nombre:
            QMessageBox.warning(self, "Error de validación", "El nombre es obligatorio")
            return
        
        if not email:
            QMessageBox.warning(self, "Error de validación", "El email es obligatorio")
            return
        
        if not password:
            QMessageBox.warning(self, "Error de validación", "La contraseña es obligatoria")
            return
        
        if password != confirm_password:
            QMessageBox.warning(self, "Error de validación", "Las contraseñas no coinciden")
            return
        
        # Crear diccionario de datos
        user_data = {
            "nombre": nombre,
            "email": email,
            "password": password,
            "rol": rol
        }
        
        # Emitir señal de registro
        self.register_requested.emit(user_data)
    
    def clear_fields(self):
        """Limpia los campos del formulario"""
        self.nombre_input.clear()
        self.email_input.clear()
        self.password_input.clear()
        self.confirm_password_input.clear()
        self.rol_combo.setCurrentIndex(0)