class WorkAreasModel:
    """
    Modelo para gestionar los datos de áreas de trabajo a través del api_client.
    """

    def __init__(self, api_client):
        self.api_client = api_client

    def get_all_work_areas(self):
        """
        Obtiene la lista de todas las áreas de trabajo.
        """
        return self.api_client.get_work_areas()

    def get_work_area(self, area_id):
        """
        Obtiene los detalles de un área de trabajo por su ID.
        """
        return self.api_client.get_work_area(area_id)

    def create_work_area(self, data):
        """
        Crea una nueva área de trabajo.
        """
        return self.api_client.create_work_area(data)

    def update_work_area(self, area_id, data):
        """
        Actualiza los datos de una área de trabajo existente.
        """
        return self.api_client.update_work_area(area_id, data)

    def delete_work_area(self, area_id):
        """
        Elimina una área de trabajo por su ID.
        """
        return self.api_client.delete_work_area(area_id)