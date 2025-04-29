from PyQt6.QtWidgets import (QWidget,QDialog, QVBoxLayout, QFormLayout, QLineEdit, 
                            QPushButton, QMessageBox, QDateEdit, QComboBox,
                            QTableWidget, QTableWidgetItem, QHeaderView,
                            QHBoxLayout, QLabel)
from PyQt6.QtGui import QDoubleValidator
from PyQt6.QtCore import Qt, QDate
from controllers.purchase_order_controller import PurchaseOrderController

class PurchaseOrderFormView(QDialog):
    def __init__(self, api_client, order=None, on_save_callback=None):
        super().__init__()
        self.api_client = api_client
        self.on_save_callback = on_save_callback
        self.order = order
        self.materials = []
        self.init_ui()
        self.load_suppliers()
        self.load_materials()

    def init_ui(self):
        layout = QVBoxLayout()
        
        # Formulario principal
        form = QFormLayout()
        
        # ID (solo lectura para edición)
        self.id_input = QLineEdit()
        self.id_input.setReadOnly(True)
        
        # Proveedor (combobox)
        self.supplier_combo = QComboBox()
        
        # Fecha y fecha de entrega
        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(True)
        self.date_input.setDate(QDate.currentDate())
        
        self.delivery_date_input = QDateEdit()
        self.delivery_date_input.setCalendarPopup(True)
        self.delivery_date_input.setDate(QDate.currentDate().addDays(7))
        
        # Estado
        self.status_combo = QComboBox()
        self.status_combo.addItems(["pendiente", "aprobada", "recibida", "cancelada"])
        
        # Tabla de detalles
        self.details_table = QTableWidget(0, 5)
        self.details_table.setHorizontalHeaderLabels(["Material", "Cantidad", "P. Unitario", "Subtotal", "Acciones"])
        self.details_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        # Botones para detalles
        self.add_detail_btn = QPushButton("Agregar Detalle")
        self.add_detail_btn.clicked.connect(self.add_detail_row)
        
        # Total
        self.total_label = QLabel("0.00")
        
        # Botones de acción
        btn_layout = QHBoxLayout()
        self.save_btn = QPushButton("Guardar")
        self.save_btn.clicked.connect(self.save)
        self.cancel_btn = QPushButton("Cancelar")
        self.cancel_btn.clicked.connect(self.close)
        
        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(self.cancel_btn)
        
        # Añadir campos al formulario
        form.addRow("ID:", self.id_input)
        form.addRow("Proveedor:", self.supplier_combo)
        form.addRow("Fecha:", self.date_input)
        form.addRow("Fecha Entrega:", self.delivery_date_input)
        form.addRow("Estado:", self.status_combo)
        
        layout.addLayout(form)
        layout.addWidget(QLabel("Detalles:"))
        layout.addWidget(self.details_table)
        layout.addWidget(self.add_detail_btn)
        layout.addWidget(QLabel("Total:"))
        layout.addWidget(self.total_label)
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)
        
        # Si estamos editando, cargar los datos
        if self.order:
            self.load_order(self.order)

    def load_suppliers(self):
        try:
            suppliers = self.api_client.get_suppliers()
            self.supplier_combo.clear()
            for supplier in suppliers:
                self.supplier_combo.addItem(supplier.get('nombre', f"Proveedor {supplier['id_proveedor']}"), 
                                           userData=supplier['id_proveedor'])
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudieron cargar los proveedores: {str(e)}")

    def load_materials(self):
        try:
            self.materials = self.api_client.get_materials()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudieron cargar los materiales: {str(e)}")
            self.materials = []

    def add_detail_row(self, detail=None):
        row = self.details_table.rowCount()
        self.details_table.insertRow(row)
        
        # Combo para materiales
        material_combo = QComboBox()
        for material in self.materials:
            material_combo.addItem(material.get('nombre', f"Material {material['id_material']}"), 
                                 userData=material['id_material'])
        
        # Cantidad
        quantity_input = QLineEdit()
        quantity_input.setValidator(QDoubleValidator(0, 999999, 2))
        
        # Precio unitario
        unit_price_input = QLineEdit()
        unit_price_input.setValidator(QDoubleValidator(0, 999999, 2))
        
        # Subtotal (calculado automáticamente)
        subtotal_label = QLabel("0.00")
        
        # Botón para eliminar
        delete_btn = QPushButton("Eliminar")
        delete_btn.clicked.connect(lambda: self.remove_detail_row(row))
        
        # Conectar señales para calcular subtotal
        quantity_input.textChanged.connect(lambda: self.calculate_subtotal(row))
        unit_price_input.textChanged.connect(lambda: self.calculate_subtotal(row))
        
        # Añadir widgets a la tabla
        self.details_table.setCellWidget(row, 0, material_combo)
        self.details_table.setCellWidget(row, 1, quantity_input)
        self.details_table.setCellWidget(row, 2, unit_price_input)
        self.details_table.setCellWidget(row, 3, subtotal_label)
        self.details_table.setCellWidget(row, 4, delete_btn)
        
        # Si estamos editando y hay detalles, cargarlos
        if detail:
            # Seleccionar material
            index = material_combo.findData(detail['material_id'])
            if index >= 0:
                material_combo.setCurrentIndex(index)
            
            quantity_input.setText(str(detail['quantity']))
            unit_price_input.setText(str(detail['unit_price']))
            subtotal_label.setText(str(detail['subtotal']))
        
        self.calculate_total()

    def remove_detail_row(self, row):
        self.details_table.removeRow(row)
        self.calculate_total()

    def calculate_subtotal(self, row):
        try:
            quantity = float(self.details_table.cellWidget(row, 1).text() or 0)
            unit_price = float(self.details_table.cellWidget(row, 2).text() or 0)
            subtotal = quantity * unit_price
            self.details_table.cellWidget(row, 3).setText(f"{subtotal:.2f}")
            self.calculate_total()
        except ValueError:
            pass

    def calculate_total(self):
        total = 0.0
        for row in range(self.details_table.rowCount()):
            try:
                subtotal_text = self.details_table.cellWidget(row, 3).text()
                subtotal = float(subtotal_text) if subtotal_text else 0.0
                total += subtotal
            except ValueError:
                pass
        self.total_label.setText(f"{total:.2f}")

    def load_order(self, order):
        self.id_input.setText(str(order.get('po_id')))
        
        # Seleccionar proveedor
        index = self.supplier_combo.findData(order.get('supplier_id'))
        if index >= 0:
            self.supplier_combo.setCurrentIndex(index)
        
        # Fechas
        if 'date' in order:
            date = QDate.fromString(order['date'], Qt.DateFormat.ISODate)
            self.date_input.setDate(date)
        
        if 'delivery_date' in order and order['delivery_date']:
            delivery_date = QDate.fromString(order['delivery_date'], Qt.DateFormat.ISODate)
            self.delivery_date_input.setDate(delivery_date)
        
        # Estado
        index = self.status_combo.findText(order.get('status', 'pendiente'))
        if index >= 0:
            self.status_combo.setCurrentIndex(index)
        
        # Limpiar y cargar detalles
        self.details_table.setRowCount(0)
        for detail in order.get('details', []):
            self.add_detail_row(detail)
        
        # Total
        if 'total' in order:
            self.total_label.setText(f"{float(order['total']):.2f}")

    def get_form_data(self):
        data = {
            'supplier_id': self.supplier_combo.currentData(),  # 👈 obligatorio
            'date': self.date_input.date().toString(Qt.DateFormat.ISODate),
            'delivery_date': self.delivery_date_input.date().toString(Qt.DateFormat.ISODate),
            'status': self.status_combo.currentText(),
            'details': [],
            'total': float(self.total_label.text() or 0),
            'user_id': 1  # Hardcodeado temporal
        }

        # SOLO si estás editando, agregas po_id
        if self.id_input.text():
            data['po_id'] = int(self.id_input.text())

        # Recoger detalles de materiales
        for row in range(self.details_table.rowCount()):
            material_combo = self.details_table.cellWidget(row, 0)
            quantity_input = self.details_table.cellWidget(row, 1)
            unit_price_input = self.details_table.cellWidget(row, 2)
            subtotal_label = self.details_table.cellWidget(row, 3)

            detail = {
                'material_id': material_combo.currentData(),
                'material_name': material_combo.currentText(),
                'quantity': float(quantity_input.text()),
                'unit_price': float(unit_price_input.text()),
                'subtotal': float(subtotal_label.text())
            }
            data['details'].append(detail)

        return data

    def save(self):
        data = self.get_form_data()

        # Validación básica
        if not data['supplier_id']:
            QMessageBox.warning(self, "Error", "Debe seleccionar un proveedor")
            return

        if not data['details']:
            QMessageBox.warning(self, "Error", "Debe agregar al menos un detalle")
            return

        try:
            if 'po_id' in data and data['po_id']:  # Edición
                result = self.api_client.update_purchase_order(data['po_id'], data)
            else:  # Creación
                data.pop('po_id', None)  # <-- Remueve po_id si existe
                result = self.api_client.create_purchase_order(data)

            if result:
                QMessageBox.information(self, "Éxito", "Orden guardada correctamente")
                if self.on_save_callback:
                    self.on_save_callback()
                self.close()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo guardar la orden: {str(e)}")
