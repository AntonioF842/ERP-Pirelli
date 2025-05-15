from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QScrollArea, QPushButton, QGroupBox, QGridLayout,
                            QMessageBox, QDialog, QFrame)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QPixmap, QIcon
from utils.theme import Theme

class ProductionAssetDetailView(QDialog):
    """Vista detallada de un activo de producción"""
    
    # Señales
    edit_requested = pyqtSignal(dict)
    delete_requested = pyqtSignal(int)
    
    def __init__(self, api_client, asset_data, parent=None):
        super().__init__(parent)
        Theme.apply_window_light_theme(self)
        
        self.api_client = api_client
        self.asset_data = asset_data
        
        self.init_ui()
    
    def init_ui(self):
        """Inicializa la interfaz de usuario"""
        # Configuración de la ventana
        self.setWindowTitle(f"Activo: {self.asset_data.get('nombre', 'Detalle')}")
        self.setMinimumSize(600, 400)
        
        # Layout principal
        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Encabezado
        header_layout = QHBoxLayout()
        
        # Icono y Título
        icon_label = QLabel()
        icon_pixmap = QPixmap("resources/icons/machine.png")
        if not icon_pixmap.isNull():
            icon_label.setPixmap(icon_pixmap.scaled(64, 64, Qt.AspectRatioMode.KeepAspectRatio))
        
        title_label = QLabel(self.asset_data.get("nombre", "Activo"))
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
        edit_button.clicked.connect(lambda: self.edit_requested.emit(self.asset_data))
        delete_button.clicked.connect(self.confirm_delete)
        close_button.clicked.connect(self.close)
        
        # Información del activo
        info_group = QGroupBox("Información del Activo")
        info_layout = QGridLayout()
        
        # ID
        info_layout.addWidget(QLabel("ID:"), 0, 0)
        id_label = QLabel(str(self.asset_data.get("id_activo", "N/A")))
        id_label.setStyleSheet("font-weight: bold;")
        info_layout.addWidget(id_label, 0, 1)
        
        # Tipo
        info_layout.addWidget(QLabel("Tipo:"), 0, 2)
        tipo_label = QLabel(self.asset_data.get("tipo", "N/A"))
        tipo_label.setStyleSheet("font-weight: bold;")
        info_layout.addWidget(tipo_label, 0, 3)
        
        # Área
        info_layout.addWidget(QLabel("Área:"), 1, 0)
        area_label = QLabel(self.asset_data.get("area_name", "N/A"))
        area_label.setStyleSheet("font-weight: bold;")
        info_layout.addWidget(area_label, 1, 1)
        
        # Fecha Adquisición
        info_layout.addWidget(QLabel("Fecha Adquisición:"), 1, 2)
        fecha_label = QLabel(self.asset_data.get("fecha_adquisicion", "N/A"))
        fecha_label.setStyleSheet("font-weight: bold;")
        info_layout.addWidget(fecha_label, 1, 3)
        
        # Estado
        info_layout.addWidget(QLabel("Estado:"), 2, 0)
        estado = self.asset_data.get("estado", "N/A")
        estado_label = QLabel(estado)
        
        # Color según estado
        if estado.lower() == "operativo":
            estado_label.setStyleSheet("font-weight: bold; color: #28a745;")
        elif estado.lower() == "mantenimiento":
            estado_label.setStyleSheet("font-weight: bold; color: #ffc107;")
        elif estado.lower() == "baja":
            estado_label.setStyleSheet("font-weight: bold; color: #dc3545;")
        else:
            estado_label.setStyleSheet("font-weight: bold;")
            
        info_layout.addWidget(estado_label, 2, 1)
        
        info_group.setLayout(info_layout)
        
        # Agregar widgets al layout principal
        main_layout.addLayout(header_layout)
        main_layout.addWidget(info_group)
        main_layout.addStretch()
        main_layout.addLayout(action_layout)
        
        # Establecer el layout
        self.setLayout(main_layout)
    
    def confirm_delete(self):
        """Solicita confirmación para eliminar el activo"""
        reply = QMessageBox.question(
            self,
            "Confirmar eliminación",
            f"¿Está seguro que desea eliminar el activo '{self.asset_data.get('nombre')}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Emitir señal con el ID del activo
            self.delete_requested.emit(self.asset_data.get("id_activo"))
            self.close()