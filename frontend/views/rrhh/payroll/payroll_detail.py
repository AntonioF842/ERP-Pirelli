from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QMessageBox
from controllers.payroll_controller import PayrollController

class PayrollDetailView(QDialog):
    def __init__(self, api_client, payroll_id, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Detalle de Nómina #{payroll_id}")
        self.controller = PayrollController(api_client)
        self.api_client = api_client
        self.layout = QVBoxLayout(self)
        pr = self.controller.fetch_payroll_detail(payroll_id)
        if pr:
            msg = []
            for k, v in pr.items():
                msg.append(f"<b>{k.replace('_',' ').capitalize()}:</b> {v}")
            self.layout.addWidget(QLabel("<br>".join(msg)))
        else:
            QMessageBox.warning(self, "Error", "No se encontró la nómina.")
            self.close()
