from PyQt6.QtWidgets import (
    QMainWindow, QTabWidget, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QPushButton, QStatusBar, QMenu, QMenuBar, QToolBar, 
    QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QIcon, QAction, QFont

from views.products.product_list import ProductListView
from views.sales.sales_list import SalesListView
from views.dashboard_view import DashboardView

class MainWindow(QMainWindow):
    """Ventana principal de la aplicación ERP Pirelli"""
    
    # Señal que se emite cuando se solicita cerrar sesión
    logout_requested = pyqtSignal()
    
    def __init__(self, api_client, user_data):
        super().__init__()
        
        self.api_client = api_client
        self.user_data = user_data
        
        self.init_ui()
    
    def init_ui(self):
        """Inicializa la interfaz de usuario"""
        # Configuración de la ventana
        self.setWindowTitle("ERP Pirelli")
        self.setMinimumSize(1024, 768)
        self.setWindowIcon(QIcon("resources/icons/pirelli_logo.png"))
        
        # Crear la barra de menú
        self.create_menu_bar()
        
        # Crear la barra de herramientas
        self.create_toolbar()
        
        # Widget central con pestañas
        self.tab_widget = QTabWidget()
        
        # Agregar pestañas
        self.dashboard_view = DashboardView(self.api_client)
        self.tab_widget.addTab(self.dashboard_view, "Dashboard")
        
        self.product_list_view = ProductListView(self.api_client)
        self.tab_widget.addTab(self.product_list_view, "Productos")
        
        self.sales_list_view = SalesListView(self.api_client)
        self.tab_widget.addTab(self.sales_list_view, "Ventas")
        
        # Configurar tabs adicionales según el rol del usuario
        role = self.user_data.get('rol', 'empleado')
        if role in ['admin', 'supervisor']:
            # Vistas para administradores y supervisores
            self.tab_widget.addTab(QWidget(), "Empleados")
            self.tab_widget.addTab(QWidget(), "Inventario")
            
            if role == 'admin':
                # Vistas exclusivas para administradores
                self.tab_widget.addTab(QWidget(), "Usuarios")
                self.tab_widget.addTab(QWidget(), "Configuración")
        
        # Establecer el widget central
        self.setCentralWidget(self.tab_widget)
        
        # Crear barra de estado
        self.create_status_bar()
        
        # Conectar eventos
        self.api_client.request_error.connect(self.on_api_error)
    
    def create_menu_bar(self):
        """Crea la barra de menú"""
        menu_bar = self.menuBar()
        
        # Menú Archivo
        file_menu = menu_bar.addMenu("Archivo")
        
        # Acciones del menú Archivo
        logout_action = QAction(QIcon("resources/icons/logout.png"), "Cerrar Sesión", self)
        logout_action.setShortcut("Ctrl+Q")
        logout_action.triggered.connect(self.logout)
        
        exit_action = QAction(QIcon("resources/icons/exit.png"), "Salir", self)
        exit_action.setShortcut("Alt+F4")
        exit_action.triggered.connect(self.close)
        
        file_menu.addAction(logout_action)
        file_menu.addSeparator()
        file_menu.addAction(exit_action)
        
        # Menú Editar
        edit_menu = menu_bar.addMenu("Editar")
        
        # Acciones del menú Editar
        preferences_action = QAction("Preferencias", self)
        edit_menu.addAction(preferences_action)
        
        # Menú Ayuda
        help_menu = menu_bar.addMenu("Ayuda")
        
        # Acciones del menú Ayuda
        about_action = QAction("Acerca de", self)
        about_action.triggered.connect(self.show_about_dialog)
        
        help_menu.addAction(about_action)
    
    def create_toolbar(self):
        """Crea la barra de herramientas"""
        toolbar = QToolBar("Barra de herramientas principal")
        toolbar.setMovable(False)
        self.addToolBar(toolbar)
        
        # Botones de la barra de herramientas
        dashboard_action = QAction(QIcon("resources/icons/dashboard.png"), "Dashboard", self)
        dashboard_action.triggered.connect(lambda: self.tab_widget.setCurrentIndex(0))
        
        products_action = QAction(QIcon("resources/icons/product.png"), "Productos", self)
        products_action.triggered.connect(lambda: self.tab_widget.setCurrentIndex(1))
        
        sales_action = QAction(QIcon("resources/icons/sales.png"), "Ventas", self)
        sales_action.triggered.connect(lambda: self.tab_widget.setCurrentIndex(2))
        
        refresh_action = QAction(QIcon("resources/icons/refresh.png"), "Actualizar", self)
        refresh_action.triggered.connect(self.refresh_current_view)
        
        # Agregar acciones a la barra de herramientas
        toolbar.addAction(dashboard_action)
        toolbar.addAction(products_action)
        toolbar.addAction(sales_action)
        toolbar.addSeparator()
        toolbar.addAction(refresh_action)
    
    def create_status_bar(self):
        """Crea la barra de estado"""
        status_bar = QStatusBar()
        self.setStatusBar(status_bar)
        
        # Usuario actual
        user_label = QLabel(f"Usuario: {self.user_data.get('nombre', 'Desconocido')}")
        user_label.setStyleSheet("margin-right: 10px;")
        
        # Rol
        role_label = QLabel(f"Rol: {self.user_data.get('rol', 'N/A')}")
        role_label.setStyleSheet("margin-right: 10px;")
        
        # Agregar widgets a la barra de estado
        status_bar.addPermanentWidget(user_label)
        status_bar.addPermanentWidget(role_label)
        
        # Mensaje inicial
        status_bar.showMessage("Listo", 3000)
    
    def refresh_current_view(self):
        """Actualiza la vista actual"""
        current_index = self.tab_widget.currentIndex()
        current_widget = self.tab_widget.widget(current_index)
        
        # Verificar si el widget tiene un método de actualización
        if hasattr(current_widget, "refresh_data"):
            current_widget.refresh_data()
            self.statusBar().showMessage("Datos actualizados", 3000)
    
    def logout(self):
        """Cierra la sesión actual"""
        reply = QMessageBox.question(
            self, 
            "Confirmar cierre de sesión", 
            "¿Está seguro que desea cerrar sesión?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.logout_requested.emit()
    
    def show_about_dialog(self):
        """Muestra el diálogo Acerca de"""
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
    
    def on_api_error(self, error_message):
        """Maneja errores de la API"""
        self.statusBar().showMessage(f"Error: {error_message}", 5000)
    
    def closeEvent(self, event):
        """Maneja el evento de cierre de la ventana"""
        reply = QMessageBox.question(
            self, 
            "Confirmar salida", 
            "¿Está seguro que desea salir de la aplicación?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Cerrar sesión antes de salir
            self.api_client.logout()
            event.accept()
        else:
            event.ignore()