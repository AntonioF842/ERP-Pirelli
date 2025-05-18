from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QGroupBox, QGridLayout, QTextBrowser,
    QFrame, QSizePolicy, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QPixmap, QIcon
from utils.theme import Theme
import logging

logger = logging.getLogger(__name__)

class QualityControlDetailView(QDialog):
    """Vista detallada de un control de calidad"""
    
    # Señales
    edit_requested = pyqtSignal(dict)  # Emitida al solicitar edición
    delete_requested = pyqtSignal(int) # Emitida al solicitar eliminación
    
    def __init__(self, api_client, control_data, parent=None):
        super().__init__(parent)
        Theme.apply_window_light_theme(self)
        
        self.api_client = api_client
        self.control_data = control_data
        
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        """Configura la interfaz de usuario"""
        self.setWindowTitle(f"Control de Calidad: #{self.control_data.get('id_control', 'Detalle')}")
        self.setMinimumSize(600, 500)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Encabezado
        self.setup_header(main_layout)
        
        # Información principal
        self.setup_info_section(main_layout)
        
        # Observaciones
        self.setup_observations_section(main_layout)
        
        # Botones de acción
        self.setup_action_buttons(main_layout)

    def setup_header(self, parent_layout):
        """Configura el encabezado con icono y título"""
        header_layout = QHBoxLayout()
        header_layout.setSpacing(15)
        
        # Icono
        icon_label = QLabel()
        icon_pixmap = QPixmap("resources/icons/quality_large.png")
        if not icon_pixmap.isNull():
            icon_label.setPixmap(icon_pixmap.scaled(80, 80, Qt.AspectRatioMode.KeepAspectRatio))
        
        # Título y código
        title_layout = QVBoxLayout()
        title_layout.setSpacing(5)
        
        title_label = QLabel(f"Control #{self.control_data.get('id_control', 'N/A')}")
        title_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        
        op_label = QLabel(f"Orden Producción: {self.control_data.get('id_orden_produccion', 'N/A')}")
        op_label.setFont(QFont("Arial", 10))
        op_label.setStyleSheet(f"color: {Theme.SECONDARY_COLOR};")
        
        title_layout.addWidget(title_label)
        title_layout.addWidget(op_label)
        title_layout.addStretch()
        
        header_layout.addWidget(icon_label)
        header_layout.addLayout(title_layout)
        header_layout.addStretch()
        
        parent_layout.addLayout(header_layout)

    def setup_info_section(self, parent_layout):
        """Configura la sección de información básica"""
        info_group = QGroupBox("Información del Control")
        info_layout = QGridLayout(info_group)
        info_layout.setVerticalSpacing(10)
        info_layout.setHorizontalSpacing(20)
        
        # Fecha
        info_layout.addWidget(QLabel("Fecha:"), 0, 0)
        fecha_label = QLabel(self.control_data.get('fecha', 'N/A'))
        fecha_label.setStyleSheet("font-weight: bold;")
        info_layout.addWidget(fecha_label, 0, 1)
        
        # Resultado
        info_layout.addWidget(QLabel("Resultado:"), 0, 2)
        resultado = self.control_data.get('resultado', 'aprobado')
        resultado_label = QLabel(self.get_result_display(resultado))
        resultado_label.setStyleSheet(f"font-weight: bold; color: {self.get_result_color(resultado)};")
        info_layout.addWidget(resultado_label, 0, 3)
        
        # Usuario
        info_layout.addWidget(QLabel("Usuario:"), 1, 0)
        usuario_label = QLabel(str(self.control_data.get('id_usuario', 'N/A')))
        usuario_label.setStyleSheet("font-weight: bold;")
        info_layout.addWidget(usuario_label, 1, 1)
        
        parent_layout.addWidget(info_group)

    def setup_observations_section(self, parent_layout):
        """Configura la sección de observaciones"""
        obs_group = QGroupBox("Observaciones")
        obs_layout = QVBoxLayout(obs_group)
        
        self.obs_browser = QTextBrowser()
        self.obs_browser.setOpenExternalLinks(True)
        self.obs_browser.setStyleSheet("""
            QTextBrowser {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 3px;
                padding: 10px;
            }
        """)
        
        obs_layout.addWidget(self.obs_browser)
        parent_layout.addWidget(obs_group)

    def setup_action_buttons(self, parent_layout):
        """Configura los botones de acción"""
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        self.edit_btn = QPushButton("Editar")
        self.edit_btn.setIcon(QIcon("resources/icons/edit.png"))
        self.edit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        
        self.delete_btn = QPushButton("Eliminar")
        self.delete_btn.setIcon(QIcon("resources/icons/delete.png"))
        self.delete_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.delete_btn.setStyleSheet(f"color: {Theme.DANGER_COLOR};")
        
        self.close_btn = QPushButton("Cerrar")
        self.close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        
        button_layout.addWidget(self.edit_btn)
        button_layout.addWidget(self.delete_btn)
        button_layout.addStretch()
        button_layout.addWidget(self.close_btn)
        
        parent_layout.addLayout(button_layout)
        
        # Conectar señales
        self.edit_btn.clicked.connect(lambda: self.edit_requested.emit(self.control_data))
        self.delete_btn.clicked.connect(self.confirm_delete)
        self.close_btn.clicked.connect(self.close)

    def load_data(self):
        """Carga los datos del control en la vista"""
        observaciones = self.control_data.get('observaciones', 'Sin observaciones disponibles')
        if not observaciones.strip():
            observaciones = "Sin observaciones disponibles"
        
        # Formatear observaciones como HTML
        html_obs = f"<p style='margin: 5px; line-height: 1.5;'>{observaciones}</p>"
        self.obs_browser.setHtml(html_obs)

    def get_result_display(self, result):
        """Devuelve el texto a mostrar según el resultado"""
        result = result.lower()
        if result == "aprobado":
            return "Aprobado"
        elif result == "rechazado":
            return "Rechazado"
        elif result == "reparacion":
            return "Requiere Reparación"
        return result.capitalize()

    def get_result_color(self, result):
        """Devuelve el color según el resultado"""
        result = result.lower()
        if result == "aprobado":
            return Theme.SUCCESS_COLOR
        elif result == "rechazado":
            return Theme.DANGER_COLOR
        elif result == "reparacion":
            return Theme.WARNING_COLOR
        return Theme.PRIMARY_COLOR

    def confirm_delete(self):
        """Confirma la eliminación del control"""
        reply = QMessageBox.question(
            self,
            "Confirmar Eliminación",
            f"¿Está seguro que desea eliminar el control #{self.control_data.get('id_control')}?\n\n"
            "Esta acción no se puede deshacer.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.delete_requested.emit(self.control_data.get('id_control'))
            self.close()