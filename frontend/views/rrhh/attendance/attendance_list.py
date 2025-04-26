from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem,
    QHeaderView, QComboBox, QLineEdit, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon

class AttendanceListView(QWidget):
    def __init__(self, api_client):
        super().__init__()
        self.api_client = api_client
        self.last_records = []
        self.init_ui()
        self.refresh_data()

    def init_ui(self):
        main_layout = QVBoxLayout()
        title_label = QLabel("Asistencia")
        title_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        toolbar_layout = QHBoxLayout()

        self.estado_combo = QComboBox()
        self.estado_combo.addItems(["Todos", "Presente", "Ausente", "Tardanza"])
        self.estado_combo.currentIndexChanged.connect(self.apply_filters)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Buscar por nombre de empleado...")
        self.search_input.textChanged.connect(self.apply_filters)

        add_btn = QPushButton("Agregar asistencia")
        add_btn.setIcon(QIcon("resources/icons/add.png"))
        add_btn.clicked.connect(self.add_attendance)

        toolbar_layout.addWidget(QLabel("Estado:"))
        toolbar_layout.addWidget(self.estado_combo)
        toolbar_layout.addStretch()
        toolbar_layout.addWidget(self.search_input)
        toolbar_layout.addWidget(add_btn)

        self.table = QTableWidget(0, 7)
        self.table.setHorizontalHeaderLabels([
            "ID", "Empleado", "Fecha", "Entrada", "Salida", "Estado", "Acciones"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setAlternatingRowColors(True)

        main_layout.addWidget(title_label)
        main_layout.addLayout(toolbar_layout)
        main_layout.addWidget(self.table)
        self.setLayout(main_layout)

    def refresh_data(self):
        try:
            records = self.api_client.get_attendance()
            self.last_records = records if isinstance(records, list) else []
            self.apply_filters()
        except Exception as e:
            self.show_error(str(e))

    def apply_filters(self):
        estado = self.estado_combo.currentText().lower()
        buscar = self.search_input.text().strip().lower()
        filtered = self.last_records
        if estado != "todos":
            filtered = [r for r in filtered if r.get('estado', '').lower() == estado]
        if buscar:
            filtered = [
                r for r in filtered
                if buscar in (r.get("empleado_name", "") or "").lower()
            ]
        self.populate_table(filtered)

    def populate_table(self, records):
        self.table.setRowCount(0)
        for row, rec in enumerate(records):
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(str(rec.get("id_asistencia", ""))))
            self.table.setItem(row, 1, QTableWidgetItem(rec.get("empleado_name", "")))
            self.table.setItem(row, 2, QTableWidgetItem(rec.get("fecha", "")))
            self.table.setItem(row, 3, QTableWidgetItem(rec.get("hora_entrada", "")))
            self.table.setItem(row, 4, QTableWidgetItem(rec.get("hora_salida", "")))
            self.table.setItem(row, 5, QTableWidgetItem(rec.get("estado", "")))

            # Botones de acción
            actions_layout = QHBoxLayout()
            actions_layout.setContentsMargins(0,0,0,0)
            actions_layout.setSpacing(5)
            view_btn = QPushButton(); view_btn.setIcon(QIcon("resources/icons/view.png"))
            view_btn.setToolTip("Ver detalles"); view_btn.setFixedSize(30,30)
            view_btn.clicked.connect(lambda checked, r=rec: self.view_attendance(r))
            edit_btn = QPushButton(); edit_btn.setIcon(QIcon("resources/icons/edit.png"))
            edit_btn.setToolTip("Editar"); edit_btn.setFixedSize(30,30)
            edit_btn.clicked.connect(lambda checked, r=rec: self.edit_attendance(r))
            delete_btn = QPushButton(); delete_btn.setIcon(QIcon("resources/icons/delete.png"))
            delete_btn.setToolTip("Eliminar"); delete_btn.setFixedSize(30,30)
            delete_btn.clicked.connect(lambda checked, r=rec: self.delete_attendance(r))
            actions_layout.addWidget(view_btn); actions_layout.addWidget(edit_btn); actions_layout.addWidget(delete_btn)
            actions_widget = QWidget(); actions_widget.setLayout(actions_layout)
            self.table.setCellWidget(row, 6, actions_widget)

    def add_attendance(self):
        from .attendance_form import AttendanceForm
        dlg = AttendanceForm(self.api_client)
        if dlg.exec():
            self.refresh_data()

    def view_attendance(self, rec):
        from .attendance_detail import AttendanceDetailView
        dlg = AttendanceDetailView(self.api_client, attendance_id=rec.get("id_asistencia"))
        dlg.exec()

    def edit_attendance(self, rec):
        from .attendance_form import AttendanceForm
        dlg = AttendanceForm(self.api_client, attendance_id=rec.get("id_asistencia"))
        if dlg.exec():
            self.refresh_data()

    def delete_attendance(self, rec):
        answer = QMessageBox.question(
            self, "Eliminar asistencia",
            f"¿Eliminar el registro #{rec.get('id_asistencia')} de {rec.get('empleado_name', '')}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if answer == QMessageBox.StandardButton.Yes:
            try:
                self.api_client.delete_attendance(rec.get("id_asistencia"))
                self.refresh_data()
            except Exception as e:
                self.show_error(f"No se pudo eliminar el registro: {e}")

    def show_error(self, msg):
        QMessageBox.critical(self, "Error", msg)