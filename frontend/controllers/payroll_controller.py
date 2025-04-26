from models.payroll_model import PayrollModel

class PayrollController:
    """
    Controlador para gestionar la lógica de negocio de nóminas.
    """

    def __init__(self, api_client):
        self.model = PayrollModel(api_client)

    def fetch_payrolls(self):
        """
        Devuelve la lista de nóminas.
        """
        return self.model.get_all_payrolls()

    def fetch_payroll_detail(self, payroll_id):
        """
        Devuelve los detalles de una nómina.
        """
        return self.model.get_payroll(payroll_id)

    def add_payroll(self, data):
        """
        Agrega una nueva nómina.
        """
        return self.model.create_payroll(data)

    def edit_payroll(self, payroll_id, data):
        """
        Edita una nómina existente.
        """
        return self.model.update_payroll(payroll_id, data)

    def remove_payroll(self, payroll_id):
        """
        Elimina una nómina.
        """
        return self.model.delete_payroll(payroll_id)