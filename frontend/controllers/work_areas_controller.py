from models.work_areas_model import WorkAreasModel

class WorkAreasController:
    """
    Controlador para gestionar la lógica de negocio de áreas de trabajo.
    """

    def __init__(self, api_client):
        self.model = WorkAreasModel(api_client)

    def fetch_work_areas(self):
        """
        Devuelve la lista de áreas de trabajo.
        """
        return self.model.get_all_work_areas()

    def fetch_work_area_detail(self, area_id):
        """
        Devuelve los detalles de una área de trabajo.
        """
        return self.model.get_work_area(area_id)

    def add_work_area(self, data):
        """
        Agrega una nueva área de trabajo.
        """
        return self.model.create_work_area(data)

    def edit_work_area(self, area_id, data):
        """
        Edita una área de trabajo existente.
        """
        return self.model.update_work_area(area_id, data)

    def remove_work_area(self, area_id):
        """
        Elimina una área de trabajo.
        """
        return self.model.delete_work_area(area_id)