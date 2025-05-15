from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QScrollArea, QPushButton, QGroupBox, QGridLayout,
                            QMessageBox, QDialog, QFrame)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QPixmap, QIcon

class QualityControlDetailView(QDialog):
    """Vista detallada de un control de calidad"""
    
    # Señales
    edit_requested = pyqtSignal(dict)
    delete_requested = pyqtSignal(int)
    
    def __init__(self, api_client, control_data, parent=None):
        super().__init__(parent)
        from utils.theme import Theme
        Theme.apply_window_light_theme(self)
        
        self.api_client = api_client
        self.control_data = control_data
        
        self.init_ui()
    
    def init_ui(self):
        """Inicializa la interfaz de usuario"""
        # Configuración de la ventana
        self.setWindowTitle(f"Control de Calidad: #{self.control_data.get('id_control', 'Detalle')}")
        self.setMinimumSize(600, 400)
        
        # Layout principal
        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Encabezado
        header_layout = QHBoxLayout()
        
        # Icono y Título
        icon_label = QLabel()
        icon_pixmap = QPixmap("resources/icons/quality.png")
        if not icon_pixmap.isNull():
            icon_label.setPixmap(icon_pixmap.scaled(64, 64, Qt.AspectRatioMode.KeepAspectRatio))
        
        title_label = QLabel(f"Control de Calidad #{self.control_data.get('id_control', '')}")
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
        edit_button.clicked.connect(lambda: self.edit_requested.emit(self.control_data))
        delete_button.clicked.connect(self.confirm_delete)
        close_button.clicked.connect(self.close)
        
        # Información del control
        info_group = QGroupBox("Información del Control")
        info_layout = QGridLayout()
        
        # Orden de Producción
        info_layout.addWidget(QLabel("Orden Producción:"), 0, 0)
        op_label = QLabel(str(self.control_data.get("id_orden_produccion", "N/A")))
        op_label.setStyleSheet("font-weight: bold;")
        info_layout.addWidget(op_label, 0, 1)
        
        # Fecha
        info_layout.addWidget(QLabel("Fecha:"), 1, 0)
        fecha_label = QLabel(self.control_data.get("fecha", "N/A"))
        fecha_label.setStyleSheet("font-weight: bold;")
        info_layout.addWidget(fecha_label, 1, 1)
        
        # Resultado
        info_layout.addWidget(QLabel("Resultado:"), 0, 2)
        resultado = self.control_data.get("resultado", "aprobado")
        resultado_display = "Aprobado" if resultado == "aprobado" else "Rechazado" if resultado == "rechazado" else "Requiere Reparación"
        resultado_label = QLabel(resultado_display)
        resultado_label.setStyleSheet("font-weight: bold; color: #d60000;" if resultado == "rechazado" else "font-weight: bold; color: #00aa00;" if resultado == "aprobado" else "font-weight: bold; color: #ff8c00;")
        info_layout.addWidget(resultado_label, 0, 3)
        
        # Usuario
        info_layout.addWidget(QLabel("Usuario:"), 1, 2)
        usuario_label = QLabel(str(self.control_data.get("id_usuario", "N/A")))
        usuario_label.setStyleSheet("font-weight: bold;")
        info_layout.addWidget(usuario_label, 1, 3)
        
        # Observaciones
        info_layout.addWidget(QLabel("Observaciones:"), 2, 0, Qt.AlignmentFlag.AlignTop)
        obs = self.control_data.get("observaciones", "Sin observaciones")
        obs_label = QLabel(obs if obs else "Sin observaciones")
        obs_label.setWordWrap(True)
        obs_label.setStyleSheet("background-color: #f5f5f5; padding: 10px; border-radius: 5px;")
        info_layout.addWidget(obs_label, 2, 1, 1, 3)
        
        info_group.setLayout(info_layout)
        
        # Agregar widgets al layout principal
        main_layout.addLayout(header_layout)
        main_layout.addWidget(info_group)
        main_layout.addStretch()
        main_layout.addLayout(action_layout)
        
        # Establecer el layout
        self.setLayout(main_layout)
    
    def confirm_delete(self):
        """Solicita confirmación para eliminar el control"""
        reply = QMessageBox.question(
            self,
            "Confirmar eliminación",
            f"¿Está seguro que desea eliminar el control #{self.control_data.get('id_control')}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Emitir señal con el ID del control
            self.delete_requested.emit(self.control_data.get("id_control"))
            self.close()