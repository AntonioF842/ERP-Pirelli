from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                           QLineEdit, QPushButton, QCheckBox, QFrame)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

class LoginForm(QWidget):
    """Formulario de inicio de sesión"""
    
    # Señales
    login_requested = pyqtSignal(str, str, bool)
    register_requested = pyqtSignal()
    
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
        title_label = QLabel("Iniciar Sesión")
        title_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        
        # Correo electrónico
        email_label = QLabel("Correo electrónico:")
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Ingrese su correo electrónico")
        
        # Contraseña
        password_label = QLabel("Contraseña:")
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Ingrese su contraseña")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        
        # Recordar usuario
        self.remember_checkbox = QCheckBox("Recordar usuario")
        
        # Botones
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)
        
        self.login_button = QPushButton("Iniciar Sesión")
        self.login_button.setFixedHeight(40)
        self.login_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.login_button.setStyleSheet("""
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
        
        self.register_button = QPushButton("Registrarse")
        self.register_button.setFixedHeight(40)
        self.register_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.register_button.setStyleSheet("""
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
        
        buttons_layout.addWidget(self.login_button)
        buttons_layout.addWidget(self.register_button)
        
        # Conectar eventos
        self.login_button.clicked.connect(self.request_login)
        self.password_input.returnPressed.connect(self.request_login)
        self.register_button.clicked.connect(self.request_register)
        
        # Línea divisoria
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        
        # Agregar widgets al layout principal
        main_layout.addWidget(title_label)
        main_layout.addWidget(email_label)
        main_layout.addWidget(self.email_input)
        main_layout.addWidget(password_label)
        main_layout.addWidget(self.password_input)
        main_layout.addWidget(self.remember_checkbox)
        main_layout.addLayout(buttons_layout)
        
        # Establecer el layout
        self.setLayout(main_layout)
    
    def request_login(self):
        """Emite la señal de solicitud de inicio de sesión"""
        email = self.email_input.text().strip()
        password = self.password_input.text()
        remember = self.remember_checkbox.isChecked()
        
        self.login_requested.emit(email, password, remember)
    
    def request_register(self):
        """Emite la señal de solicitud de registro"""
        self.register_requested.emit()
    
    def clear_fields(self):
        """Limpia los campos de entrada"""
        self.email_input.clear()
        self.password_input.clear()
        self.remember_checkbox.setChecked(False)
    
    def set_email(self, email):
        """Establece el correo electrónico"""
        self.email_input.setText(email)