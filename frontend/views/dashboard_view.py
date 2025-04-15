from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QFrame, QGridLayout, QSizePolicy, QScrollArea
)
from PyQt6.QtCore import Qt, QSize, pyqtSignal
from PyQt6.QtGui import QFont, QIcon, QColor, QPalette, QPainter
from PyQt6.QtCharts import QChart, QChartView, QPieSeries, QBarSeries, QBarSet, QBarCategoryAxis, QValueAxis

class StatisticCard(QFrame):
    """Tarjeta para mostrar una estadística"""
    
    def __init__(self, title, value, icon_path=None, color="#4C72B0"):
        super().__init__()
        
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border-radius: 10px;
                border-left: 5px solid {color};
            }}
        """)
        
        # Layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Contenido
        text_layout = QVBoxLayout()
        text_layout.setSpacing(5)
        
        title_label = QLabel(title)
        title_label.setStyleSheet("color: #666; font-size: 14px;")
        
        value_label = QLabel(value)
        value_label.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        
        text_layout.addWidget(title_label)
        text_layout.addWidget(value_label)
        
        # Icono (si existe)
        if icon_path:
            icon_label = QLabel()
            icon_label.setPixmap(QIcon(icon_path).pixmap(QSize(32, 32)))
            layout.addWidget(icon_label)
        
        layout.addLayout(text_layout)
        layout.addStretch()
        
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setMinimumHeight(100)

class ChartCard(QFrame):
    """Tarjeta para mostrar un gráfico"""
    
    def __init__(self, title, chart_type="pie"):
        super().__init__()
        
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 10px;
            }
        """)
        
        # Layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Título
        title_label = QLabel(title)
        title_label.setStyleSheet("color: #333; font-size: 16px; font-weight: bold;")
        layout.addWidget(title_label)
        
        # Crear el gráfico
        self.chart = QChart()
        self.chart.setAnimationOptions(QChart.AnimationOption.SeriesAnimations)
        self.chart.setTheme(QChart.ChartTheme.ChartThemeLight)
        self.chart.setBackgroundVisible(False)
        self.chart.legend().setVisible(True)
        self.chart.legend().setAlignment(Qt.AlignmentFlag.AlignBottom)
        
        # Crear vista del gráfico
        self.chart_view = QChartView(self.chart)
        self.chart_view.setRenderHint(QPainter.RenderHint.Antialiasing, False)
        
        layout.addWidget(self.chart_view)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        # Agregar datos de prueba según el tipo de gráfico
        if chart_type == "pie":
            self.create_pie_chart()
        elif chart_type == "bar":
            self.create_bar_chart()
    
    def create_pie_chart(self):
        """Crea un gráfico de pastel con datos de prueba"""
        series = QPieSeries()
        series.append("Caucho", 35)
        series.append("Acero", 20)
        series.append("Químicos", 15)
        series.append("Otros", 30)
        
        # Destacar la porción más grande
        slice = series.slices()[0]
        slice.setExploded(True)
        slice.setLabelVisible(True)
        
        self.chart.addSeries(series)
        self.chart.setTitle("Distribución de Materiales")
    
    def create_bar_chart(self):
        """Crea un gráfico de barras con datos de prueba"""
        set0 = QBarSet("Ventas")
        set1 = QBarSet("Producción")
        
        set0.append([50, 65, 70, 85, 60])
        set1.append([40, 55, 65, 70, 55])
        
        series = QBarSeries()
        series.append(set0)
        series.append(set1)
        
        self.chart.addSeries(series)
        
        categories = ["Ene", "Feb", "Mar", "Abr", "May"]
        axis_x = QBarCategoryAxis()
        axis_x.append(categories)
        self.chart.addAxis(axis_x, Qt.AlignmentFlag.AlignBottom)
        series.attachAxis(axis_x)
        
        axis_y = QValueAxis()
        axis_y.setRange(0, 100)
        self.chart.addAxis(axis_y, Qt.AlignmentFlag.AlignLeft)
        series.attachAxis(axis_y)
        
        self.chart.setTitle("Comparación Ventas vs Producción")

