from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QComboBox, QDateEdit, QTimeEdit, QMessageBox
)
from PyQt6.QtCore import QDate, QTime
from datetime import datetime

class AttendanceForm(QDialog):
    def __init__(self, api_client, attendance_id=None):
        super().__init__()
        self.api_client = api_client
        self.attendance_id = attendance_id
        self.setWindowTitle("Editar asistencia" if attendance_id else "Agregar asistencia")
        self.init_ui()
        if attendance_id:
            self.load_attendance()

    def init_ui(self):
        layout = QVBoxLayout()
        self.empleado_combo = QComboBox()
        self.fecha_input = QDateEdit()
        self.fecha_input.setCalendarPopup(True)
        self.hora_entrada_input = QTimeEdit()
        self.hora_salida_input = QTimeEdit()
        self.estado_combo = QComboBox()
        self.estado_combo.addItems(["presente", "ausente", "tardanza"])

        # Cargar empleados
        self.empleados = self.api_client.get_employees()
        self.empleado_combo.addItem("Seleccione empleado...", None)
        for emp in self.empleados:
            self.empleado_combo.addItem(f"{emp['nombre']} {emp['apellidos']}", emp["id_empleado"])

        layout.addWidget(QLabel("Empleado:"))
        layout.addWidget(self.empleado_combo)
        layout.addWidget(QLabel("Fecha:"))
        layout.addWidget(self.fecha_input)
        layout.addWidget(QLabel("Hora de entrada:"))
        layout.addWidget(self.hora_entrada_input)
        layout.addWidget(QLabel("Hora de salida:"))
        layout.addWidget(self.hora_salida_input)
        layout.addWidget(QLabel("Estado:"))
        layout.addWidget(self.estado_combo)

        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Guardar")
        save_btn.clicked.connect(self.save)
        cancel_btn = QPushButton("Cancelar")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def load_attendance(self):
        att = self.api_client.get_attendance_by_id(self.attendance_id)
        if att:
            idx = self.empleado_combo.findData(att.get("id_empleado"))
            self.empleado_combo.setCurrentIndex(idx if idx != -1 else 0)
            if att.get("fecha"):
                dt = datetime.strptime(att["fecha"], "%Y-%m-%d")
                self.fecha_input.setDate(QDate(dt.year, dt.month, dt.day))
            if att.get("hora_entrada"):
                t = datetime.strptime(att["hora_entrada"], "%H:%M:%S").time()
                self.hora_entrada_input.setTime(QTime(t.hour, t.minute, t.second))
            if att.get("hora_salida"):
                t = datetime.strptime(att["hora_salida"], "%H:%M:%S").time()
                self.hora_salida_input.setTime(QTime(t.hour, t.minute, t.second))
            idx_estado = self.estado_combo.findText(att.get("estado", "presente"))
            self.estado_combo.setCurrentIndex(idx_estado if idx_estado != -1 else 0)

    def save(self):
        id_empleado = self.empleado_combo.currentData()
        fecha = self.fecha_input.date().toString("yyyy-MM-dd")
        hora_entrada = self.hora_entrada_input.time().toString("HH:mm:ss")
        hora_salida = self.hora_salida_input.time().toString("HH:mm:ss")
        estado = self.estado_combo.currentText()

        if not id_empleado:
            QMessageBox.warning(self, "Validación", "Debe seleccionar un empleado.")
            return

        data = {
            "id_empleado": id_empleado,
            "fecha": fecha,
            "hora_entrada": hora_entrada,
            "hora_salida": hora_salida,
            "estado": estado
        }
        try:
            if self.attendance_id:
                self.api_client.update_attendance(self.attendance_id, data)
            else:
                self.api_client.create_attendance(data)
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo guardar el registro: {e}")