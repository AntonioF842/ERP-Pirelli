from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QGridLayout, QSizePolicy, QScrollArea, QMessageBox,
    QGraphicsDropShadowEffect, QSpacerItem, QDialog,
    QTableWidget, QTableWidgetItem, QHeaderView, QToolTip, QApplication
)
from datetime import datetime
import locale
from PyQt6.QtCore import Qt, QSize, pyqtSignal, QPropertyAnimation, QEasingCurve, QTimer, QRect
from PyQt6.QtGui import QFont, QIcon, QPainter, QColor
from PyQt6.QtCharts import QChart, QChartView, QPieSeries, QBarSeries, QBarSet, QBarCategoryAxis, QValueAxis
import logging

# Configuración de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Colores Pirelli
PIRELLI_RED = "#D50000"
PIRELLI_RED_LIGHT = "#FF5252"
PIRELLI_RED_DARK = "#B71C1C"
PIRELLI_YELLOW = "#FFCD00"
PIRELLI_YELLOW_LIGHT = "#E7EA28"
PIRELLI_DARK = "#1A1A1A"
PIRELLI_DARK_LIGHT = "#424242"
PIRELLI_GRAY = "#666666"
PIRELLI_LIGHT_GRAY = "#E6E6E6"
CARD_BG = "#FFFFFF"
CARD_BORDER = "#EEEEEE"

def get_formatted_date():
    """Obtiene la fecha y hora actual formateada en español"""
    now = datetime.now()
    
    try:
        locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')
        date = now.strftime("%d de %B, %Y")
        time = now.strftime("%H:%M")
    except:
        try:
            locale.setlocale(locale.LC_TIME, 'Spanish_Spain.1252')
            date = now.strftime("%d de %B, %Y")
            time = now.strftime("%H:%M")
        except:
            months = {
                1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
                5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
                9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
            }
            
            day = now.day
            month = months[now.month]
            year = now.year
            time = f"{now.hour:02d}:{now.minute:02d}"
            date = f"{day} de {month}, {year}"
    
    return date, time

