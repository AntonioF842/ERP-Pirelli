import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from views.main_window import MainWindow
from views.login_view import LoginView
from utils.api_client import ApiClient
from utils.theme import Theme

class ERP_Pirelli(QApplication):
    """Aplicación principal del ERP de Pirelli"""
    
    def __init__(self, argv):
        super().__init__(argv)
        
        # Configuración de la aplicación
        self.setApplicationName("ERP Pirelli")
        self.setApplicationVersion("1.0")
        
        # Instancia del cliente API
        self.api_client = ApiClient()
        
        # Ventana principal (se mostrará después del login)
        self.main_window = None
        
        # Ventana de login (primera en mostrarse)
        self.login_view = LoginView(self.api_client)
        self.login_view.login_successful.connect(self.on_login_successful)
        
        # Mostrar ventana de login
        self.login_view.show()
    
    def on_login_successful(self, user_data):
        """Maneja el evento de inicio de sesión exitoso"""
        # Cerrar la ventana de login
        self.login_view.close()
        
        # Crear y mostrar la ventana principal
        self.main_window = MainWindow(self.api_client, user_data)
        self.main_window.logout_requested.connect(self.on_logout_requested)
        self.main_window.show()
    
    def on_logout_requested(self):
        """Maneja el evento de cierre de sesión"""
        # Cerrar la ventana principal
        if self.main_window:
            self.main_window.close()
            self.main_window = None
        
        # Limpiar datos de sesión
        self.api_client.logout()
        
        # Mostrar de nuevo la ventana de login
        self.login_view.clear_fields()
        self.login_view.show()

if __name__ == "__main__":
    # Iniciar la aplicación (sin configurar atributos de high DPI - ya están habilitados por defecto)
    app = ERP_Pirelli(sys.argv)
    Theme.apply_window_light_theme(app)
    sys.exit(app.exec())