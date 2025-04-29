from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QFormLayout, QPushButton, QMessageBox, QWidget
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

class InventoryDetailView(QDialog):
    def __init__(self, api_client, inventory_id=None):
        super().__init__()
        from utils.theme import Theme
        Theme.apply_window_light_theme(self)

        self.api_client = api_client
        self.inventory_id = inventory_id
        self.inventory = {}

        self.setWindowTitle(f"Detalle Inventario #{inventory_id}")
        self.setMinimumSize(450, 250)

        self.init_ui()
        if self.inventory_id:
            try:
                self.inventory = self.api_client.get_inventory_item(self.inventory_id)
                self.update_view()
            except Exception as e:
                self.show_error(str(e))

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

        self.lbl_producto = QLabel("N/A")
        self.lbl_cantidad = QLabel("N/A")
        self.lbl_lote = QLabel("N/A")
        self.lbl_fecha = QLabel("N/A")
        self.lbl_ubicacion = QLabel("N/A")

        form_layout.addRow("Producto:", self.lbl_producto)
        form_layout.addRow("Cantidad:", self.lbl_cantidad)
        form_layout.addRow("Lote:", self.lbl_lote)
        form_layout.addRow("Fecha de ingreso:", self.lbl_fecha)
        form_layout.addRow("Ubicación:", self.lbl_ubicacion)

        layout.addWidget(form_container)

        close_btn = QPushButton("Cerrar")
        close_btn.setFixedWidth(100)
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn, alignment=Qt.AlignmentFlag.AlignRight)

    def update_view(self):
        prod = self.inventory.get("material", {})
        self.lbl_producto.setText(prod.get("nombre", "") if prod else "")
        self.lbl_cantidad.setText(str(self.inventory.get("cantidad", 0)))
        self.lbl_lote.setText(self.inventory.get("lote", ""))
        fecha = self.inventory.get("fecha_ingreso", "")
        self.lbl_fecha.setText(str(fecha) if fecha else "N/A")
        self.lbl_ubicacion.setText(self.inventory.get("ubicacion", ""))

    def show_error(self, msg):
        QMessageBox.critical(self, "Error", str(msg))
