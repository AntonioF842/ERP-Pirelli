from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QPushButton, QComboBox, QSpinBox,
    QDoubleSpinBox, QTextEdit, QFormLayout, 
    QMessageBox, QDialog, QDateEdit
)
from PyQt6.QtCore import Qt, pyqtSignal, QDate
from PyQt6.QtGui import QFont
from utils.theme import Theme

class RDProjectForm(QDialog):
    """Formulario para crear o editar proyectos I+D"""
    
    # Señal emitida cuando se guarda un proyecto
    project_saved = pyqtSignal(dict)
    
    def __init__(self, api_client, project_data=None, parent=None):
        super().__init__(parent)
        from utils.theme import Theme
        Theme.apply_window_light_theme(self)
        
        self.api_client = api_client
        self.project_data = project_data
        self.edit_mode = project_data is not None
        
        self.init_ui()
        
        if self.edit_mode:
            self.fill_form()
    
    def init_ui(self):
        """Inicializa la interfaz de usuario"""
        self.setWindowTitle("Nuevo Proyecto I+D" if not self.edit_mode else "Editar Proyecto I+D")
        self.setMinimumWidth(600)
        self.setModal(True)
        
        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Título
        title_label = QLabel("Nuevo Proyecto I+D" if not self.edit_mode else "Editar Proyecto I+D")
        title_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        title_label.setProperty("heading", True)
        
        # Formulario
        form_layout = QFormLayout()
        form_layout.setVerticalSpacing(10)
        form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        
        # Nombre del proyecto
        self.nombre_input = QLineEdit()
        self.nombre_input.setPlaceholderText("Nombre del proyecto")
        form_layout.addRow("Nombre:", self.nombre_input)
        
        # Descripción
        self.descripcion_input = QTextEdit()
        self.descripcion_input.setPlaceholderText("Descripción detallada del proyecto")
        self.descripcion_input.setMaximumHeight(100)
        form_layout.addRow("Descripción:", self.descripcion_input)
        
        # Fecha de inicio
        self.fecha_inicio_input = QDateEdit()
        self.fecha_inicio_input.setDisplayFormat("yyyy-MM-dd")
        self.fecha_inicio_input.setDate(QDate.currentDate())
        self.fecha_inicio_input.setCalendarPopup(True)
        form_layout.addRow("Fecha Inicio:", self.fecha_inicio_input)
        
        # Fecha fin estimada
        self.fecha_fin_input = QDateEdit()
        self.fecha_fin_input.setDisplayFormat("yyyy-MM-dd")
        self.fecha_fin_input.setDate(QDate.currentDate().addMonths(3))
        self.fecha_fin_input.setCalendarPopup(True)
        form_layout.addRow("Fecha Fin Estimada:", self.fecha_fin_input)
        
        # Presupuesto
        self.presupuesto_input = QDoubleSpinBox()
        self.presupuesto_input.setRange(0, 9999999.99)
        self.presupuesto_input.setDecimals(2)
        self.presupuesto_input.setPrefix("$ ")
        form_layout.addRow("Presupuesto:", self.presupuesto_input)
        
        # Estado
        self.estado_combo = QComboBox()
        self.estado_combo.addItem("Planificación", "planificacion")
        self.estado_combo.addItem("En Desarrollo", "en_desarrollo")
        self.estado_combo.addItem("Completado", "completado")
        self.estado_combo.addItem("Cancelado", "cancelado")
        form_layout.addRow("Estado:", self.estado_combo)
        
        # Botones
        buttons_layout = QHBoxLayout()
        
        self.save_button = QPushButton("Guardar")
        self.save_button.setFixedHeight(40)
        self.save_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.save_button.setProperty("secondary", True)
        
        self.cancel_button = QPushButton("Cancelar")
        self.cancel_button.setFixedHeight(40)
        self.cancel_button.setCursor(Qt.CursorShape.PointingHandCursor)
        
        buttons_layout.addWidget(self.save_button)
        buttons_layout.addWidget(self.cancel_button)
        
        # Conectar eventos
        self.save_button.clicked.connect(self.save_project)
        self.cancel_button.clicked.connect(self.reject)
        
        # Agregar widgets al layout principal
        main_layout.addWidget(title_label)
        main_layout.addLayout(form_layout)
        main_layout.addStretch()
        main_layout.addLayout(buttons_layout)
        
        self.setLayout(main_layout)
    
    def fill_form(self):
        """Rellena el formulario con los datos del proyecto"""
        if not self.project_data:
            return
            
        self.nombre_input.setText(self.project_data.get("nombre", ""))
        self.descripcion_input.setText(self.project_data.get("descripcion", ""))
        
        # Fechas
        if self.project_data.get("fecha_inicio"):
            self.fecha_inicio_input.setDate(QDate.fromString(self.project_data["fecha_inicio"], "yyyy-MM-dd"))
        if self.project_data.get("fecha_fin_estimada"):
            self.fecha_fin_input.setDate(QDate.fromString(self.project_data["fecha_fin_estimada"], "yyyy-MM-dd"))
        
        self.presupuesto_input.setValue(float(self.project_data.get("presupuesto", 0)))
        
        # Estado
        estado = self.project_data.get("estado", "")
        index = self.estado_combo.findData(estado)
        if index >= 0:
            self.estado_combo.setCurrentIndex(index)
    
    def save_project(self):
        """Valida y guarda el proyecto"""
        nombre = self.nombre_input.text().strip()
        descripcion = self.descripcion_input.toPlainText().strip()
        fecha_inicio = self.fecha_inicio_input.date().toString("yyyy-MM-dd")
        fecha_fin = self.fecha_fin_input.date().toString("yyyy-MM-dd")
        presupuesto = self.presupuesto_input.value()
        estado = self.estado_combo.currentData()
        
        # Validar campos obligatorios
        if not nombre:
            QMessageBox.warning(self, "Error de validación", "El nombre es obligatorio")
            return
            
        if not fecha_inicio:
            QMessageBox.warning(self, "Error de validación", "La fecha de inicio es obligatoria")
            return
        
        # Crear diccionario de datos
        project_data = {
            "nombre": nombre,
            "descripcion": descripcion,
            "fecha_inicio": fecha_inicio,
            "fecha_fin_estimada": fecha_fin,
            "presupuesto": str(presupuesto),
            "estado": estado
        }
        
        # Si estamos editando, incluir el ID
        if self.edit_mode and "id_proyecto" in self.project_data:
            project_data["id_proyecto"] = self.project_data["id_proyecto"]
        
        # Emitir señal
        self.project_saved.emit(project_data)
        self.accept()