from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QLineEdit, QPushButton, QComboBox, QSpinBox,
                            QDoubleSpinBox, QTextEdit, QFormLayout, 
                            QMessageBox, QDialog, QDateEdit)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from utils.theme import Theme
from datetime import datetime

class LegalRegulationForm(QDialog):
    """Formulario para crear o editar normativas legales"""
    
    # Señal emitida cuando se guarda una normativa
    regulation_saved = pyqtSignal(dict)
    
    def __init__(self, api_client, regulation_data=None, parent=None):
        super().__init__(parent)
        from utils.theme import Theme
        Theme.apply_window_light_theme(self)
        
        self.api_client = api_client
        self.regulation_data = regulation_data  # None para nueva normativa, dict para edición
        self.edit_mode = regulation_data is not None
        
        self.init_ui()
        
        # Si estamos en modo edición, rellenar el formulario
        if self.edit_mode:
            self.fill_form()
    
    def init_ui(self):
        """Inicializa la interfaz de usuario"""
        # Configuración de la ventana
        self.setWindowTitle("Nueva Normativa" if not self.edit_mode else "Editar Normativa")
        self.setMinimumWidth(500)
        self.setModal(True)
        
        # Layout principal
        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Título
        title = "Nueva Normativa Legal" if not self.edit_mode else "Editar Normativa Legal"
        title_label = QLabel(title)
        title_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        title_label.setProperty("heading", True)  # Usar propiedad de estilo del tema
        
        # Formulario
        form_layout = QFormLayout()
        form_layout.setVerticalSpacing(10)
        form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        
        # Nombre de la normativa
        self.nombre_input = QLineEdit()
        self.nombre_input.setPlaceholderText("Nombre de la normativa")
        form_layout.addRow("Nombre:", self.nombre_input)
        
        # Tipo de normativa
        self.tipo_combo = QComboBox()
        self.tipo_combo.addItems(["ambiental", "seguridad", "laboral", "calidad"])
        form_layout.addRow("Tipo:", self.tipo_combo)
        
        # Descripción
        self.descripcion_input = QTextEdit()
        self.descripcion_input.setPlaceholderText("Descripción detallada de la normativa")
        self.descripcion_input.setMaximumHeight(100)
        form_layout.addRow("Descripción:", self.descripcion_input)
        
        # Fecha de actualización
        self.fecha_edit = QDateEdit()
        self.fecha_edit.setCalendarPopup(True)
        self.fecha_edit.setDate(datetime.now().date())
        form_layout.addRow("Fecha Actualización:", self.fecha_edit)
        
        # Aplicable a
        self.aplicable_input = QLineEdit()
        self.aplicable_input.setPlaceholderText("Área a la que aplica la normativa")
        form_layout.addRow("Aplicable a:", self.aplicable_input)
        
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
        self.save_button.clicked.connect(self.save_regulation)
        self.cancel_button.clicked.connect(self.reject)
        
        # Agregar widgets al layout principal
        main_layout.addWidget(title_label)
        main_layout.addLayout(form_layout)
        main_layout.addStretch()
        main_layout.addLayout(buttons_layout)
        
        # Establecer el layout
        self.setLayout(main_layout)
    
    def fill_form(self):
        """Rellena el formulario con los datos de la normativa"""
        if not self.regulation_data:
            return
            
        self.nombre_input.setText(self.regulation_data.get("nombre", ""))
        self.descripcion_input.setText(self.regulation_data.get("descripcion", ""))
        self.aplicable_input.setText(self.regulation_data.get("aplicable_a", ""))
        
        # Establecer el tipo
        tipo = self.regulation_data.get("tipo", "")
        index = self.tipo_combo.findText(tipo)
        if index >= 0:
            self.tipo_combo.setCurrentIndex(index)
        
        # Establecer la fecha
        fecha_str = self.regulation_data.get("fecha_actualizacion")
        if fecha_str:
            try:
                fecha = datetime.strptime(fecha_str, "%Y-%m-%d").date()
                self.fecha_edit.setDate(fecha)
            except (ValueError, TypeError):
                pass
    
    def save_regulation(self):
        """Valida y guarda la normativa"""
        # Obtener datos
        nombre = self.nombre_input.text().strip()
        descripcion = self.descripcion_input.toPlainText().strip()
        tipo = self.tipo_combo.currentText()
        fecha_actualizacion = self.fecha_edit.date().toString("yyyy-MM-dd")
        aplicable_a = self.aplicable_input.text().strip()
        
        # Validar campos obligatorios
        if not nombre:
            QMessageBox.warning(self, "Error de validación", "El nombre es obligatorio")
            return
            
        if not tipo:
            QMessageBox.warning(self, "Error de validación", "El tipo es obligatorio")
            return
        
        # Crear diccionario de datos
        regulation_data = {
            "nombre": nombre,
            "tipo": tipo,
            "descripcion": descripcion,
            "fecha_actualizacion": fecha_actualizacion,
            "aplicable_a": aplicable_a
        }
        
        # Si estamos editando, incluir el ID
        if self.edit_mode and "id_normativa" in self.regulation_data:
            regulation_data["id_normativa"] = self.regulation_data["id_normativa"]
        
        # Emitir señal
        self.regulation_saved.emit(regulation_data)
        self.accept()