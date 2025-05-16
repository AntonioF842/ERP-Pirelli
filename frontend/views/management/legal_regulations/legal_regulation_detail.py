from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QScrollArea, QPushButton, QGroupBox, QGridLayout,
                            QMessageBox, QDialog, QFrame)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QPixmap, QIcon

class LegalRegulationDetailView(QDialog):
    """Vista detallada de una normativa legal"""
    
    # Señales
    edit_requested = pyqtSignal(dict)
    delete_requested = pyqtSignal(int)
    
    def __init__(self, api_client, regulation_data, parent=None):
        super().__init__(parent)
        from utils.theme import Theme
        Theme.apply_window_light_theme(self)
        
        self.api_client = api_client
        self.regulation_data = regulation_data
        
        self.init_ui()
    
    def init_ui(self):
        """Inicializa la interfaz de usuario"""
        # Configuración de la ventana
        self.setWindowTitle(f"Normativa: {self.regulation_data.get('nombre', 'Detalle')}")
        self.setMinimumSize(600, 400)
        
        # Layout principal
        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Encabezado
        header_layout = QHBoxLayout()
        
        # Icono y Título
        icon_label = QLabel()
        icon_pixmap = QPixmap("resources/icons/law.png")
        if not icon_pixmap.isNull():
            icon_label.setPixmap(icon_pixmap.scaled(64, 64, Qt.AspectRatioMode.KeepAspectRatio))
        
        title_label = QLabel(self.regulation_data.get("nombre", "Normativa"))
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
        edit_button.clicked.connect(lambda: self.edit_requested.emit(self.regulation_data))
        delete_button.clicked.connect(self.confirm_delete)
        close_button.clicked.connect(self.close)
        
        # Información de la normativa
        info_group = QGroupBox("Información de la Normativa")
        info_layout = QGridLayout()
        
        # Tipo
        info_layout.addWidget(QLabel("Tipo:"), 0, 0)
        tipo_label = QLabel(self.regulation_data.get("tipo", "N/A"))
        tipo_label.setStyleSheet("font-weight: bold;")
        info_layout.addWidget(tipo_label, 0, 1)
        
        # Fecha Actualización
        info_layout.addWidget(QLabel("Fecha Actualización:"), 0, 2)
        fecha_label = QLabel(self.regulation_data.get("fecha_actualizacion", "N/A"))
        fecha_label.setStyleSheet("font-weight: bold;")
        info_layout.addWidget(fecha_label, 0, 3)
        
        # Aplicable a
        info_layout.addWidget(QLabel("Aplicable a:"), 1, 0)
        aplicable_label = QLabel(self.regulation_data.get("aplicable_a", "N/A"))
        aplicable_label.setStyleSheet("font-weight: bold;")
        info_layout.addWidget(aplicable_label, 1, 1, 1, 3)
        
        # Descripción
        info_layout.addWidget(QLabel("Descripción:"), 2, 0, Qt.AlignmentFlag.AlignTop)
        descripcion_label = QLabel(self.regulation_data.get("descripcion", "Sin descripción"))
        descripcion_label.setWordWrap(True)
        descripcion_label.setStyleSheet("background-color: #f5f5f5; padding: 10px; border-radius: 5px;")
        info_layout.addWidget(descripcion_label, 2, 1, 1, 3)
        
        info_group.setLayout(info_layout)
        
        # Agregar widgets al layout principal
        main_layout.addLayout(header_layout)
        main_layout.addWidget(info_group)
        main_layout.addStretch()
        main_layout.addLayout(action_layout)
        
        # Establecer el layout
        self.setLayout(main_layout)
    
    def confirm_delete(self):
        """Solicita confirmación para eliminar la normativa"""
        reply = QMessageBox.question(
            self,
            "Confirmar eliminación",
            f"¿Está seguro que desea eliminar la normativa '{self.regulation_data.get('nombre')}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Emitir señal con el ID de la normativa
            self.delete_requested.emit(self.regulation_data.get("id_normativa"))
            self.close()