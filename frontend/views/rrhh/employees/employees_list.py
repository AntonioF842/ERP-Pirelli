from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem,
    QHeaderView, QComboBox, QLineEdit, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon

class EmployeesListView(QWidget):
    def __init__(self, api_client):
        super().__init__()
        self.api_client = api_client
        self.last_employees = []
        self.init_ui()
        self.refresh_data()

    def init_ui(self):
        main_layout = QVBoxLayout()
        title_label = QLabel("Empleados")
        title_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        toolbar_layout = QHBoxLayout()

        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["Todos", "Activos", "Inactivos"])
        self.filter_combo.currentIndexChanged.connect(self.apply_filters)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Buscar por nombre o apellidos...")
        self.search_input.textChanged.connect(self.apply_filters)

        add_btn = QPushButton("Agregar empleado")
        add_btn.setIcon(QIcon("resources/icons/add.png"))
        add_btn.clicked.connect(self.add_employee)

        toolbar_layout.addWidget(QLabel("Estado:"))
        toolbar_layout.addWidget(self.filter_combo)
        toolbar_layout.addStretch()
        toolbar_layout.addWidget(self.search_input)
        toolbar_layout.addWidget(add_btn)

        self.employees_table = QTableWidget(0, 7)
        self.employees_table.setHorizontalHeaderLabels([
            "ID", "Nombre", "Apellidos", "Área", "Puesto", "Activo", "Acciones"
        ])
        self.employees_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.employees_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.employees_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.employees_table.setAlternatingRowColors(True)

        main_layout.addWidget(title_label)
        main_layout.addLayout(toolbar_layout)
        main_layout.addWidget(self.employees_table)
        self.setLayout(main_layout)

    def refresh_data(self):
        try:
            employees_data = self.api_client.get_employees()
            self.last_employees = employees_data if isinstance(employees_data, list) else employees_data.get('empleados', [])
            self.apply_filters()
        except Exception as e:
            self.show_error(str(e))

    def apply_filters(self):
        estado = self.filter_combo.currentText().lower()
        buscar = self.search_input.text().strip().lower()
        filtered = self.last_employees
        if estado != "todos":
            activo = True if estado == "activos" else False
            filtered = [e for e in filtered if e.get('activo', True) == activo]
        if buscar:
            filtered = [
                e for e in filtered
                if buscar in (e.get("nombre", "") or "").lower() or
                   buscar in (e.get("apellidos", "") or "").lower()
            ]
        self.populate_table(filtered)

    def populate_table(self, empleados):
        self.employees_table.setRowCount(0)
        for row, emp in enumerate(empleados):
            self.employees_table.insertRow(row)
            self.employees_table.setItem(row, 0, QTableWidgetItem(str(emp.get("id_empleado", ""))))
            self.employees_table.setItem(row, 1, QTableWidgetItem(emp.get("nombre", "")))
            self.employees_table.setItem(row, 2, QTableWidgetItem(emp.get("apellidos", "")))
            self.employees_table.setItem(row, 3, QTableWidgetItem(emp.get("area_name", "N/A")))
            self.employees_table.setItem(row, 4, QTableWidgetItem(emp.get("puesto", "")))
            activo = "Sí" if emp.get("activo", True) else "No"
            activo_item = QTableWidgetItem(activo)
            self.employees_table.setItem(row, 5, activo_item)

            # Botones de acción
            actions_layout = QHBoxLayout()
            actions_layout.setContentsMargins(0,0,0,0)
            actions_layout.setSpacing(5)
            view_btn = QPushButton(); view_btn.setIcon(QIcon("resources/icons/view.png"))
            view_btn.setToolTip("Ver detalles"); view_btn.setFixedSize(30,30)
            view_btn.clicked.connect(lambda checked, e=emp: self.view_employee(e))
            edit_btn = QPushButton(); edit_btn.setIcon(QIcon("resources/icons/edit.png"))
            edit_btn.setToolTip("Editar"); edit_btn.setFixedSize(30,30)
            edit_btn.clicked.connect(lambda checked, e=emp: self.edit_employee(e))
            delete_btn = QPushButton(); delete_btn.setIcon(QIcon("resources/icons/delete.png"))
            delete_btn.setToolTip("Eliminar"); delete_btn.setFixedSize(30,30)
            delete_btn.clicked.connect(lambda checked, e=emp: self.delete_employee(e))
            actions_layout.addWidget(view_btn); actions_layout.addWidget(edit_btn); actions_layout.addWidget(delete_btn)

            if not emp.get("activo", True):
                edit_btn.setEnabled(False)
                delete_btn.setEnabled(False)

            actions_widget = QWidget(); actions_widget.setLayout(actions_layout)
            self.employees_table.setCellWidget(row, 6, actions_widget)

    def add_employee(self):
        from .employees_form import EmployeesForm
        dlg = EmployeesForm(self.api_client)
        if dlg.exec():
            self.refresh_data()

    def view_employee(self, emp):
        from .employees_detail import EmployeesDetailView
        dlg = EmployeesDetailView(self.api_client, employee_id=emp.get("id_empleado"))
        dlg.exec()

    def edit_employee(self, emp):
        from .employees_form import EmployeesForm
        dlg = EmployeesForm(self.api_client, employee_id=emp.get("id_empleado"))
        if dlg.exec():
            self.refresh_data()

    def delete_employee(self, emp):
        answer = QMessageBox.question(
            self, "Eliminar empleado",
            f"¿Eliminar al empleado #{emp.get('id_empleado')} {emp.get('nombre', '')} {emp.get('apellidos', '')}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if answer == QMessageBox.StandardButton.Yes:
            try:
                self.api_client.delete_employee(emp.get("id_empleado"))
                self.refresh_data()
            except Exception as e:
                self.show_error(f"No se pudo eliminar el empleado: {e}")

    def show_error(self, msg):
        QMessageBox.critical(self, "Error", msg)