"""
Configuración de temas y estilos para la aplicación
"""

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QPalette, QColor, QFont
from PyQt6.QtCore import Qt

class Theme:
    """Clase para gestionar temas y estilos de la aplicación"""
    
    # Colores base Pirelli
    PRIMARY_COLOR = "#000000"      # Negro
    SECONDARY_COLOR = "#ED1C24"    # Rojo Pirelli
    ACCENT_COLOR = "#FFCC00"       # Amarillo Pirelli
    
    # Otros colores
    SUCCESS_COLOR = "#28a745"      # Verde
    WARNING_COLOR = "#ffc107"      # Amarillo
    DANGER_COLOR = "#dc3545"       # Rojo
    INFO_COLOR = "#17a2b8"         # Azul claro
    
    # Colores de fondo
    LIGHT_BG = "#F8F9FA"
    DARK_BG = "#343A40"
    
    @staticmethod
    def apply_base_theme(app):
        """Aplica el tema base a toda la aplicación"""
        if not isinstance(app, QApplication):
            raise TypeError("Se esperaba una instancia de QApplication")
        
        # Establecer fuente predeterminada
        font = QFont("Segoe UI", 10)
        app.setFont(font)
        
        # Aplicar hoja de estilos
        app.setStyleSheet(Theme.get_base_stylesheet())

    @staticmethod
    def get_base_stylesheet():
        """Devuelve la hoja de estilos base"""
        return f"""
        /* Estilo general */
        QWidget {{
            font-family: 'Segoe UI';
            font-size: 10pt;
        }}
        
        /* Estilo para botones principales */
        QPushButton[primary=true] {{
            background-color: {Theme.PRIMARY_COLOR};
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
        }}
        
        QPushButton[primary=true]:hover {{
            background-color: #333333;
        }}
        
        QPushButton[primary=true]:pressed {{
            background-color: #555555;
        }}
        
        /* Estilo para botones secundarios */
        QPushButton[secondary=true] {{
            background-color: {Theme.SECONDARY_COLOR};
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
        }}
        
        QPushButton[secondary=true]:hover {{
            background-color: #ff3333;
        }}
        
        QPushButton[secondary=true]:pressed {{
            background-color: #cc0000;
        }}
        
        /* Estilo para etiquetas de título */
        QLabel[heading=true] {{
            font-size: 18pt;
            font-weight: bold;
            color: {Theme.PRIMARY_COLOR};
        }}
        
        /* Estilo para campos de entrada */
        QLineEdit, QTextEdit, QComboBox {{
            border: 1px solid #cccccc;
            border-radius: 4px;
            padding: 6px;
        }}
        
        QLineEdit:focus, QTextEdit:focus, QComboBox:focus {{
            border: 1px solid {Theme.SECONDARY_COLOR};
        }}
        
        /* Estilo para tablas */
        QTableView {{
            gridline-color: #e0e0e0;
            selection-background-color: #f0f0f0;
            selection-color: {Theme.PRIMARY_COLOR};
            border: 1px solid #cccccc;
        }}
        
        QTableView::item:selected {{
            background-color: #e0e0e0;
        }}
        
        QHeaderView::section {{
            background-color: #f5f5f5;
            padding: 6px;
            border: 1px solid #cccccc;
            border-left: 0px;
            border-top: 0px;
        }}
        
        /* Estilo para pestañas */
        QTabWidget::pane {{
            border: 1px solid #cccccc;
            border-top: 0px;
        }}
        
        QTabBar::tab {{
            background-color: #f0f0f0;
            border: 1px solid #cccccc;
            border-bottom-color: transparent;
            padding: 8px 12px;
            margin-right: 2px;
        }}
        
        QTabBar::tab:selected {{
            background-color: white;
            border-bottom-color: white;
        }}
        
        QTabBar::tab:!selected {{
            margin-top: 2px;
        }}
        
        /* Estilo para barras de menú */
        QMenuBar {{
            background-color: {Theme.PRIMARY_COLOR};
            color: white;
        }}
        
        QMenuBar::item {{
            padding: 4px 8px;
        }}
        
        QMenuBar::item:selected {{
            background-color: #333333;
        }}
        
        /* Estilo para menús desplegables */
        QMenu {{
            background-color: white;
            border: 1px solid #cccccc;
        }}
        
        QMenu::item {{
            padding: 6px 20px 6px 20px;
        }}
        
        QMenu::item:selected {{
            background-color: #f0f0f0;
        }}
        """
    
    @staticmethod
    def get_card_style(border_color=None):
        """Devuelve el estilo para tarjetas/paneles"""
        border = f"border-left: 5px solid {border_color};" if border_color else ""
        return f"""
            QFrame {{
                background-color: white;
                border-radius: 8px;
                {border}
                border: 1px solid #e0e0e0;
            }}
        """
    
    @staticmethod
    def apply_dark_mode(app):
        """Aplica el modo oscuro a la aplicación"""
        if not isinstance(app, QApplication):
            raise TypeError("Se esperaba una instancia de QApplication")
            
        # Crear una paleta oscura
        dark_palette = QPalette()
        
        # Colores del modo oscuro
        dark_palette.setColor(QPalette.ColorRole.Window, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.white)
        dark_palette.setColor(QPalette.ColorRole.Base, QColor(25, 25, 25))
        dark_palette.setColor(QPalette.ColorRole.AlternateBase, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ColorRole.ToolTipBase, Qt.GlobalColor.white)
        dark_palette.setColor(QPalette.ColorRole.ToolTipText, Qt.GlobalColor.white)
        dark_palette.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.white)
        dark_palette.setColor(QPalette.ColorRole.Button, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.white)
        dark_palette.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.red)
        dark_palette.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))
        dark_palette.setColor(QPalette.ColorRole.Highlight, QColor(Theme.SECONDARY_COLOR))
        dark_palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.black)
        
        # Aplicar la paleta
        app.setPalette(dark_palette)
        
        # Aplicar hoja de estilos para modo oscuro
        app.setStyleSheet(Theme.get_dark_stylesheet())
    
    @staticmethod
    def get_dark_stylesheet():
        """Devuelve la hoja de estilos para modo oscuro"""
        return f"""
        /* Estilo general para modo oscuro */
        QWidget {{
            font-family: 'Segoe UI';
            font-size: 10pt;
            color: white;
            background-color: #2D2D30;
        }}
        
        QPushButton {{
            background-color: #444444;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
        }}
        
        QPushButton:hover {{
            background-color: #555555;
        }}
        
        QPushButton:pressed {{
            background-color: #666666;
        }}
        
        QLineEdit, QTextEdit, QComboBox {{
            border: 1px solid #555555;
            border-radius: 4px;
            padding: 6px;
            background-color: #3C3C3C;
            color: white;
        }}
        
        QTableView {{
            gridline-color: #555555;
            background-color: #2D2D30;
            color: white;
            selection-background-color: #3C3C3C;
            selection-color: white;
            border: 1px solid #555555;
        }}
        
        QHeaderView::section {{
            background-color: #3C3C3C;
            color: white;
            padding: 6px;
            border: 1px solid #555555;
        }}
        
        QTabWidget::pane {{
            border: 1px solid #555555;
            border-top: 0px;
        }}
        
        QTabBar::tab {{
            background-color: #3C3C3C;
            color: white;
            border: 1px solid #555555;
            padding: 8px 12px;
        }}
        
        QTabBar::tab:selected {{
            background-color: #2D2D30;
            border-bottom-color: #2D2D30;
        }}
        
        QMenuBar {{
            background-color: #1E1E1E;
            color: white;
        }}
        
        QMenuBar::item:selected {{
            background-color: #3C3C3C;
        }}
        
        QMenu {{
            background-color: #2D2D30;
            border: 1px solid #555555;
        }}
        
        QMenu::item:selected {{
            background-color: #3C3C3C;
        }}
        """