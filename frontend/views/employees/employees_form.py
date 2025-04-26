from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QComboBox, QDateEdit, QCheckBox, QMessageBox
)
from PyQt6.QtCore import QDate
from datetime import datetime

class EmployeesForm(QDialog):
    def __init__(self, api_client, employee_id=None):
        super().__init__()
        self.api_client = api_client
        self.employee_id = employee_id
        self.setWindowTitle("Editar empleado" if employee_id else "Agregar empleado")
        self.init_ui()
        if employee_id:
            self.load_employee()

    def init_ui(self):
        layout = QVBoxLayout()
        self.nombre_input = QLineEdit()
        self.apellidos_input = QLineEdit()
        self.area_combo = QComboBox()
        self.puesto_input = QLineEdit()
        self.salario_input = QLineEdit()
        self.fecha_contratacion_input = QDateEdit()
        self.fecha_contratacion_input.setCalendarPopup(True)
        self.activo_checkbox = QCheckBox("Activo")
        self.activo_checkbox.setChecked(True)

        # Cargar áreas de trabajo
        self.areas = self.api_client.get_areas_trabajo()
        self.area_combo.addItem("Seleccione área...", None)
        for area in self.areas:
            self.area_combo.addItem(area["nombre_area"], area["id_area"])

        layout.addWidget(QLabel("Nombre:"))
        layout.addWidget(self.nombre_input)
        layout.addWidget(QLabel("Apellidos:"))
        layout.addWidget(self.apellidos_input)
        layout.addWidget(QLabel("Área de trabajo:"))
        layout.addWidget(self.area_combo)
        layout.addWidget(QLabel("Puesto:"))
        layout.addWidget(self.puesto_input)
        layout.addWidget(QLabel("Salario:"))
        layout.addWidget(self.salario_input)
        layout.addWidget(QLabel("Fecha de contratación:"))
        layout.addWidget(self.fecha_contratacion_input)
        layout.addWidget(self.activo_checkbox)

        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Guardar")
        save_btn.clicked.connect(self.save)
        cancel_btn = QPushButton("Cancelar")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def load_employee(self):
        try:
            emp = self.api_client.get_employee(self.employee_id)
            self.nombre_input.setText(emp.get("nombre", ""))
            self.apellidos_input.setText(emp.get("apellidos", ""))
            area_idx = self.area_combo.findData(emp.get("id_area"))
            self.area_combo.setCurrentIndex(area_idx if area_idx != -1 else 0)
            self.puesto_input.setText(emp.get("puesto", ""))
            self.salario_input.setText(str(emp.get("salario", "")))
            if emp.get("fecha_contratacion"):
                dt = datetime.strptime(emp["fecha_contratacion"], "%Y-%m-%d")
                self.fecha_contratacion_input.setDate(QDate(dt.year, dt.month, dt.day))
            self.activo_checkbox.setChecked(emp.get("activo", True))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo cargar el empleado: {e}")
            self.reject()

    def save(self):
        nombre = self.nombre_input.text().strip()
        apellidos = self.apellidos_input.text().strip()
        id_area = self.area_combo.currentData()
        puesto = self.puesto_input.text().strip()
        salario = self.salario_input.text().strip()
        fecha_contratacion = self.fecha_contratacion_input.date().toString("yyyy-MM-dd")
        activo = self.activo_checkbox.isChecked()

        if not nombre or not apellidos or not id_area:
            QMessageBox.warning(self, "Validación", "Nombre, apellidos y área son obligatorios.")
            return

        data = {
            "nombre": nombre,
            "apellidos": apellidos,
            "id_area": id_area,
            "puesto": puesto,
            "salario": float(salario) if salario else None,
            "fecha_contratacion": fecha_contratacion,
            "activo": activo
        }
        try:
            if self.employee_id:
                self.api_client.update_employee(self.employee_id, data)
            else:
                self.api_client.create_employee(data)
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo guardar el empleado: {e}")