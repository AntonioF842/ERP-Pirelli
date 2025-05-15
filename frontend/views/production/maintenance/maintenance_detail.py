from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QScrollArea, QPushButton, QGroupBox, QGridLayout,
                            QMessageBox, QDialog, QFrame)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QPixmap, QIcon

class MaintenanceDetailView(QDialog):
    """Vista detallada de un registro de mantenimiento"""
    
    # Señales
    edit_requested = pyqtSignal(dict)
    delete_requested = pyqtSignal(int)
    
    def __init__(self, api_client, maintenance_data, parent=None):
        super().__init__(parent)
        from utils.theme import Theme
        Theme.apply_window_light_theme(self)
        
        self.api_client = api_client
        self.maintenance_data = maintenance_data
        
        self.init_ui()
    
    def init_ui(self):
        """Inicializa la interfaz de usuario"""
        # Configuración de la ventana
        self.setWindowTitle(f"Mantenimiento: {self.maintenance_data.get('id_mantenimiento', 'Detalle')}")
        self.setMinimumSize(600, 400)
        
        # Layout principal
        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Encabezado
        header_layout = QHBoxLayout()
        
        # Icono y Título
        icon_label = QLabel()
        icon_pixmap = QPixmap("resources/icons/maintenance.png")
        if not icon_pixmap.isNull():
            icon_label.setPixmap(icon_pixmap.scaled(64, 64, Qt.AspectRatioMode.KeepAspectRatio))
        
        title_label = QLabel(f"Mantenimiento #{self.maintenance_data.get('id_mantenimiento', '')}")
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
        edit_button.clicked.connect(lambda: self.edit_requested.emit(self.maintenance_data))
        delete_button.clicked.connect(self.confirm_delete)
        close_button.clicked.connect(self.close)
        
        # Información del mantenimiento
        info_group = QGroupBox("Detalles del Mantenimiento")
        info_layout = QGridLayout()
        
        # Activo
        info_layout.addWidget(QLabel("Activo:"), 0, 0)
        activo_label = QLabel(self.maintenance_data.get("activo_nombre", "N/A"))
        activo_label.setStyleSheet("font-weight: bold;")
        info_layout.addWidget(activo_label, 0, 1)
        
        # Tipo
        info_layout.addWidget(QLabel("Tipo:"), 0, 2)
        tipo_label = QLabel("Preventivo" if self.maintenance_data.get("tipo") == "preventivo" else "Correctivo")
        tipo_label.setStyleSheet("font-weight: bold;")
        info_layout.addWidget(tipo_label, 0, 3)
        
        # Fecha
        info_layout.addWidget(QLabel("Fecha:"), 1, 0)
        fecha_label = QLabel(self.maintenance_data.get("fecha", "N/A"))
        fecha_label.setStyleSheet("font-weight: bold;")
        info_layout.addWidget(fecha_label, 1, 1)
        
        # Técnico
        info_layout.addWidget(QLabel("Técnico:"), 1, 2)
        tecnico_label = QLabel(self.maintenance_data.get("empleado_nombre", "No asignado"))
        tecnico_label.setStyleSheet("font-weight: bold;")
        info_layout.addWidget(tecnico_label, 1, 3)
        
        # Costo
        info_layout.addWidget(QLabel("Costo:"), 2, 0)
        costo = float(self.maintenance_data.get("costo", 0))
        costo_label = QLabel(f"${costo:.2f}")
        costo_label.setStyleSheet("font-weight: bold; color: #d60000;")
        info_layout.addWidget(costo_label, 2, 1)
        
        # Descripción
        info_layout.addWidget(QLabel("Descripción:"), 3, 0, Qt.AlignmentFlag.AlignTop)
        descripcion = self.maintenance_data.get("descripcion", "Sin descripción disponible")
        descripcion_label = QLabel(descripcion)
        descripcion_label.setWordWrap(True)
        descripcion_label.setStyleSheet("background-color: #f5f5f5; padding: 10px; border-radius: 5px;")
        info_layout.addWidget(descripcion_label, 3, 1, 1, 3)
        
        info_group.setLayout(info_layout)
        
        # Agregar widgets al layout principal
        main_layout.addLayout(header_layout)
        main_layout.addWidget(info_group)
        main_layout.addStretch()
        main_layout.addLayout(action_layout)
        
        # Establecer el layout
        self.setLayout(main_layout)
    
    def confirm_delete(self):
        """Solicita confirmación para eliminar el registro"""
        reply = QMessageBox.question(
            self,
            "Confirmar eliminación",
            f"¿Está seguro que desea eliminar este registro de mantenimiento?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Emitir señal con el ID del registro
            self.delete_requested.emit(self.maintenance_data.get("id_mantenimiento"))
            self.close()