class SalesVsProductionDialog(QDialog):
    """Dialog to show sales vs production chart in detail with data table"""
    def __init__(self, data, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Detalles de Ventas vs Producción")
        
        # CALCULAR TAMAÑO Y POSICIÓN BASADO EN LA PANTALLA
        self.setup_window_geometry()
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)  # Márgenes más pequeños
        layout.setSpacing(15)  # Espaciado reducido

        # Title with style
        title_label = QLabel("Comparación Detallada de Ventas vs Producción")
        title_label.setStyleSheet(f"""
            font-family: 'Segoe UI';
            font-size: 20px;
            font-weight: bold;
            color: {PIRELLI_DARK};
            margin-bottom: 8px;
        """)
        layout.addWidget(title_label)

        # Large chart - TAMAÑO MÁS PEQUEÑO
        chart = QChart()
        chart.setAnimationOptions(QChart.AnimationOption.SeriesAnimations)
        chart.setTheme(QChart.ChartTheme.ChartThemeLight)
        chart.setBackgroundVisible(False)
        chart.legend().setVisible(True)
        chart.legend().setAlignment(Qt.AlignmentFlag.AlignBottom)
        chart.legend().setFont(QFont("Segoe UI", 10))

        ventas = [float(v) if v else 0 for v in data.get("ventas", [])]
        produccion = [float(p) if p else 0 for p in data.get("produccion", [])]
        categorias = data.get("categorias", [f"Item {i+1}" for i in range(max(len(ventas), len(produccion)))])

        set0 = QBarSet("Ventas")
        set1 = QBarSet("Producción")
        set0.setColor(QColor(PIRELLI_RED))
        set1.setColor(QColor(PIRELLI_DARK))
        set0.append(ventas)
        set1.append(produccion)
        series = QBarSeries()
        series.append(set0)
        series.append(set1)
        chart.addSeries(series)

        axis_x = QBarCategoryAxis()
        axis_x.append(categorias)
        chart.addAxis(axis_x, Qt.AlignmentFlag.AlignBottom)
        series.attachAxis(axis_x)

        axis_y = QValueAxis()
        max_value = max(ventas + produccion) if (ventas + produccion) else 10
        axis_y.setRange(0, max_value * 1.1 if max_value > 0 else 10)
        axis_y.setLabelsFont(QFont("Segoe UI", 9))
        chart.addAxis(axis_y, Qt.AlignmentFlag.AlignLeft)
        series.attachAxis(axis_y)

        chart_view = QChartView(chart)
        chart_view.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        chart_view.setFixedHeight(200)  # Altura más pequeña
        layout.addWidget(chart_view)

        # TABLA CON SCROLL OPTIMIZADA
        table_frame = QFrame()
        table_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {CARD_BG};
                border-radius: 10px;
                border: 1px solid {CARD_BORDER};
            }}
        """)
        table_layout = QVBoxLayout(table_frame)
        table_layout.setContentsMargins(15, 15, 15, 15)
        
        table_title = QLabel("Detalles numéricos de ventas y producción")
        table_title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        table_title.setStyleSheet(f"color: {PIRELLI_DARK}; margin-bottom: 8px;")
        table_layout.addWidget(table_title)
        
        # CREAR TABLA CON ALTURA OPTIMIZADA
        table = QTableWidget()
        table.setColumnCount(3)
        table.setHorizontalHeaderLabels(["Categoría", "Ventas", "Producción"])
        table.setRowCount(len(categorias))
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        table.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
        table.setAlternatingRowColors(True)
        
        # CONFIGURAR SCROLL POLICIES
        table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        table.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        # ALTURA DINÁMICA MÁS COMPACTA
        row_height = 30  # Altura más pequeña por fila
        header_height = 35
        min_height = 150
        max_height = 280  # Altura máxima reducida
        
        if len(categorias) > 7:  # Más de 7 filas
            table.setFixedHeight(max_height)
        else:
            calculated_height = header_height + (len(categorias) * row_height) + 15
            table.setFixedHeight(max(min_height, calculated_height))
        
        table.setStyleSheet("""
            QTableWidget {
                background-color: #FFFFFF;
                font-family: 'Segoe UI';
                font-size: 13px;
                border: 1px solid #E0E0E0;
                border-radius: 6px;
            }
            QHeaderView::section {
                background-color: #1A1A1A;
                color: white;
                font-weight: bold;
                font-size: 13px;
                border: none;
                padding: 8px;
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #F0F0F0;
            }
            QTableWidget::item:selected {
                background-color: #F5F5F5;
            }
            QScrollBar:vertical {
                border: none;
                background: #F5F5F5;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background: #C1C1C1;
                min-height: 20px;
                border-radius: 6px;
                margin: 1px;
            }
            QScrollBar::handle:vertical:hover {
                background: #A8A8A8;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
        
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table.verticalHeader().setVisible(False)

        # Llenar la tabla con datos
        for row, categoria in enumerate(categorias):
            v = ventas[row] if row < len(ventas) else 0
            p = produccion[row] if row < len(produccion) else 0
            table.setItem(row, 0, QTableWidgetItem(str(categoria)))
            table.setItem(row, 1, QTableWidgetItem(f"{v:,.2f}".replace(",", ".")))
            table.setItem(row, 2, QTableWidgetItem(f"{p:,.2f}".replace(",", ".")))

        table_layout.addWidget(table)
        layout.addWidget(table_frame, 1)

        # Close button más compacto
        close_button = QPushButton("Cerrar")
        close_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {PIRELLI_DARK};
                color: white;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
                font-size: 13px;
                min-width: 100px;
            }}
            QPushButton:hover {{
                background-color: {PIRELLI_DARK_LIGHT};
            }}
        """)
        close_button.clicked.connect(self.accept)
        
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(close_button)
        layout.addLayout(button_layout)

    def setup_window_geometry(self):
        """Configura el tamaño y posición de la ventana basado en la pantalla"""
        # Obtener información de la pantalla
        screen = QApplication.primaryScreen()
        screen_geometry = screen.availableGeometry()
        
        # Calcular tamaño de la ventana (70% del ancho y 80% del alto de la pantalla)
        window_width = int(screen_geometry.width() * 0.7)
        window_height = int(screen_geometry.height() * 0.8)
        
        # Limitar tamaños mínimos y máximos
        window_width = max(800, min(window_width, 1200))  # Entre 800px y 1200px
        window_height = max(600, min(window_height, 900))  # Entre 600px y 900px
        
        # Calcular posición para centrar
        x = (screen_geometry.width() - window_width) // 2
        y = (screen_geometry.height() - window_height) // 2
        
        # Aplicar geometría
        self.setGeometry(x, y, window_width, window_height)
        self.setMinimumSize(800, 600)

class MaterialDistributionDialog(QDialog):
    """Dialog to show material distribution in detail with data table"""
    def __init__(self, data, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Detalles de Distribución de Materiales")
        
        # CALCULAR TAMAÑO Y POSICIÓN BASADO EN LA PANTALLA
        self.setup_window_geometry()
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)  # Márgenes más pequeños
        layout.setSpacing(15)  # Espaciado reducido
        
        # Title with style
        title_label = QLabel("Distribución Detallada de Materiales")
        title_label.setStyleSheet(f"""
            font-family: 'Segoe UI';
            font-size: 20px;
            font-weight: bold;
            color: {PIRELLI_DARK};
            margin-bottom: 8px;
        """)
        layout.addWidget(title_label)
        
        # Large chart - TAMAÑO MÁS PEQUEÑO
        chart = QChart()
        chart.setAnimationOptions(QChart.AnimationOption.SeriesAnimations)
        chart.setTheme(QChart.ChartTheme.ChartThemeLight)
        chart.setBackgroundVisible(False)
        chart.legend().setVisible(True)
        chart.legend().setAlignment(Qt.AlignmentFlag.AlignBottom)
        chart.legend().setFont(QFont("Segoe UI", 10))
        series = QPieSeries()
        total = sum(float(v) for v in data.values() if v)
        
        # Colors for the chart
        colors = [
            PIRELLI_RED, 
            PIRELLI_DARK, 
            PIRELLI_YELLOW, 
            PIRELLI_GRAY, 
            PIRELLI_RED_LIGHT,
            PIRELLI_DARK_LIGHT,
            PIRELLI_YELLOW_LIGHT
        ]
        
        for i, (material, valor) in enumerate(data.items()):
            val = float(valor)
            slice = series.append(f"{material}: {val} ({val/total*100:.1f}%)", val)
            color_idx = i % len(colors)
            slice.setBrush(QColor(colors[color_idx]))
            slice.setLabelVisible(True)
            if i == 0:
                slice.setExploded(True)
                
        chart.addSeries(series)
        chart_view = QChartView(chart)
        chart_view.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        chart_view.setFixedHeight(200)  # Altura más pequeña
        layout.addWidget(chart_view)
        
        # TABLA CON SCROLL OPTIMIZADA
        table_frame = QFrame()
        table_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {CARD_BG};
                border-radius: 10px;
                border: 1px solid {CARD_BORDER};
            }}
        """)
        table_layout = QVBoxLayout(table_frame)
        table_layout.setContentsMargins(15, 15, 15, 15)
        
        table_title = QLabel("Detalles numéricos de distribución de materiales")
        table_title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        table_title.setStyleSheet(f"color: {PIRELLI_DARK}; margin-bottom: 8px;")
        table_layout.addWidget(table_title)
        
        # CREAR TABLA CON ALTURA OPTIMIZADA
        table = QTableWidget()
        table.setColumnCount(3)
        table.setHorizontalHeaderLabels(["Material", "Valor", "Porcentaje"])
        table.setRowCount(len(data))
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        table.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
        table.setAlternatingRowColors(True)
        
        # CONFIGURAR SCROLL POLICIES
        table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        table.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        # ALTURA DINÁMICA MÁS COMPACTA
        row_height = 30  # Altura más pequeña por fila
        header_height = 35
        min_height = 150
        max_height = 280  # Altura máxima reducida
        
        if len(data) > 7:  # Más de 7 filas
            table.setFixedHeight(max_height)
        else:
            calculated_height = header_height + (len(data) * row_height) + 15
            table.setFixedHeight(max(min_height, calculated_height))
        
        table.setStyleSheet("""
            QTableWidget {
                background-color: #FFFFFF;
                font-family: 'Segoe UI';
                font-size: 13px;
                border: 1px solid #E0E0E0;
                border-radius: 6px;
            }
            QHeaderView::section {
                background-color: #1A1A1A;
                color: white;
                font-weight: bold;
                font-size: 13px;
                border: none;
                padding: 8px;
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #F0F0F0;
            }
            QTableWidget::item:selected {
                background-color: #F5F5F5;
            }
            QScrollBar:vertical {
                border: none;
                background: #F5F5F5;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background: #C1C1C1;
                min-height: 20px;
                border-radius: 6px;
                margin: 1px;
            }
            QScrollBar::handle:vertical:hover {
                background: #A8A8A8;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
        
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table.verticalHeader().setVisible(False)

        # Llenar la tabla con datos
        for row, (material, valor) in enumerate(data.items()):
            val = float(valor)
            percent = (val / total * 100) if total else 0
            table.setItem(row, 0, QTableWidgetItem(str(material)))
            table.setItem(row, 1, QTableWidgetItem(f"{val:,.2f}".replace(",", ".")))
            table.setItem(row, 2, QTableWidgetItem(f"{percent:.2f}%"))

        table_layout.addWidget(table)
        layout.addWidget(table_frame, 1)
        
        # Close button más compacto
        close_button = QPushButton("Cerrar")
        close_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {PIRELLI_DARK};
                color: white;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
                font-size: 13px;
                min-width: 100px;
            }}
            QPushButton:hover {{
                background-color: {PIRELLI_DARK_LIGHT};
            }}
        """)
        close_button.clicked.connect(self.accept)
        
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(close_button)
        layout.addLayout(button_layout)

    def setup_window_geometry(self):
        """Configura el tamaño y posición de la ventana basado en la pantalla"""
        # Obtener información de la pantalla
        screen = QApplication.primaryScreen()
        screen_geometry = screen.availableGeometry()
        
        # Calcular tamaño de la ventana (65% del ancho y 75% del alto de la pantalla)
        window_width = int(screen_geometry.width() * 0.65)
        window_height = int(screen_geometry.height() * 0.75)
        
        # Limitar tamaños mínimos y máximos
        window_width = max(750, min(window_width, 1100))  # Entre 750px y 1100px
        window_height = max(550, min(window_height, 850))  # Entre 550px y 850px
        
        # Calcular posición para centrar
        x = (screen_geometry.width() - window_width) // 2
        y = (screen_geometry.height() - window_height) // 2
        
        # Aplicar geometría
        self.setGeometry(x, y, window_width, window_height)
        self.setMinimumSize(750, 550)

