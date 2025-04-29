from PyQt6.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QLineEdit, QPushButton, QMessageBox, QHBoxLayout, QComboBox

# Centralize allowed material types here:
MATERIAL_TYPES = ['caucho', 'acero', 'quimicos', 'otros']

class SuppliersFormView(QDialog):
    def __init__(self, api_client, on_save_callback=None, supplier=None):
        super().__init__()
        self.api_client = api_client
        self.on_save_callback = on_save_callback
        self.supplier = supplier
        self.init_ui()
        if self.supplier:
            self.load_supplier(self.supplier)

    def init_ui(self):
        layout = QVBoxLayout()
        form = QFormLayout()
        self.name_input = QLineEdit()
        self.contact_input = QLineEdit()
        self.phone_input = QLineEdit()
        self.email_input = QLineEdit()
        # Use QComboBox instead of QLineEdit for material_type
        self.material_type_input = QComboBox()
        self.material_type_input.addItems(MATERIAL_TYPES)
        form.addRow("Nombre:", self.name_input)
        form.addRow("Contacto:", self.contact_input)
        form.addRow("Teléfono:", self.phone_input)
        form.addRow("Email:", self.email_input)
        form.addRow("Tipo de material:", self.material_type_input)
        layout.addLayout(form)
        
        # Button layout with Save and Cancel
        button_layout = QHBoxLayout()
        self.save_btn = QPushButton("Guardar")
        self.save_btn.clicked.connect(self.save)
        self.cancel_btn = QPushButton("Cancelar")
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.save_btn)
        button_layout.addWidget(self.cancel_btn)
        layout.addLayout(button_layout)
        self.setLayout(layout)

    def load_supplier(self, supplier):
        self.name_input.setText(supplier.name)
        self.contact_input.setText(supplier.contact)
        self.phone_input.setText(supplier.phone)
        self.email_input.setText(supplier.email)
        # Set combobox to correct material type or default if not in list
        if hasattr(supplier, 'material_type') and supplier.material_type:
            idx = self.material_type_input.findText(supplier.material_type)
            if idx >= 0:
                self.material_type_input.setCurrentIndex(idx)
            else:
                self.material_type_input.setCurrentIndex(0)
        else:
            self.material_type_input.setCurrentIndex(0)
        self.supplier = supplier

    def save(self):
        name = self.name_input.text()
        contact = self.contact_input.text()
        phone = self.phone_input.text()
        email = self.email_input.text()
        material_type = self.material_type_input.currentText()
        if not all([name, contact, phone, email, material_type]):
            QMessageBox.warning(self, "Error", "Completa todos los campos")
            return
        try:
            if self.supplier is None:
                self.api_client.create_supplier({
                    "name": name,
                    "contact": contact,
                    "phone": phone,
                    "email": email,
                    "material_type": material_type,
                })
                message = "Proveedor creado correctamente"
            else:
                self.api_client.update_supplier(
                    self.supplier.supplier_id,
                    {
                        "name": name,
                        "contact": contact,
                        "phone": phone,
                        "email": email,
                        "material_type": material_type,
                    }
                )
                message = "Proveedor actualizado correctamente"
            QMessageBox.information(self, "Éxito", message)
            if self.on_save_callback:
                self.on_save_callback()
            self.accept()  # Use accept() for dialog result
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo guardar: {e}")
