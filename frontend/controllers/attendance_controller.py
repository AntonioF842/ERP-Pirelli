from models.attendance_model import AttendanceModel

class AttendanceController:
    """
    Controlador para gestionar la lógica de negocio de asistencia.
    """

    def __init__(self, api_client):
        self.model = AttendanceModel(api_client)

    def fetch_attendance(self):
        return self.model.get_all_attendance()

    def fetch_attendance_detail(self, attendance_id):
        return self.model.get_attendance(attendance_id)

    def add_attendance(self, data):
        return self.model.create_attendance(data)

    def edit_attendance(self, attendance_id, data):
        return self.model.update_attendance(attendance_id, data)

    def remove_attendance(self, attendance_id):
        return self.model.delete_attendance(attendance_id)

    def fetch_employees(self):
        return self.model.get_employees()