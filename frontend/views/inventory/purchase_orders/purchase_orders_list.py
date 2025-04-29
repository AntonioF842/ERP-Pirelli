from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget,
    QTableWidgetItem, QHeaderView, QComboBox, QLineEdit, QMessageBox, QDialog
)
from views.inventory.purchase_orders.purchase_orders_form import PurchaseOrderFormView
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt

class PurchaseOrderListView(QWidget):
    def __init__(self, api_client, details_callback=None):
        super().__init__()
        self.api_client = api_client
        self.details_callback = details_callback
        self.orders_data = []
        self.filtered_orders = []
        self.init_ui()
        self.refresh_data()

    def init_ui(self):
        main_layout = QVBoxLayout()
        
        # Title
        title_label = QLabel("Órdenes de Compra")
        title_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        
        # Toolbar with filters, search and add button
        toolbar_layout = QHBoxLayout()
        
        # Status filter
        self.status_combo = QComboBox()
        self.status_combo.addItem("Todos")
        self.status_combo.addItem("Pendiente")
        self.status_combo.addItem("Procesada")
        self.status_combo.addItem("Cancelada")
        self.status_combo.currentIndexChanged.connect(self.apply_filters)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Buscar por Proveedor, Estado o Fecha...")
        self.search_input.textChanged.connect(self.apply_filters)
        
        add_btn = QPushButton("Agregar Orden")
        add_btn.setIcon(QIcon("resources/icons/add.png"))
        add_btn.clicked.connect(self.add_purchase_order)
        
        toolbar_layout.addWidget(QLabel("Estado:"))
        toolbar_layout.addWidget(self.status_combo)
        toolbar_layout.addStretch()
        toolbar_layout.addWidget(self.search_input)
        toolbar_layout.addWidget(add_btn)
        
        # Table setup with actions column
        self.orders_table = QTableWidget(0, 6)
        self.orders_table.setHorizontalHeaderLabels([
            "ID", "Proveedor", "Fecha", "Estado", "Total", "Acciones"
        ])
        self.orders_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.orders_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.orders_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.orders_table.setAlternatingRowColors(True)
        self.orders_table.cellDoubleClicked.connect(self.open_details_dialog)
        
        # Add all components to main layout
        main_layout.addWidget(title_label)
        main_layout.addLayout(toolbar_layout)
        main_layout.addWidget(self.orders_table)
        self.setLayout(main_layout)

    def refresh_data(self):
        try:
            orders = self.api_client.get_purchase_orders()
            if not isinstance(orders, list):
                orders = []
            self.orders_data = orders
            self.apply_filters()
        except Exception as e:
            self.show_error(f"Error al obtener órdenes de compra: {e}")
            self.orders_data = []
            self.apply_filters()

    def apply_filters(self):
        estado_filtro = self.status_combo.currentText()
        buscar = self.search_input.text().strip().lower()
        filtered = self.orders_data
        
        if estado_filtro != "Todos":
            filtered = [o for o in filtered if (o.get("status") or "").lower() == estado_filtro.lower()]
        
        if buscar:
            filtered = [
                order for order in filtered
                if buscar in str(order.get("po_id", "")).lower()
                or buscar in str(order.get("supplier_name", "")).lower()
                or buscar in str(order.get("supplier_id", "")).lower()
                or buscar in str(order.get("date", "")).lower()
                or buscar in str(order.get("status", "")).lower()
            ]
        
        self.filtered_orders = filtered
        self.populate_table(filtered)

    def populate_table(self, orders):
        self.orders_table.setRowCount(0)
        for row, order in enumerate(orders):
            self.orders_table.insertRow(row)
            self.orders_table.setItem(row, 0, QTableWidgetItem(str(order.get("po_id", ""))))
            self.orders_table.setItem(row, 1, QTableWidgetItem(str(order.get("supplier_name", "")) or str(order.get("supplier_id", ""))))
            self.orders_table.setItem(row, 2, QTableWidgetItem(str(order.get("date", ""))))
            self.orders_table.setItem(row, 3, QTableWidgetItem(str(order.get("status", ""))))
            self.orders_table.setItem(row, 4, QTableWidgetItem(str(order.get("total", ""))))
            
            # Action buttons
            actions_layout = QHBoxLayout()
            actions_layout.setContentsMargins(0, 0, 0, 0)
            actions_layout.setSpacing(5)
            
            view_btn = QPushButton()
            view_btn.setIcon(QIcon("resources/icons/view.png"))
            view_btn.setToolTip("Ver")
            view_btn.setFixedSize(30, 30)
            view_btn.clicked.connect(lambda checked, o=order: self.view_order(o))
            
            edit_btn = QPushButton()
            edit_btn.setIcon(QIcon("resources/icons/edit.png"))
            edit_btn.setToolTip("Editar")
            edit_btn.setFixedSize(30, 30)
            edit_btn.clicked.connect(lambda checked, o=order: self.edit_order(o))
            
            delete_btn = QPushButton()
            delete_btn.setIcon(QIcon("resources/icons/delete.png"))
            delete_btn.setToolTip("Eliminar")
            delete_btn.setFixedSize(30, 30)
            delete_btn.clicked.connect(lambda checked, o=order: self.delete_order(o))
            
            actions_layout.addWidget(view_btn)
            actions_layout.addWidget(edit_btn)
            actions_layout.addWidget(delete_btn)
            
            actions_widget = QWidget()
            actions_widget.setLayout(actions_layout)
            self.orders_table.setCellWidget(row, 5, actions_widget)

    def open_details_dialog(self, row, column):
        if self.details_callback and row < len(self.filtered_orders):
            self.details_callback(self.filtered_orders[row])
        else:
            self.view_order(self.filtered_orders[row])
    
    # Action button handlers
    def add_purchase_order(self):
        """Abre el formulario para crear una nueva orden de compra"""
        dlg = PurchaseOrderFormView(
            api_client=self.api_client,
            on_save_callback=self.refresh_data
        )
        dlg.setWindowTitle("Nueva Orden de Compra")
        dlg.exec()
    
    def view_order(self, order):
        QMessageBox.information(
            self, "Detalles de Orden", 
            f"ID: {order.get('po_id')}\n"
            f"Proveedor: {order.get('supplier_name') or order.get('supplier_id')}\n"
            f"Fecha: {order.get('date')}\n"
            f"Estado: {order.get('status')}\n"
            f"Total: {order.get('total')}"
        )
    
    def edit_order(self, order):
        """Abre el formulario para editar una orden existente"""
        # Obtener los datos completos de la orden
        full_order = self.api_client.get_purchase_order(order['po_id'])
        if not full_order:
            QMessageBox.warning(self, "Error", "No se pudo cargar la orden para edición")
            return
        
        dlg = PurchaseOrderFormView(
            api_client=self.api_client,
            order=full_order,
            on_save_callback=self.refresh_data
        )
        dlg.setWindowTitle(f"Editar Orden #{order['po_id']}")
        dlg.exec()
    
    def delete_order(self, order):
        answer = QMessageBox.question(
            self, "Eliminar orden",
            f"¿Eliminar orden de compra {order.get('po_id')}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if answer == QMessageBox.StandardButton.Yes:
            try:
                self.api_client.delete_purchase_order(order.get("po_id"))
                self.refresh_data()
            except Exception as e:
                self.show_error(f"No se pudo eliminar la orden: {e}")
    
    def show_order_details(self, order):
        details = order.get("details", [])
        if not details:
            QMessageBox.information(self, "Detalles de Orden", "No hay detalles para esta orden.")
            return
        
        text = ""
        for d in details:
            text += f"- Material: {d.get('item', d.get('material_id', ''))}\n"
            text += f"  Cantidad: {d.get('quantity', '')}\n"
            text += f"  Precio Unitario: {d.get('unit_price', '')}\n"
            text += f"  Subtotal: {d.get('subtotal', '')}\n\n"
        
        QMessageBox.information(
            self, 
            f"Detalles de la Orden {order.get('po_id')}", 
            text
        )

    def show_error(self, msg):
        QMessageBox.critical(self, "Error", msg)
