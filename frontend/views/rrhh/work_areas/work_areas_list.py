from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem, 
    QHeaderView, QLineEdit, QComboBox, QMessageBox, QDialog, QFormLayout, QDialogButtonBox
)
from PyQt6.QtGui import QIcon
from controllers.work_areas_controller import WorkAreasController

class WorkAreasListView(QWidget):
    """
    Vista en PyQt para listar las áreas de trabajo en una tabla con filtros y acciones.
    """
    def __init__(self, api_client=None, parent=None):
        super().__init__(parent)
        self.api_client = api_client
        self.controller = WorkAreasController(self.api_client) if self.api_client else WorkAreasController()
        self.last_areas = []
        self.init_ui()
        self.refresh_data()
        
    def init_ui(self):
        main_layout = QVBoxLayout()
        
        # Título
        title_label = QLabel("Áreas de Trabajo")
        title_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        
        # Barra de herramientas con filtros y búsqueda
        toolbar_layout = QHBoxLayout()
        
        # Filtro por responsable
        self.responsable_combo = QComboBox()
        self.responsable_combo.addItem("Todos")
        self.responsable_combo.currentIndexChanged.connect(self.apply_filters)
        
        # Buscador
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Buscar por nombre o descripción...")
        self.search_input.textChanged.connect(self.apply_filters)
        
        # Botón para agregar área
        add_btn = QPushButton("Agregar área")
        add_btn.setIcon(QIcon("resources/icons/add.png"))
        add_btn.clicked.connect(self.add_area_dialog)
        
        toolbar_layout.addWidget(QLabel("Responsable:"))
        toolbar_layout.addWidget(self.responsable_combo)
        toolbar_layout.addStretch()
        toolbar_layout.addWidget(self.search_input)
        toolbar_layout.addWidget(add_btn)
        
        # Tabla de áreas
        self.areas_table = QTableWidget(0, 5)
        self.areas_table.setHorizontalHeaderLabels([
            "ID", "Nombre Área", "Descripción", "Responsable", "Acciones"
        ])
        self.areas_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.areas_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.areas_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.areas_table.setAlternatingRowColors(True)
        
        main_layout.addWidget(title_label)
        main_layout.addLayout(toolbar_layout)
        main_layout.addWidget(self.areas_table)
        self.setLayout(main_layout)

    def refresh_data(self):
        try:
            areas_data = self.controller.fetch_work_areas()
            # Si areas_data es una lista, adapta los IDs
            if isinstance(areas_data, list):
                # Asegura que todas las áreas tengan una clave 'id'.
                for area in areas_data:
                    if "id" not in area:
                        # Si viene como "id_area", "pk", etc. adapta aquí
                        if "id_area" in area:
                            area["id"] = area["id_area"]
                        elif "pk" in area:
                            area["id"] = area["pk"]
                        # Puedes agregar más variantes según tu backend
                self.last_areas = areas_data
            else:
                # Si viene como dict con clave 'areas'
                areas_list = areas_data.get('areas', [])
                for area in areas_list:
                    if "id" not in area:
                        if "id_area" in area:
                            area["id"] = area["id_area"]
                        elif "pk" in area:
                            area["id"] = area["pk"]
                self.last_areas = areas_list
            
            self.update_responsables_filter()
            self.apply_filters()
        except Exception as e:
            self.show_error(str(e))
            
    def update_responsables_filter(self):
        responsables = {"Todos"}
        for area in self.last_areas:
            # Usa responsable_name si existe, sino id
            nombre = area.get("responsable_name") or str(area.get("responsable", "---"))
            if nombre: responsables.add(nombre)
        
        self.responsable_combo.blockSignals(True)
        prev = self.responsable_combo.currentText()
        self.responsable_combo.clear()
        self.responsable_combo.addItems(sorted(list(responsables)))
        idx = self.responsable_combo.findText(prev)
        if idx >= 0: self.responsable_combo.setCurrentIndex(idx)
        self.responsable_combo.blockSignals(False)
        
    def apply_filters(self):
        responsable = self.responsable_combo.currentText()
        buscar = self.search_input.text().strip().lower()
        filtered = self.last_areas
        
        if responsable != "Todos":
            filtered = [a for a in filtered if (a.get("responsable_name") == responsable or 
                                               str(a.get("responsable", "")) == responsable)]
        if buscar:
            filtered = [
                a for a in filtered
                if buscar in (a.get("nombre_area", "") or "").lower() or
                   buscar in (a.get("descripcion", "") or "").lower()
            ]
            
        self.populate_table(filtered)
        
    def populate_table(self, areas):
        self.areas_table.setRowCount(0)
        for row, area in enumerate(areas):
            self.areas_table.insertRow(row)
            self.areas_table.setItem(row, 0, QTableWidgetItem(str(area.get("id", ""))))
            self.areas_table.setItem(row, 1, QTableWidgetItem(area.get("nombre_area", "")))
            self.areas_table.setItem(row, 2, QTableWidgetItem(area.get("descripcion", "")))
            responsable = area.get("responsable_name") or str(area.get("responsable", ""))
            self.areas_table.setItem(row, 3, QTableWidgetItem(responsable if responsable else "—"))
            
            # Botones de acción (ver, editar, eliminar)
            actions_layout = QHBoxLayout()
            actions_layout.setContentsMargins(0, 0, 0, 0)
            actions_layout.setSpacing(5)
            
            view_btn = QPushButton()
            view_btn.setIcon(QIcon("resources/icons/view.png"))
            view_btn.setToolTip("Ver detalles")
            view_btn.setFixedSize(30, 30)
            view_btn.clicked.connect(lambda checked, a=area: self.view_area(a))
            
            edit_btn = QPushButton()
            edit_btn.setIcon(QIcon("resources/icons/edit.png"))
            edit_btn.setToolTip("Editar")
            edit_btn.setFixedSize(30, 30)
            edit_btn.clicked.connect(lambda checked, a=area: self.edit_area_dialog(a))
            
            delete_btn = QPushButton()
            delete_btn.setIcon(QIcon("resources/icons/delete.png"))
            delete_btn.setToolTip("Eliminar")
            delete_btn.setFixedSize(30, 30)
            delete_btn.clicked.connect(lambda checked, a=area: self.delete_area(a))
            
            actions_layout.addWidget(view_btn)
            actions_layout.addWidget(edit_btn)
            actions_layout.addWidget(delete_btn)
            actions_widget = QWidget()
            actions_widget.setLayout(actions_layout)
            self.areas_table.setCellWidget(row, 4, actions_widget)

    def add_area_dialog(self):
        # Formulario básico embebido
        class AreaFormDialog(QDialog):
            def __init__(self):
                super().__init__()
                self.setWindowTitle("Agregar área de trabajo")
                self.layout = QFormLayout(self)
                self.nombre = QLineEdit()
                self.descripcion = QLineEdit()
                self.responsable = QLineEdit()
                self.layout.addRow("Nombre área:", self.nombre)
                self.layout.addRow("Descripción:", self.descripcion)
                self.layout.addRow("Responsable (ID):", self.responsable)
                self.buttons = QDialogButtonBox(
                    QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
                )
                self.buttons.accepted.connect(self.accept)
                self.buttons.rejected.connect(self.reject)
                self.layout.addWidget(self.buttons)

            def get_data(self):
                return {
                    "nombre_area": self.nombre.text().strip(),
                    "descripcion": self.descripcion.text().strip(),
                    "responsable": self.responsable.text().strip()
                }
                
        dialog = AreaFormDialog()
        if dialog.exec():
            data = dialog.get_data()
            if not data["nombre_area"]:
                QMessageBox.warning(self, "Error", "El campo nombre es obligatorio.")
                return
            msg = self.controller.add_work_area(data)
            QMessageBox.information(self, "Área agregada", 
                                   "Área creada con éxito." if msg else "Error al crear área.")
            self.refresh_data()

    def view_area(self, area):
        QMessageBox.information(self, "Detalles del área",
            f"Nombre: {area.get('nombre_area', '')}\n"
            f"Descripción: {area.get('descripcion', '')}\n"
            f"Responsable: {area.get('responsable_name', '') or area.get('responsable', '')}"
        )

    def edit_area_dialog(self, area):
        class AreaEditDialog(QDialog):
            def __init__(self, area):
                super().__init__()
                self.setWindowTitle("Editar área de trabajo")
                self.layout = QFormLayout(self)
                self.nombre = QLineEdit()
                self.nombre.setText(area.get("nombre_area", ""))
                self.descripcion = QLineEdit()
                self.descripcion.setText(area.get("descripcion", ""))
                self.responsable = QLineEdit()
                self.responsable.setText(str(area.get("responsable", "")))
                self.layout.addRow("Nombre área:", self.nombre)
                self.layout.addRow("Descripción:", self.descripcion)
                self.layout.addRow("Responsable (ID):", self.responsable)
                self.buttons = QDialogButtonBox(
                    QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
                )
                self.buttons.accepted.connect(self.accept)
                self.buttons.rejected.connect(self.reject)
                self.layout.addWidget(self.buttons)
                
            def get_data(self):
                return {
                    "nombre_area": self.nombre.text().strip(),
                    "descripcion": self.descripcion.text().strip(),
                    "responsable": self.responsable.text().strip()
                }
                
        print(f"DEBUG: Editando área con ID: {area.get('id')}, Nombre: {area.get('nombre_area')}")
        if not area.get('id'):
            QMessageBox.critical(self, "Error", "ID de área inválido.")
            return
            
        dialog = AreaEditDialog(area)
        if dialog.exec():
            data = dialog.get_data()
            area_id = area.get("id")
            if not data["nombre_area"]:
                QMessageBox.warning(self, "Error", "El campo nombre es obligatorio.")
                return
            msg = self.controller.edit_work_area(area_id, data)
            QMessageBox.information(self, "Área editada", 
                                   "Área actualizada." if msg else "Error al editar área.")
            self.refresh_data()

    def delete_area(self, area):
        area_id = area.get("id")
        nombre = area.get("nombre_area")
        print(f"DEBUG: Eliminando área con ID: {area_id}, Nombre: {nombre}")  # Línea de debug
        if not area_id:
            QMessageBox.critical(self, "Error", "ID de área inválido.")
            return
        confirm = QMessageBox.question(
            self, "Eliminar área",
            f"¿Eliminar el área \"{nombre}\" (ID {area_id})?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if confirm == QMessageBox.StandardButton.Yes:
            ok = self.controller.remove_work_area(area_id)
            QMessageBox.information(self, "Área eliminada", 
                                   "Área eliminada." if ok else "Error al eliminar área.")
            self.refresh_data()

    def show_error(self, msg):
        QMessageBox.critical(self, "Error", msg)

# Para pruebas independientes
if __name__ == '__main__':
    import sys
    from PyQt6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    window = WorkAreasListView()
    window.setWindowTitle("Lista de Áreas de Trabajo")
    window.resize(950, 500)
    window.show()
    sys.exit(app.exec())
