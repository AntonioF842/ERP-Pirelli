from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLabel, QComboBox, QDateEdit, QLineEdit, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QHBoxLayout, QSpinBox, QDialogButtonBox, QMessageBox
)
from PyQt6.QtCore import QDate, Qt
from PyQt6.QtGui import QIcon

class SalesForm(QDialog):
    def __init__(self, api_client, sale_id=None):
        super().__init__()
        from utils.theme import Theme
        Theme.apply_window_light_theme(self)
        self.api_client = api_client
        self.sale_id = sale_id
        self.setWindowTitle("Nueva Venta" if not self.sale_id else "Editar Venta")
        self.setMinimumSize(850, 600)

        self.sale_data = None
        self.products = []
        self.clients = []
        self.sale_items = []

        self.init_ui()
        self.load_clients()
        self.load_products()
        if self.sale_id:
            self.load_sale()

    def init_ui(self):
        main_layout = QVBoxLayout()
        title = QLabel(self.windowTitle())
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        main_layout.addWidget(title)

        form = QFormLayout()
        self.client_combo = QComboBox(); self.client_combo.setMinimumWidth(250)
        self.date_edit = QDateEdit(QDate.currentDate()); self.date_edit.setCalendarPopup(True)
        self.status_combo = QComboBox(); self.status_combo.addItems(["Pendiente", "Completada", "Cancelada"])
        self.total_edit = QLineEdit("$0.00"); self.total_edit.setReadOnly(True)
        form.addRow("Cliente:", self.client_combo)
        form.addRow("Fecha:", self.date_edit)
        form.addRow("Estado:", self.status_combo)
        form.addRow("Total:", self.total_edit)
        main_layout.addLayout(form)

        # Productos section
        products_label = QLabel("Productos"); products_label.setStyleSheet("font-size:16px;font-weight:bold;")
        main_layout.addWidget(products_label)

        toolbar = QHBoxLayout()
        self.product_combo = QComboBox(); self.product_combo.setMinimumWidth(220)
        self.qty_spin = QSpinBox(); self.qty_spin.setMinimum(1); self.qty_spin.setMaximum(999)
        add_prod_btn = QPushButton("Agregar"); add_prod_btn.setIcon(QIcon("resources/icons/add.png"))
        add_prod_btn.clicked.connect(self.add_product)
        toolbar.addWidget(QLabel("Producto:"))
        toolbar.addWidget(self.product_combo)
        toolbar.addWidget(QLabel("Cantidad:"))
        toolbar.addWidget(self.qty_spin)
        toolbar.addWidget(add_prod_btn)
        main_layout.addLayout(toolbar)

        self.products_table = QTableWidget()
        self.products_table.setColumnCount(5)
        self.products_table.setHorizontalHeaderLabels([
            "Código", "Nombre", "Cantidad", "Precio", "Subtotal"
        ])
        self.products_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.products_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        main_layout.addWidget(self.products_table)

        # Accion
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.save)
        buttons.rejected.connect(self.reject)
        main_layout.addWidget(buttons)

        self.setLayout(main_layout)

    def load_clients(self):
        try:
            clients = self.api_client.get_clients()
            self.clients = clients if isinstance(clients, list) else clients.get("clientes", [])
            self.client_combo.clear()
            for c in self.clients:
                self.client_combo.addItem(c.get("nombre",""), c.get("id_cliente"))
        except Exception as e:
            self.show_error(str(e))

    def load_products(self):
        try:
            productos = self.api_client.get_products()
            self.products = productos if isinstance(productos, list) else productos.get("productos", [])
            self.product_combo.clear()
            for p in self.products:
                self.product_combo.addItem(f"{p.get('codigo')} - {p.get('nombre')}", p.get('id_producto'))
        except Exception as e:
            self.show_error(str(e))

    def load_sale(self):
        try:
            venta = self.api_client.get_sale(self.sale_id)
            if 'id_cliente' in venta:
                idx = self.client_combo.findData(venta.get("id_cliente"))
                if idx >= 0: self.client_combo.setCurrentIndex(idx)
            if 'fecha' in venta:
                self.date_edit.setDate(QDate.fromString(venta.get("fecha") or QDate.currentDate().toString("yyyy-MM-dd"),"yyyy-MM-dd"))
            if 'estado' in venta:
                st = venta.get("estado","Pendiente").capitalize()
                idx = self.status_combo.findText(st)
                if idx >= 0: self.status_combo.setCurrentIndex(idx)
            self.sale_items = venta.get("detalles", [])
            self.update_products_table()
        except Exception as e:
            self.show_error(str(e))

    def add_product(self):
        product_id = self.product_combo.currentData()
        if not product_id:
            self.show_error("Seleccione un producto.")
            return
        cantidad = self.qty_spin.value()
        prod = next((p for p in self.products if p["id_producto"] == product_id), None)
        if not prod:
            self.show_error("Producto no hallado.")
            return
        exist_idx = next((i for i, x in enumerate(self.sale_items) if x["id_producto"]==product_id), -1)
        if exist_idx >= 0:
            self.sale_items[exist_idx]["cantidad"] += cantidad
        else:
            self.sale_items.append({
                "id_producto": product_id,
                "cantidad": cantidad,
                "precio_unitario": float(prod["precio"]),
                "subtotal": float(prod["precio"])*cantidad
            })
        self.update_products_table()

    def update_products_table(self):
        self.products_table.setRowCount(0)
        total = 0.0
        for idx, item in enumerate(self.sale_items):
            prod = next((p for p in self.products if p["id_producto"] == item["id_producto"]), {})
            self.products_table.insertRow(idx)
            self.products_table.setItem(idx,0,QTableWidgetItem(prod.get("codigo","")))
            self.products_table.setItem(idx,1,QTableWidgetItem(prod.get("nombre","")))
            self.products_table.setItem(idx,2,QTableWidgetItem(str(item.get("cantidad",0))))
            precio = float(item.get("precio_unitario",0)); subtotal=precio*item.get("cantidad",0)
            self.products_table.setItem(idx,3,QTableWidgetItem(f"${precio:,.2f}"))
            self.products_table.setItem(idx,4,QTableWidgetItem(f"${subtotal:,.2f}"))
            total+=subtotal
        self.total_edit.setText(f"${total:,.2f}")

    def save(self):
        if not self.sale_items or not self.client_combo.currentData():
            self.show_error("Debe seleccionar cliente y al menos un producto.")
            return
        venta = {
            "id_cliente": self.client_combo.currentData(),
            "fecha": self.date_edit.date().toString("yyyy-MM-dd"),
            "estado": self.status_combo.currentText().lower(),
            "total": sum([item.get("cantidad",0)*item.get("precio_unitario",0) for item in self.sale_items]),
            "detalles": [
                {
                    "id_producto": item["id_producto"],
                    "cantidad": item["cantidad"],
                    "precio_unitario": item["precio_unitario"],
                    "subtotal": item["cantidad"]*item["precio_unitario"]
                }
                for item in self.sale_items
            ]
        }
        try:
            if self.sale_id:
                self.api_client.update_sale(self.sale_id, venta)
            else:
                self.api_client.create_sale(venta)
            self.accept()
        except Exception as e:
            self.show_error(str(e))

    def show_error(self,msg):
        QMessageBox.critical(self, "Error", str(msg))