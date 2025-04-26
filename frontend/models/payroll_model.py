class PayrollModel:
    """
    Modelo para gestionar los datos de nóminas a través del api_client.
    """

    def __init__(self, api_client):
        self.api_client = api_client

    def get_all_payrolls(self):
        """
        Obtiene la lista de todas las nóminas.
        """
        return self.api_client.get_payrolls()

    def get_payroll(self, payroll_id):
        """
        Obtiene los detalles de una nómina por su ID.
        """
        return self.api_client.get_payroll(payroll_id)

    def create_payroll(self, data):
        """
        Crea una nueva nómina.
        """
        return self.api_client.create_payroll(data)

    def update_payroll(self, payroll_id, data):
        """
        Actualiza los datos de una nómina existente.
        """
        return self.api_client.update_payroll(payroll_id, data)

    def delete_payroll(self, payroll_id):
        """
        Elimina una nómina por su ID.
        """
        return self.api_client.delete_payroll(payroll_id)