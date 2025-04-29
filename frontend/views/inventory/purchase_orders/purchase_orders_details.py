from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QPushButton, QHeaderView

class PurchaseOrderDetailsView(QWidget):
    def __init__(self, api_client, on_edit_callback=None):
        super().__init__()
        self.api_client = api_client
        self.on_edit_callback = on_edit_callback
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        self.id_label = QLabel("")
        self.supplier_label = QLabel("")
        self.date_label = QLabel("")
        self.delivery_label = QLabel("")
        self.status_label = QLabel("")
        self.total_label = QLabel("")
        
        layout.addWidget(self.id_label)
        layout.addWidget(self.supplier_label)
        layout.addWidget(self.date_label)
        layout.addWidget(self.delivery_label)
        layout.addWidget(self.status_label)
        layout.addWidget(self.total_label)

        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(['Material', 'Cantidad', 'Precio Unitario', 'Subtotal'])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.table)

        self.edit_btn = QPushButton("Editar")
        self.edit_btn.clicked.connect(self.edit)
        layout.addWidget(self.edit_btn)
        self.setLayout(layout)
        self.order = None

    def load_order(self, order):
        self.order = order
        self.id_label.setText(f"ID: {order.get('po_id', 'N/A')}")
        self.supplier_label.setText(f"Proveedor: {order.get('supplier_name', order.get('supplier_id', 'N/A'))}")
        self.date_label.setText(f"Fecha: {order.get('date', 'N/A')}")
        self.delivery_label.setText(f"Fecha Entrega: {order.get('delivery_date', order.get('expected_delivery', 'N/A'))}")
        self.status_label.setText(f"Estado: {order.get('status', 'N/A')}")
        self.total_label.setText(f"Total: {order.get('total', '0.00')}")
        
        self.table.setRowCount(0)
        for detail in order.get('details', []):
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(detail.get('material_name', detail.get('material_id', 'N/A'))))
            self.table.setItem(row, 1, QTableWidgetItem(str(detail.get('quantity', 'N/A'))))
            self.table.setItem(row, 2, QTableWidgetItem(str(detail.get('unit_price', 'N/A'))))
            self.table.setItem(row, 3, QTableWidgetItem(str(detail.get('subtotal', 'N/A'))))

    def edit(self):
        if self.on_edit_callback and self.order:
            self.on_edit_callback(self.order)