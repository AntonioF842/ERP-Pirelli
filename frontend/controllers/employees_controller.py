from models.employees_model import EmployeesModel

class EmployeesController:
    """
    Controlador para gestionar la lógica de negocio de empleados.
    """

    def __init__(self, api_client):
        self.model = EmployeesModel(api_client)

    def fetch_employees(self):
        """
        Devuelve la lista de empleados.
        """
        return self.model.get_all_employees()

    def fetch_employee_detail(self, employee_id):
        """
        Devuelve los detalles de un empleado.
        """
        return self.model.get_employee(employee_id)

    def add_employee(self, data):
        """
        Agrega un nuevo empleado.
        """
        return self.model.create_employee(data)

    def edit_employee(self, employee_id, data):
        """
        Edita un empleado existente.
        """
        return self.model.update_employee(employee_id, data)

    def remove_employee(self, employee_id):
        """
        Elimina un empleado.
        """
        return self.model.delete_employee(employee_id)

    def fetch_areas_trabajo(self):
        """
        Devuelve las áreas de trabajo.
        """
        return self.model.get_areas_trabajo()