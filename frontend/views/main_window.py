from PyQt6.QtWidgets import (
    QMainWindow, QMenuBar, QMenu, QMessageBox, QStatusBar
)
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtCore import pyqtSignal

from views.dashboard_view import DashboardView
from views.rrhh.rrhh_window import RecursosHumanosWindow
# from views.inventario_window import InventarioWindow  # Crea ventanas similares para otros módulos
# from views.produccion_window import ProduccionWindow
# from views.ventas_window import VentasWindow
# from views.gestion_window import GestionWindow

class MainWindow(QMainWindow):
    logout_requested = pyqtSignal()

    def __init__(self, api_client, user_data):
        super().__init__()
        from utils.theme import Theme
        Theme.apply_window_light_theme(self)
        self.api_client = api_client
        self.user_data = user_data

        self.rrhh_window = None
        # self.inventario_window = None
        # self.produccion_window = None
        # self.ventas_window = None
        # self.gestion_window = None

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("ERP Pirelli")
        self.setMinimumSize(1024, 768)
        self.setWindowIcon(QIcon("resources/icons/pirelli_logo.png"))
        
        # Configurar barra de estado
        self.statusBar().showMessage("Bienvenido al sistema ERP Pirelli")
        
        # Crear dashboard como widget central
        self.dashboard_view = DashboardView(self.api_client)
        self.setCentralWidget(self.dashboard_view)
        
        # Conectar señales del dashboard
        self.dashboard_view.refresh_requested.connect(self.refresh_dashboard)
        
        self.create_menu_bar()

    def create_menu_bar(self):
        menu_bar = self.menuBar()

        # Menú Archivo
        file_menu = menu_bar.addMenu("Archivo")
        logout_action = QAction(QIcon("resources/icons/logout.png"), "Cerrar Sesión", self)
        logout_action.setShortcut("Ctrl+Q")
        logout_action.triggered.connect(self.logout)
        exit_action = QAction(QIcon("resources/icons/exit.png"), "Salir", self)
        exit_action.setShortcut("Alt+F4")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(logout_action)
        file_menu.addSeparator()
        file_menu.addAction(exit_action)

         # Menú Módulos
        modules_menu = menu_bar.addMenu("Módulos")

        rrhh_action = QAction("Recursos Humanos", self)
        rrhh_action.triggered.connect(self.open_rrhh_module)
        modules_menu.addAction(rrhh_action)

        # Repite para otros módulos:
        # inventario_action = QAction("Inventario y Compras", self)
        # inventario_action.triggered.connect(self.open_inventario_module)
        # modules_menu.addAction(inventario_action)
        # ...

        # Menú Ayuda
        help_menu = menu_bar.addMenu("Ayuda")
        about_action = QAction("Acerca de", self)
        about_action.triggered.connect(self.show_about_dialog)
        help_menu.addAction(about_action)

    def show_dashboard(self):
        """Muestra el dashboard como widget central"""
        if not hasattr(self, 'dashboard_view') or self.dashboard_view is None:
            self.dashboard_view = DashboardView(self.api_client)
        self.setCentralWidget(self.dashboard_view)
        self.statusBar().showMessage("Dashboard cargado", 3000)

    def refresh_dashboard(self):
        """Actualiza los datos del dashboard"""
        self.dashboard_view.refresh_data()
        self.statusBar().showMessage("Dashboard actualizado", 3000)

    def open_rrhh_module(self):
        if self.rrhh_window is None:
            self.rrhh_window = RecursosHumanosWindow(self.api_client)
            self.rrhh_window.show()
            self.rrhh_window.destroyed.connect(lambda: setattr(self, 'rrhh_window', None))
        else:
            self.rrhh_window.raise_()
            self.rrhh_window.activateWindow()

    def logout(self):
        reply = QMessageBox.question(
            self, "Confirmar cierre de sesión", "¿Está seguro que desea cerrar sesión?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.logout_requested.emit()

    def show_about_dialog(self):
        QMessageBox.about(
            self,
            "Acerca de ERP Pirelli",
            """
            <h2>Sistema ERP Pirelli</h2>
            <p>Versión 1.0</p>
            <p>Un sistema de gestión empresarial desarrollado para Pirelli.</p>
            <p>© 2025 Pirelli</p>
            """
        )