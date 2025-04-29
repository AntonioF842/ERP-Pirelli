from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton

class SuppliersDetailsView(QWidget):
    def __init__(self, on_edit_callback=None):
        super().__init__()
        self.on_edit_callback = on_edit_callback
        self.supplier = None
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        self.name_label = QLabel()
        self.contact_label = QLabel()
        self.phone_label = QLabel()
        self.email_label = QLabel()
        layout.addWidget(self.name_label)
        layout.addWidget(self.contact_label)
        layout.addWidget(self.phone_label)
        layout.addWidget(self.email_label)
        self.edit_btn = QPushButton("Editar")
        self.edit_btn.clicked.connect(self.edit)
        layout.addWidget(self.edit_btn)
        self.setLayout(layout)

    def load_supplier(self, supplier):
        self.supplier = supplier
        self.name_label.setText(f"Nombre: {supplier.name}")
        self.contact_label.setText(f"Contacto: {supplier.contact}")
        self.phone_label.setText(f"Teléfono: {supplier.phone}")
        self.email_label.setText(f"Email: {supplier.email}")

    def edit(self):
        # Llama la función de edit_supplier desde la lista, PASANDO supplier
        if self.on_edit_callback and self.supplier:
            self.on_edit_callback(self.supplier)
