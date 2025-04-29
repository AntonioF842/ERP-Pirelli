from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLabel, QComboBox, QSpinBox, QDateEdit,
    QLineEdit, QDialogButtonBox, QMessageBox, QWidget
)
from PyQt6.QtCore import QDate, Qt
from datetime import date

class InventoryForm(QDialog):
    def __init__(self, api_client, inventory_id=None):
        super().__init__()
        from utils.theme import Theme
        Theme.apply_window_light_theme(self)

        self.api_client = api_client
        self.inventory_id = inventory_id
        self.materials = []

        self.setWindowTitle("Nuevo Inventario" if not self.inventory_id else "Editar Inventario")
        self.setMinimumSize(450, 300)
        
        self.init_ui()
        self.load_materials()
        if self.inventory_id:
            self.load_inventory()

    def init_ui(self):
        layout = QVBoxLayout(self)

        title = QLabel(self.windowTitle())
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 20px; font-weight: bold; margin-bottom: 20px;")
        layout.addWidget(title)

        form_container = QWidget()
        form_layout = QFormLayout(form_container)
        form_layout.setContentsMargins(20, 0, 20, 0)
        form_layout.setSpacing(10)

        self.material_combo = QComboBox()
        self.material_combo.currentIndexChanged.connect(self.update_qty_limits)

        self.qty_spin = QSpinBox()
        self.qty_spin.setMinimum(0)
        self.qty_spin.setMaximum(99999)

        self.lote_input = QLineEdit()
        self.ubicacion_input = QLineEdit()

        self.fecha_ingreso_input = QDateEdit(QDate.currentDate())
        self.fecha_ingreso_input.setCalendarPopup(True)

        form_layout.addRow("Material:", self.material_combo)
        form_layout.addRow("Cantidad:", self.qty_spin)
        form_layout.addRow("Lote:", self.lote_input)
        form_layout.addRow("Ubicación:", self.ubicacion_input)
        form_layout.addRow("Fecha de ingreso:", self.fecha_ingreso_input)

        layout.addWidget(form_container)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.save)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons, alignment=Qt.AlignmentFlag.AlignRight)

    def load_materials(self):
        try:
            materiales = self.api_client.get_materials()
            self.materials = materiales if isinstance(materiales, list) else materiales.get("materiales", [])
            self.material_combo.clear()
            for m in self.materials:
                self.material_combo.addItem(m.get('nombre', ''), str(m.get('id_material')))
            self.update_qty_limits()
        except Exception as e:
            self.show_error(str(e))

    def update_qty_limits(self):
        idx = self.material_combo.currentIndex()
        if idx < 0 or not self.materials:
            self.qty_spin.setMinimum(0)
            self.qty_spin.setMaximum(99999)
            return
        id_material = self.material_combo.currentData()
        mat = next((m for m in self.materials if str(m.get("id_material")) == str(id_material)), None)
        stock_min = mat.get("stock_minimo", 0) if mat else 0
        stock_max = mat.get("stock_maximo", 99999) if mat else 99999
        self.qty_spin.setMinimum(stock_min)
        self.qty_spin.setMaximum(stock_max)
        if self.qty_spin.value() < stock_min:
            self.qty_spin.setValue(stock_min)
        elif self.qty_spin.value() > stock_max:
            self.qty_spin.setValue(stock_max)

    def load_inventory(self):
        try:
            inventario = self.api_client.get_inventory_item(self.inventory_id)
            id_material = str(inventario.get("id_material"))
            for idx in range(self.material_combo.count()):
                if str(self.material_combo.itemData(idx)) == id_material:
                    self.material_combo.setCurrentIndex(idx)
                    break
            self.update_qty_limits()
            self.qty_spin.setValue(inventario.get("cantidad", 0))
            self.lote_input.setText(inventario.get("lote", ""))
            self.ubicacion_input.setText(inventario.get("ubicacion", ""))
            if inventario.get('fecha_ingreso'):
                self.fecha_ingreso_input.setDate(QDate.fromString(str(inventario.get("fecha_ingreso")), "yyyy-MM-dd"))
        except Exception as e:
            self.show_error(str(e))

    def save(self):
        id_material = self.material_combo.currentData()
        cantidad = self.qty_spin.value()
        lote = self.lote_input.text()
        ubicacion = self.ubicacion_input.text()
        fecha_ingreso = self.fecha_ingreso_input.date().toString("yyyy-MM-dd")

        if not id_material:
            self.show_error("Seleccione un material.")
            return
        mat = next((m for m in self.materials if str(m.get("id_material")) == str(id_material)), None)
        stock_min = mat.get("stock_minimo", 0) if mat else 0
        stock_max = mat.get("stock_maximo", 99999) if mat else 99999
        if cantidad < stock_min or cantidad > stock_max:
            self.show_error(f"La cantidad debe estar entre mínimo {stock_min} y máximo {stock_max} para este material.")
            return

        inventario = {
            "id_material": id_material,
            "cantidad": cantidad,
            "lote": lote,
            "ubicacion": ubicacion,
            "fecha_ingreso": fecha_ingreso
        }
        try:
            if self.inventory_id:
                self.api_client.update_inventory_item(self.inventory_id, inventario)
            else:
                self.api_client.create_inventory_item(inventario)
            self.accept()
        except Exception as e:
            self.show_error(str(e))

    def show_error(self, msg):
        QMessageBox.critical(self, "Error", str(msg))
