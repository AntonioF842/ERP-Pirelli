from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLabel, QLineEdit, QSpinBox, QDialogButtonBox, QMessageBox
)

class MaterialForm(QDialog):
    def __init__(self, api_client, material_id=None):
        super().__init__()
        from utils.theme import Theme
        Theme.apply_window_light_theme(self)
        self.api_client = api_client
        self.material_id = material_id
        self.setWindowTitle("Nuevo Material" if not self.material_id else "Editar Material")
        self.setMinimumSize(400, 270)
        self.init_ui()
        if self.material_id:
            self.load_material()

    def init_ui(self):
        layout = QVBoxLayout()
        title = QLabel(self.windowTitle())
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title)

        form = QFormLayout()
        self.nombre_input = QLineEdit()
        self.descripcion_input = QLineEdit()
        self.unidad_input = QLineEdit()
        self.stock_min_input = QSpinBox(); self.stock_min_input.setMaximum(999999)
        self.stock_max_input = QSpinBox(); self.stock_max_input.setMaximum(999999)

        form.addRow("Nombre:", self.nombre_input)
        form.addRow("Descripción:", self.descripcion_input)
        form.addRow("Unidad medida:", self.unidad_input)
        form.addRow("Stock mínimo:", self.stock_min_input)
        form.addRow("Stock máximo:", self.stock_max_input)

        layout.addLayout(form)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.save)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        self.setLayout(layout)

    def load_material(self):
        mat = self.api_client.get_material(self.material_id)
        self.nombre_input.setText(mat.get("nombre", ""))
        self.descripcion_input.setText(mat.get("descripcion", ""))
        self.unidad_input.setText(mat.get("unidad_medida", ""))
        self.stock_min_input.setValue(mat.get("stock_minimo", 0))
        self.stock_max_input.setValue(mat.get("stock_maximo", 0))

    def save(self):
        nombre = self.nombre_input.text().strip()
        unidad = self.unidad_input.text().strip()

        if not nombre:
            QMessageBox.warning(self, "Validación", "El nombre del material es obligatorio.")
            self.nombre_input.setFocus()
            return
        if not unidad:
            QMessageBox.warning(self, "Validación", "La unidad de medida es obligatoria.")
            self.unidad_input.setFocus()
            return

        data = {
            "nombre": nombre,
            "descripcion": self.descripcion_input.text().strip(),
            "unidad_medida": unidad,
            "stock_minimo": self.stock_min_input.value(),
            "stock_maximo": self.stock_max_input.value(),
        }

        try:
            if self.material_id:
                resp = self.api_client.update_material(self.material_id, data)
                if not resp:
                    raise Exception("Error del backend al actualizar el material.")
            else:
                resp = self.api_client.create_material(data)
                if not resp:
                    raise Exception("Error del backend al crear el material.")
            self.accept()
        except Exception as e:
            msg = str(e)
            if hasattr(e, 'response') and e.response is not None:
                try:
                    backend_msg = e.response.json().get("error") or e.response.text
                except Exception:
                    backend_msg = e.response.text
                msg += f"\n\nDetalle backend: {backend_msg}"
            QMessageBox.critical(self, "Error", msg)
