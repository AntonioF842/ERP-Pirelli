from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                           QLineEdit, QPushButton, QMessageBox, QFrame)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QIcon, QPixmap, QFont

class LoginView(QWidget):
    """Vista de inicio de sesión"""
    
    login_successful = pyqtSignal(dict)
    
    def __init__(self, api_client):
        super().__init__()
        from utils.theme import Theme
        Theme.apply_window_light_theme(self)
        self.api_client = api_client
        self.api_client.login_success.connect(self.on_login_success)
        self.api_client.login_error.connect(self.on_login_error)
        self.api_client.request_error.connect(self.on_request_error)
        self.init_ui()
    
    def init_ui(self):
        """Inicializa la interfaz de usuario"""
        self.setWindowTitle("ERP Pirelli - Iniciar Sesión")
        self.setFixedSize(400, 550)
        self.setWindowIcon(QIcon("resources/icons/pirelli_logo.png"))
        
        # Estilos principales con los nuevos colores
        self.setStyleSheet(f"""
            QWidget {{
                background-color: #fbe50d;
            }}
            QMessageBox {{
                background-color: white;
            }}
            QMessageBox QLabel {{
                color: black;
                font-size: 14px;
            }}
            QMessageBox QPushButton {{
                background-color: #ee221c;
                color: white;
                padding: 5px 15px;
                border-radius: 4px;
                font-weight: bold;
                min-width: 80px;
            }}
            QMessageBox QPushButton:hover {{
                background-color: #c61b17;
            }}
            QMessageBox QPushButton:pressed {{
                background-color: #a51714;
            }}
            QMessageBox QLabel#qt_msgboxex_icon_label {{
                color: white;
            }}
        """)

        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(40, 20, 40, 30)
        
        # Logo
        logo_label = QLabel()
        try:
            logo_pixmap = QPixmap("resources/images/pirelli_logo.png")
            if logo_pixmap.isNull():
                raise FileNotFoundError
            logo_label.setPixmap(logo_pixmap.scaledToWidth(320, Qt.TransformationMode.SmoothTransformation))
        except:
            logo_label = QLabel("PIRELLI ERP")
            logo_label.setFont(QFont("Arial", 24, QFont.Weight.Bold))
            logo_label.setStyleSheet("color: #ee221c;")
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Título
        title_label = QLabel("Sistema ERP Pirelli")
        title_label.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("color: #ee221c;")
        
        # Formulario
        form_frame = QFrame()
        form_frame.setFrameShape(QFrame.Shape.StyledPanel)
        form_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 10px;
                border: 2px solid #ee221c;
            }
        """)
        
        form_layout = QVBoxLayout(form_frame)
        form_layout.setSpacing(15)
        form_layout.setContentsMargins(20, 20, 20, 20)
        
        # Campos del formulario
        email_label = QLabel("Correo electrónico:")
        email_label.setStyleSheet("color: #ee221c; font-weight: bold;")
        
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Ingrese su correo electrónico")
        self.email_input.setStyleSheet("""
            QLineEdit {
                background-color: white;
                border: 1px solid #ee221c;
                border-radius: 5px;
                padding: 5px;
                color: black;
            }
            QLineEdit:focus {
                border: 2px solid #ee221c;
            }
            QLineEdit::placeholder {
                color: #ff9999;
                font-style: italic;
            }
        """)

        password_label = QLabel("Contraseña:")
        password_label.setStyleSheet("color: #ee221c; font-weight: bold;")
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Ingrese su contraseña")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setStyleSheet(self.email_input.styleSheet())
        
        # Botón de login
        self.login_button = QPushButton("Iniciar Sesión")
        self.login_button.setFixedHeight(40)
        self.login_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.login_button.setStyleSheet(f"""
            QPushButton {{
                background-color: #ee221c;
                color: white;
                font-weight: bold;
                border-radius: 5px;
                border: 1px solid #c61b17;
            }}
            QPushButton:hover {{
                background-color: #c61b17;
            }}
            QPushButton:pressed {{
                background-color: #a51714;
            }}
            QPushButton:disabled {{
                background-color: #ee221c;
                color: #cccccc;
            }}
        """)
        
        # Conexiones y disposición
        self.login_button.clicked.connect(self.authenticate)
        self.password_input.returnPressed.connect(self.authenticate)
        
        form_layout.addWidget(email_label)
        form_layout.addWidget(self.email_input)
        form_layout.addWidget(password_label)
        form_layout.addWidget(self.password_input)
        form_layout.addWidget(self.login_button)
        
        main_layout.addWidget(logo_label)
        main_layout.addWidget(title_label)
        main_layout.addWidget(form_frame)
        main_layout.addStretch()
        
        # Footer
        footer_label = QLabel("© 2025 Pirelli - Todos los derechos reservados")
        footer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        footer_label.setStyleSheet("color: #ee221c; font-weight: bold;")
        main_layout.addWidget(footer_label)
        
        self.setLayout(main_layout)
    
    def authenticate(self):
        email = self.email_input.text().strip()
        password = self.password_input.text()
        
        if not email:
            self.show_message("Advertencia", "Por favor ingrese su correo electrónico", QMessageBox.Icon.Warning)
            return
        
        if not password:
            self.show_message("Advertencia", "Por favor ingrese su contraseña", QMessageBox.Icon.Warning)
            return
        
        self.login_button.setEnabled(False)
        self.login_button.setText("Autenticando...")
        self.api_client.login(email, password)
    
    def show_message(self, title, message, icon):
        msg = QMessageBox()
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.setIcon(icon)
        msg.setStyleSheet("""
            QMessageBox QLabel#qt_msgboxex_icon_label {
                color: white;
            }
        """)
        msg.exec()
    
    def on_login_success(self, data):
        self.login_button.setEnabled(True)
        self.login_button.setText("Iniciar Sesión")
        self.login_successful.emit(data)
    
    def on_login_error(self, error_message):
        self.login_button.setEnabled(True)
        self.login_button.setText("Iniciar Sesión")
        self.show_message("Error de autenticación", error_message, QMessageBox.Icon.Warning)
    
    def on_request_error(self, error_message):
        self.login_button.setEnabled(True)
        self.login_button.setText("Iniciar Sesión")
        self.show_message("Error de conexión", error_message, QMessageBox.Icon.Critical)
    
    def clear_fields(self):
        self.email_input.clear()
        self.password_input.clear()
        self.email_input.setFocus()