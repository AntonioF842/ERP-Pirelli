from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QScrollArea, QPushButton, QGroupBox, QGridLayout,
                            QMessageBox, QDialog, QFrame)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QPixmap, QIcon
from utils.theme import Theme

class SystemConfigurationDetailView(QDialog):
    """Vista detallada de una configuración del sistema"""
    
    edit_requested = pyqtSignal(dict)
    delete_requested = pyqtSignal(int)
    
    def __init__(self, api_client, config_data, parent=None):
        super().__init__(parent)
        Theme.apply_window_light_theme(self)
        
        self.api_client = api_client
        self.config_data = config_data
        
        self.init_ui()
    
    def init_ui(self):
        """Inicializa la interfaz de usuario"""
        self.setWindowTitle(f"Configuración: {self.config_data.get('parametro', 'Detalle')}")
        self.setMinimumSize(500, 300)
        
        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        header_layout = QHBoxLayout()
        
        icon_label = QLabel()
        icon_pixmap = QPixmap("resources/icons/settings.png")
        if not icon_pixmap.isNull():
            icon_label.setPixmap(icon_pixmap.scaled(48, 48, Qt.AspectRatioMode.KeepAspectRatio))
        
        title_label = QLabel(self.config_data.get("parametro", "Configuración"))
        title_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        
        header_layout.addWidget(icon_label)
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
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
        
        edit_button.clicked.connect(lambda: self.edit_requested.emit(self.config_data))
        delete_button.clicked.connect(self.confirm_delete)
        close_button.clicked.connect(self.close)
        
        info_group = QGroupBox("Detalles de la Configuración")
        info_layout = QGridLayout()
        
        info_layout.addWidget(QLabel("ID:"), 0, 0)
        id_label = QLabel(str(self.config_data.get("id_config", "N/A")))
        id_label.setStyleSheet("font-weight: bold;")
        info_layout.addWidget(id_label, 0, 1)
        
        info_layout.addWidget(QLabel("Valor:"), 1, 0)
        valor_label = QLabel(str(self.config_data.get("valor", "N/A")))
        valor_label.setStyleSheet("font-weight: bold;")
        info_layout.addWidget(valor_label, 1, 1)
        
        info_layout.addWidget(QLabel("Descripción:"), 2, 0, Qt.AlignmentFlag.AlignTop)
        descripcion_label = QLabel(self.config_data.get("descripcion", "Sin descripción"))
        descripcion_label.setWordWrap(True)
        descripcion_label.setStyleSheet("background-color: #f5f5f5; padding: 10px; border-radius: 5px;")
        info_layout.addWidget(descripcion_label, 2, 1, 1, 3)
        
        info_group.setLayout(info_layout)
        
        main_layout.addLayout(header_layout)
        main_layout.addWidget(info_group)
        main_layout.addStretch()
        main_layout.addLayout(action_layout)
        
        self.setLayout(main_layout)
    
    def confirm_delete(self):
        """Solicita confirmación para eliminar la configuración"""
        reply = QMessageBox.question(
            self,
            "Confirmar eliminación",
            f"¿Está seguro que desea eliminar la configuración '{self.config_data.get('parametro')}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.delete_requested.emit(self.config_data.get("id_config"))
            self.close()