from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QHBoxLayout, QPushButton
from PyQt6.QtCore import Qt

class EmployeesDetailView(QDialog):
    def __init__(self, api_client, employee_id):
        super().__init__()
        self.api_client = api_client
        self.employee_id = employee_id
        self.setWindowTitle("Detalle de empleado")
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        try:
            emp = self.api_client.get_employee(self.employee_id)
            layout.addWidget(QLabel(f"<b>ID:</b> {emp.get('id_empleado', '')}"))
            layout.addWidget(QLabel(f"<b>Nombre:</b> {emp.get('nombre', '')}"))
            layout.addWidget(QLabel(f"<b>Apellidos:</b> {emp.get('apellidos', '')}"))
            layout.addWidget(QLabel(f"<b>Área:</b> {emp.get('area_name', 'N/A')}"))
            layout.addWidget(QLabel(f"<b>Puesto:</b> {emp.get('puesto', '')}"))
            layout.addWidget(QLabel(f"<b>Salario:</b> ${emp.get('salario', 0):,.2f}"))
            layout.addWidget(QLabel(f"<b>Fecha de contratación:</b> {emp.get('fecha_contratacion', '')}"))
            layout.addWidget(QLabel(f"<b>Activo:</b> {'Sí' if emp.get('activo', True) else 'No'}"))
        except Exception as e:
            layout.addWidget(QLabel(f"<b>Error al cargar empleado:</b> {e}"))

        btn_layout = QHBoxLayout()
        close_btn = QPushButton("Cerrar")
        close_btn.clicked.connect(self.accept)
        btn_layout.addStretch()
        btn_layout.addWidget(close_btn)
        layout.addLayout(btn_layout)
        self.setLayout(layout)