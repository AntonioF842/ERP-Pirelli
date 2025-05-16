from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem, QPushButton,
    QLabel, QComboBox, QLineEdit, QHeaderView, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon

class SalesDetailsListView(QWidget):
    def __init__(self, api_client):
        super().__init__()
        from utils.theme import Theme
        Theme.apply_window_light_theme(self)
        self.api_client = api_client
        self.init_ui()
        self.last_details = []
        self.refresh_data()

    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        title_label = QLabel("Gestión de Detalles de Venta")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold;")

        toolbar_layout = QHBoxLayout()

        self.sale_filter = QComboBox()
        self.sale_filter.setPlaceholderText("Filtrar por venta...")

        self.product_filter = QComboBox()
        self.product_filter.setPlaceholderText("Filtrar por producto...")

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Buscar por ID...")
        self.search_input.textChanged.connect(self.apply_filters)

        search_btn = QPushButton("Buscar")
        search_btn.clicked.connect(self.apply_filters)

        self.add_btn = QPushButton("Nuevo Detalle")
        self.add_btn.setIcon(QIcon("resources/icons/add.png"))
        self.add_btn.clicked.connect(self.add_detail)

        self.refresh_btn = QPushButton("Actualizar")
        self.refresh_btn.setIcon(QIcon("resources/icons/refresh.png"))
        self.refresh_btn.clicked.connect(self.refresh_data)

        toolbar_layout.addWidget(QLabel("Venta:"))
        toolbar_layout.addWidget(self.sale_filter)
        toolbar_layout.addWidget(QLabel("Producto:"))
        toolbar_layout.addWidget(self.product_filter)
        toolbar_layout.addWidget(self.search_input)
        toolbar_layout.addWidget(search_btn)
        toolbar_layout.addStretch()
        toolbar_layout.addWidget(self.add_btn)
        toolbar_layout.addWidget(self.refresh_btn)

        self.details_table = QTableWidget()
        self.details_table.setColumnCount(8)
        self.details_table.setHorizontalHeaderLabels([
            "ID", "Venta ID", "Fecha Venta", "Producto", "Código", "Cantidad", "Precio", "Subtotal", "Acciones"
        ])
        self.details_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.details_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.details_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.details_table.setAlternatingRowColors(True)

        main_layout.addWidget(title_label)
        main_layout.addLayout(toolbar_layout)
        main_layout.addWidget(self.details_table)

        self.setLayout(main_layout)

    def refresh_data(self):
        try:
            # Load sales for filter
            sales = self.api_client.get_sales()
            self.sale_filter.clear()
            self.sale_filter.addItem("Todas las ventas", None)
            for sale in sales:
                self.sale_filter.addItem(f"Venta #{sale['id_venta']} - {sale.get('cliente_nombre', '')}", sale['id_venta'])

            # Load products for filter
            products = self.api_client.get_products()
            self.product_filter.clear()
            self.product_filter.addItem("Todos los productos", None)
            for prod in products:
                self.product_filter.addItem(f"{prod['codigo']} - {prod['nombre']}", prod['id_producto'])

            # Load details
            details = self.api_client.get_sales_details()
            self.last_details = details if isinstance(details, list) else details.get('detalles', [])
            self.apply_filters()
        except Exception as e:
            self.show_error(str(e))

    def apply_filters(self):
        sale_id = self.sale_filter.currentData()
        product_id = self.product_filter.currentData()
        search_text = self.search_input.text().strip().lower()

        filtered = self.last_details
        
        if sale_id is not None:
            filtered = [d for d in filtered if d.get('id_venta') == sale_id]
            
        if product_id is not None:
            filtered = [d for d in filtered if d.get('id_producto') == product_id]
            
        if search_text:
            filtered = [d for d in filtered if search_text in str(d.get('id_detalle', '')).lower()]

        self.populate_table(filtered)

    def populate_table(self, detalles):
        self.details_table.setRowCount(0)
        for row, detalle in enumerate(detalles):
            self.details_table.insertRow(row)
            
            self.details_table.setItem(row, 0, QTableWidgetItem(str(detalle.get('id_detalle', ''))))
            self.details_table.setItem(row, 1, QTableWidgetItem(str(detalle.get('id_venta', ''))))
            self.details_table.setItem(row, 2, QTableWidgetItem(detalle.get('venta_fecha', '')))
            self.details_table.setItem(row, 3, QTableWidgetItem(detalle.get('producto_nombre', '')))
            self.details_table.setItem(row, 4, QTableWidgetItem(detalle.get('producto_codigo', '')))
            self.details_table.setItem(row, 5, QTableWidgetItem(str(detalle.get('cantidad', 0))))
            
            precio = float(detalle.get('precio_unitario', 0))
            precio_item = QTableWidgetItem(f"${precio:,.2f}")
            precio_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.details_table.setItem(row, 6, precio_item)
            
            subtotal = float(detalle.get('subtotal', 0))
            subtotal_item = QTableWidgetItem(f"${subtotal:,.2f}")
            subtotal_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.details_table.setItem(row, 7, subtotal_item)

            # Action buttons
            actions_layout = QHBoxLayout()
            actions_layout.setContentsMargins(0,0,0,0)
            actions_layout.setSpacing(5)
            
            view_btn = QPushButton()
            view_btn.setIcon(QIcon("resources/icons/view.png"))
            view_btn.setToolTip("Ver detalle")
            view_btn.setFixedSize(30,30)
            view_btn.clicked.connect(lambda checked, d=detalle: self.view_detail(d))
            
            edit_btn = QPushButton()
            edit_btn.setIcon(QIcon("resources/icons/edit.png"))
            edit_btn.setToolTip("Editar")
            edit_btn.setFixedSize(30,30)
            edit_btn.clicked.connect(lambda checked, d=detalle: self.edit_detail(d))
            
            delete_btn = QPushButton()
            delete_btn.setIcon(QIcon("resources/icons/delete.png"))
            delete_btn.setToolTip("Eliminar")
            delete_btn.setFixedSize(30,30)
            delete_btn.clicked.connect(lambda checked, d=detalle: self.delete_detail(d))
            
            actions_layout.addWidget(view_btn)
            actions_layout.addWidget(edit_btn)
            actions_layout.addWidget(delete_btn)
            
            actions_widget = QWidget()
            actions_widget.setLayout(actions_layout)
            self.details_table.setCellWidget(row, 8, actions_widget)

    def add_detail(self):
        from .sales_details_form import SalesDetailsForm
        dlg = SalesDetailsForm(self.api_client)
        if dlg.exec():
            self.refresh_data()

    def view_detail(self, detail):
        from .sales_details_detail import SalesDetailsDetailView
        dlg = SalesDetailsDetailView(self.api_client, detail_id=detail.get('id_detalle'))
        dlg.exec()

    def edit_detail(self, detail):
        from .sales_details_form import SalesDetailsForm
        dlg = SalesDetailsForm(self.api_client, detail_id=detail.get('id_detalle'))
        if dlg.exec():
            self.refresh_data()

    def delete_detail(self, detail):
        answer = QMessageBox.question(
            self, "Eliminar detalle",
            f"¿Eliminar el detalle #{detail.get('id_detalle')} de la venta #{detail.get('id_venta')}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if answer == QMessageBox.StandardButton.Yes:
            try:
                self.api_client.delete_sales_detail(detail.get("id_detalle"))
                self.refresh_data()
            except Exception as e:
                self.show_error(f"No se pudo eliminar el detalle: {e}")

    def show_error(self, msg):
        QMessageBox.critical(self, "Error", msg)