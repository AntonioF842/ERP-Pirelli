from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem,
    QHeaderView, QComboBox, QLineEdit, QMessageBox
)
from PyQt6.QtGui import QIcon
from controllers.payroll_controller import PayrollController

class PayrollListView(QWidget):
    """
    Vista en PyQt para listar los registros de nómina en una tabla con filtros y acciones.
    """
    def __init__(self, api_client, parent=None):
        super().__init__(parent)
        self.api_client = api_client
        self.controller = PayrollController(api_client)
        self.last_payrolls = []
        self.init_ui()
        self.refresh_data()

    def init_ui(self):
        """Configura la interfaz de usuario avanzada con filtros y acciones"""
        self.setWindowTitle("Listado de Nóminas")
        
        # Layout principal
        main_layout = QVBoxLayout(self)
        
        # Título
        title_label = QLabel("Nóminas")
        title_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        
        # Barra de herramientas con filtros y botones
        toolbar_layout = QHBoxLayout()

        # Filtro por periodo
        self.period_filter = QComboBox()
        self.period_filter.addItem("Todos los periodos")
        self.period_filter.currentIndexChanged.connect(self.apply_filters)

        # Búsqueda
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Buscar por empleado o periodo...")
        self.search_input.textChanged.connect(self.apply_filters)

        # Botón para agregar nómina
        add_btn = QPushButton("Agregar nómina")
        add_btn.setIcon(QIcon("resources/icons/add.png"))
        add_btn.clicked.connect(self.add_payroll)

        # Organizar la barra de herramientas
        toolbar_layout.addWidget(QLabel("Periodo:"))
        toolbar_layout.addWidget(self.period_filter)
        toolbar_layout.addStretch()
        toolbar_layout.addWidget(self.search_input)
        toolbar_layout.addWidget(add_btn)

        # Tabla de nóminas
        self.payroll_table = QTableWidget(0, 9)  # 9 columnas incluyendo acciones
        self.payroll_table.setHorizontalHeaderLabels([
            "ID", "Empleado", "Periodo", "Fecha Pago", "Salario Bruto",
            "Deducciones", "Bonos", "Salario Neto", "Acciones"
        ])
        
        # Configuración de la tabla
        self.payroll_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.payroll_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.payroll_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.payroll_table.setAlternatingRowColors(True)

        # Agregar widgets al layout principal
        main_layout.addWidget(title_label)
        main_layout.addLayout(toolbar_layout)
        main_layout.addWidget(self.payroll_table)
        self.setLayout(main_layout)

    def refresh_data(self):
        """Actualiza los datos de la tabla y los filtros"""
        try:
            payrolls_data = self.controller.fetch_payrolls()
            self.last_payrolls = payrolls_data if isinstance(payrolls_data, list) else payrolls_data.get('nominas', [])
            self.update_period_filter()
            self.apply_filters()
        except Exception as e:
            self.show_error(str(e))

    def update_period_filter(self):
        """Actualiza las opciones del filtro de periodos basado en los datos disponibles"""
        periodos = {"Todos los periodos"}
        for p in self.last_payrolls:
            periodo = p.get("periodo")
            if periodo:
                periodos.add(periodo)
        
        self.period_filter.blockSignals(True)
        prev = self.period_filter.currentText()
        self.period_filter.clear()
        self.period_filter.addItems(sorted(list(periodos)))
        idx = self.period_filter.findText(prev)
        if idx >= 0:
            self.period_filter.setCurrentIndex(idx)
        self.period_filter.blockSignals(False)

    def apply_filters(self):
        """Aplica los filtros seleccionados a los datos de la tabla"""
        periodo = self.period_filter.currentText()
        buscar = self.search_input.text().strip().lower()
        filtered = self.last_payrolls
        
        if periodo != "Todos los periodos":
            filtered = [p for p in filtered if p.get("periodo") == periodo]
        
        if buscar:
            filtered = [
                p for p in filtered
                if buscar in str(p.get("empleado_name", "")).lower() or
                   buscar in str(p.get("periodo", "")).lower()
            ]
        
        self.populate_table(filtered)

    def populate_table(self, payrolls):
        """Llena la tabla con los datos de nómina filtrados"""
        self.payroll_table.setRowCount(0)
        
        for row, pr in enumerate(payrolls):
            self.payroll_table.insertRow(row)
            self.payroll_table.setItem(row, 0, QTableWidgetItem(str(pr.get("id_nomina", ""))))
            self.payroll_table.setItem(row, 1, QTableWidgetItem(str(pr.get("empleado_name", ""))))
            self.payroll_table.setItem(row, 2, QTableWidgetItem(pr.get("periodo", "")))
            self.payroll_table.setItem(row, 3, QTableWidgetItem(pr.get("fecha_pago", "")))
            self.payroll_table.setItem(row, 4, QTableWidgetItem(str(pr.get("salario_bruto", ""))))
            self.payroll_table.setItem(row, 5, QTableWidgetItem(str(pr.get("deducciones", ""))))
            self.payroll_table.setItem(row, 6, QTableWidgetItem(str(pr.get("bonos", ""))))
            self.payroll_table.setItem(row, 7, QTableWidgetItem(str(pr.get("salario_neto", ""))))

            # Botones de acción
            actions_layout = QHBoxLayout()
            actions_layout.setContentsMargins(0, 0, 0, 0)
            actions_layout.setSpacing(5)
            
            view_btn = QPushButton()
            view_btn.setIcon(QIcon("resources/icons/view.png"))
            view_btn.setToolTip("Ver detalles")
            view_btn.setFixedSize(30, 30)
            view_btn.clicked.connect(lambda checked, p=pr: self.view_payroll(p))
            
            edit_btn = QPushButton()
            edit_btn.setIcon(QIcon("resources/icons/edit.png"))
            edit_btn.setToolTip("Editar")
            edit_btn.setFixedSize(30, 30)
            edit_btn.clicked.connect(lambda checked, p=pr: self.edit_payroll(p))
            
            delete_btn = QPushButton()
            delete_btn.setIcon(QIcon("resources/icons/delete.png"))
            delete_btn.setToolTip("Eliminar")
            delete_btn.setFixedSize(30, 30)
            delete_btn.clicked.connect(lambda checked, p=pr: self.delete_payroll(p))
            
            actions_layout.addWidget(view_btn)
            actions_layout.addWidget(edit_btn)
            actions_layout.addWidget(delete_btn)
            
            actions_widget = QWidget()
            actions_widget.setLayout(actions_layout)
            self.payroll_table.setCellWidget(row, 8, actions_widget)

    def add_payroll(self):
        """Abre el formulario para agregar una nueva nómina"""
        try:
            from .payroll_form import PayrollForm
            dlg = PayrollForm(self.api_client)
            if dlg.exec():
                self.refresh_data()
        except Exception as e:
            self.show_error(f"Error al abrir el formulario: {e}")

    def view_payroll(self, pr):
        """Muestra los detalles de una nómina seleccionada"""
        try:
            from .payroll_detail import PayrollDetailView
            dlg = PayrollDetailView(self.api_client, payroll_id=pr.get("id_nomina"))
            dlg.exec()
        except Exception as e:
            self.show_error(f"Error al mostrar detalles: {e}")

    def edit_payroll(self, pr):
        """Abre el formulario para editar una nómina existente"""
        try:
            from .payroll_form import PayrollForm
            dlg = PayrollForm(self.api_client, payroll_id=pr.get("id_nomina"))
            if dlg.exec():
                self.refresh_data()
        except Exception as e:
            self.show_error(f"Error al editar: {e}")

    def delete_payroll(self, pr):
        """Elimina una nómina después de confirmar con el usuario"""
        answer = QMessageBox.question(
            self, "Eliminar nómina",
            f"¿Eliminar la nómina #{pr.get('id_nomina')} del empleado {pr.get('empleado_name', '')} ({pr.get('periodo', '')})?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if answer == QMessageBox.StandardButton.Yes:
            try:
                # Usamos remove_payroll para mantener consistencia con el nombre del método en el controlador
                self.controller.remove_payroll(pr.get("id_nomina"))
                self.refresh_data()
            except Exception as e:
                self.show_error(f"No se pudo eliminar la nómina: {e}")

    def show_error(self, msg):
        """Muestra un mensaje de error en un cuadro de diálogo"""
        QMessageBox.critical(self, "Error", msg)

# Ejemplo de ejecución
if __name__ == '__main__':
    import sys
    from PyQt6.QtWidgets import QApplication
    from utils.api_client import ApiClient
    
    api_client = ApiClient()
    app = QApplication(sys.argv)
    window = PayrollListView(api_client)
    window.resize(800, 600)
    window.show()
    sys.exit(app.exec())
