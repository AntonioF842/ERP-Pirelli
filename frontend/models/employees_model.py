class EmployeesModel:
    """
    Modelo para gestionar los datos de empleados a través del api_client.
    """

    def __init__(self, api_client):
        self.api_client = api_client

    def get_all_employees(self):
        """
        Obtiene la lista de todos los empleados.
        """
        return self.api_client.get_employees()

    def get_employee(self, employee_id):
        """
        Obtiene los detalles de un empleado por su ID.
        """
        return self.api_client.get_employee(employee_id)

    def create_employee(self, data):
        """
        Crea un nuevo empleado.
        """
        return self.api_client.create_employee(data)

    def update_employee(self, employee_id, data):
        """
        Actualiza los datos de un empleado existente.
        """
        return self.api_client.update_employee(employee_id, data)

    def delete_employee(self, employee_id):
        """
        Elimina un empleado por su ID.
        """
        return self.api_client.delete_employee(employee_id)

    def get_areas_trabajo(self):
        """
        Obtiene la lista de áreas de trabajo.
        """
        return self.api_client.get_areas_trabajo()