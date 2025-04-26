class UsersModel:
    """
    Modelo para gestionar los datos de usuarios a través del api_client.
    """

    def __init__(self, api_client):
        self.api_client = api_client

    def get_all_users(self):
        """
        Obtiene la lista de todos los usuarios.
        """
        return self.api_client.get_users()

    def get_user(self, user_id):
        """
        Obtiene los detalles de un usuario por su ID.
        """
        return self.api_client.get_user(user_id)

    def create_user(self, data):
        """
        Crea un nuevo usuario.
        """
        return self.api_client.create_user(data)

    def update_user(self, user_id, data):
        """
        Actualiza los datos de un usuario existente.
        """
        return self.api_client.update_user(user_id, data)

    def delete_user(self, user_id):
        """
        Elimina un usuario por su ID.
        """
        return self.api_client.delete_user(user_id)