from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QFormLayout, QPushButton
from PyQt6.QtGui import QFont

class MaterialDetailView(QDialog):
    def __init__(self, api_client, material_id=None):
        super().__init__()
        from utils.theme import Theme
        Theme.apply_window_light_theme(self)
        self.api_client = api_client
        self.material_id = material_id
        self.setMinimumSize(400, 250)
        self.setWindowTitle(f"Detalle Material #{material_id}")
        self.material = {}
        self.init_ui()
        if self.material_id:
            self.material = self.api_client.get_material(self.material_id)
            self.update_view()

    def init_ui(self):
        self.layout = QVBoxLayout(self)
        title = QLabel(self.windowTitle())
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        self.layout.addWidget(title)

        self.form = QFormLayout()
        self.lbl_nombre = QLabel("N/A")
        self.lbl_descripcion = QLabel("N/A")
        self.lbl_unidad = QLabel("N/A")
        self.lbl_stock_minimo = QLabel("N/A")
        self.lbl_stock_maximo = QLabel("N/A")

        self.form.addRow("Nombre:", self.lbl_nombre)
        self.form.addRow("Descripción:", self.lbl_descripcion)
        self.form.addRow("Unidad medida:", self.lbl_unidad)
        self.form.addRow("Stock mínimo:", self.lbl_stock_minimo)
        self.form.addRow("Stock máximo:", self.lbl_stock_maximo)

        self.layout.addLayout(self.form)

        close_btn = QPushButton("Cerrar")
        close_btn.clicked.connect(self.accept)
        self.layout.addWidget(close_btn)

    def update_view(self):
        m = self.material
        self.lbl_nombre.setText(m.get("nombre", ""))
        self.lbl_descripcion.setText(m.get("descripcion", ""))
        self.lbl_unidad.setText(m.get("unidad_medida", ""))
        self.lbl_stock_minimo.setText(str(m.get("stock_minimo", "")))
        self.lbl_stock_maximo.setText(str(m.get("stock_maximo", "")))
