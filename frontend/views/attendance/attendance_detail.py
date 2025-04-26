from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QHBoxLayout, QPushButton
from PyQt6.QtCore import Qt

class AttendanceDetailView(QDialog):
    def __init__(self, api_client, attendance_id):
        super().__init__()
        self.api_client = api_client
        self.attendance_id = attendance_id
        self.setWindowTitle("Detalle de asistencia")
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        try:
            att = self.api_client.get_attendance_by_id(self.attendance_id)
            layout.addWidget(QLabel(f"<b>ID:</b> {att.get('id_asistencia', '')}"))
            layout.addWidget(QLabel(f"<b>Empleado:</b> {att.get('empleado_name', '')}"))
            layout.addWidget(QLabel(f"<b>Fecha:</b> {att.get('fecha', '')}"))
            layout.addWidget(QLabel(f"<b>Hora de entrada:</b> {att.get('hora_entrada', '')}"))
            layout.addWidget(QLabel(f"<b>Hora de salida:</b> {att.get('hora_salida', '')}"))
            layout.addWidget(QLabel(f"<b>Estado:</b> {att.get('estado', '')}"))
        except Exception as e:
            layout.addWidget(QLabel(f"<b>Error al cargar asistencia:</b> {e}"))

        btn_layout = QHBoxLayout()
        close_btn = QPushButton("Cerrar")
        close_btn.clicked.connect(self.accept)
        btn_layout.addStretch()
        btn_layout.addWidget(close_btn)
        layout.addLayout(btn_layout)
        self.setLayout(layout)