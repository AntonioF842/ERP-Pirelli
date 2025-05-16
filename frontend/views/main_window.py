from PyQt6.QtWidgets import QMainWindow, QMenuBar, QMenu, QMessageBox
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtCore import pyqtSignal, Qt

from views.dashboard_view import DashboardView
from views.rrhh.rrhh_window import RecursosHumanosWindow
from views.inventory.inventory_window import InventoryWindow
from views.production.production_window import ProductionWindow
from views.sales.sales_window import VentasWindow
from views.management.management_window import GestionWindow 

class MainWindow(QMainWindow):
    logout_requested = pyqtSignal()

    def __init__(self, api_client, user_data):
        super().__init__()
        from utils.theme import Theme
        Theme.apply_window_light_theme(self)
        self.api_client = api_client
        self.user_data = user_data

        self.rrhh_window = None
        self.inventario_window = None
        self.production_window = None
        self.ventas_window = None
        self.management_window = None

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

        self.center_window()

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
        rrhh_action.triggered.connect(lambda: self.open_module_window('rrhh_window', RecursosHumanosWindow))
        modules_menu.addAction(rrhh_action)

        inventario_action = QAction("Inventario y Compras", self)
        inventario_action.triggered.connect(lambda: self.open_module_window('inventario_window', InventoryWindow))
        modules_menu.addAction(inventario_action)

        production_action = QAction("Producción", self)
        production_action.triggered.connect(lambda: self.open_module_window('production_window', ProductionWindow))
        modules_menu.addAction(production_action)

        ventas_action = QAction("Ventas", self)
        ventas_action.triggered.connect(lambda: self.open_module_window('ventas_window', VentasWindow))
        modules_menu.addAction(ventas_action)

        gestion_action = QAction("Gestión", self)
        gestion_action.triggered.connect(lambda: self.open_module_window('management_window', GestionWindow))
        modules_menu.addAction(gestion_action)

        # ... Agregar más módulos aquí

        # Menú Ayuda
        help_menu = menu_bar.addMenu("Ayuda")
        about_action = QAction("Acerca de", self)
        about_action.triggered.connect(self.show_about_dialog)
        help_menu.addAction(about_action)

    def open_module_window(self, window_attr_name, window_class):
        """Abre una ventana de módulo, si no está ya abierta."""
        window = getattr(self, window_attr_name, None)
        if window is None:
            window = window_class(self.api_client)
            window.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
            window.show()
            setattr(self, window_attr_name, window)
            window.destroyed.connect(lambda: setattr(self, window_attr_name, None))
        else:
            window.raise_()
            window.activateWindow()

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

    def closeEvent(self, event):
        reply = QMessageBox.question(
            self,
            "Salir del ERP",
            "¿Está seguro que desea salir del ERP?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            # Cerrar todas las ventanas hijas abiertas
            if self.rrhh_window is not None:
                self.rrhh_window.close()
            if self.inventario_window is not None:
                self.inventario_window.close()
            if self.production_window is not None:
                self.production_window.close()
            if self.ventas_window is not None:
                self.ventas_window.close()
            if self.management_window is not None:
                self.management_window.close()
            # Agrega aquí más módulos si tienes otros
            event.accept()
        else:
            event.ignore()

    def center_window(self):
        screen = self.screen().availableGeometry()
        window_size = self.frameGeometry()
        x = screen.center().x() - window_size.width() // 2
        y = screen.center().y() - window_size.height() // 2
        self.move(x, y)
