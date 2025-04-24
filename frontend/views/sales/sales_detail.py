from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QFormLayout, QTableWidget, QTableWidgetItem, QHeaderView, QPushButton
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

class SalesDetailView(QDialog):
    def __init__(self, api_client, sale_id=None):
        super().__init__()
        from utils.theme import Theme
        Theme.apply_window_light_theme(self)

        self.api_client = api_client
        self.sale_id = sale_id
        self.setWindowTitle(f"Detalle venta #{sale_id}")
        self.setMinimumSize(600, 400)
        self.sale = {}
        self.detalles = []
        self.init_ui()
        if self.sale_id:
            try:
                self.sale = self.api_client.get_sale(self.sale_id)
                self.detalles = self.sale.get("detalles", [])
                self.update_view()
            except Exception as e:
                self.show_error(str(e))

    def init_ui(self):
        self.layout = QVBoxLayout(self)
        title = QLabel(self.windowTitle())
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        self.layout.addWidget(title)
        self.form = QFormLayout()
        self.lbl_cliente = QLabel("N/A")
        self.lbl_fecha = QLabel("N/A")
        self.lbl_estado = QLabel("N/A")
        self.lbl_total = QLabel("$0.00")
        self.form.addRow("Cliente:", self.lbl_cliente)
        self.form.addRow("Fecha:", self.lbl_fecha)
        self.form.addRow("Estado:", self.lbl_estado)
        self.form.addRow("Total:", self.lbl_total)
        self.layout.addLayout(self.form)
        # Tabla de productos
        label_items = QLabel("Productos vendidos")
        label_items.setFont(QFont("Arial", 13, QFont.Weight.Bold))
        self.layout.addWidget(label_items)
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Producto","Cantidad","P. Unitario","Subtotal"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.layout.addWidget(self.table)
        close_btn = QPushButton("Cerrar")
        close_btn.clicked.connect(self.accept)
        self.layout.addWidget(close_btn)

    def update_view(self):
        cliente = self.sale.get("cliente_nombre","")
        estado = self.sale.get("estado","").capitalize()
        fecha = self.sale.get("fecha","")
        total = float(self.sale.get("total",0) or 0)
        self.lbl_cliente.setText(cliente)
        self.lbl_fecha.setText(fecha)
        self.lbl_estado.setText(estado)
        self.lbl_total.setText(f"${total:,.2f}")

        self.table.setRowCount(0)
        for idx, item in enumerate(self.detalles):
            self.table.insertRow(idx)
            self.table.setItem(idx,0, QTableWidgetItem(str(item.get("producto_nombre",""))))
            self.table.setItem(idx,1, QTableWidgetItem(str(item.get("cantidad",0))))
            self.table.setItem(idx,2, QTableWidgetItem(f"${item.get('precio_unitario',0):,.2f}"))
            subtotal = float(item.get("subtotal",item.get("precio_unitario",0)*item.get("cantidad",0)))
            self.table.setItem(idx,3, QTableWidgetItem(f"${subtotal:,.2f}"))

    def show_error(self,msg):
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.critical(self, "Error", str(msg))