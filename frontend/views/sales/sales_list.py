from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem, QPushButton,
    QLabel, QComboBox, QLineEdit, QHeaderView, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon

class SalesListView(QWidget):
    def __init__(self, api_client):
        super().__init__()
        from utils.theme import Theme
        Theme.apply_window_light_theme(self)
        self.api_client = api_client
        self.init_ui()
        self.last_sales = []
        self.refresh_data()

    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        title_label = QLabel("Gestión de Ventas")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold;")

        toolbar_layout = QHBoxLayout()

        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["Todos", "Pendiente", "Completada", "Cancelada"])

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Buscar por cliente o ID...")
        self.search_input.textChanged.connect(self.apply_filters)

        search_btn = QPushButton("Buscar")
        search_btn.clicked.connect(self.apply_filters)

        self.add_btn = QPushButton("Nueva Venta")
        self.add_btn.setIcon(QIcon("resources/icons/add.png"))
        self.add_btn.clicked.connect(self.add_sale)

        self.refresh_btn = QPushButton("Actualizar")
        self.refresh_btn.setIcon(QIcon("resources/icons/refresh.png"))
        self.refresh_btn.clicked.connect(self.refresh_data)

        toolbar_layout.addWidget(QLabel("Filtrar por estado:"))
        toolbar_layout.addWidget(self.filter_combo)
        toolbar_layout.addWidget(self.search_input)
        toolbar_layout.addWidget(search_btn)
        toolbar_layout.addStretch()
        toolbar_layout.addWidget(self.add_btn)
        toolbar_layout.addWidget(self.refresh_btn)

        self.sales_table = QTableWidget()
        self.sales_table.setColumnCount(7)
        self.sales_table.setHorizontalHeaderLabels([
            "ID", "Cliente", "Fecha", "Total", "Estado", "Creado por", "Acciones"
        ])
        self.sales_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.sales_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.sales_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.sales_table.setAlternatingRowColors(True)

        main_layout.addWidget(title_label)
        main_layout.addLayout(toolbar_layout)
        main_layout.addWidget(self.sales_table)

        self.setLayout(main_layout)

    def refresh_data(self):
        try:
            # Solicitar datos de ventas
            sales_data = self.api_client.get_sales()
            self.last_sales = sales_data if isinstance(sales_data, list) else sales_data.get('ventas', [])
            self.apply_filters()
        except Exception as e:
            self.show_error(str(e))

    def apply_filters(self):
        estado = self.filter_combo.currentText().lower()
        buscar = self.search_input.text().strip().lower()
        filtered = self.last_sales
        if estado != "todos":
            filtered = [v for v in filtered if v.get('estado', '').lower() == estado]
        if buscar:
            filtered = [
                v for v in filtered
                if buscar in str(v.get("id_venta", "")).lower() or
                   buscar in (v.get("cliente_nombre", "") or "").lower()
            ]
        self.populate_table(filtered)

    def populate_table(self, ventas):
        self.sales_table.setRowCount(0)
        for row, sale in enumerate(ventas):
            self.sales_table.insertRow(row)
            self.sales_table.setItem(row, 0, QTableWidgetItem(str(sale.get("id_venta", ""))))
            self.sales_table.setItem(row, 1, QTableWidgetItem(sale.get("cliente_nombre", "N/A")))
            self.sales_table.setItem(row, 2, QTableWidgetItem(sale.get("fecha", "")))
            total = float(sale.get("total", 0) or 0)
            total_item = QTableWidgetItem(f"${total:,.2f}")
            total_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.sales_table.setItem(row, 3, total_item)
            estado = sale.get("estado", "").capitalize()
            estado_item = QTableWidgetItem(estado)
            self.sales_table.setItem(row, 4, estado_item)
            self.sales_table.setItem(row, 5, QTableWidgetItem(sale.get("usuario_nombre", "N/A")))

            # Botones de acción
            actions_layout = QHBoxLayout()
            actions_layout.setContentsMargins(0,0,0,0)
            actions_layout.setSpacing(5)
            view_btn = QPushButton(); view_btn.setIcon(QIcon("resources/icons/view.png"))
            view_btn.setToolTip("Ver detalles"); view_btn.setFixedSize(30,30)
            view_btn.clicked.connect(lambda checked, s=sale: self.view_sale(s))
            edit_btn = QPushButton(); edit_btn.setIcon(QIcon("resources/icons/edit.png"))
            edit_btn.setToolTip("Editar"); edit_btn.setFixedSize(30,30)
            edit_btn.clicked.connect(lambda checked, s=sale: self.edit_sale(s))
            delete_btn = QPushButton(); delete_btn.setIcon(QIcon("resources/icons/delete.png"))
            delete_btn.setToolTip("Eliminar"); delete_btn.setFixedSize(30,30)
            delete_btn.clicked.connect(lambda checked, s=sale: self.delete_sale(s))
            actions_layout.addWidget(view_btn); actions_layout.addWidget(edit_btn); actions_layout.addWidget(delete_btn)

            if estado in ["Completada", "Cancelada"]:
                edit_btn.setEnabled(False)
                delete_btn.setEnabled(False)

            actions_widget = QWidget(); actions_widget.setLayout(actions_layout)
            self.sales_table.setCellWidget(row, 6, actions_widget)

    def add_sale(self):
        from .sales_form import SalesForm
        dlg = SalesForm(self.api_client)
        if dlg.exec():
            self.refresh_data()

    def view_sale(self, sale):
        from .sales_detail import SalesDetailView
        dlg = SalesDetailView(self.api_client, sale_id=sale.get("id_venta"))
        dlg.exec()

    def edit_sale(self, sale):
        from .sales_form import SalesForm
        dlg = SalesForm(self.api_client, sale_id=sale.get("id_venta"))
        if dlg.exec():
            self.refresh_data()

    def delete_sale(self, sale):
        answer = QMessageBox.question(
            self, "Eliminar venta",
            f"¿Eliminar la venta #{sale.get('id_venta')} de {sale.get('cliente_nombre', 'Cliente')}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if answer == QMessageBox.StandardButton.Yes:
            try:
                self.api_client.delete_sale(sale.get("id_venta"))
                self.refresh_data()
            except Exception as e:
                self.show_error(f"No se pudo eliminar la venta: {e}")

    def show_error(self, msg):
        QMessageBox.critical(self, "Error", msg)