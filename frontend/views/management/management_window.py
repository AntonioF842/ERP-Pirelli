from PyQt6.QtWidgets import QMainWindow, QTabWidget

from views.management.rd_projects.rd_project_list import RDProjectListView
from views.management.legal_regulations.legal_regulation_list import LegalRegulationListView
from views.management.incidents.incident_list import IncidentListView
from views.management.system_config.system_configuration_list import SystemConfigurationListView

class GestionWindow(QMainWindow):
    def __init__(self, api_client):
        super().__init__()
        self.setWindowTitle("Gestión de Clientes")
        self.setMinimumSize(900, 600)
        self.tab_widget = QTabWidget(self)
        self.setCentralWidget(self.tab_widget)

        self.tab_widget.addTab(RDProjectListView(api_client), "Proyectos I+D")
        self.tab_widget.addTab(LegalRegulationListView(api_client), "Normativas Legales")
        self.tab_widget.addTab(IncidentListView(api_client), "Incidentes")
        self.tab_widget.addTab(SystemConfigurationListView(api_client), "Configuraciones del Sistema")


    def center_window(self):
        screen = self.screen().availableGeometry()
        window_size = self.frameGeometry()
        x = screen.center().x() - window_size.width() // 2
        y = screen.center().y() - window_size.height() // 2
        self.move(x, y)