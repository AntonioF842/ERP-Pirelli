from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem,
    QHeaderView, QComboBox, QLineEdit, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon

class InventoryListView(QWidget):
    def __init__(self, api_client):
        super().__init__()
        self.api_client = api_client
        self.last_inventory = []
        self.init_ui()
        self.refresh_data()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        
        # Título principal
        title_label = QLabel("Inventario")
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; margin-bottom: 10px;")
        main_layout.addWidget(title_label)

        # Toolbar de filtros y búsqueda
        toolbar_layout = QHBoxLayout()
        
        status_label = QLabel("Estado:")
        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["Todos", "Stock bajo", "Stock suficiente"])
        self.filter_combo.currentIndexChanged.connect(self.apply_filters)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Buscar por producto, lote o ubicación...")
        self.search_input.textChanged.connect(self.apply_filters)

        add_btn = QPushButton()
        add_btn.setText("Agregar")
        add_btn.setIcon(QIcon("resources/icons/add.png"))
        add_btn.setFixedSize(100, 36)
        add_btn.clicked.connect(self.add_inventory)

        toolbar_layout.addWidget(status_label)
        toolbar_layout.addWidget(self.filter_combo)
        toolbar_layout.addStretch()
        toolbar_layout.addWidget(self.search_input)
        toolbar_layout.addWidget(add_btn)

        main_layout.addLayout(toolbar_layout)

        # Tabla de inventario
        self.inventory_table = QTableWidget(0, 7)
        self.inventory_table.setHorizontalHeaderLabels([
            "ID", "Material", "Cantidad", "Lote", "Fecha ingreso", "Ubicación", "Acciones"
        ])
        self.inventory_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.inventory_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.inventory_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.inventory_table.setAlternatingRowColors(True)
        self.inventory_table.verticalHeader().setVisible(False)

        main_layout.addWidget(self.inventory_table)

    def refresh_data(self):
        try:
            inventory_data = self.api_client.get_inventory()
            self.last_inventory = inventory_data if isinstance(inventory_data, list) else inventory_data.get('inventario', [])
            self.apply_filters()
        except Exception as e:
            self.show_error(str(e))

    def apply_filters(self):
        filtro = self.filter_combo.currentText().lower()
        buscar = self.search_input.text().strip().lower()
        filtered = self.last_inventory

        if filtro == "stock bajo":
            filtered = [i for i in filtered if i.get("cantidad", 0) < 10]
        elif filtro == "stock suficiente":
            filtered = [i for i in filtered if i.get("cantidad", 0) >= 10]

        if buscar:
            filtered = [
                i for i in filtered
                if buscar in str(i.get("id_inventario", "")).lower()
                or buscar in (i.get("material_name", "") or "").lower()
                or buscar in (i.get("lote", "") or "").lower()
                or buscar in (i.get("ubicacion", "") or "").lower()
            ]
        self.populate_table(filtered)

    def populate_table(self, inventory_items):
        self.inventory_table.setRowCount(0)

        for row, inv in enumerate(inventory_items):
            self.inventory_table.insertRow(row)

            self.inventory_table.setItem(row, 0, QTableWidgetItem(str(inv.get("id_inventario", ""))))
            self.inventory_table.setItem(row, 1, QTableWidgetItem(inv.get("material_name", "")))
            self.inventory_table.setItem(row, 2, QTableWidgetItem(str(inv.get("cantidad", ""))))
            self.inventory_table.setItem(row, 3, QTableWidgetItem(inv.get("lote", "")))
            self.inventory_table.setItem(row, 4, QTableWidgetItem(inv.get("fecha_ingreso", "")))
            self.inventory_table.setItem(row, 5, QTableWidgetItem(inv.get("ubicacion", "")))

            # Layout de acciones
            actions_layout = QHBoxLayout()
            actions_layout.setContentsMargins(0, 0, 0, 0)
            actions_layout.setSpacing(5)

            view_btn = QPushButton()
            view_btn.setIcon(QIcon("resources/icons/view.png"))
            view_btn.setFixedSize(30, 30)
            view_btn.setToolTip("Ver detalles")
            view_btn.clicked.connect(lambda checked, x=inv: self.view_inventory(x))

            edit_btn = QPushButton()
            edit_btn.setIcon(QIcon("resources/icons/edit.png"))
            edit_btn.setFixedSize(30, 30)
            edit_btn.setToolTip("Editar")
            edit_btn.clicked.connect(lambda checked, x=inv: self.edit_inventory(x))

            delete_btn = QPushButton()
            delete_btn.setIcon(QIcon("resources/icons/delete.png"))
            delete_btn.setFixedSize(30, 30)
            delete_btn.setToolTip("Eliminar")
            delete_btn.clicked.connect(lambda checked, x=inv: self.delete_inventory(x))

            actions_layout.addWidget(view_btn)
            actions_layout.addWidget(edit_btn)
            actions_layout.addWidget(delete_btn)

            actions_widget = QWidget()
            actions_widget.setLayout(actions_layout)
            self.inventory_table.setCellWidget(row, 6, actions_widget)

    def add_inventory(self):
        from .inventory_form import InventoryForm
        dlg = InventoryForm(self.api_client)
        if dlg.exec():
            self.refresh_data()

    def view_inventory(self, inv):
        from .inventory_detail import InventoryDetailView
        dlg = InventoryDetailView(self.api_client, inventory_id=inv.get("id_inventario"))
        dlg.exec()

    def edit_inventory(self, inv):
        from .inventory_form import InventoryForm
        dlg = InventoryForm(self.api_client, inventory_id=inv.get("id_inventario"))
        if dlg.exec():
            self.refresh_data()

    def delete_inventory(self, inv):
        answer = QMessageBox.question(
            self,
            "Eliminar registro",
            f"¿Eliminar lote #{inv.get('id_inventario')} de {inv.get('material_name', '')}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if answer == QMessageBox.StandardButton.Yes:
            try:
                self.api_client.delete_inventory(inv.get("id_inventario"))
                self.refresh_data()
            except Exception as e:
                self.show_error(f"No se pudo eliminar el registro: {e}")

    def show_error(self, msg):
        QMessageBox.critical(self, "Error", msg)