class DashboardView(QWidget):
    """Vista del dashboard"""
    
    # Señal para solicitar actualización de datos
    refresh_requested = pyqtSignal()
    
    def __init__(self, api_client):
        super().__init__()
        
        self.api_client = api_client
        
        # Conectar señales
        self.api_client.data_received.connect(self.update_data)
        
        self.init_ui()
        
        # Cargar datos iniciales
        self.refresh_data()
    
    def init_ui(self):
        """Inicializa la interfaz de usuario"""
        # Layout principal con scroll
        main_container = QWidget()
        self.main_layout = QVBoxLayout(main_container)
        self.main_layout.setSpacing(20)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Scroll Area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(main_container)
        
        # Layout para este widget
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(scroll_area)
        
        # Encabezado
        header_layout = QHBoxLayout()
        
        # Título
        title_label = QLabel("Panel de Control")
        title_label.setFont(QFont("Arial", 24))
        header_layout.addWidget(title_label)
        
        # Botón de actualizar
        refresh_button = QPushButton("Actualizar")
        refresh_button.setIcon(QIcon("resources/icons/refresh.png"))
        refresh_button.clicked.connect(self.refresh_data)
        header_layout.addWidget(refresh_button, alignment=Qt.AlignmentFlag.AlignRight)
        
        self.main_layout.addLayout(header_layout)
        
        # Tarjetas de estadísticas
        self.create_statistic_cards()
        
        # Gráficos
        self.create_chart_cards()
        
        # Actividades recientes
        self.create_recent_activities()
    
    def create_statistic_cards(self):
        """Crea las tarjetas de estadísticas"""
        stats_layout = QGridLayout()
        stats_layout.setSpacing(15)
        
        # Tarjetas de estadísticas
        ventas_card = StatisticCard(
            "Ventas Mensuales", 
            "$235,800", 
            "resources/icons/sales.png", 
            "#28a745"
        )
        
        produccion_card = StatisticCard(
            "Producción Mensual", 
            "18,540 unidades", 
            "resources/icons/production.png", 
            "#007bff"
        )
        
        inventario_card = StatisticCard(
            "Nivel de Inventario", 
            "85%", 
            "resources/icons/inventory.png", 
            "#fd7e14"
        )
        
        empleados_card = StatisticCard(
            "Empleados Activos", 
            "86", 
            "resources/icons/employee.png", 
            "#6f42c1"
        )
        
        # Agregar tarjetas al layout
        stats_layout.addWidget(ventas_card, 0, 0)
        stats_layout.addWidget(produccion_card, 0, 1)
        stats_layout.addWidget(inventario_card, 1, 0)
        stats_layout.addWidget(empleados_card, 1, 1)
        
        # Agregar layout al principal
        self.main_layout.addLayout(stats_layout)
    
    def create_chart_cards(self):
        """Crea las tarjetas de gráficos"""
        charts_layout = QHBoxLayout()
        
        # Gráfico de pastel
        materials_chart = ChartCard("Distribución de Materiales", "pie")
        
        # Gráfico de barras
        production_chart = ChartCard("Ventas vs Producción", "bar")
        
        # Agregar gráficos al layout
        charts_layout.addWidget(materials_chart)
        charts_layout.addWidget(production_chart)
        
        # Agregar layout al principal
        self.main_layout.addLayout(charts_layout)
    
    def create_recent_activities(self):
        """Crea la sección de actividades recientes"""
        # Título de la sección
        section_label = QLabel("Actividades Recientes")
        section_label.setFont(QFont("Arial", 16))
        self.main_layout.addWidget(section_label)
        
        # Contenedor para actividades
        activities_frame = QFrame()
        activities_frame.setFrameShape(QFrame.Shape.StyledPanel)
        activities_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 10px;
            }
        """)
        
        activities_layout = QVBoxLayout(activities_frame)
        
        # Actividades de ejemplo
        activities = [
            ("Pedido #1234 completado", "Hace 2 horas", "resources/icons/order.png"),
            ("Nueva producción iniciada", "Hace 5 horas", "resources/icons/production.png"),
            ("Recibido envío de caucho", "Ayer", "resources/icons/delivery.png"),
            ("Actualización de inventario", "Hace 2 días", "resources/icons/inventory.png"),
        ]
        
        for title, time, icon_path in activities:
            # Crear item de actividad
            activity_layout = QHBoxLayout()
            
            # Icono
            if icon_path:
                icon_label = QLabel()
                icon_label.setPixmap(QIcon(icon_path).pixmap(QSize(24, 24)))
                activity_layout.addWidget(icon_label)
            
            # Información
            info_layout = QVBoxLayout()
            info_layout.setSpacing(2)
            
            title_label = QLabel(title)
            title_label.setStyleSheet("font-weight: bold;")
            
            time_label = QLabel(time)
            time_label.setStyleSheet("color: #888; font-size: 12px;")
            
            info_layout.addWidget(title_label)
            info_layout.addWidget(time_label)
            
            activity_layout.addLayout(info_layout)
            activity_layout.addStretch()
            
            # Agregar a la lista de actividades
            activities_layout.addLayout(activity_layout)
            
            # Añadir separador excepto para el último item
            if title != activities[-1][0]:
                separator = QFrame()
                separator.setFrameShape(QFrame.Shape.HLine)
                separator.setStyleSheet("background-color: #ddd;")
                activities_layout.addWidget(separator)
        
        # Agregar al layout principal
        self.main_layout.addWidget(activities_frame)
    
    def refresh_data(self):
        """Solicita actualización de datos"""
        # Esto emitiría una solicitud al API, pero por ahora solo simulamos
        # self.api_client.get_dashboard_data()
        self.update_data({})  # Datos de prueba
    
    def update_data(self, data):
        """Actualiza la interfaz con los datos recibidos"""
        # En una implementación real, aquí actualizaríamos los widgets con los datos
        # Por ahora, solo mostrar un mensaje en la barra de estado
        # if hasattr(self.parent(), 'statusBar'):
        #     self.parent().parent().statusBar().showMessage("Dashboard actualizado", 3000)
        pass