class AnimatedCard(QFrame):
    """Tarjeta base con animación de hover"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMouseTracking(True)
        self.setup_animation()
        self.setup_style()
        
    def setup_animation(self):
        """Configura la animación de hover"""
        self.hover_animation = QPropertyAnimation(self, b"geometry")
        self.hover_animation.setDuration(200)
        self.hover_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.original_geometry = None
        
    def setup_style(self):
        """Configura el estilo base de la tarjeta"""
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {CARD_BG};
                border-radius: 16px;
                border: 1px solid {CARD_BORDER};
            }}
        """)
        
        # Sombra
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setOffset(0, 3)
        shadow.setColor(QColor(0, 0, 0, 20))
        self.setGraphicsEffect(shadow)
        
    def enterEvent(self, event):
        """Animación al entrar el mouse"""
        if not self.original_geometry:
            self.original_geometry = self.geometry()
        
        target_geometry = self.geometry()
        target_geometry.setY(target_geometry.y() - 5)
        
        self.hover_animation.setStartValue(self.geometry())
        self.hover_animation.setEndValue(target_geometry)
        self.hover_animation.start()
        super().enterEvent(event)
        
    def leaveEvent(self, event):
        """Animación al salir el mouse"""
        if self.original_geometry:
            self.hover_animation.setStartValue(self.geometry())
            self.hover_animation.setEndValue(self.original_geometry)
            self.hover_animation.start()
        super().leaveEvent(event)

