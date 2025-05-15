from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QComboBox, QDateEdit, QTextEdit, QDoubleSpinBox,
    QFormLayout, QMessageBox, QDialog
)
from PyQt6.QtCore import Qt, pyqtSignal, QDate
from PyQt6.QtGui import QFont
from utils.theme import Theme

class MaintenanceForm(QDialog):
    """Formulario para crear o editar registros de mantenimiento"""
    
    # Señal emitida cuando se guarda un registro
    maintenance_saved = pyqtSignal(dict)
    
    def __init__(self, api_client, maintenance_data=None, parent=None):
        super().__init__(parent)
        from utils.theme import Theme
        Theme.apply_window_light_theme(self)
        
        self.api_client = api_client
        self.maintenance_data = maintenance_data  # None para nuevo registro, dict para edición
        self.edit_mode = maintenance_data is not None
        
        self.init_ui()
        
        # Si estamos en modo edición, rellenar el formulario
        if self.edit_mode:
            self.fill_form()
        else:
            # Establecer fecha actual por defecto
            self.date_input.setDate(QDate.currentDate())
    
    def init_ui(self):
        """Inicializa la interfaz de usuario"""
        # Configuración de la ventana
        self.setWindowTitle("Nuevo Mantenimiento" if not self.edit_mode else "Editar Mantenimiento")
        self.setMinimumWidth(500)
        self.setModal(True)
        
        # Layout principal
        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Título
        title = "Nuevo Registro de Mantenimiento" if not self.edit_mode else "Editar Registro de Mantenimiento"
        title_label = QLabel(title)
        title_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        title_label.setProperty("heading", True)
        
        # Formulario
        form_layout = QFormLayout()
        form_layout.setVerticalSpacing(10)
        form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        
        # Activo (se cargará dinámicamente)
        self.asset_combo = QComboBox()
        self.load_assets()
        form_layout.addRow("Activo:", self.asset_combo)
        
        # Tipo de mantenimiento
        self.type_combo = QComboBox()
        self.type_combo.addItem("Preventivo", "preventivo")
        self.type_combo.addItem("Correctivo", "correctivo")
        form_layout.addRow("Tipo:", self.type_combo)
        
        # Fecha
        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(True)
        self.date_input.setDisplayFormat("dd/MM/yyyy")
        form_layout.addRow("Fecha:", self.date_input)
        
        # Descripción
        self.description_input = QTextEdit()
        self.description_input.setPlaceholderText("Descripción del trabajo realizado...")
        self.description_input.setMaximumHeight(100)
        form_layout.addRow("Descripción:", self.description_input)
        
        # Costo
        self.cost_input = QDoubleSpinBox()
        self.cost_input.setRange(0, 999999.99)
        self.cost_input.setDecimals(2)
        self.cost_input.setPrefix("$ ")
        form_layout.addRow("Costo:", self.cost_input)
        
        # Técnico (se cargará dinámicamente)
        self.employee_combo = QComboBox()
        self.load_employees()
        self.employee_combo.insertItem(0, "No asignado", None)
        form_layout.addRow("Técnico:", self.employee_combo)
        
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
        self.save_button.clicked.connect(self.save_maintenance)
        self.cancel_button.clicked.connect(self.reject)
        
        # Agregar widgets al layout principal
        main_layout.addWidget(title_label)
        main_layout.addLayout(form_layout)
        main_layout.addStretch()
        main_layout.addLayout(buttons_layout)
        
        # Establecer el layout
        self.setLayout(main_layout)
    
    def load_assets(self):
        """Carga los activos disponibles desde la API"""
        self.api_client.get_production_assets()
        # La respuesta se manejará en on_data_loaded
    
    def load_employees(self):
        """Carga los empleados disponibles desde la API"""
        self.api_client.get_employees()
        # La respuesta se manejará en on_data_loaded
    
    def on_data_loaded(self, data):
        """Maneja los datos cargados desde la API"""
        if data.get("type") == "production_assets":
            self.asset_combo.clear()
            for asset in data.get("data", []):
                self.asset_combo.addItem(asset.get("nombre"), asset.get("id_activo"))
        elif data.get("type") == "employees":
            self.employee_combo.clear()
            self.employee_combo.addItem("No asignado", None)
            for employee in data.get("data", []):
                name = f"{employee.get('nombre')} {employee.get('apellidos', '')}"
                self.employee_combo.addItem(name, employee.get("id_empleado"))
    
    def fill_form(self):
        """Rellena el formulario con los datos del registro"""
        if not self.maintenance_data:
            return
            
        # Activo
        index = self.asset_combo.findData(self.maintenance_data.get("id_activo"))
        if index >= 0:
            self.asset_combo.setCurrentIndex(index)
        
        # Tipo
        index = self.type_combo.findData(self.maintenance_data.get("tipo"))
        if index >= 0:
            self.type_combo.setCurrentIndex(index)
        
        # Fecha
        if "fecha" in self.maintenance_data:
            date = QDate.fromString(self.maintenance_data["fecha"], "yyyy-MM-dd")
            self.date_input.setDate(date)
        
        # Descripción
        self.description_input.setText(self.maintenance_data.get("descripcion", ""))
        
        # Costo
        self.cost_input.setValue(float(self.maintenance_data.get("costo", 0)))
        
        # Técnico
        index = self.employee_combo.findData(self.maintenance_data.get("id_empleado"))
        if index >= 0:
            self.employee_combo.setCurrentIndex(index)
    
    def save_maintenance(self):
        """Valida y guarda el registro de mantenimiento"""
        # Obtener datos
        id_activo = self.asset_combo.currentData()
        tipo = self.type_combo.currentData()
        fecha = self.date_input.date().toString("yyyy-MM-dd")
        descripcion = self.description_input.toPlainText().strip()
        costo = self.cost_input.value()
        id_empleado = self.employee_combo.currentData()
        
        # Validar campos obligatorios
        if not id_activo:
            QMessageBox.warning(self, "Error de validación", "Debe seleccionar un activo")
            return
            
        if not tipo:
            QMessageBox.warning(self, "Error de validación", "Debe seleccionar un tipo de mantenimiento")
            return
        
        # Crear diccionario de datos
        maintenance_data = {
            "id_activo": id_activo,
            "tipo": tipo,
            "fecha": fecha,
            "descripcion": descripcion,
            "costo": str(costo),
            "id_empleado": id_empleado
        }
        
        # Si estamos editando, incluir el ID
        if self.edit_mode and "id_mantenimiento" in self.maintenance_data:
            maintenance_data["id_mantenimiento"] = self.maintenance_data["id_mantenimiento"]
        
        # Emitir señal
        self.maintenance_saved.emit(maintenance_data)
        self.accept()