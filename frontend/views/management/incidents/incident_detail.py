from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QScrollArea, QPushButton, QGroupBox, QGridLayout,
    QMessageBox, QDialog, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QPixmap, QIcon
from utils.theme import Theme

class IncidentDetailView(QDialog):
    """Vista detallada de un incidente"""
    
    edit_requested = pyqtSignal(dict)
    delete_requested = pyqtSignal(int)
    
    def __init__(self, api_client, incident_data, parent=None):
        super().__init__(parent)
        Theme.apply_window_light_theme(self)
        
        self.api_client = api_client
        self.incident_data = incident_data
        
        self.init_ui()
    
    def init_ui(self):
        """Inicializa la interfaz de usuario"""
        self.setWindowTitle(f"Incidente #{self.incident_data.get('id_incidente', 'Detalle')}")
        self.setMinimumSize(600, 400)
        
        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Encabezado
        header_layout = QHBoxLayout()
        
        icon_label = QLabel()
        icon_pixmap = QPixmap("resources/icons/incident.png")
        if not icon_pixmap.isNull():
            icon_label.setPixmap(icon_pixmap.scaled(64, 64, Qt.AspectRatioMode.KeepAspectRatio))
        
        title_label = QLabel(f"Incidente #{self.incident_data.get('id_incidente', '')}")
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
        
        edit_button.clicked.connect(lambda: self.edit_requested.emit(self.incident_data))
        delete_button.clicked.connect(self.confirm_delete)
        close_button.clicked.connect(self.close)
        
        # Información del incidente
        info_group = QGroupBox("Detalles del Incidente")
        info_layout = QGridLayout()
        
        # Tipo
        info_layout.addWidget(QLabel("Tipo:"), 0, 0)
        tipo_label = QLabel(str(self.incident_data.get("tipo", "N/A")).capitalize())
        tipo_label.setStyleSheet("font-weight: bold;")
        info_layout.addWidget(tipo_label, 0, 1)
        
        # Estado
        info_layout.addWidget(QLabel("Estado:"), 0, 2)
        estado_label = QLabel(str(self.incident_data.get("estado", "N/A")).capitalize())
        estado_label.setStyleSheet("font-weight: bold;")
        info_layout.addWidget(estado_label, 0, 3)
        
        # Fecha
        info_layout.addWidget(QLabel("Fecha:"), 1, 0)
        fecha_label = QLabel(self.incident_data.get("fecha", "N/A"))
        fecha_label.setStyleSheet("font-weight: bold;")
        info_layout.addWidget(fecha_label, 1, 1)
        
        # Área
        info_layout.addWidget(QLabel("Área:"), 1, 2)
        area_label = QLabel(str(self.incident_data.get("id_area", "N/A")))
        area_label.setStyleSheet("font-weight: bold;")
        info_layout.addWidget(area_label, 1, 3)
        
        # Reportado por
        info_layout.addWidget(QLabel("Reportado por:"), 2, 0)
        reportado_label = QLabel(str(self.incident_data.get("id_empleado_reporta", "N/A")))
        reportado_label.setStyleSheet("font-weight: bold;")
        info_layout.addWidget(reportado_label, 2, 1)
        
        # Descripción
        info_layout.addWidget(QLabel("Descripción:"), 3, 0, Qt.AlignmentFlag.AlignTop)
        descripcion_label = QLabel(self.incident_data.get("descripcion", "Sin descripción"))
        descripcion_label.setWordWrap(True)
        descripcion_label.setStyleSheet("background-color: #f5f5f5; padding: 10px; border-radius: 5px;")
        info_layout.addWidget(descripcion_label, 3, 1, 1, 3)
        
        info_group.setLayout(info_layout)
        
        main_layout.addLayout(header_layout)
        main_layout.addWidget(info_group)
        main_layout.addStretch()
        main_layout.addLayout(action_layout)
        
        self.setLayout(main_layout)
    
    def confirm_delete(self):
        """Solicita confirmación para eliminar el incidente"""
        reply = QMessageBox.question(
            self,
            "Confirmar eliminación",
            f"¿Está seguro que desea eliminar el incidente #{self.incident_data.get('id_incidente')}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.delete_requested.emit(self.incident_data.get("id_incidente"))
            self.close()