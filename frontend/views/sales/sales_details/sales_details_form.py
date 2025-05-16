from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLabel, QComboBox, QSpinBox, 
    QDoubleSpinBox, QDialogButtonBox, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon

class SalesDetailsForm(QDialog):
    def __init__(self, api_client, detail_id=None):
        super().__init__()
        from utils.theme import Theme
        Theme.apply_window_light_theme(self)
        self.api_client = api_client
        self.detail_id = detail_id
        self.setWindowTitle("Nuevo Detalle" if not self.detail_id else "Editar Detalle")
        self.setMinimumSize(500, 300)

        self.sales = []
        self.products = []
        self.detail_data = None

        self.init_ui()
        self.load_data()
        if self.detail_id:
            self.load_detail()

    def init_ui(self):
        main_layout = QVBoxLayout()
        title = QLabel(self.windowTitle())
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        main_layout.addWidget(title)

        form = QFormLayout()
        
        self.sale_combo = QComboBox()
        self.product_combo = QComboBox()
        self.quantity_spin = QSpinBox()
        self.quantity_spin.setMinimum(1)
        self.quantity_spin.setMaximum(9999)
        self.price_spin = QDoubleSpinBox()
        self.price_spin.setMinimum(0.01)
        self.price_spin.setMaximum(999999.99)
        self.price_spin.setDecimals(2)
        self.price_spin.setPrefix("$")
        self.subtotal_label = QLabel("$0.00")
        
        form.addRow("Venta:", self.sale_combo)
        form.addRow("Producto:", self.product_combo)
        form.addRow("Cantidad:", self.quantity_spin)
        form.addRow("Precio unitario:", self.price_spin)
        form.addRow("Subtotal:", self.subtotal_label)
        
        main_layout.addLayout(form)

        # Connect signals
        self.quantity_spin.valueChanged.connect(self.update_subtotal)
        self.price_spin.valueChanged.connect(self.update_subtotal)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.save)
        buttons.rejected.connect(self.reject)
        main_layout.addWidget(buttons)

        self.setLayout(main_layout)

    def load_data(self):
        try:
            # Load sales
            self.sales = self.api_client.get_sales()
            self.sale_combo.clear()
            for sale in self.sales:
                self.sale_combo.addItem(f"Venta #{sale['id_venta']} - {sale.get('cliente_nombre', '')}", sale['id_venta'])

            # Load products
            self.products = self.api_client.get_products()
            self.product_combo.clear()
            for product in self.products:
                self.product_combo.addItem(f"{product['codigo']} - {product['nombre']} (${product['precio']})", product['id_producto'])

        except Exception as e:
            self.show_error(str(e))

    def load_detail(self):
        try:
            detail = self.api_client.get_sales_detail(self.detail_id)
            if not detail:
                self.show_error("Detalle no encontrado")
                self.reject()
                return

            self.detail_data = detail
            
            # Set sale
            sale_idx = self.sale_combo.findData(detail.get('id_venta'))
            if sale_idx >= 0:
                self.sale_combo.setCurrentIndex(sale_idx)
                self.sale_combo.setEnabled(False)  # Don't allow changing sale after creation

            # Set product
            product_idx = self.product_combo.findData(detail.get('id_producto'))
            if product_idx >= 0:
                self.product_combo.setCurrentIndex(product_idx)

            self.quantity_spin.setValue(detail.get('cantidad', 1))
            self.price_spin.setValue(float(detail.get('precio_unitario', 0)))
            self.update_subtotal()

        except Exception as e:
            self.show_error(str(e))

    def update_subtotal(self):
        subtotal = self.quantity_spin.value() * self.price_spin.value()
        self.subtotal_label.setText(f"${subtotal:,.2f}")

    def save(self):
        if not self.sale_combo.currentData() or not self.product_combo.currentData():
            self.show_error("Debe seleccionar una venta y un producto")
            return

        detail = {
            'id_venta': self.sale_combo.currentData(),
            'id_producto': self.product_combo.currentData(),
            'cantidad': self.quantity_spin.value(),
            'precio_unitario': self.price_spin.value()
        }

        try:
            if self.detail_id:
                self.api_client.update_sales_detail(self.detail_id, detail)
            else:
                self.api_client.create_sales_detail(detail)
            self.accept()
        except Exception as e:
            self.show_error(str(e))

    def show_error(self, msg):
        QMessageBox.critical(self, "Error", msg)