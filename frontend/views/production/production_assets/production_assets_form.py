from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QPushButton, QComboBox, QDateEdit,
    QTextEdit, QFormLayout, QMessageBox, QDialog
)
from PyQt6.QtCore import Qt, pyqtSignal, QDate
from PyQt6.QtGui import QFont
from utils.theme import Theme

class ProductionAssetForm(QDialog):
    """Formulario para crear o editar activos de producción"""
    
    # Señal emitida cuando se guarda un activo
    asset_saved = pyqtSignal(dict)
    
    def __init__(self, api_client, asset_data=None, parent=None):
        super().__init__(parent)
        Theme.apply_window_light_theme(self)
        
        self.api_client = api_client
        self.asset_data = asset_data  # None para nuevo activo, dict para edición
        self.edit_mode = asset_data is not None
        
        self.init_ui()
        
        # Si estamos en modo edición, rellenar el formulario
        if self.edit_mode:
            self.fill_form()
    
    def init_ui(self):
        """Inicializa la interfaz de usuario"""
        # Configuración de la ventana
        self.setWindowTitle("Nuevo Activo" if not self.edit_mode else "Editar Activo")
        self.setMinimumWidth(500)
        self.setModal(True)
        
        # Layout principal
        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Título
        title = "Nuevo Activo de Producción" if not self.edit_mode else "Editar Activo de Producción"
        title_label = QLabel(title)
        title_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        title_label.setProperty("heading", True)
        
        # Formulario
        form_layout = QFormLayout()
        form_layout.setVerticalSpacing(10)
        form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        
        # Nombre del activo
        self.nombre_input = QLineEdit()
        self.nombre_input.setPlaceholderText("Nombre del activo")
        form_layout.addRow("Nombre:", self.nombre_input)
        
        # Tipo de activo
        self.tipo_combo = QComboBox()
        self.tipo_combo.addItems(["maquinaria", "herramienta", "equipo"])
        form_layout.addRow("Tipo:", self.tipo_combo)
        
        # Área de trabajo
        self.area_combo = QComboBox()
        self.load_work_areas()
        form_layout.addRow("Área:", self.area_combo)
        
        # Fecha de adquisición
        self.fecha_input = QDateEdit()
        self.fecha_input.setCalendarPopup(True)
        self.fecha_input.setDate(QDate.currentDate())
        form_layout.addRow("Fecha Adquisición:", self.fecha_input)
        
        # Estado
        self.estado_combo = QComboBox()
        self.estado_combo.addItems(["operativo", "mantenimiento", "baja"])
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
        self.save_button.clicked.connect(self.save_asset)
        self.cancel_button.clicked.connect(self.reject)
        
        # Agregar widgets al layout principal
        main_layout.addWidget(title_label)
        main_layout.addLayout(form_layout)
        main_layout.addStretch()
        main_layout.addLayout(buttons_layout)
        
        # Establecer el layout
        self.setLayout(main_layout)
    
    def load_work_areas(self):
        """Carga las áreas de trabajo desde la API"""
        self.api_client.get_work_areas()
        # La respuesta se manejará en on_data_loaded
    
    def fill_form(self):
        """Rellena el formulario con los datos del activo"""
        if not self.asset_data:
            return
            
        self.nombre_input.setText(self.asset_data.get("nombre", ""))
        
        # Establecer tipo
        tipo = self.asset_data.get("tipo", "")
        index = self.tipo_combo.findText(tipo)
        if index >= 0:
            self.tipo_combo.setCurrentIndex(index)
        
        # Establecer estado
        estado = self.asset_data.get("estado", "")
        index = self.estado_combo.findText(estado)
        if index >= 0:
            self.estado_combo.setCurrentIndex(index)
        
        # Establecer fecha
        fecha = self.asset_data.get("fecha_adquisicion")
        if fecha:
            self.fecha_input.setDate(QDate.fromString(fecha, "yyyy-MM-dd"))
    
    def save_asset(self):
        """Valida y guarda el activo"""
        # Obtener datos
        nombre = self.nombre_input.text().strip()
        tipo = self.tipo_combo.currentText()
        id_area = self.area_combo.currentData()
        fecha = self.fecha_input.date().toString("yyyy-MM-dd")
        estado = self.estado_combo.currentText()
        
        # Validar campos obligatorios
        if not nombre:
            QMessageBox.warning(self, "Error de validación", "El nombre es obligatorio")
            return
            
        if not tipo:
            QMessageBox.warning(self, "Error de validación", "El tipo es obligatorio")
            return
        
        # Crear diccionario de datos
        asset_data = {
            "nombre": nombre,
            "tipo": tipo,
            "id_area": id_area,
            "fecha_adquisicion": fecha,
            "estado": estado
        }
        
        # Si estamos editando, incluir el ID
        if self.edit_mode and "id_activo" in self.asset_data:
            asset_data["id_activo"] = self.asset_data["id_activo"]
        
        # Emitir señal
        self.asset_saved.emit(asset_data)
        self.accept()
    
    def on_data_loaded(self, data):
        """Maneja los datos cargados desde la API"""
        if data.get("type") == "work_areas":
            self.area_combo.clear()
            for area in data.get("data", []):
                self.area_combo.addItem(area.get("nombre_area"), area.get("id_area"))
            
            # Si estamos editando, establecer el área seleccionada
            if self.edit_mode and "id_area" in self.asset_data:
                index = self.area_combo.findData(self.asset_data["id_area"])
                if index >= 0:
                    self.area_combo.setCurrentIndex(index)