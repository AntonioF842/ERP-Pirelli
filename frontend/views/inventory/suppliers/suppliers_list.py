from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget,
    QTableWidgetItem, QHeaderView, QComboBox, QLineEdit, QMessageBox, QDialog
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from models.suppliers_model import Supplier
from .suppliers_form import SuppliersFormView

class SuppliersListView(QWidget):
    def __init__(self, api_client, details_callback=None):
        super().__init__()
        self.api_client = api_client
        self.details_callback = details_callback
        self.supplier_data = []
        self.last_suppliers = []
        self.init_ui()
        self.refresh_data()

    def init_ui(self):
        main_layout = QVBoxLayout()
        title_label = QLabel("Proveedores")
        title_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        toolbar_layout = QHBoxLayout()

        # Filtro tipo material
        self.filter_combo = QComboBox()
        self.filter_combo.addItem("Todos")
        # Se puede poblar dinámicamente si tienes tipos únicos de material
        self.filter_combo.addItem("Tipo: Materia Prima")
        self.filter_combo.addItem("Tipo: Servicios")
        self.filter_combo.addItem("Tipo: Otro")
        self.filter_combo.currentIndexChanged.connect(self.apply_filters)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Buscar por nombre, contacto, email, teléfono...")
        self.search_input.textChanged.connect(self.apply_filters)

        add_btn = QPushButton("Agregar proveedor")
        add_btn.setIcon(QIcon("resources/icons/add.png"))
        add_btn.clicked.connect(self.add_supplier)

        toolbar_layout.addWidget(QLabel("Filtro:"))
        toolbar_layout.addWidget(self.filter_combo)
        toolbar_layout.addStretch()
        toolbar_layout.addWidget(self.search_input)
        toolbar_layout.addWidget(add_btn)

        # Tabla de proveedores ajustada
        self.suppliers_table = QTableWidget(0, 6)
        self.suppliers_table.setHorizontalHeaderLabels([
            "Nombre", "Contacto", "Teléfono", "Email", "Tipo Material", "Acciones"
        ])
        self.suppliers_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.suppliers_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.suppliers_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.suppliers_table.setAlternatingRowColors(True)
        self.suppliers_table.cellDoubleClicked.connect(self.open_details)

        main_layout.addWidget(title_label)
        main_layout.addLayout(toolbar_layout)
        main_layout.addWidget(self.suppliers_table)
        self.setLayout(main_layout)

    def refresh_data(self):
        try:
            raw_suppliers = self.api_client.get_suppliers()
            self.last_suppliers = [
                Supplier(
                    supplier_id=s.get('id') or s.get('id_proveedor'),
                    name=s.get('name') or s.get('nombre'),
                    contact=s.get('contact') or s.get('contacto'),
                    phone=s.get('phone') or s.get('telefono'),
                    email=s.get('email'),
                    material_type=s.get('material_type') or s.get('tipo_material')
                )
                for s in raw_suppliers
            ]
            self.apply_filters()
        except Exception as e:
            self.show_error(f"Error al obtener proveedores: {e}")
            self.last_suppliers = []
            self.apply_filters()

    def apply_filters(self):
        tipo_filtro = self.filter_combo.currentText()
        buscar = self.search_input.text().strip().lower()
        filtered = self.last_suppliers
        # Filtro por tipo de material
        if "Tipo: " in tipo_filtro:
            buscado = tipo_filtro.replace("Tipo: ", "")
            filtered = [s for s in filtered if buscado.lower() in (s.material_type or '').lower()]
        # Búsqueda libre
        if buscar:
            filtered = [
                s for s in filtered
                if buscar in (s.name or "").lower()
                or buscar in (s.contact or "").lower()
                or buscar in (s.email or "").lower()
                or buscar in (s.phone or "").lower()
                or buscar in (s.material_type or "").lower()
            ]
        self.populate_table(filtered)

    def populate_table(self, suppliers):
        self.suppliers_table.setRowCount(0)
        for row, sup in enumerate(suppliers):
            self.suppliers_table.insertRow(row)
            self.suppliers_table.setItem(row, 0, QTableWidgetItem(sup.name or ""))
            self.suppliers_table.setItem(row, 1, QTableWidgetItem(sup.contact or ""))
            self.suppliers_table.setItem(row, 2, QTableWidgetItem(sup.phone or ""))
            self.suppliers_table.setItem(row, 3, QTableWidgetItem(sup.email or ""))
            self.suppliers_table.setItem(row, 4, QTableWidgetItem(sup.material_type or ""))

            # Botones de acción
            actions_layout = QHBoxLayout()
            actions_layout.setContentsMargins(0,0,0,0)
            actions_layout.setSpacing(5)

            view_btn = QPushButton(); view_btn.setIcon(QIcon("resources/icons/view.png"))
            view_btn.setToolTip("Ver detalles"); view_btn.setFixedSize(30,30)
            view_btn.clicked.connect(lambda checked, x=sup: self.view_supplier(x))

            edit_btn = QPushButton(); edit_btn.setIcon(QIcon("resources/icons/edit.png"))
            edit_btn.setToolTip("Editar"); edit_btn.setFixedSize(30,30)
            edit_btn.clicked.connect(lambda checked, x=sup: self.edit_supplier(x))

            delete_btn = QPushButton(); delete_btn.setIcon(QIcon("resources/icons/delete.png"))
            delete_btn.setToolTip("Eliminar"); delete_btn.setFixedSize(30,30)
            delete_btn.clicked.connect(lambda checked, x=sup: self.delete_supplier(x))

            actions_layout.addWidget(view_btn)
            actions_layout.addWidget(edit_btn)
            actions_layout.addWidget(delete_btn)
            actions_widget = QWidget(); actions_widget.setLayout(actions_layout)
            self.suppliers_table.setCellWidget(row, 5, actions_widget)

    ## Métodos para acciones
    def add_supplier(self):
        dlg = SuppliersFormView(api_client=self.api_client, on_save_callback=self.refresh_data)
        dlg.setWindowTitle("Agregar Proveedor")
        dlg.setWindowModality(Qt.WindowModality.ApplicationModal)
        dlg.exec()  # <- CORRECTO

    def view_supplier(self, supplier):
        # Muestra información detallada del proveedor
        QMessageBox.information(
            self, "Detalles del proveedor",
            f"Nombre: {supplier.name}\n"
            f"Contacto: {supplier.contact}\n"
            f"Teléfono: {supplier.phone}\n"
            f"Email: {supplier.email}\n"
            f"Tipo Material: {supplier.material_type or ''}"
        )

    def edit_supplier(self, supplier):
        dlg = SuppliersFormView(
            api_client=self.api_client,
            on_save_callback=self.refresh_data,
            supplier=supplier
        )
        dlg.setWindowTitle("Editar Proveedor")
        dlg.setWindowModality(Qt.WindowModality.ApplicationModal)
        dlg.exec()  # <- CORRECTO

    def delete_supplier(self, supplier):
        answer = QMessageBox.question(
            self, "Eliminar proveedor",
            f"¿Eliminar proveedor {supplier.name}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if answer == QMessageBox.StandardButton.Yes:
            try:
                self.api_client.delete_supplier(supplier.supplier_id)
                self.refresh_data()
            except Exception as e:
                self.show_error(f"No se pudo eliminar el proveedor: {e}")

    def open_details(self, row, column):
        # Esta función puede abrir el detalle visual o llamar a tu callback si lo tienes definido
        filtered_suppliers = []
        tipo_filtro = self.filter_combo.currentText()
        buscar = self.search_input.text().strip().lower()
        filtered_suppliers = self.last_suppliers
        if "Tipo: " in tipo_filtro:
            buscado = tipo_filtro.replace("Tipo: ", "")
            filtered_suppliers = [s for s in filtered_suppliers if buscado.lower() in (s.material_type or '').lower()]
        if buscar:
            filtered_suppliers = [
                s for s in filtered_suppliers
                if buscar in (s.name or "").lower()
                or buscar in (s.contact or "").lower()
                or buscar in (s.email or "").lower()
                or buscar in (s.phone or "").lower()
                or buscar in (s.material_type or "").lower()
            ]
        if self.details_callback:
            self.details_callback(filtered_suppliers[row])
        else:
            self.view_supplier(filtered_suppliers[row])

    def show_error(self, msg):
        QMessageBox.critical(self, "Error", msg)