class StatisticCard(AnimatedCard):
    """Tarjeta de estadística mejorada"""
    clicked = pyqtSignal()
    
    def __init__(self, title, value, icon_path=None, color=PIRELLI_RED):
        super().__init__()
        self.title = title
        self.color = color
        self.setup_ui(title, value, icon_path, color)
        
    def setup_ui(self, title, value, icon_path, color):
        """Configura la interfaz de la tarjeta"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)
        
        # Icono circular
        if icon_path:
            icon_container = QFrame()
            icon_container.setFixedSize(64, 64)
            icon_container.setStyleSheet(f"""
                QFrame {{
                    background-color: {color}15;
                    border-radius: 32px;
                }}
            """)
            
            icon_layout = QHBoxLayout(icon_container)
            icon_layout.setContentsMargins(0, 0, 0, 0)
            
            icon_label = QLabel()
            icon_label.setPixmap(QIcon(icon_path).pixmap(QSize(32, 32)))
            icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            icon_layout.addWidget(icon_label)
            
            layout.addWidget(icon_container)
        
        # Contenido de texto
        text_layout = QVBoxLayout()
        text_layout.setSpacing(8)
        
        title_label = QLabel(title)
        title_label.setStyleSheet(f"""
            color: {PIRELLI_GRAY}; 
            font-size: 14px; 
            font-family: 'Segoe UI'; 
            font-weight: 500;
        """)
        
        self.value_label = QLabel(value)
        self.value_label.setFont(QFont("Segoe UI", 28, QFont.Weight.Bold))
        self.value_label.setStyleSheet(f"""
            color: {color}; 
            font-family: 'Segoe UI'; 
            letter-spacing: -0.5px;
        """)
        
        text_layout.addWidget(title_label)
        text_layout.addWidget(self.value_label)
        
        layout.addLayout(text_layout)
        layout.addStretch()
        
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setMinimumHeight(130)
        
    def update_value(self, new_value):
        """Actualiza el valor con animación"""
        self.value_label.setText(new_value)
        
        # Efecto de actualización
        self.value_label.setStyleSheet(f"""
            color: {self.color}; 
            font-family: 'Segoe UI'; 
            letter-spacing: -0.5px;
            background-color: {self.color}10;
            border-radius: 8px;
            padding: 4px;
        """)
        
        # Restaurar estilo después de 500ms
        QTimer.singleShot(500, self.restore_value_style)
        
    def restore_value_style(self):
        """Restaura el estilo normal del valor"""
        self.value_label.setStyleSheet(f"""
            color: {self.color}; 
            font-family: 'Segoe UI'; 
            letter-spacing: -0.5px;
        """)

class ChartCard(AnimatedCard):
    """Tarjeta de gráfico con funcionalidad completa de diálogos"""
    
    def __init__(self, title, chart_type="pie"):
        super().__init__()
        self.chart_type = chart_type
        self.chart_data = None
        self.setup_ui(title)
        self.create_chart()
        
    def setup_ui(self, title):
        """Configura la interfaz de la tarjeta"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)
        
        # Header con título y botón expandir
        header_layout = QHBoxLayout()
        
        title_label = QLabel(title)
        title_label.setStyleSheet(f"""
            color: {PIRELLI_DARK}; 
            font-size: 18px; 
            font-weight: bold; 
            font-family: 'Segoe UI';
        """)
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # Botón de expandir funcional
        expand_btn = QPushButton("🔍")
        expand_btn.setFixedSize(32, 32)
        expand_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {PIRELLI_LIGHT_GRAY};
                border-radius: 16px;
                border: none;
                font-size: 16px;
            }}
            QPushButton:hover {{
                background-color: {PIRELLI_RED};
                color: white;
            }}
        """)
        expand_btn.clicked.connect(self.show_detailed_dialog)
        header_layout.addWidget(expand_btn)
        
        layout.addLayout(header_layout)
        
        # Separador
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet(f"background-color: {CARD_BORDER}; margin: 8px 0;")
        layout.addWidget(separator)
        
        # Gráfico
        self.chart = QChart()
        self.chart.setAnimationOptions(QChart.AnimationOption.SeriesAnimations)
        self.chart.setTheme(QChart.ChartTheme.ChartThemeLight)
        self.chart.setBackgroundVisible(False)
        self.chart.legend().setVisible(True)
        self.chart.legend().setAlignment(Qt.AlignmentFlag.AlignBottom)
        self.chart.legend().setFont(QFont("Segoe UI", 10))
        
        self.chart_view = QChartView(self.chart)
        self.chart_view.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        self.chart_view.setMinimumHeight(300)
        
        layout.addWidget(self.chart_view)
        
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
    def create_chart(self):
        """Crea el gráfico según el tipo"""
        if self.chart_type == "pie":
            self.create_pie_chart()
        elif self.chart_type == "bar":
            self.create_bar_chart()
            
    def create_pie_chart(self, data=None):
        """Crea un gráfico de pastel"""
        self.chart.removeAllSeries()
        series = QPieSeries()
        
        if data:
            self.chart_data = data
            colors = [PIRELLI_RED, PIRELLI_DARK, PIRELLI_YELLOW, PIRELLI_GRAY, 
                     PIRELLI_RED_LIGHT, PIRELLI_DARK_LIGHT]
            
            for i, (material, valor) in enumerate(data.items()):
                val = float(valor)
                slice = series.append(material, val)
                color_idx = i % len(colors)
                slice.setBrush(QColor(colors[color_idx]))
                
                if i == 0:
                    slice.setExploded(True)
                    slice.setLabelVisible(True)
                    
                # Conectar eventos de hover
                slice.hovered.connect(lambda state, s=slice: self.on_slice_hovered(state, s))
        else:
            # Datos de ejemplo
            test_data = {"Caucho": 35, "Acero": 20, "Químicos": 15, "Otros": 30}
            self.create_pie_chart(test_data)
            return
            
        self.chart.addSeries(series)
        self.chart.setTitle("")
        
    def create_bar_chart(self, data=None):
        """Crea un gráfico de barras"""
        self.chart.removeAllSeries()
        
        if data:
            self.chart_data = data
            ventas = [float(v) if v else 0 for v in data.get("ventas", [])]
            produccion = [float(p) if p else 0 for p in data.get("produccion", [])]
            categorias = data.get("categorias", [])
        else:
            # Datos de ejemplo
            ventas = [50, 65, 70, 85, 60]
            produccion = [40, 55, 65, 70, 55]
            categorias = ["Ene", "Feb", "Mar", "Abr", "May"]
            self.chart_data = {
                "ventas": ventas,
                "produccion": produccion,
                "categorias": categorias
            }
            
        set0 = QBarSet("Ventas")
        set1 = QBarSet("Producción")
        set0.setColor(QColor(PIRELLI_RED))
        set1.setColor(QColor(PIRELLI_DARK))
        set0.append(ventas)
        set1.append(produccion)
        
        series = QBarSeries()
        series.append(set0)
        series.append(set1)
        self.chart.addSeries(series)
        
        axis_x = QBarCategoryAxis()
        axis_x.append(categorias)
        self.chart.addAxis(axis_x, Qt.AlignmentFlag.AlignBottom)
        series.attachAxis(axis_x)
        
        axis_y = QValueAxis()
        max_value = max(ventas + produccion) if (ventas + produccion) else 10
        axis_y.setRange(0, max_value * 1.1 if max_value > 0 else 10)
        axis_y.setLabelsFont(QFont("Segoe UI", 9))
        self.chart.addAxis(axis_y, Qt.AlignmentFlag.AlignLeft)
        series.attachAxis(axis_y)
        
        self.chart.setTitle("")
        
    def on_slice_hovered(self, state, slice):
        """Maneja el hover sobre las rebanadas del pie chart"""
        if state:
            label = slice.label()
            value = slice.value()
            percent = slice.percentage() * 100
            QToolTip.showText(
                self.chart_view.mapToGlobal(self.chart_view.cursor().pos()),
                f"<div style='background-color: white; padding: 8px; border-radius: 6px; border: 1px solid #ddd;'>"
                f"<b style='color: {PIRELLI_DARK}; font-size: 14px;'>{label}</b><br>"
                f"<span style='color: {PIRELLI_GRAY};'>Valor: {value}</span><br>"
                f"<span style='color: {PIRELLI_RED}; font-weight: bold;'>Porcentaje: {percent:.1f}%</span>"
                f"</div>"
            )
        else:
            QToolTip.hideText()
        
    def update_data(self, data):
        """Actualiza los datos del gráfico"""
        if self.chart_type == "pie":
            self.create_pie_chart(data)
        elif self.chart_type == "bar":
            self.create_bar_chart(data)
            
    def show_detailed_dialog(self):
        """Muestra el diálogo detallado correspondiente"""
        if not self.chart_data:
            QMessageBox.information(self, "Sin datos", "No hay datos disponibles para mostrar.")
            return
            
        try:
            if self.chart_type == "pie":
                dialog = MaterialDistributionDialog(self.chart_data, self)
                dialog.exec()
            elif self.chart_type == "bar":
                dialog = SalesVsProductionDialog(self.chart_data, self)
                dialog.exec()
        except Exception as e:
            logging.error(f"Error al mostrar diálogo: {e}")
            QMessageBox.critical(self, "Error", f"Error al mostrar los detalles: {str(e)}")

class ModernTable(QTableWidget):
    """Tabla moderna con estilo mejorado"""
    def __init__(self, headers, parent=None):
        super().__init__(parent)
        self.setColumnCount(len(headers))
        self.setHorizontalHeaderLabels(headers)
        self.setup_style()
        
    def setup_style(self):
        """Configura el estilo de la tabla"""
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.verticalHeader().setVisible(False)
        self.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.setAlternatingRowColors(True)
        self.setVerticalScrollMode(QTableWidget.ScrollMode.ScrollPerPixel)
        
        self.setStyleSheet(f"""
            QTableWidget {{
                background-color: {CARD_BG};
                font-family: 'Segoe UI';
                font-size: 13px;
                border: none;
                border-radius: 8px;
                gridline-color: {CARD_BORDER};
            }}
            QHeaderView::section {{
                background-color: {PIRELLI_DARK};
                color: white;
                font-weight: bold;
                font-size: 13px;
                border: none;
                padding: 12px 8px;
            }}
            QTableWidget::item {{
                padding: 12px 8px;
                border-bottom: 1px solid {CARD_BORDER};
            }}
            QTableWidget::item:selected {{
                background-color: {PIRELLI_RED}20;
                color: {PIRELLI_DARK};
            }}
            QTableWidget::item:hover {{
                background-color: {PIRELLI_LIGHT_GRAY}50;
            }}
            QScrollBar:vertical {{
                border: none;
                background: {PIRELLI_LIGHT_GRAY};
                width: 12px;
                border-radius: 6px;
            }}
            QScrollBar::handle:vertical {{
                background: {PIRELLI_GRAY};
                min-height: 20px;
                border-radius: 6px;
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
        """)

class DashboardView(QWidget):
    """Vista principal del dashboard con diálogos funcionales"""
    refresh_requested = pyqtSignal()
    
    def __init__(self, api_client):
        super().__init__()
        self.api_client = api_client
        self.setup_connections()
        self.init_ui()
        self.setup_timer()
        self.refresh_data()
        
    def setup_connections(self):
        """Configura las conexiones de señales"""
        self.api_client.data_received.connect(self.update_data)
        self.api_client.request_error.connect(self.handle_api_error)
        
    def setup_timer(self):
        """Configura el timer para actualizar la hora"""
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_time)
        self.timer.start(60000)  # Actualizar cada minuto
        
    def init_ui(self):
        """Inicializa la interfaz de usuario"""
        # Contenedor principal con scroll
        main_container = QWidget()
        main_container.setStyleSheet(f"""
            QWidget {{
                background-color: #f8f9fa;
                font-family: 'Segoe UI';
            }}
        """)
        
        self.main_layout = QVBoxLayout(main_container)
        self.main_layout.setSpacing(30)
        self.main_layout.setContentsMargins(36, 36, 36, 36)
        
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(main_container)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: #f8f9fa;
            }
            QScrollBar:vertical {
                border: none;
                background: #f0f0f0;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background: #c1c1c1;
                min-height: 20px;
                border-radius: 6px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(scroll_area)
        
        # Crear secciones
        self.create_header()
        self.create_controls()
        self.create_statistics_section()
        self.create_charts_section()
        self.create_activities_section()
        self.create_footer()
        
    def create_header(self):
        """Crea el header del dashboard con diseño más limpio y fecha centrada"""
        banner_frame = QFrame()
        banner_frame.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                    stop:0 {PIRELLI_DARK}, stop:1 {PIRELLI_DARK_LIGHT});
                border-radius: 20px;
                min-height: 100px;
            }}
        """)

        banner_shadow = QGraphicsDropShadowEffect()
        banner_shadow.setBlurRadius(30)
        banner_shadow.setOffset(0, 8)
        banner_shadow.setColor(QColor(0, 0, 0, 60))
        banner_frame.setGraphicsEffect(banner_shadow)

        banner_layout = QHBoxLayout(banner_frame)
        banner_layout.setContentsMargins(30, 20, 30, 20)
        banner_layout.setSpacing(50)
        # CAMBIO CLAVE: Asegurar alineación vertical centrada
        banner_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        # Logo
        logo_frame = QFrame()
        logo_frame.setFixedSize(220, 70)
        logo_frame.setStyleSheet(f"""
            QFrame {{
                background: {PIRELLI_RED};
                border-radius: 14px;
            }}
        """)

        logo_layout = QHBoxLayout(logo_frame)
        logo_layout.setContentsMargins(20, 0, 20, 0)

        logo_label = QLabel("PIRELLI ERP")
        logo_label.setStyleSheet("""
            color: white;
            font-size: 28px;
            font-weight: bold;
            font-family: 'Segoe UI', Arial, sans-serif;
        """)
        logo_layout.addWidget(logo_label, Qt.AlignmentFlag.AlignCenter)

        logo_shadow = QGraphicsDropShadowEffect()
        logo_shadow.setBlurRadius(25)
        logo_shadow.setOffset(0, 6)
        logo_shadow.setColor(QColor(0, 0, 0, 100))
        logo_frame.setGraphicsEffect(logo_shadow)

        banner_layout.addWidget(logo_frame, 0, Qt.AlignmentFlag.AlignVCenter)

        # Título directo (sin contenedor)
        title_label = QLabel("Sistema de Gestión Empresarial")
        title_label.setFont(QFont("Segoe UI", 15, QFont.Weight.Bold))
        title_label.setStyleSheet("background: transparent; color: white; letter-spacing: 1px;")
        # CAMBIO: Agregar alineación vertical al título
        banner_layout.addWidget(title_label, 1, Qt.AlignmentFlag.AlignVCenter)

        # Fecha y hora
        self.create_date_widget(banner_layout)

        self.main_layout.addWidget(banner_frame)


    def create_date_widget(self, parent_layout):
        """Crea el widget de fecha y hora más transparente y centrado"""
        date_frame = QFrame()
        # CAMBIO: Ajustar el tamaño para que coincida mejor con otros elementos
        date_frame.setFixedSize(200, 70)  # Usar setFixedSize en lugar de setMinimumSize
        date_frame.setStyleSheet(f"""
            QFrame {{
                background-color: rgba(255, 255, 255, 0.05);  
                border-radius: 10px;
            }}
        """)

        date_layout = QVBoxLayout(date_frame)
        # CAMBIO: Ajustar márgenes para centrado perfecto
        date_layout.setContentsMargins(10, 10, 10, 10)
        date_layout.setSpacing(0)
        date_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        fecha_actual, hora_actual = get_formatted_date()

        self.date_label = QLabel(fecha_actual)
        self.date_label.setStyleSheet("""
            background: transparent; 
            color: white; 
            font-size: 14px; 
            font-weight: bold;
        """)
        self.date_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.date_label.setWordWrap(False)

        self.time_label = QLabel(hora_actual)
        self.time_label.setStyleSheet("""
            background: transparent; 
            color: #e0e0e0; 
            font-size: 12px;
        """)
        self.time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.time_label.setWordWrap(False)

        date_layout.addWidget(self.date_label)
        date_layout.addWidget(self.time_label)

        # CAMBIO CLAVE: Agregar alineación vertical al widget de fecha
        parent_layout.addWidget(date_frame, 0, Qt.AlignmentFlag.AlignVCenter)
   
    def create_controls(self):
        """Crea los controles del dashboard"""
        controls_layout = QHBoxLayout()
        controls_layout.setContentsMargins(0, 10, 0, 10)
        
        # Período actual
        period_frame = QFrame()
        period_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {PIRELLI_LIGHT_GRAY}50;
                border-radius: 8px;
                padding: 8px 16px;
            }}
        """)
        
        period_layout = QHBoxLayout(period_frame)
        period_layout.setContentsMargins(16, 8, 16, 8)
        
        period_label = QLabel("Período actual: Q1 2025")
        period_label.setStyleSheet(f"""
            color: {PIRELLI_DARK}; 
            font-weight: bold; 
            font-size: 14px;
        """)
        period_layout.addWidget(period_label)
        
        controls_layout.addWidget(period_frame)
        controls_layout.addStretch()
        
        # Botón de actualización
        self.refresh_button = QPushButton(" Actualizar Dashboard")
        self.refresh_button.setIcon(QIcon("resources/icons/refresh.png"))
        self.refresh_button.clicked.connect(self.refresh_data)
        self.refresh_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {PIRELLI_RED};
                color: white;
                border-radius: 8px;
                padding: 12px 28px;
                font-weight: bold;
                font-family: 'Segoe UI';
                font-size: 14px;
            }}
            QPushButton:hover {{
                background-color: {PIRELLI_RED_DARK};
            }}
            QPushButton:pressed {{
                background-color: #800000;
            }}
            QPushButton:disabled {{
                background-color: {PIRELLI_GRAY};
            }}
        """)
        
        controls_layout.addWidget(self.refresh_button)
        self.main_layout.addLayout(controls_layout)
        
    def create_statistics_section(self):
        """Crea la sección de estadísticas"""
        section_title = QLabel("Indicadores Clave de Rendimiento")
        section_title.setStyleSheet(f"""
            color: {PIRELLI_DARK}; 
            font-size: 22px; 
            font-weight: bold; 
            margin-top: 10px; 
            margin-bottom: 10px;
        """)
        self.main_layout.addWidget(section_title)
        
        stats_layout = QGridLayout()
        stats_layout.setSpacing(24)
        
        # Crear tarjetas de estadísticas
        self.sales_card = StatisticCard(
            "Ventas Mensuales", "$0", 
            "resources/icons/sales.png", PIRELLI_DARK
        )
        
        self.production_card = StatisticCard(
            "Producción Mensual", "0 unidades", 
            "resources/icons/production.png", PIRELLI_DARK
        )
        
        self.inventory_card = StatisticCard(
            "Nivel de Inventario", "0%", 
            "resources/icons/inventory.png", PIRELLI_DARK
        )
        
        self.employees_card = StatisticCard(
            "Empleados Activos", "0", 
            "resources/icons/employee.png", PIRELLI_DARK
        )
        
        stats_layout.addWidget(self.sales_card, 0, 0)
        stats_layout.addWidget(self.production_card, 0, 1)
        stats_layout.addWidget(self.inventory_card, 1, 0)
        stats_layout.addWidget(self.employees_card, 1, 1)
        
        self.main_layout.addLayout(stats_layout)
        
    def create_charts_section(self):
        """Crea la sección de gráficos con diálogos funcionales"""
        section_title = QLabel("Análisis de Rendimiento")
        section_title.setStyleSheet(f"""
            color: {PIRELLI_DARK}; 
            font-size: 22px; 
            font-weight: bold; 
            margin-top: 20px; 
            margin-bottom: 10px;
        """)
        self.main_layout.addWidget(section_title)
        
        charts_layout = QHBoxLayout()
        charts_layout.setSpacing(24)
        
        # Gráfico de distribución de materiales con diálogo funcional
        self.materials_chart = ChartCard("Distribución de Materiales", "pie")
        self.materials_chart.setMinimumHeight(400)
        
        # Gráfico de ventas vs producción con diálogo funcional
        self.production_chart = ChartCard("Ventas vs Producción", "bar")
        self.production_chart.setMinimumHeight(400)
        
        charts_layout.addWidget(self.materials_chart)
        charts_layout.addWidget(self.production_chart)
        
        self.main_layout.addLayout(charts_layout)
        
    def create_activities_section(self):
        """Crea la sección de actividades recientes"""
        section_title = QLabel("Actividades Recientes")
        section_title.setStyleSheet(f"""
            color: {PIRELLI_DARK}; 
            font-size: 22px; 
            font-weight: bold; 
            margin-top: 20px; 
            margin-bottom: 10px;
        """)
        self.main_layout.addWidget(section_title)
        
        # Tabla de actividades
        self.activities_table = ModernTable([
            "Actividad", "Fecha", "Estado", "Detalles"
        ])
        self.activities_table.setMinimumHeight(300)
        
        # Frame contenedor
        activities_frame = AnimatedCard()
        activities_layout = QVBoxLayout(activities_frame)
        activities_layout.setContentsMargins(24, 24, 24, 24)
        
        # Header
        header_layout = QHBoxLayout()
        header_title = QLabel("Últimas Actualizaciones")
        header_title.setStyleSheet(f"""
            color: {PIRELLI_DARK}; 
            font-size: 18px; 
            font-weight: bold;
        """)
        header_layout.addWidget(header_title)
        
        header_layout.addStretch()
        
        view_all_btn = QPushButton("Ver Todo")
        view_all_btn.setStyleSheet(f"""
            QPushButton {{
                color: {PIRELLI_RED};
                background-color: transparent;
                border: 1px solid {PIRELLI_RED};
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 12px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {PIRELLI_RED};
                color: white;
            }}
        """)
        header_layout.addWidget(view_all_btn)
        
        activities_layout.addLayout(header_layout)
        
        # Separador
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet(f"background-color: {CARD_BORDER}; margin: 8px 0;")
        activities_layout.addWidget(separator)
        
        activities_layout.addWidget(self.activities_table)
        
        self.main_layout.addWidget(activities_frame)
        
    def create_footer(self):
        """Crea el footer del dashboard"""
        footer = QFrame()
        footer.setStyleSheet(f"""
            QFrame {{
                background-color: transparent;
                margin-top: 20px;
                padding-top: 20px;
                border-top: 1px solid {CARD_BORDER};
            }}
        """)
        
        footer_layout = QHBoxLayout(footer)
        footer_layout.setContentsMargins(0, 20, 0, 0)
        
        # Información de la empresa
        company_layout = QVBoxLayout()
        company_logo = QLabel("PIRELLI")
        company_logo.setStyleSheet(f"""
            color: {PIRELLI_RED}; 
            font-size: 18px; 
            font-weight: bold;
        """)
        
        company_text = QLabel("© 2025 Pirelli - Sistema de Gestión Empresarial - v.2.4.0")
        company_text.setStyleSheet(f"""
            color: {PIRELLI_GRAY}; 
            font-size: 12px;
        """)
        
        company_layout.addWidget(company_logo)
        company_layout.addWidget(company_text)
        footer_layout.addLayout(company_layout)
        
        footer_layout.addStretch()
        
        self.main_layout.addWidget(footer)
        
    def update_time(self):
        """Actualiza la fecha y hora"""
        fecha_actual, hora_actual = get_formatted_date()
        self.date_label.setText(fecha_actual)
        self.time_label.setText(hora_actual)
        
    def refresh_data(self):
        """Actualiza los datos del dashboard"""
        logging.info("Solicitando datos del dashboard...")
        
        if hasattr(self, "refresh_button"):
            self.refresh_button.setEnabled(False)
            self.refresh_button.setText(" Actualizando...")
            
        try:
            self.api_client.get_dashboard_data()
        except Exception as e:
            logging.exception("Error al solicitar datos del dashboard")
            self.show_error_message("Error de conexión", str(e))
            self.restore_refresh_button()
            
    def restore_refresh_button(self):
        """Restaura el botón de actualización"""
        if hasattr(self, "refresh_button"):
            self.refresh_button.setEnabled(True)
            self.refresh_button.setText(" Actualizar Dashboard")
            
    def update_data(self, data):
        """Actualiza los datos del dashboard"""
        logging.info(f"Datos recibidos: {data}")
        
        if not (isinstance(data, dict) and data.get('type') == 'dashboard' and 'data' in data):
            logging.info("Datos ignorados: no son del tipo dashboard")
            self.restore_refresh_button()
            return
            
        dashboard_data = data['data']
        
        try:
            # Actualizar estadísticas
            self.update_statistics(dashboard_data)
            
            # Actualizar gráficos
            self.update_charts(dashboard_data)
            
            # Actualizar actividades
            self.update_activities(dashboard_data)
            
            self.restore_refresh_button()
            logging.info("Dashboard actualizado correctamente")
            
        except Exception as e:
            logging.exception("Error al actualizar datos del dashboard")
            self.show_error_message("Error al actualizar", str(e))
            self.restore_refresh_button()
            
    def update_statistics(self, data):
        """Actualiza las tarjetas de estadísticas"""
        def format_number(val, decimals=0, prefix="", suffix=""):
            try:
                if val is None or val == "":
                    return "Sin datos"
                if isinstance(val, str):
                    val = float(val)
                if decimals == 0:
                    return f"{prefix}{int(val):,}{suffix}".replace(",", ".")
                else:
                    return f"{prefix}{val:,.{decimals}f}{suffix}".replace(",", ".")
            except Exception:
                return "Sin datos"
                
        # Actualizar valores
        ventas = format_number(data.get('ventas_mensuales', 0), 2, "$")
        produccion = format_number(data.get('produccion_mensual', 0), 0, "", " unidades")
        inventario = format_number(data.get('nivel_inventario', 0), 0, "", "%")
        empleados = format_number(data.get('empleados_activos', 0), 0)
        
        self.sales_card.update_value(ventas)
        self.production_card.update_value(produccion)
        self.inventory_card.update_value(inventario)
        self.employees_card.update_value(empleados)
        
    def update_charts(self, data):
        """Actualiza los gráficos"""
        # Actualizar gráfico de materiales
        if 'distribucion_materiales' in data:
            self.materials_chart.update_data(data['distribucion_materiales'])
            
        # Actualizar gráfico de ventas vs producción
        if 'ventas_vs_produccion' in data:
            self.production_chart.update_data(data['ventas_vs_produccion'])
            
    def update_activities(self, data):
        """Actualiza la tabla de actividades"""
        if 'actividades_recientes' in data:
            activities = data['actividades_recientes']
            self.activities_table.setRowCount(len(activities))
            
            for row, activity in enumerate(activities):
                self.activities_table.setItem(row, 0, QTableWidgetItem(
                    activity.get("titulo", "")
                ))
                self.activities_table.setItem(row, 1, QTableWidgetItem(
                    activity.get("tiempo", "")
                ))
                self.activities_table.setItem(row, 2, QTableWidgetItem(
                    activity.get("tipo", "").capitalize()
                ))
                self.activities_table.setItem(row, 3, QTableWidgetItem(
                    "Ver detalles"
                ))
                
    def handle_api_error(self, error_msg):
        """Maneja errores de la API"""
        logging.error(f"Error de API: {error_msg}")
        self.show_error_message("Error de API", error_msg)
        self.restore_refresh_button()
        
    def show_error_message(self, title, message):
        """Muestra un mensaje de error"""
        error_box = QMessageBox(self)
        error_box.setWindowTitle(title)
        error_box.setText(message)
        error_box.setIcon(QMessageBox.Icon.Critical)
        error_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        error_box.setStyleSheet(f"""
            QMessageBox {{
                background-color: {CARD_BG};
                font-family: 'Segoe UI';
            }}
            QLabel {{
                color: {PIRELLI_DARK};
                font-size: 14px;
                min-width: 300px;
            }}
            QPushButton {{
                background-color: {PIRELLI_RED};
                color: white;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
                font-size: 13px;
                min-width: 100px;
            }}
            QPushButton:hover {{
                background-color: {PIRELLI_RED_DARK};
            }}
        """)
        error_box.exec()