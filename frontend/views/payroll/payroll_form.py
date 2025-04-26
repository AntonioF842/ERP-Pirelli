from PyQt6.QtWidgets import (
    QDialog, QFormLayout, QLineEdit, QComboBox, QDialogButtonBox, QMessageBox, QDateEdit
)
from PyQt6.QtCore import QDate
from controllers.payroll_controller import PayrollController

class PayrollForm(QDialog):
    def __init__(self, api_client, payroll_id=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Formulario de Nómina")
        self.controller = PayrollController(api_client)
        self.api_client = api_client
        self.payroll_id = payroll_id
        self.layout = QFormLayout(self)
        
        # Campos de formulario
        self.employee_id_edit = QLineEdit()
        self.period_edit = QLineEdit()
        self.amount_edit = QLineEdit()
        self.date_edit = QDateEdit()
        self.date_edit.setDisplayFormat("yyyy-MM-dd")
        self.date_edit.setDate(QDate.currentDate())
        self.deducciones_edit = QLineEdit()
        self.bonos_edit = QLineEdit()
        self.status_combo = QComboBox()
        self.status_combo.addItems(["Pendiente", "Pagado", "Cancelado"])
        
        self.layout.addRow("ID Empleado:", self.employee_id_edit)
        self.layout.addRow("Periodo (YYYY-MM):", self.period_edit)
        self.layout.addRow("Monto:", self.amount_edit)
        self.layout.addRow("Fecha de Pago:", self.date_edit)
        self.layout.addRow("Deducciones:", self.deducciones_edit)
        self.layout.addRow("Bonos:", self.bonos_edit)
        self.layout.addRow("Estado:", self.status_combo)
        
        # Botones
        self.buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        self.buttons.accepted.connect(self.accept_form)
        self.buttons.rejected.connect(self.reject)
        self.layout.addWidget(self.buttons)
        
        # Si es edición, precarga los datos
        if payroll_id is not None:
            self.load_payroll(payroll_id)

    def load_payroll(self, payroll_id):
        """Carga los datos iniciales para editar"""
        pr = self.controller.fetch_payroll_detail(payroll_id)
        if pr:
            self.employee_id_edit.setText(str(pr.get("id_empleado", "")))
            self.period_edit.setText(pr.get("periodo", ""))
            self.amount_edit.setText(str(pr.get("salario_bruto", "")))
            # Establecer la fecha si existe y es válida
            fecha_pago_str = pr.get("fecha_pago", "")
            if fecha_pago_str:
                try:
                    y, m, d = map(int, fecha_pago_str.split("-"))
                    self.date_edit.setDate(QDate(y, m, d))
                except Exception:
                    self.date_edit.setDate(QDate.currentDate())
            else:
                self.date_edit.setDate(QDate.currentDate())
            self.deducciones_edit.setText(str(pr.get("deducciones", "")))
            self.bonos_edit.setText(str(pr.get("bonos", "")))
            if pr.get("status", "") in ["Pendiente", "Pagado", "Cancelado"]:
                self.status_combo.setCurrentText(pr.get("status"))
        else:
            QMessageBox.warning(self, "Error", "No se encontró la nómina a editar.")

    def get_data(self):
        """Obtiene los datos del formulario en un dict con las claves que espera el backend."""
        fecha_pago_qdate = self.date_edit.date()
        fecha_pago_str = fecha_pago_qdate.toString("yyyy-MM-dd")
        return {
            "id_empleado": self.employee_id_edit.text().strip(),
            "periodo": self.period_edit.text().strip(),
            "salario_bruto": self.amount_edit.text().strip(),
            "fecha_pago": fecha_pago_str,
            "deducciones": self.deducciones_edit.text().strip(),
            "bonos": self.bonos_edit.text().strip(),
            "status": self.status_combo.currentText()
        }

    def accept_form(self):
        data = self.get_data()
        # Validación básica
        if (not data["id_empleado"] or not data["periodo"] or not data["salario_bruto"]
                or not data["fecha_pago"]):
            QMessageBox.warning(self, "Faltan datos", "Todos los campos obligatorios deben estar completos.")
            return
        try:
            data["id_empleado"] = int(data["id_empleado"])
            data["salario_bruto"] = float(data["salario_bruto"])
            # Deducciones y bonos pueden estar vacíos (opcional), solo convertir si no es vacío
            if data["deducciones"]:
                data["deducciones"] = float(data["deducciones"])
            else:
                data["deducciones"] = 0.0
            if data["bonos"]:
                data["bonos"] = float(data["bonos"])
            else:
                data["bonos"] = 0.0
            
            # Calcula el salario neto antes de enviar
            data["salario_neto"] = data["salario_bruto"] - data["deducciones"] + data["bonos"]
        except ValueError:
            QMessageBox.warning(self, "Datos inválidos", "ID Empleado, Monto, Deducciones y Bonos deben ser numéricos.")
            return
        # Validación del formato de fecha (QDateEdit lo garantiza, pero revisamos)
        import datetime
        try:
            datetime.datetime.strptime(data["fecha_pago"], "%Y-%m-%d")
        except ValueError:
            QMessageBox.warning(self, "Fecha inválida", "La fecha debe tener formato YYYY-MM-DD.")
            return
        # Guardar (alta o edición)
        if self.payroll_id is None:
            nuevo = self.controller.add_payroll(data)
            if nuevo:
                QMessageBox.information(self, "Listo", "Nómina creada.")
                self.accept()
            else:
                QMessageBox.warning(self, "Error", "No se pudo crear la nómina.")
        else:
            actualizado = self.controller.edit_payroll(self.payroll_id, data)
            if actualizado:
                QMessageBox.information(self, "Listo", "Nómina actualizada.")
                self.accept()
            else:
                QMessageBox.warning(self, "Error", "No se pudo actualizar la nómina.")
