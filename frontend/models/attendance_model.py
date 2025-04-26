class AttendanceModel:
    """
    Modelo para gestionar los datos de asistencia a través del api_client.
    """

    def __init__(self, api_client):
        self.api_client = api_client

    def get_all_attendance(self):
        return self.api_client.get_attendance()

    def get_attendance(self, attendance_id):
        return self.api_client.get_attendance_by_id(attendance_id)

    def create_attendance(self, data):
        return self.api_client.create_attendance(data)

    def update_attendance(self, attendance_id, data):
        return self.api_client.update_attendance(attendance_id, data)

    def delete_attendance(self, attendance_id):
        return self.api_client.delete_attendance(attendance_id)

    def get_employees(self):
        return self.api_client.get_employees()