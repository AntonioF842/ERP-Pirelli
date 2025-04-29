from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem,
    QHeaderView, QComboBox, QLineEdit, QMessageBox
)
from PyQt6.QtGui import QIcon

class MaterialListView(QWidget):
    def __init__(self, api_client):
        super().__init__()
        self.api_client = api_client
        self.last_materials = []
        self.init_ui()
        self.refresh_data()

    def init_ui(self):
        main_layout = QVBoxLayout()
        title_label = QLabel("Materiales")
        title_label.setStyleSheet("font-size: 24px; font-weight: bold;")

        toolbar_layout = QHBoxLayout()

        self.unit_filter = QComboBox()
        self.unit_filter.addItem("Todas las unidades")
        self.unit_filter.currentIndexChanged.connect(self.apply_filters)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Buscar por nombre o descripción...")
        self.search_input.textChanged.connect(self.apply_filters)

        add_btn = QPushButton("Agregar material")
        add_btn.setIcon(QIcon("resources/icons/add.png"))
        add_btn.clicked.connect(self.add_material)

        toolbar_layout.addWidget(QLabel("Unidad:"))
        toolbar_layout.addWidget(self.unit_filter)
        toolbar_layout.addStretch()
        toolbar_layout.addWidget(self.search_input)
        toolbar_layout.addWidget(add_btn)

        self.materials_table = QTableWidget(0, 7)
        self.materials_table.setHorizontalHeaderLabels([
            "ID", "Nombre", "Descripción", "Unidad", "Stock Min", "Stock Max", "Acciones"
        ])
        self.materials_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.materials_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.materials_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.materials_table.setAlternatingRowColors(True)

        main_layout.addWidget(title_label)
        main_layout.addLayout(toolbar_layout)
        main_layout.addWidget(self.materials_table)
        self.setLayout(main_layout)

    def refresh_data(self):
        try:
            materials_data = self.api_client.get_materials()
            self.last_materials = materials_data if isinstance(materials_data, list) else materials_data.get('materiales', [])
            self.update_unit_filter_options()
            self.apply_filters()
        except Exception as e:
            self.show_error(str(e))

    def update_unit_filter_options(self):
        units = sorted(set(m.get("unidad_medida", "") for m in self.last_materials if m.get("unidad_medida")))
        current = self.unit_filter.currentText()
        self.unit_filter.blockSignals(True)
        self.unit_filter.clear()
        self.unit_filter.addItem("Todas las unidades")
        for u in units:
            self.unit_filter.addItem(u)
        idx = self.unit_filter.findText(current)
        if idx >= 0:
            self.unit_filter.setCurrentIndex(idx)
        self.unit_filter.blockSignals(False)

    def apply_filters(self):
        unidad = self.unit_filter.currentText()
        buscar = self.search_input.text().strip().lower()
        filtered = self.last_materials

        if unidad and unidad != "Todas las unidades":
            filtered = [m for m in filtered if (m.get("unidad_medida") or "") == unidad]
        if buscar:
            filtered = [m for m in filtered if buscar in m.get("nombre", "").lower() or buscar in m.get("descripcion", "").lower()]
        self.populate_table(filtered)

    def populate_table(self, materiales):
        self.materials_table.setRowCount(0)
        for row, m in enumerate(materiales):
            self.materials_table.insertRow(row)
            self.materials_table.setItem(row, 0, QTableWidgetItem(str(m.get("id_material", ""))))
            self.materials_table.setItem(row, 1, QTableWidgetItem(m.get("nombre", "")))
            self.materials_table.setItem(row, 2, QTableWidgetItem(m.get("descripcion", "")))
            self.materials_table.setItem(row, 3, QTableWidgetItem(m.get("unidad_medida", "")))
            self.materials_table.setItem(row, 4, QTableWidgetItem(str(m.get("stock_minimo", ""))))
            self.materials_table.setItem(row, 5, QTableWidgetItem(str(m.get("stock_maximo", ""))))

            actions_layout = QHBoxLayout()
            actions_layout.setContentsMargins(0, 0, 0, 0)
            actions_layout.setSpacing(5)

            view_btn = QPushButton()
            view_btn.setIcon(QIcon("resources/icons/view.png"))
            view_btn.setToolTip("Ver detalles")
            view_btn.setFixedSize(30, 30)
            view_btn.clicked.connect(lambda checked, x=m: self.ver_material(x))

            edit_btn = QPushButton()
            edit_btn.setIcon(QIcon("resources/icons/edit.png"))
            edit_btn.setToolTip("Editar")
            edit_btn.setFixedSize(30, 30)
            edit_btn.clicked.connect(lambda checked, x=m: self.editar_material(x))

            delete_btn = QPushButton()
            delete_btn.setIcon(QIcon("resources/icons/delete.png"))
            delete_btn.setToolTip("Eliminar")
            delete_btn.setFixedSize(30, 30)
            delete_btn.clicked.connect(lambda checked, x=m: self.eliminar_material(x))

            actions_layout.addWidget(view_btn)
            actions_layout.addWidget(edit_btn)
            actions_layout.addWidget(delete_btn)

            actions_widget = QWidget()
            actions_widget.setLayout(actions_layout)
            self.materials_table.setCellWidget(row, 6, actions_widget)

    def add_material(self):
        from .material_form import MaterialForm
        dlg = MaterialForm(self.api_client)
        if dlg.exec():
            self.refresh_data()

    def ver_material(self, mat):
        from .material_detail import MaterialDetailView
        dlg = MaterialDetailView(self.api_client, material_id=mat.get("id_material"))
        dlg.exec()

    def editar_material(self, mat):
        from .material_form import MaterialForm
        dlg = MaterialForm(self.api_client, material_id=mat.get("id_material"))
        if dlg.exec():
            self.refresh_data()

    def eliminar_material(self, mat):
        resp = QMessageBox.question(
            self, "Eliminar material",
            f"¿Eliminar material '{mat.get('nombre', '')}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if resp == QMessageBox.StandardButton.Yes:
            try:
                self.api_client.delete_material(mat.get("id_material"))
                self.refresh_data()
            except Exception as e:
                self.show_error(f"No se pudo eliminar el material: {e}")

    def show_error(self, msg):
        QMessageBox.critical(self, "Error", msg)
