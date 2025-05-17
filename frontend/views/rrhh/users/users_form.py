# users_form.py
from PyQt6.QtWidgets import (QDialog, QFormLayout, QLineEdit, 
                            QComboBox, QDialogButtonBox)

class UserFormDialog(QDialog):
    def __init__(self, user=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Agregar Usuario" if user is None else "Editar Usuario")
        self.layout = QFormLayout(self)
        
        self.name = QLineEdit()
        self.email = QLineEdit()
        self.role = QComboBox()
        self.role.addItems(["admin", "supervisor", "empleado"])
        self.password = QLineEdit()
        self.password.setPlaceholderText("Dejar vacío para no cambiar")
        self.password.setEchoMode(QLineEdit.EchoMode.Password)
        
        if user is not None:
            self.name.setText(user.get('nombre', ''))
            self.email.setText(user.get('email', ''))
            self.role.setCurrentText(user.get('rol', ''))
            self.password.setPlaceholderText("Dejar vacío para mantener contraseña actual")
        
        self.layout.addRow("Nombre:", self.name)
        self.layout.addRow("Email:", self.email)
        self.layout.addRow("Rol:", self.role)
        self.layout.addRow("Contraseña:", self.password)
        
        self.buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        self.layout.addWidget(self.buttons)

    def get_data(self):
        data = {
            "nombre": self.name.text().strip(),
            "email": self.email.text().strip(),
            "rol": self.role.currentText()
        }
        password = self.password.text().strip()
        if password:
            data["password"] = password
        return data