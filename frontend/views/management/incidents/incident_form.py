from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QComboBox, QTextEdit, QFormLayout, 
    QMessageBox, QDialog, QDateEdit
)
from PyQt6.QtCore import Qt, pyqtSignal, QDate
from PyQt6.QtGui import QFont
from utils.theme import Theme

class IncidentForm(QDialog):
    """Formulario para crear/editar incidentes"""
    
    incident_saved = pyqtSignal(dict)
    
    def __init__(self, api_client, incident_data=None, parent=None):
        super().__init__(parent)
        Theme.apply_window_light_theme(self)
        
        self.api_client = api_client
        self.incident_data = incident_data
        self.edit_mode = incident_data is not None
        
        self.init_ui()
        
        if self.edit_mode:
            self.fill_form()
    
    def init_ui(self):
        """Inicializa la interfaz de usuario"""
        self.setWindowTitle("Nuevo Incidente" if not self.edit_mode else "Editar Incidente")
        self.setMinimumWidth(500)
        
        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        title_label = QLabel("Nuevo Incidente" if not self.edit_mode else "Editar Incidente")
        title_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        main_layout.addWidget(title_label)
        
        form_layout = QFormLayout()
        form_layout.setVerticalSpacing(10)
        
        # Tipo
        self.type_combo = QComboBox()
        self.type_combo.addItem("Seguridad", "seguridad")
        self.type_combo.addItem("Calidad", "calidad")
        self.type_combo.addItem("Logística", "logistica")
        form_layout.addRow("Tipo:", self.type_combo)
        
        # Descripción
        self.desc_input = QTextEdit()
        self.desc_input.setPlaceholderText("Descripción detallada del incidente...")
        self.desc_input.setMaximumHeight(100)
        form_layout.addRow("Descripción:", self.desc_input)
        
        # Fecha
        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(True)
        self.date_input.setDate(QDate.currentDate())
        form_layout.addRow("Fecha:", self.date_input)
        
        # Área (simplificado - en una implementación real podrías cargar áreas desde la API)
        self.area_input = QLineEdit()
        self.area_input.setPlaceholderText("ID de área")
        form_layout.addRow("Área (ID):", self.area_input)
        
        # Reportado por (simplificado)
        self.reported_by_input = QLineEdit()
        self.reported_by_input.setPlaceholderText("ID de empleado")
        form_layout.addRow("Reportado por (ID):", self.reported_by_input)
        
        # Estado
        self.status_combo = QComboBox()
        self.status_combo.addItem("Reportado", "reportado")
        self.status_combo.addItem("En investigación", "investigacion")
        self.status_combo.addItem("Resuelto", "resuelto")
        form_layout.addRow("Estado:", self.status_combo)
        
        # Botones
        buttons_layout = QHBoxLayout()
        self.save_btn = QPushButton("Guardar")
        self.save_btn.clicked.connect(self.save_incident)
        
        self.cancel_btn = QPushButton("Cancelar")
        self.cancel_btn.clicked.connect(self.reject)
        
        buttons_layout.addWidget(self.save_btn)
        buttons_layout.addWidget(self.cancel_btn)
        
        main_layout.addLayout(form_layout)
        main_layout.addStretch()
        main_layout.addLayout(buttons_layout)
        
        self.setLayout(main_layout)
    
    def fill_form(self):
        """Rellena el formulario con datos existentes"""
        if not self.incident_data:
            return
            
        # Tipo
        index = self.type_combo.findData(self.incident_data.get("tipo"))
        if index >= 0:
            self.type_combo.setCurrentIndex(index)
        
        # Descripción
        self.desc_input.setPlainText(self.incident_data.get("descripcion", ""))
        
        # Fecha
        if "fecha" in self.incident_data:
            date = QDate.fromString(self.incident_data["fecha"], "yyyy-MM-dd")
            if date.isValid():
                self.date_input.setDate(date)
        
        # Área
        if "id_area" in self.incident_data:
            self.area_input.setText(str(self.incident_data["id_area"]))
        
        # Reportado por
        if "id_empleado_reporta" in self.incident_data:
            self.reported_by_input.setText(str(self.incident_data["id_empleado_reporta"]))
        
        # Estado
        index = self.status_combo.findData(self.incident_data.get("estado", "reportado"))
        if index >= 0:
            self.status_combo.setCurrentIndex(index)
    
    def save_incident(self):
        """Valida y guarda el incidente"""
        incident_data = {
            "tipo": self.type_combo.currentData(),
            "descripcion": self.desc_input.toPlainText().strip(),
            "fecha": self.date_input.date().toString("yyyy-MM-dd"),
            "estado": self.status_combo.currentData()
        }
        
        # Campos opcionales
        if self.area_input.text().strip():
            incident_data["id_area"] = int(self.area_input.text())
        
        if self.reported_by_input.text().strip():
            incident_data["id_empleado_reporta"] = int(self.reported_by_input.text())
        
        # Validación
        if not incident_data["descripcion"]:
            QMessageBox.warning(self, "Error", "La descripción es obligatoria")
            return
        
        # Si estamos editando, agregar el ID
        if self.edit_mode and "id_incidente" in self.incident_data:
            incident_data["id_incidente"] = self.incident_data["id_incidente"]
        
        self.incident_saved.emit(incident_data)
        self.accept()