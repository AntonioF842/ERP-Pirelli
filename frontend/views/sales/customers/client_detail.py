from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QScrollArea, QPushButton, QGroupBox, QGridLayout,
                            QMessageBox, QDialog, QFrame)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QPixmap, QIcon

class ClientDetailView(QDialog):
    """Vista detallada de un cliente"""
    
    # Señales
    edit_requested = pyqtSignal(dict)
    delete_requested = pyqtSignal(int)
    
    def __init__(self, api_client, client_data, parent=None):
        super().__init__(parent)
        from utils.theme import Theme
        Theme.apply_window_light_theme(self)
        
        self.api_client = api_client
        self.client_data = client_data
        
        self.init_ui()
    
    def init_ui(self):
        """Inicializa la interfaz de usuario"""
        # Configuración de la ventana
        self.setWindowTitle(f"Cliente: {self.client_data.get('nombre', 'Detalle')}")
        self.setMinimumSize(600, 400)
        
        # Layout principal
        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Encabezado
        header_layout = QHBoxLayout()
        
        # Icono y Título
        icon_label = QLabel()
        icon_pixmap = QPixmap("resources/icons/client.png")
        if not icon_pixmap.isNull():
            icon_label.setPixmap(icon_pixmap.scaled(64, 64, Qt.AspectRatioMode.KeepAspectRatio))
        
        title_label = QLabel(self.client_data.get("nombre", "Cliente"))
        title_label.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        
        header_layout.addWidget(icon_label)
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        # Botones de acción
        action_layout = QHBoxLayout()
        
        edit_button = QPushButton("Editar")
        edit_button.setIcon(QIcon("resources/icons/edit.png"))
        edit_button.setCursor(Qt.CursorShape.PointingHandCursor)
        
        delete_button = QPushButton("Eliminar")
        delete_button.setIcon(QIcon("resources/icons/delete.png"))
        delete_button.setCursor(Qt.CursorShape.PointingHandCursor)
        delete_button.setStyleSheet("color: #d60000;")
        
        close_button = QPushButton("Cerrar")
        close_button.setCursor(Qt.CursorShape.PointingHandCursor)
        
        action_layout.addWidget(edit_button)
        action_layout.addWidget(delete_button)
        action_layout.addStretch()
        action_layout.addWidget(close_button)
        
        # Conectar eventos
        edit_button.clicked.connect(lambda: self.edit_requested.emit(self.client_data))
        delete_button.clicked.connect(self.confirm_delete)
        close_button.clicked.connect(self.close)
        
        # Información del cliente
        info_group = QGroupBox("Información del Cliente")
        info_layout = QGridLayout()
        
        # Contacto
        info_layout.addWidget(QLabel("Contacto:"), 0, 0)
        contacto_label = QLabel(self.client_data.get("contacto", "N/A"))
        contacto_label.setStyleSheet("font-weight: bold;")
        info_layout.addWidget(contacto_label, 0, 1)
        
        # Tipo
        info_layout.addWidget(QLabel("Tipo:"), 0, 2)
        tipo_label = QLabel(self.client_data.get("tipo", "N/A"))
        tipo_label.setStyleSheet("font-weight: bold;")
        info_layout.addWidget(tipo_label, 0, 3)
        
        # Teléfono
        info_layout.addWidget(QLabel("Teléfono:"), 1, 0)
        telefono_label = QLabel(self.client_data.get("telefono", "N/A"))
        telefono_label.setStyleSheet("font-weight: bold;")
        info_layout.addWidget(telefono_label, 1, 1)
        
        # Email
        info_layout.addWidget(QLabel("Email:"), 1, 2)
        email_label = QLabel(self.client_data.get("email", "N/A"))
        email_label.setStyleSheet("font-weight: bold;")
        info_layout.addWidget(email_label, 1, 3)
        
        # Dirección
        info_layout.addWidget(QLabel("Dirección:"), 2, 0, Qt.AlignmentFlag.AlignTop)
        direccion_label = QLabel(self.client_data.get("direccion", "Sin dirección"))
        direccion_label.setWordWrap(True)
        direccion_label.setStyleSheet("background-color: #f5f5f5; padding: 10px; border-radius: 5px;")
        info_layout.addWidget(direccion_label, 2, 1, 1, 3)
        
        info_group.setLayout(info_layout)
        
        # Agregar widgets al layout principal
        main_layout.addLayout(header_layout)
        main_layout.addWidget(info_group)
        main_layout.addStretch()
        main_layout.addLayout(action_layout)
        
        # Establecer el layout
        self.setLayout(main_layout)
    
    def confirm_delete(self):
        """Solicita confirmación para eliminar el cliente"""
        reply = QMessageBox.question(
            self,
            "Confirmar eliminación",
            f"¿Está seguro que desea eliminar el cliente '{self.client_data.get('nombre')}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Emitir señal con el ID del cliente
            self.delete_requested.emit(self.client_data.get("id_cliente"))
            self.close()