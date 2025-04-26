from models.users_model import UsersModel

class UsersController:
    """
    Controlador para gestionar la lógica de negocio de usuarios.
    """

    def __init__(self, api_client):
        self.model = UsersModel(api_client)

    def fetch_users(self):
        """
        Devuelve la lista de usuarios.
        """
        return self.model.get_all_users()

    def fetch_user_detail(self, user_id):
        """
        Devuelve los detalles de un usuario.
        """
        return self.model.get_user(user_id)

    def add_user(self, data):
        """
        Agrega un nuevo usuario.
        """
        return self.model.create_user(data)

    def edit_user(self, user_id, data):
        """
        Edita un usuario existente.
        """
        return self.model.update_user(user_id, data)

    def remove_user(self, user_id):
        """
        Elimina un usuario.
        """
        return self.model.delete_user(user_id)