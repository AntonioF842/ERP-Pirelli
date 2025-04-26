from PyQt6.QtWidgets import QMainWindow, QTabWidget

from views.rrhh.employees.employees_list import EmployeesListView
from views.rrhh.users.users_list import UsersListView
from views.rrhh.work_areas.work_areas_list import WorkAreasListView
from views.rrhh.attendance.attendance_list import AttendanceListView
from views.rrhh.payroll.payroll_list import PayrollListView

class RecursosHumanosWindow(QMainWindow):
    def __init__(self, api_client):
        super().__init__()
        self.setWindowTitle("Recursos Humanos")
        self.setMinimumSize(900, 600)
        self.tab_widget = QTabWidget()
        self.setCentralWidget(self.tab_widget)

        # Agrega cada sub-vista como una pestaña
        self.tab_widget.addTab(UsersListView(api_client), "Usuarios")
        self.tab_widget.addTab(EmployeesListView(api_client), "Empleados")
        self.tab_widget.addTab(WorkAreasListView(api_client), "Áreas de Trabajo")
        self.tab_widget.addTab(AttendanceListView(api_client), "Asistencia")
        self.tab_widget.addTab(PayrollListView(api_client), "Nóminas")
