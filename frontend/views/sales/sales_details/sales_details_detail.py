from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLabel, QTableWidget, 
    QTableWidgetItem, QHeaderView, QPushButton
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

class SalesDetailsDetailView(QDialog):
    def __init__(self, api_client, detail_id=None):
        super().__init__()
        from utils.theme import Theme
        Theme.apply_window_light_theme(self)

        self.api_client = api_client
        self.detail_id = detail_id
        self.setWindowTitle(f"Detalle de Venta #{detail_id}" if detail_id else "Detalle de Venta")
        self.setMinimumSize(500, 300)
        self.detail = {}
        self.init_ui()
        if self.detail_id:
            self.load_data()

    def init_ui(self):
        self.layout = QVBoxLayout(self)
        title = QLabel(self.windowTitle())
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        self.layout.addWidget(title)

        self.form = QFormLayout()
        self.lbl_sale = QLabel("N/A")
        self.lbl_date = QLabel("N/A")
        self.lbl_product = QLabel("N/A")
        self.lbl_code = QLabel("N/A")
        self.lbl_quantity = QLabel("N/A")
        self.lbl_price = QLabel("N/A")
        self.lbl_subtotal = QLabel("N/A")

        self.form.addRow("Venta:", self.lbl_sale)
        self.form.addRow("Fecha:", self.lbl_date)
        self.form.addRow("Producto:", self.lbl_product)
        self.form.addRow("Código:", self.lbl_code)
        self.form.addRow("Cantidad:", self.lbl_quantity)
        self.form.addRow("Precio unitario:", self.lbl_price)
        self.form.addRow("Subtotal:", self.lbl_subtotal)

        self.layout.addLayout(self.form)

        close_btn = QPushButton("Cerrar")
        close_btn.clicked.connect(self.accept)
        self.layout.addWidget(close_btn)

    def load_data(self):
        try:
            self.detail = self.api_client.get_sales_detail(self.detail_id)
            if not self.detail:
                self.show_error("Detalle no encontrado")
                self.reject()
                return

            self.lbl_sale.setText(str(self.detail.get('id_venta', 'N/A')))
            self.lbl_date.setText(self.detail.get('venta_fecha', 'N/A'))
            self.lbl_product.setText(self.detail.get('producto_nombre', 'N/A'))
            self.lbl_code.setText(self.detail.get('producto_codigo', 'N/A'))
            self.lbl_quantity.setText(str(self.detail.get('cantidad', 'N/A')))
            self.lbl_price.setText(f"${float(self.detail.get('precio_unitario', 0)):,.2f}")
            self.lbl_subtotal.setText(f"${float(self.detail.get('subtotal', 0)):,.2f}")

        except Exception as e:
            self.show_error(str(e))

    def show_error(self, msg):
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.critical(self, "Error", str(msg))