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
from PyQt6.QtCharts import QChart, QChartView, QPieSeries, QBarSeries, QBarSet, QBarCategoryAxis, QValueAxis, QLineSeries
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

# ==================== DIÁLOGOS EXISTENTES ====================

class SalesVsProductionDialog(QDialog):
    """Dialog to show sales vs production chart in detail with data table"""
    def __init__(self, data, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Detalles de Ventas vs Producción")
        self.setup_window_geometry()
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Title
        title_label = QLabel("Comparación Detallada de Ventas vs Producción")
        title_label.setStyleSheet(f"""
            font-family: 'Segoe UI';
            font-size: 20px;
            font-weight: bold;
            color: {PIRELLI_DARK};
            margin-bottom: 8px;
        """)
        layout.addWidget(title_label)

        # Chart
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
        chart_view.setFixedHeight(200)
        layout.addWidget(chart_view)

        # Table
        self.create_table(layout, categorias, ventas, produccion, 
                         ["Categoría", "Ventas", "Producción"],
                         "Detalles numéricos de ventas y producción")

        # Close button
        self.add_close_button(layout)

    def create_table(self, layout, data_rows, col1_data, col2_data, headers, title):
        """Crea una tabla con scroll optimizada"""
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
        
        table_title = QLabel(title)
        table_title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        table_title.setStyleSheet(f"color: {PIRELLI_DARK}; margin-bottom: 8px;")
        table_layout.addWidget(table_title)
        
        table = QTableWidget()
        table.setColumnCount(len(headers))
        table.setHorizontalHeaderLabels(headers)
        table.setRowCount(len(data_rows))
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        table.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
        table.setAlternatingRowColors(True)
        
        table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        table.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        # Altura dinámica
        row_height = 30
        header_height = 35
        min_height = 150
        max_height = 280
        
        if len(data_rows) > 7:
            table.setFixedHeight(max_height)
        else:
            calculated_height = header_height + (len(data_rows) * row_height) + 15
            table.setFixedHeight(max(min_height, calculated_height))
        
        table.setStyleSheet(self.get_table_style())
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table.verticalHeader().setVisible(False)

        # Llenar tabla
        for row, categoria in enumerate(data_rows):
            v = col1_data[row] if row < len(col1_data) else 0
            p = col2_data[row] if row < len(col2_data) else 0
            table.setItem(row, 0, QTableWidgetItem(str(categoria)))
            table.setItem(row, 1, QTableWidgetItem(f"{v:,.2f}".replace(",", ".")))
            table.setItem(row, 2, QTableWidgetItem(f"{p:,.2f}".replace(",", ".")))

        table_layout.addWidget(table)
        layout.addWidget(table_frame, 1)

    def get_table_style(self):
        return """
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
        """

    def add_close_button(self, layout):
        """Agrega botón de cerrar"""
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
        """Configura el tamaño y posición de la ventana"""
        screen = QApplication.primaryScreen()
        screen_geometry = screen.availableGeometry()
        
        window_width = int(screen_geometry.width() * 0.7)
        window_height = int(screen_geometry.height() * 0.8)
        
        window_width = max(800, min(window_width, 1200))
        window_height = max(600, min(window_height, 900))
        
        x = (screen_geometry.width() - window_width) // 2
        y = (screen_geometry.height() - window_height) // 2
        
        self.setGeometry(x, y, window_width, window_height)
        self.setMinimumSize(800, 600)

class MaterialDistributionDialog(QDialog):
    """Dialog to show material distribution in detail with data table"""
    def __init__(self, data, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Detalles de Distribución de Materiales")
        self.setup_window_geometry()
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Title
        title_label = QLabel("Distribución Detallada de Materiales")
        title_label.setStyleSheet(f"""
            font-family: 'Segoe UI';
            font-size: 20px;
            font-weight: bold;
            color: {PIRELLI_DARK};
            margin-bottom: 8px;
        """)
        layout.addWidget(title_label)
        
        # Chart
        chart = QChart()
        chart.setAnimationOptions(QChart.AnimationOption.SeriesAnimations)
        chart.setTheme(QChart.ChartTheme.ChartThemeLight)
        chart.setBackgroundVisible(False)
        chart.legend().setVisible(True)
        chart.legend().setAlignment(Qt.AlignmentFlag.AlignBottom)
        chart.legend().setFont(QFont("Segoe UI", 10))
        series = QPieSeries()
        total = sum(float(v) for v in data.values() if v)
        
        colors = [PIRELLI_RED, PIRELLI_DARK, PIRELLI_YELLOW, PIRELLI_GRAY, 
                 PIRELLI_RED_LIGHT, PIRELLI_DARK_LIGHT, PIRELLI_YELLOW_LIGHT]
        
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
        chart_view.setFixedHeight(200)
        layout.addWidget(chart_view)
        
        # Table
        self.create_material_table(layout, data, total)
        self.add_close_button(layout)

    def create_material_table(self, layout, data, total):
        """Crea tabla de materiales"""
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
        
        table = QTableWidget()
        table.setColumnCount(3)
        table.setHorizontalHeaderLabels(["Material", "Valor", "Porcentaje"])
        table.setRowCount(len(data))
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        table.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
        table.setAlternatingRowColors(True)
        
        table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        table.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        if len(data) > 7:
            table.setFixedHeight(280)
        else:
            calculated_height = 35 + (len(data) * 30) + 15
            table.setFixedHeight(max(150, calculated_height))
        
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

        for row, (material, valor) in enumerate(data.items()):
            val = float(valor)
            percent = (val / total * 100) if total else 0
            table.setItem(row, 0, QTableWidgetItem(str(material)))
            table.setItem(row, 1, QTableWidgetItem(f"{val:,.2f}".replace(",", ".")))
            table.setItem(row, 2, QTableWidgetItem(f"{percent:.2f}%"))

        table_layout.addWidget(table)
        layout.addWidget(table_frame, 1)

    def add_close_button(self, layout):
        """Agrega botón de cerrar"""
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
        """Configura el tamaño y posición de la ventana"""
        screen = QApplication.primaryScreen()
        screen_geometry = screen.availableGeometry()
        
        window_width = int(screen_geometry.width() * 0.65)
        window_height = int(screen_geometry.height() * 0.75)
        
        window_width = max(750, min(window_width, 1100))
        window_height = max(550, min(window_height, 850))
        
        x = (screen_geometry.width() - window_width) // 2
        y = (screen_geometry.height() - window_height) // 2
        
        self.setGeometry(x, y, window_width, window_height)
        self.setMinimumSize(750, 550)

# ==================== NUEVOS DIÁLOGOS ====================

class QualityControlDialog(QDialog):
    """Análisis de control de calidad"""
    def __init__(self, data, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Análisis de Control de Calidad")
        self.setup_window_geometry()
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Title
        title_label = QLabel("Control de Calidad Detallado")
        title_label.setStyleSheet(f"""
            font-family: 'Segoe UI';
            font-size: 20px;
            font-weight: bold;
            color: {PIRELLI_DARK};
            margin-bottom: 8px;
        """)
        layout.addWidget(title_label)
        
        # Pie Chart
        chart = QChart()
        chart.setAnimationOptions(QChart.AnimationOption.SeriesAnimations)
        chart.setTheme(QChart.ChartTheme.ChartThemeLight)
        chart.setBackgroundVisible(False)
        chart.legend().setVisible(True)
        chart.legend().setAlignment(Qt.AlignmentFlag.AlignBottom)
        
        series = QPieSeries()
        colors = [PIRELLI_DARK, PIRELLI_RED, PIRELLI_YELLOW]
        labels = ["Aprobado", "Rechazado", "Reparación"]
        
        total = sum(data.values()) if data.values() else 1
        for i, (estado, cantidad) in enumerate(data.items()):
            slice = series.append(f"{labels[i]}: {cantidad}", cantidad)
            slice.setBrush(QColor(colors[i % len(colors)]))
            if i == 0:
                slice.setExploded(True)
        
        chart.addSeries(series)
        chart_view = QChartView(chart)
        chart_view.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        chart_view.setFixedHeight(200)
        layout.addWidget(chart_view)
        
        # Table
        self.create_quality_table(layout, data)
        self.add_close_button(layout)

    def create_quality_table(self, layout, data):
        """Crea tabla de control de calidad"""
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
        
        table_title = QLabel("Detalles de control de calidad")
        table_title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        table_title.setStyleSheet(f"color: {PIRELLI_DARK}; margin-bottom: 8px;")
        table_layout.addWidget(table_title)
        
        table = QTableWidget()
        table.setColumnCount(3)
        table.setHorizontalHeaderLabels(["Estado", "Cantidad", "Porcentaje"])
        table.setRowCount(len(data))
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        table.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
        table.setAlternatingRowColors(True)
        
        table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        table.setFixedHeight(200)
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

        total = sum(data.values()) if data.values() else 1
        estados = ["Aprobado", "Rechazado", "Reparación"]
        
        for row, (estado, cantidad) in enumerate(data.items()):
            percent = (cantidad / total * 100) if total else 0
            table.setItem(row, 0, QTableWidgetItem(estados[row] if row < len(estados) else estado))
            table.setItem(row, 1, QTableWidgetItem(str(cantidad)))
            table.setItem(row, 2, QTableWidgetItem(f"{percent:.1f}%"))

        table_layout.addWidget(table)
        layout.addWidget(table_frame, 1)

    def add_close_button(self, layout):
        """Agrega botón de cerrar"""
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
        """Configura el tamaño y posición de la ventana"""
        screen = QApplication.primaryScreen()
        screen_geometry = screen.availableGeometry()
        
        window_width = int(screen_geometry.width() * 0.65)
        window_height = int(screen_geometry.height() * 0.75)
        
        window_width = max(750, min(window_width, 1100))
        window_height = max(550, min(window_height, 850))
        
        x = (screen_geometry.width() - window_width) // 2
        y = (screen_geometry.height() - window_height) // 2
        
        self.setGeometry(x, y, window_width, window_height)
        self.setMinimumSize(750, 550)

class InventoryAnalysisDialog(QDialog):
    """Análisis de inventario y stock crítico"""
    def __init__(self, data, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Análisis de Inventario")
        self.setup_window_geometry()
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Title
        title_label = QLabel("Análisis de Stock e Inventario")
        title_label.setStyleSheet(f"""
            font-family: 'Segoe UI';
            font-size: 20px;
            font-weight: bold;
            color: {PIRELLI_DARK};
            margin-bottom: 8px;
        """)
        layout.addWidget(title_label)
        
        # Bar Chart
        chart = QChart()
        chart.setAnimationOptions(QChart.AnimationOption.SeriesAnimations)
        chart.setTheme(QChart.ChartTheme.ChartThemeLight)
        chart.setBackgroundVisible(False)
        chart.legend().setVisible(True)
        
        materiales = list(data.keys())[:8]  # Primeros 8 materiales
        stock_actual = [data[m].get('actual', 0) for m in materiales]
        stock_minimo = [data[m].get('minimo', 0) for m in materiales]
        
        set0 = QBarSet("Stock Actual")
        set1 = QBarSet("Stock Mínimo")
        set0.setColor(QColor(PIRELLI_DARK))
        set1.setColor(QColor(PIRELLI_RED))
        set0.append(stock_actual)
        set1.append(stock_minimo)
        
        series = QBarSeries()
        series.append(set0)
        series.append(set1)
        chart.addSeries(series)
        
        axis_x = QBarCategoryAxis()
        axis_x.append(materiales)
        chart.addAxis(axis_x, Qt.AlignmentFlag.AlignBottom)
        series.attachAxis(axis_x)
        
        axis_y = QValueAxis()
        max_value = max(stock_actual + stock_minimo) if (stock_actual + stock_minimo) else 10
        axis_y.setRange(0, max_value * 1.1)
        chart.addAxis(axis_y, Qt.AlignmentFlag.AlignLeft)
        series.attachAxis(axis_y)
        
        chart_view = QChartView(chart)
        chart_view.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        chart_view.setFixedHeight(200)
        layout.addWidget(chart_view)
        
        # Table
        self.create_inventory_table(layout, data)
        self.add_close_button(layout)

    def create_inventory_table(self, layout, data):
        """Crea tabla de inventario"""
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
        
        table_title = QLabel("Estado detallado del inventario")
        table_title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        table_title.setStyleSheet(f"color: {PIRELLI_DARK}; margin-bottom: 8px;")
        table_layout.addWidget(table_title)
        
        table = QTableWidget()
        table.setColumnCount(4)
        table.setHorizontalHeaderLabels(["Material", "Stock Actual", "Stock Mínimo", "Estado"])
        table.setRowCount(len(data))
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        table.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
        table.setAlternatingRowColors(True)
        
        table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        if len(data) > 7:
            table.setFixedHeight(280)
        else:
            table.setFixedHeight(max(150, 35 + len(data) * 30 + 15))
        
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

        for row, (material, info) in enumerate(data.items()):
            actual = info.get('actual', 0)
            minimo = info.get('minimo', 0)
            estado = "⚠️ Crítico" if actual <= minimo else "✅ Normal"
            
            table.setItem(row, 0, QTableWidgetItem(material))
            table.setItem(row, 1, QTableWidgetItem(str(actual)))
            table.setItem(row, 2, QTableWidgetItem(str(minimo)))
            table.setItem(row, 3, QTableWidgetItem(estado))

        table_layout.addWidget(table)
        layout.addWidget(table_frame, 1)

    def add_close_button(self, layout):
        """Agrega botón de cerrar"""
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
        """Configura el tamaño y posición de la ventana"""
        screen = QApplication.primaryScreen()
        screen_geometry = screen.availableGeometry()
        
        window_width = int(screen_geometry.width() * 0.7)
        window_height = int(screen_geometry.height() * 0.8)
        
        window_width = max(800, min(window_width, 1200))
        window_height = max(600, min(window_height, 900))
        
        x = (screen_geometry.width() - window_width) // 2
        y = (screen_geometry.height() - window_height) // 2
        
        self.setGeometry(x, y, window_width, window_height)
        self.setMinimumSize(800, 600)

class EmployeePerformanceDialog(QDialog):
    """Análisis de rendimiento de empleados"""
    def __init__(self, data, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Análisis de Rendimiento de Empleados")
        self.setup_window_geometry()
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Title
        title_label = QLabel("Rendimiento de Empleados por Área")
        title_label.setStyleSheet(f"""
            font-family: 'Segoe UI';
            font-size: 20px;
            font-weight: bold;
            color: {PIRELLI_DARK};
            margin-bottom: 8px;
        """)
        layout.addWidget(title_label)
        
        # Bar Chart
        chart = QChart()
        chart.setAnimationOptions(QChart.AnimationOption.SeriesAnimations)
        chart.setTheme(QChart.ChartTheme.ChartThemeLight)
        chart.setBackgroundVisible(False)
        chart.legend().setVisible(True)
        
        areas = list(data.keys())
        empleados = [data[area].get('empleados', 0) for area in areas]
        asistencias = [data[area].get('asistencias', 0) for area in areas]
        
        set0 = QBarSet("Empleados")
        set1 = QBarSet("Asistencias")
        set0.setColor(QColor(PIRELLI_DARK))
        set1.setColor(QColor(PIRELLI_RED))
        set0.append(empleados)
        set1.append(asistencias)
        
        series = QBarSeries()
        series.append(set0)
        series.append(set1)
        chart.addSeries(series)
        
        axis_x = QBarCategoryAxis()
        axis_x.append(areas)
        chart.addAxis(axis_x, Qt.AlignmentFlag.AlignBottom)
        series.attachAxis(axis_x)
        
        axis_y = QValueAxis()
        max_value = max(empleados + asistencias) if (empleados + asistencias) else 10
        axis_y.setRange(0, max_value * 1.1)
        chart.addAxis(axis_y, Qt.AlignmentFlag.AlignLeft)
        series.attachAxis(axis_y)
        
        chart_view = QChartView(chart)
        chart_view.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        chart_view.setFixedHeight(200)
        layout.addWidget(chart_view)
        
        # Table
        self.create_employee_table(layout, data)
        self.add_close_button(layout)

    def create_employee_table(self, layout, data):
        """Crea tabla de empleados"""
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
        
        table_title = QLabel("Rendimiento detallado por área")
        table_title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        table_title.setStyleSheet(f"color: {PIRELLI_DARK}; margin-bottom: 8px;")
        table_layout.addWidget(table_title)
        
        table = QTableWidget()
        table.setColumnCount(4)
        table.setHorizontalHeaderLabels(["Área", "Empleados", "Asistencias", "% Asistencia"])
        table.setRowCount(len(data))
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        table.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
        table.setAlternatingRowColors(True)
        
        table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        if len(data) > 7:
            table.setFixedHeight(280)
        else:
            table.setFixedHeight(max(150, 35 + len(data) * 30 + 15))
        
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

        for row, (area, info) in enumerate(data.items()):
            empleados = info.get('empleados', 0)
            asistencias = info.get('asistencias', 0)
            porcentaje = (asistencias / empleados * 100) if empleados > 0 else 0
            
            table.setItem(row, 0, QTableWidgetItem(area))
            table.setItem(row, 1, QTableWidgetItem(str(empleados)))
            table.setItem(row, 2, QTableWidgetItem(str(asistencias)))
            table.setItem(row, 3, QTableWidgetItem(f"{porcentaje:.1f}%"))

        table_layout.addWidget(table)
        layout.addWidget(table_frame, 1)

    def add_close_button(self, layout):
        """Agrega botón de cerrar"""
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
        """Configura el tamaño y posición de la ventana"""
        screen = QApplication.primaryScreen()
        screen_geometry = screen.availableGeometry()
        
        window_width = int(screen_geometry.width() * 0.7)
        window_height = int(screen_geometry.height() * 0.8)
        
        window_width = max(800, min(window_width, 1200))
        window_height = max(600, min(window_height, 900))
        
        x = (screen_geometry.width() - window_width) // 2
        y = (screen_geometry.height() - window_height) // 2
        
        self.setGeometry(x, y, window_width, window_height)
        self.setMinimumSize(800, 600)

class CustomerAnalysisDialog(QDialog):
    """Análisis de clientes por segmento"""
    def __init__(self, data, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Análisis de Clientes")
        self.setup_window_geometry()
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Title
        title_label = QLabel("Análisis de Clientes por Segmento")
        title_label.setStyleSheet(f"""
            font-family: 'Segoe UI';
            font-size: 20px;
            font-weight: bold;
            color: {PIRELLI_DARK};
            margin-bottom: 8px;
        """)
        layout.addWidget(title_label)
        
        # Pie Chart
        chart = QChart()
        chart.setAnimationOptions(QChart.AnimationOption.SeriesAnimations)
        chart.setTheme(QChart.ChartTheme.ChartThemeLight)
        chart.setBackgroundVisible(False)
        chart.legend().setVisible(True)
        
        series = QPieSeries()
        colors = [PIRELLI_RED, PIRELLI_DARK, PIRELLI_YELLOW, PIRELLI_GRAY]
        total = sum(data.values()) if data.values() else 1
        
        for i, (tipo, ventas) in enumerate(data.items()):
            slice = series.append(f"{tipo}: ${ventas:,.0f}", ventas)
            slice.setBrush(QColor(colors[i % len(colors)]))
            if i == 0:
                slice.setExploded(True)
        
        chart.addSeries(series)
        chart_view = QChartView(chart)
        chart_view.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        chart_view.setFixedHeight(200)
        layout.addWidget(chart_view)
        
        # Table
        self.create_customer_table(layout, data)
        self.add_close_button(layout)

    def create_customer_table(self, layout, data):
        """Crea tabla de clientes"""
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
        
        table_title = QLabel("Ventas por tipo de cliente")
        table_title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        table_title.setStyleSheet(f"color: {PIRELLI_DARK}; margin-bottom: 8px;")
        table_layout.addWidget(table_title)
        
        table = QTableWidget()
        table.setColumnCount(3)
        table.setHorizontalHeaderLabels(["Tipo Cliente", "Ventas", "Porcentaje"])
        table.setRowCount(len(data))
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        table.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
        table.setAlternatingRowColors(True)
        
        table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        table.setFixedHeight(200)
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

        total = sum(data.values()) if data.values() else 1
        for row, (tipo, ventas) in enumerate(data.items()):
            percent = (ventas / total * 100) if total else 0
            table.setItem(row, 0, QTableWidgetItem(tipo.title()))
            table.setItem(row, 1, QTableWidgetItem(f"${ventas:,.2f}"))
            table.setItem(row, 2, QTableWidgetItem(f"{percent:.1f}%"))

        table_layout.addWidget(table)
        layout.addWidget(table_frame, 1)

    def add_close_button(self, layout):
        """Agrega botón de cerrar"""
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
        """Configura el tamaño y posición de la ventana"""
        screen = QApplication.primaryScreen()
        screen_geometry = screen.availableGeometry()
        
        window_width = int(screen_geometry.width() * 0.65)
        window_height = int(screen_geometry.height() * 0.75)
        
        window_width = max(750, min(window_width, 1100))
        window_height = max(550, min(window_height, 850))
        
        x = (screen_geometry.width() - window_width) // 2
        y = (screen_geometry.height() - window_height) // 2
        
        self.setGeometry(x, y, window_width, window_height)
        self.setMinimumSize(750, 550)

class MaintenanceAnalysisDialog(QDialog):
    """Análisis de mantenimiento"""
    def __init__(self, data, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Análisis de Mantenimiento")
        self.setup_window_geometry()
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Title
        title_label = QLabel("Análisis de Mantenimiento de Equipos")
        title_label.setStyleSheet(f"""
            font-family: 'Segoe UI';
            font-size: 20px;
            font-weight: bold;
            color: {PIRELLI_DARK};
            margin-bottom: 8px;
        """)
        layout.addWidget(title_label)
        
        # Bar Chart
        chart = QChart()
        chart.setAnimationOptions(QChart.AnimationOption.SeriesAnimations)
        chart.setTheme(QChart.ChartTheme.ChartThemeLight)
        chart.setBackgroundVisible(False)
        chart.legend().setVisible(True)
        
        tipos = list(data.keys())
        cantidades = [data[tipo].get('cantidad', 0) for tipo in tipos]
        costos = [data[tipo].get('costo', 0) / 1000 for tipo in tipos]  # En miles
        
        set0 = QBarSet("Cantidad")
        set1 = QBarSet("Costo (K)")
        set0.setColor(QColor(PIRELLI_DARK))
        set1.setColor(QColor(PIRELLI_RED))
        set0.append(cantidades)
        set1.append(costos)
        
        series = QBarSeries()
        series.append(set0)
        series.append(set1)
        chart.addSeries(series)
        
        axis_x = QBarCategoryAxis()
        axis_x.append([t.title() for t in tipos])
        chart.addAxis(axis_x, Qt.AlignmentFlag.AlignBottom)
        series.attachAxis(axis_x)
        
        axis_y = QValueAxis()
        max_value = max(cantidades + costos) if (cantidades + costos) else 10
        axis_y.setRange(0, max_value * 1.1)
        chart.addAxis(axis_y, Qt.AlignmentFlag.AlignLeft)
        series.attachAxis(axis_y)
        
        chart_view = QChartView(chart)
        chart_view.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        chart_view.setFixedHeight(200)
        layout.addWidget(chart_view)
        
        # Table
        self.create_maintenance_table(layout, data)
        self.add_close_button(layout)

    def create_maintenance_table(self, layout, data):
        """Crea tabla de mantenimiento"""
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
        
        table_title = QLabel("Detalles de mantenimiento")
        table_title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        table_title.setStyleSheet(f"color: {PIRELLI_DARK}; margin-bottom: 8px;")
        table_layout.addWidget(table_title)
        
        table = QTableWidget()
        table.setColumnCount(4)
        table.setHorizontalHeaderLabels(["Tipo", "Cantidad", "Costo Total", "Costo Promedio"])
        table.setRowCount(len(data))
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        table.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
        table.setAlternatingRowColors(True)
        
        table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        table.setFixedHeight(200)
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

        for row, (tipo, info) in enumerate(data.items()):
            cantidad = info.get('cantidad', 0)
            costo = info.get('costo', 0)
            promedio = costo / cantidad if cantidad > 0 else 0
            
            table.setItem(row, 0, QTableWidgetItem(tipo.title()))
            table.setItem(row, 1, QTableWidgetItem(str(cantidad)))
            table.setItem(row, 2, QTableWidgetItem(f"${costo:,.2f}"))
            table.setItem(row, 3, QTableWidgetItem(f"${promedio:,.2f}"))

        table_layout.addWidget(table)
        layout.addWidget(table_frame, 1)

    def add_close_button(self, layout):
        """Agrega botón de cerrar"""
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
        """Configura el tamaño y posición de la ventana"""
        screen = QApplication.primaryScreen()
        screen_geometry = screen.availableGeometry()
        
        window_width = int(screen_geometry.width() * 0.65)
        window_height = int(screen_geometry.height() * 0.75)
        
        window_width = max(750, min(window_width, 1100))
        window_height = max(550, min(window_height, 850))
        
        x = (screen_geometry.width() - window_width) // 2
        y = (screen_geometry.height() - window_height) // 2
        
        self.setGeometry(x, y, window_width, window_height)
        self.setMinimumSize(750, 550)

class FinancialAnalysisDialog(QDialog):
    """Análisis financiero"""
    def __init__(self, data, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Análisis Financiero")
        self.setup_window_geometry()
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Title
        title_label = QLabel("Análisis Financiero - Ingresos vs Gastos")
        title_label.setStyleSheet(f"""
            font-family: 'Segoe UI';
            font-size: 20px;
            font-weight: bold;
            color: {PIRELLI_DARK};
            margin-bottom: 8px;
        """)
        layout.addWidget(title_label)
        
        # Line Chart
        chart = QChart()
        chart.setAnimationOptions(QChart.AnimationOption.SeriesAnimations)
        chart.setTheme(QChart.ChartTheme.ChartThemeLight)
        chart.setBackgroundVisible(False)
        chart.legend().setVisible(True)
        
        ingresos_series = QLineSeries()
        gastos_series = QLineSeries()
        
        ingresos = data.get("ingresos", [])
        gastos = data.get("gastos", [])
        categorias = data.get("categorias", [])
        
        for i, categoria in enumerate(categorias):
            if i < len(ingresos):
                ingresos_series.append(i, ingresos[i])
            if i < len(gastos):
                gastos_series.append(i, gastos[i])
        
        ingresos_series.setName("Ingresos")
        gastos_series.setName("Gastos")
        ingresos_series.setColor(QColor(PIRELLI_DARK))
        gastos_series.setColor(QColor(PIRELLI_RED))
        
        chart.addSeries(ingresos_series)
        chart.addSeries(gastos_series)
        
        axis_x = QBarCategoryAxis()
        axis_x.append(categorias)
        chart.addAxis(axis_x, Qt.AlignmentFlag.AlignBottom)
        ingresos_series.attachAxis(axis_x)
        gastos_series.attachAxis(axis_x)
        
        axis_y = QValueAxis()
        max_value = max(ingresos + gastos) if (ingresos + gastos) else 10
        axis_y.setRange(0, max_value * 1.1)
        chart.addAxis(axis_y, Qt.AlignmentFlag.AlignLeft)
        ingresos_series.attachAxis(axis_y)
        gastos_series.attachAxis(axis_y)
        
        chart_view = QChartView(chart)
        chart_view.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        chart_view.setFixedHeight(200)
        layout.addWidget(chart_view)
        
        # Table
        self.create_financial_table(layout, data)
        self.add_close_button(layout)

    def create_financial_table(self, layout, data):
        """Crea tabla financiera"""
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
        
        table_title = QLabel("Análisis financiero detallado")
        table_title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        table_title.setStyleSheet(f"color: {PIRELLI_DARK}; margin-bottom: 8px;")
        table_layout.addWidget(table_title)
        
        table = QTableWidget()
        table.setColumnCount(4)
        table.setHorizontalHeaderLabels(["Período", "Ingresos", "Gastos", "Margen"])
        
        ingresos = data.get("ingresos", [])
        gastos = data.get("gastos", [])
        categorias = data.get("categorias", [])
        
        table.setRowCount(len(categorias))
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        table.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
        table.setAlternatingRowColors(True)
        
        table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        if len(categorias) > 7:
            table.setFixedHeight(280)
        else:
            table.setFixedHeight(max(150, 35 + len(categorias) * 30 + 15))
        
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

        for row, categoria in enumerate(categorias):
            ingreso = ingresos[row] if row < len(ingresos) else 0
            gasto = gastos[row] if row < len(gastos) else 0
            margen = ingreso - gasto
            
            table.setItem(row, 0, QTableWidgetItem(categoria))
            table.setItem(row, 1, QTableWidgetItem(f"${ingreso:,.2f}"))
            table.setItem(row, 2, QTableWidgetItem(f"${gasto:,.2f}"))
            table.setItem(row, 3, QTableWidgetItem(f"${margen:,.2f}"))

        table_layout.addWidget(table)
        layout.addWidget(table_frame, 1)

    def add_close_button(self, layout):
        """Agrega botón de cerrar"""
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
        """Configura el tamaño y posición de la ventana"""
        screen = QApplication.primaryScreen()
        screen_geometry = screen.availableGeometry()
        
        window_width = int(screen_geometry.width() * 0.7)
        window_height = int(screen_geometry.height() * 0.8)
        
        window_width = max(800, min(window_width, 1200))
        window_height = max(600, min(window_height, 900))
        
        x = (screen_geometry.width() - window_width) // 2
        y = (screen_geometry.height() - window_height) // 2
        
        self.setGeometry(x, y, window_width, window_height)
        self.setMinimumSize(800, 600)

# ==================== COMPONENTES PRINCIPALES ====================

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
    
    def __init__(self, title, chart_type="pie", dialog_type="material"):
        super().__init__()
        self.chart_type = chart_type
        self.dialog_type = dialog_type
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
        elif self.chart_type == "line":
            self.create_line_chart()
            
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
            # Datos de ejemplo según el tipo de diálogo
            if self.dialog_type == "material":
                test_data = {"Caucho": 35, "Acero": 20, "Químicos": 15, "Otros": 30}
            elif self.dialog_type == "quality":
                test_data = {"Aprobado": 85, "Rechazado": 10, "Reparación": 5}
            elif self.dialog_type == "customer":
                test_data = {"Distribuidor": 45000, "Mayorista": 32000, "Minorista": 18000, "OEM": 25000}
            else:
                test_data = {"Item 1": 35, "Item 2": 20, "Item 3": 15, "Item 4": 30}
            self.create_pie_chart(test_data)
            return
            
        self.chart.addSeries(series)
        self.chart.setTitle("")
        
    def create_bar_chart(self, data=None):
        """Crea un gráfico de barras"""
        self.chart.removeAllSeries()
        
        if data:
            self.chart_data = data
            if self.dialog_type == "sales":
                ventas = [float(v) if v else 0 for v in data.get("ventas", [])]
                produccion = [float(p) if p else 0 for p in data.get("produccion", [])]
                categorias = data.get("categorias", [])
            elif self.dialog_type == "inventory":
                materiales = list(data.keys())[:8]
                ventas = [data[m].get('actual', 0) for m in materiales]
                produccion = [data[m].get('minimo', 0) for m in materiales]
                categorias = materiales
            elif self.dialog_type == "employee":
                areas = list(data.keys())
                ventas = [data[area].get('empleados', 0) for area in areas]
                produccion = [data[area].get('asistencias', 0) for area in areas]
                categorias = areas
            elif self.dialog_type == "maintenance":
                tipos = list(data.keys())
                ventas = [data[tipo].get('cantidad', 0) for tipo in tipos]
                produccion = [data[tipo].get('costo', 0) / 1000 for tipo in tipos]
                categorias = [t.title() for t in tipos]
            else:
                ventas = [50, 65, 70, 85, 60]
                produccion = [40, 55, 65, 70, 55]
                categorias = ["Ene", "Feb", "Mar", "Abr", "May"]
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
            
        set0 = QBarSet("Ventas" if self.dialog_type == "sales" else "Primario")
        set1 = QBarSet("Producción" if self.dialog_type == "sales" else "Secundario")
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

    def create_line_chart(self, data=None):
        """Crea un gráfico de líneas"""
        self.chart.removeAllSeries()
        
        if data:
            self.chart_data = data
            ingresos = data.get("ingresos", [])
            gastos = data.get("gastos", [])
            categorias = data.get("categorias", [])
        else:
            # Datos de ejemplo
            ingresos = [120000, 135000, 128000, 145000, 152000, 148000]
            gastos = [95000, 102000, 98000, 115000, 118000, 112000]
            categorias = ["Ene", "Feb", "Mar", "Abr", "May", "Jun"]
            self.chart_data = {
                "ingresos": ingresos,
                "gastos": gastos,
                "categorias": categorias
            }
        
        ingresos_series = QLineSeries()
        gastos_series = QLineSeries()
        
        for i, categoria in enumerate(categorias):
            if i < len(ingresos):
                ingresos_series.append(i, ingresos[i])
            if i < len(gastos):
                gastos_series.append(i, gastos[i])
        
        ingresos_series.setName("Ingresos")
        gastos_series.setName("Gastos")
        ingresos_series.setColor(QColor(PIRELLI_DARK))
        gastos_series.setColor(QColor(PIRELLI_RED))
        
        self.chart.addSeries(ingresos_series)
        self.chart.addSeries(gastos_series)
        
        axis_x = QBarCategoryAxis()
        axis_x.append(categorias)
        self.chart.addAxis(axis_x, Qt.AlignmentFlag.AlignBottom)
        ingresos_series.attachAxis(axis_x)
        gastos_series.attachAxis(axis_x)
        
        axis_y = QValueAxis()
        max_value = max(ingresos + gastos) if (ingresos + gastos) else 10
        axis_y.setRange(0, max_value * 1.1)
        self.chart.addAxis(axis_y, Qt.AlignmentFlag.AlignLeft)
        ingresos_series.attachAxis(axis_y)
        gastos_series.attachAxis(axis_y)
        
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
        """Actualiza los datos del gráfico con validación"""
        if not data:
            logging.warning(f"No hay datos para el gráfico {self.dialog_type}")
            return
            
        try:
            self.chart_data = data
            if self.chart_type == "pie":
                self.create_pie_chart(data)
            elif self.chart_type == "bar":
                self.create_bar_chart(data)
            elif self.chart_type == "line":
                self.create_line_chart(data)
        except Exception as e:
            logging.error(f"Error al actualizar gráfico {self.dialog_type}: {e}")
            # Usar datos de ejemplo en caso de error
            self.create_chart()
            
    def show_detailed_dialog(self):
        """Muestra el diálogo detallado correspondiente"""
        if not self.chart_data:
            QMessageBox.information(self, "Sin datos", "No hay datos disponibles para mostrar.")
            return
            
        try:
            if self.dialog_type == "material":
                dialog = MaterialDistributionDialog(self.chart_data, self)
            elif self.dialog_type == "sales":
                dialog = SalesVsProductionDialog(self.chart_data, self)
            elif self.dialog_type == "quality":
                dialog = QualityControlDialog(self.chart_data, self)
            elif self.dialog_type == "inventory":
                dialog = InventoryAnalysisDialog(self.chart_data, self)
            elif self.dialog_type == "employee":
                dialog = EmployeePerformanceDialog(self.chart_data, self)
            elif self.dialog_type == "customer":
                dialog = CustomerAnalysisDialog(self.chart_data, self)
            elif self.dialog_type == "maintenance":
                dialog = MaintenanceAnalysisDialog(self.chart_data, self)
            elif self.dialog_type == "financial":
                dialog = FinancialAnalysisDialog(self.chart_data, self)
            else:
                dialog = MaterialDistributionDialog(self.chart_data, self)
            
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
    """Vista principal del dashboard con análisis completos"""
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
        """Crea el header del dashboard"""
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

        # Título
        title_label = QLabel("Sistema de Gestión Empresarial")
        title_label.setFont(QFont("Segoe UI", 15, QFont.Weight.Bold))
        title_label.setStyleSheet("background: transparent; color: white; letter-spacing: 1px;")
        banner_layout.addWidget(title_label, 1, Qt.AlignmentFlag.AlignVCenter)

        # Fecha y hora
        self.create_date_widget(banner_layout)
        self.main_layout.addWidget(banner_frame)

    def create_date_widget(self, parent_layout):
        """Crea el widget de fecha y hora"""
        date_frame = QFrame()
        date_frame.setFixedSize(200, 70)
        date_frame.setStyleSheet(f"""
            QFrame {{
                background-color: rgba(255, 255, 255, 0.05);  
                border-radius: 10px;
            }}
        """)

        date_layout = QVBoxLayout(date_frame)
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
        """Crea la sección expandida de análisis de rendimiento"""
        section_title = QLabel("Análisis de Rendimiento Completo")
        section_title.setStyleSheet(f"""
            color: {PIRELLI_DARK}; 
            font-size: 22px; 
            font-weight: bold; 
            margin-top: 20px; 
            margin-bottom: 10px;
        """)
        self.main_layout.addWidget(section_title)
        
        # Primera fila: Análisis básicos
        charts_layout_1 = QHBoxLayout()
        charts_layout_1.setSpacing(24)
        
        self.materials_chart = ChartCard("Distribución de Materiales", "pie", "material")
        self.materials_chart.setMinimumHeight(400)
        
        self.production_chart = ChartCard("Ventas vs Producción", "bar", "sales")
        self.production_chart.setMinimumHeight(400)
        
        charts_layout_1.addWidget(self.materials_chart)
        charts_layout_1.addWidget(self.production_chart)
        self.main_layout.addLayout(charts_layout_1)
        
        # Segunda fila: Control de calidad e inventario
        charts_layout_2 = QHBoxLayout()
        charts_layout_2.setSpacing(24)
        
        self.quality_chart = ChartCard("Control de Calidad", "pie", "quality")
        self.quality_chart.setMinimumHeight(400)
        
        self.inventory_chart = ChartCard("Análisis de Inventario", "bar", "inventory")
        self.inventory_chart.setMinimumHeight(400)
        
        charts_layout_2.addWidget(self.quality_chart)
        charts_layout_2.addWidget(self.inventory_chart)
        self.main_layout.addLayout(charts_layout_2)
        
        # Tercera fila: Empleados y clientes
        charts_layout_3 = QHBoxLayout()
        charts_layout_3.setSpacing(24)
        
        self.employee_chart = ChartCard("Rendimiento de Empleados", "bar", "employee")
        self.employee_chart.setMinimumHeight(400)
        
        self.customer_chart = ChartCard("Análisis de Clientes", "pie", "customer")
        self.customer_chart.setMinimumHeight(400)
        
        charts_layout_3.addWidget(self.employee_chart)
        charts_layout_3.addWidget(self.customer_chart)
        self.main_layout.addLayout(charts_layout_3)
        
        # Cuarta fila: Mantenimiento y finanzas
        charts_layout_4 = QHBoxLayout()
        charts_layout_4.setSpacing(24)
        
        self.maintenance_chart = ChartCard("Análisis de Mantenimiento", "bar", "maintenance")
        self.maintenance_chart.setMinimumHeight(400)
        
        self.financial_chart = ChartCard("Análisis Financiero", "line", "financial")
        self.financial_chart.setMinimumHeight(400)
        
        charts_layout_4.addWidget(self.maintenance_chart)
        charts_layout_4.addWidget(self.financial_chart)
        self.main_layout.addLayout(charts_layout_4)
        
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
        
        company_text = QLabel("© 2025 Pirelli - Sistema de Gestión Empresarial - v.2.5.0")
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
        """Actualiza todos los gráficos"""
        # Gráficos existentes
        if 'distribucion_materiales' in data:
            self.materials_chart.update_data(data['distribucion_materiales'])
            
        if 'ventas_vs_produccion' in data:
            self.production_chart.update_data(data['ventas_vs_produccion'])
            
        # Nuevos gráficos
        if 'control_calidad' in data:
            self.quality_chart.update_data(data['control_calidad'])
            
        if 'materiales_stock_bajo' in data:
        # Ya viene como diccionario del backend
            self.inventory_chart.update_data(data['materiales_stock_bajo'])
            
        if 'empleados_por_area' in data:
        # Ya viene como diccionario del backend
            self.employee_chart.update_data(data['empleados_por_area'])
            
        if 'clientes_por_tipo' in data:
            # Ya viene como diccionario del backend
            self.customer_chart.update_data(data['clientes_por_tipo'])
            
        if 'mantenimiento_equipos' in data:
            # Ya viene como diccionario del backend
            self.maintenance_chart.update_data(data['mantenimiento_equipos'])
            
        if 'analisis_financiero' in data:
            # Ya viene como diccionario del backend
            self.financial_chart.update_data(data['analisis_financiero'])
            
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