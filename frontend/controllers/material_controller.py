from utils.api_client import ApiClient

class MaterialController:
    def __init__(self, api_client: ApiClient):
        self.api_client = api_client

    def get_materials(self):
        return self.api_client.get_materials()

    def get_material(self, material_id):
        return self.api_client.get_material(material_id)

    def create_material(self, material_data):
        return self.api_client.create_material(material_data)

    def update_material(self, material_id, material_data):
        return self.api_client.update_material(material_id, material_data)

    def delete_material(self, material_id):
        return self.api_client.delete_material(material_id)