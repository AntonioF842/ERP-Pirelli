from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QLineEdit, QPushButton, QComboBox, QSpinBox,
                            QDoubleSpinBox, QTextEdit, QFormLayout, 
                            QMessageBox, QDialog, QDateEdit)
from PyQt6.QtCore import Qt, pyqtSignal, QDate
from PyQt6.QtGui import QFont
from utils.theme import Theme

class QualityControlForm(QDialog):
    """Formulario para crear o editar controles de calidad"""
    
    # Señal emitida cuando se guarda un control
    control_saved = pyqtSignal(dict)
    
    def __init__(self, api_client, control_data=None, parent=None):
        super().__init__(parent)
        from utils.theme import Theme
        Theme.apply_window_light_theme(self)
        
        self.api_client = api_client
        self.control_data = control_data  # None para nuevo control, dict para edición
        self.edit_mode = control_data is not None
        
        self.init_ui()
        
        # Si estamos en modo edición, rellenar el formulario
        if self.edit_mode:
            self.fill_form()
    
    def init_ui(self):
        """Inicializa la interfaz de usuario"""
        # Configuración de la ventana
        self.setWindowTitle("Nuevo Control de Calidad" if not self.edit_mode else "Editar Control de Calidad")
        self.setMinimumWidth(500)
        self.setModal(True)
        
        # Layout principal
        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Título
        title = "Nuevo Control de Calidad" if not self.edit_mode else "Editar Control de Calidad"
        title_label = QLabel(title)
        title_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        title_label.setProperty("heading", True)  # Usar propiedad de estilo del tema
        
        # Formulario
        form_layout = QFormLayout()
        form_layout.setVerticalSpacing(10)
        form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        
        # ID Orden de Producción
        self.orden_produccion_input = QSpinBox()
        self.orden_produccion_input.setRange(1, 999999)
        self.orden_produccion_input.setValue(1)
        form_layout.addRow("Orden Producción:", self.orden_produccion_input)
        
        # Fecha
        self.fecha_input = QDateEdit()
        self.fecha_input.setCalendarPopup(True)
        self.fecha_input.setDate(QDate.currentDate())
        self.fecha_input.setDisplayFormat("yyyy-MM-dd")
        form_layout.addRow("Fecha:", self.fecha_input)
        
        # Resultado
        self.resultado_combo = QComboBox()
        self.resultado_combo.addItem("Aprobado", "aprobado")
        self.resultado_combo.addItem("Rechazado", "rechazado")
        self.resultado_combo.addItem("Requiere Reparación", "reparacion")
        form_layout.addRow("Resultado:", self.resultado_combo)
        
        # Observaciones
        self.observaciones_input = QTextEdit()
        self.observaciones_input.setPlaceholderText("Observaciones del control...")
        self.observaciones_input.setMaximumHeight(100)
        form_layout.addRow("Observaciones:", self.observaciones_input)
        
        # ID Usuario
        self.usuario_input = QSpinBox()
        self.usuario_input.setRange(1, 999999)
        self.usuario_input.setValue(1)
        form_layout.addRow("ID Usuario:", self.usuario_input)
        
        # Botones
        buttons_layout = QHBoxLayout()
        
        # Usar propiedades de tema para los botones
        self.save_button = QPushButton("Guardar")
        self.save_button.setFixedHeight(40)
        self.save_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.save_button.setProperty("secondary", True)  # Usar propiedad de estilo del tema
        
        self.cancel_button = QPushButton("Cancelar")
        self.cancel_button.setFixedHeight(40)
        self.cancel_button.setCursor(Qt.CursorShape.PointingHandCursor)
        
        buttons_layout.addWidget(self.save_button)
        buttons_layout.addWidget(self.cancel_button)
        
        # Conectar eventos
        self.save_button.clicked.connect(self.save_control)
        self.cancel_button.clicked.connect(self.reject)
        
        # Agregar widgets al layout principal
        main_layout.addWidget(title_label)
        main_layout.addLayout(form_layout)
        main_layout.addStretch()
        main_layout.addLayout(buttons_layout)
        
        # Establecer el layout
        self.setLayout(main_layout)
    
    def fill_form(self):
        """Rellena el formulario con los datos del control"""
        if not self.control_data:
            return
            
        self.orden_produccion_input.setValue(int(self.control_data.get("id_orden_produccion", 1)))
        
        if "fecha" in self.control_data:
            fecha = QDate.fromString(self.control_data["fecha"], "yyyy-MM-dd")
            if fecha.isValid():
                self.fecha_input.setDate(fecha)
        
        # Establecer el resultado
        resultado = self.control_data.get("resultado", "aprobado")
        index = self.resultado_combo.findData(resultado)
        if index >= 0:
            self.resultado_combo.setCurrentIndex(index)
        
        self.observaciones_input.setText(self.control_data.get("observaciones", ""))
        self.usuario_input.setValue(int(self.control_data.get("id_usuario", 1)))
    
    def save_control(self):
        """Valida y guarda el control"""
        # Obtener datos
        id_orden_produccion = self.orden_produccion_input.value()
        fecha = self.fecha_input.date().toString("yyyy-MM-dd")
        resultado = self.resultado_combo.currentData()
        observaciones = self.observaciones_input.toPlainText().strip()
        id_usuario = self.usuario_input.value()
        
        # Validar campos obligatorios
        if id_orden_produccion <= 0:
            QMessageBox.warning(self, "Error de validación", "La orden de producción es obligatoria")
            return
            
        if not fecha:
            QMessageBox.warning(self, "Error de validación", "La fecha es obligatoria")
            return
        
        # Crear diccionario de datos
        control_data = {
            "id_orden_produccion": id_orden_produccion,
            "fecha": fecha,
            "resultado": resultado,
            "observaciones": observaciones,
            "id_usuario": id_usuario
        }
        
        # Si estamos editando, incluir el ID
        if self.edit_mode and "id_control" in self.control_data:
            control_data["id_control"] = self.control_data["id_control"]
        
        # Emitir señal
        self.control_saved.emit(control_data)
        self.accept()