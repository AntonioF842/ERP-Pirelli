# users_detail.py
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QDialogButtonBox

class UserDetailDialog(QDialog):
    def __init__(self, user_data, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Detalles de Usuario")
        self.setModal(True)
        self.resize(400, 300)
        
        layout = QVBoxLayout()
        
        details = [
            ("ID", str(user_data.get('id_usuario', ''))),
            ("Nombre", user_data.get('nombre', '')),
            ("Email", user_data.get('email', '')),
            ("Rol", user_data.get('rol', '')),
            ("Fecha Registro", user_data.get('fecha_registro', ''))
        ]
        
        for label, value in details:
            layout.addWidget(QLabel(f"<b>{label}:</b> {value}"))
        
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        buttons.accepted.connect(self.accept)
        layout.addWidget(buttons)
        
        self.setLayout(layout)