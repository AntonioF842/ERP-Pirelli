from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QGridLayout, QSizePolicy, QScrollArea, QMessageBox,
    QGraphicsDropShadowEffect, QSpacerItem, QDialog, QToolTip,
    QTableWidget, QTableWidgetItem, QHeaderView
)
from datetime import datetime
import locale
from PyQt6.QtCore import Qt, QSize, pyqtSignal, QPropertyAnimation, QEasingCurve, QPoint, QTimer
from PyQt6.QtGui import QFont, QIcon, QPainter, QColor, QLinearGradient, QPalette, QBrush, QPixmap
from PyQt6.QtCharts import QChart, QChartView, QPieSeries, QBarSeries, QBarSet, QBarCategoryAxis, QValueAxis
import logging

# Basic logging configuration: only errors and warnings
logging.basicConfig(level=logging.WARNING, format='%(asctime)s %(levelname)s %(message)s')

# Function to get formatted date and time in Spanish
def get_formatted_date():
    """Gets the current date formatted in Spanish"""
    now = datetime.now()
    
    # Try to use locale first
    try:
        locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')  # For Linux/Mac
        date = now.strftime("%d de %B, %Y")
        time = now.strftime("%H:%M")
    except:
        try:
            locale.setlocale(locale.LC_TIME, 'Spanish_Spain.1252')  # For Windows
            date = now.strftime("%d de %B, %Y")
            time = now.strftime("%H:%M")
        except:
            # Manual approach if locale fails
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

# Improved Pirelli colors
PIRELLI_RED = "#D50000"
PIRELLI_RED_LIGHT = "#FF5252"
PIRELLI_RED_DARK = "#B71C1C"
PIRELLI_YELLOW = "#FFCD00"
PIRELLI_YELLOW_LIGHT = "#FFE082"
PIRELLI_DARK = "#1A1A1A"
PIRELLI_DARK_LIGHT = "#424242"
PIRELLI_GRAY = "#666666"
PIRELLI_LIGHT_GRAY = "#E6E6E6"
CARD_BG = "#FFFFFF"  # Lighter background for cards
CARD_BORDER = "#EEEEEE"  # Subtle border for cards

class AnimatedFrame(QFrame):
    """Frame with hover animation"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMouseTracking(True)
        self.hover_animation = QPropertyAnimation(self, b"geometry")
        self.hover_animation.setDuration(150)
        self.hover_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.original_geometry = None
        
    def enterEvent(self, event):
        if not self.original_geometry:
            self.original_geometry = self.geometry()
        target_geometry = self.geometry()
        target_geometry.setY(target_geometry.y() - 3)
        
        self.hover_animation.setStartValue(self.geometry())
        self.hover_animation.setEndValue(target_geometry)
        self.hover_animation.start()
        super().enterEvent(event)
        
    def leaveEvent(self, event):
        if self.original_geometry:
            self.hover_animation.setStartValue(self.geometry())
            self.hover_animation.setEndValue(self.original_geometry)
            self.hover_animation.start()
        super().leaveEvent(event)

class StatisticCard(AnimatedFrame):
    """Card to display a statistic with improved Pirelli visual style"""
    def __init__(self, title, value, icon_path=None, color=PIRELLI_RED):
        super().__init__()
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {CARD_BG};
                border-radius: 16px;
                border: 1px solid {CARD_BORDER};
            }}
        """)
        # Shadow
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setOffset(0, 3)
        shadow.setColor(QColor(0, 0, 0, 20))
        self.setGraphicsEffect(shadow)
        # Layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        # Circular icon
        if icon_path:
            icon_label = QLabel()
            pixmap = QIcon(icon_path).pixmap(QSize(42, 42))
            icon_label.setPixmap(pixmap)
            icon_label.setFixedSize(64, 64)
            icon_label.setStyleSheet(f"""
                background-color: {color}15;
                border-radius: 32px;
                margin-right: 20px;
                padding: 10px;
            """)
            layout.addWidget(icon_label)
        # Content
        text_layout = QVBoxLayout()
        text_layout.setSpacing(8)
        title_label = QLabel(title)
        title_label.setStyleSheet(f"color: {PIRELLI_GRAY}; font-size: 15px; font-family: 'Segoe UI'; font-weight: 500;")
        self.value_label = QLabel(value)
        self.value_label.setFont(QFont("Segoe UI", 28, QFont.Weight.Bold))
        self.value_label.setObjectName("value_label")
        self.value_label.setStyleSheet(f"color: {color}; font-family: 'Segoe UI'; letter-spacing: -0.5px;")
        text_layout.addWidget(title_label)
        text_layout.addWidget(self.value_label)
        layout.addLayout(text_layout)
        layout.addStretch()
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setMinimumHeight(130)

class SalesVsProductionDialog(QDialog):
    """Dialog to show sales vs production chart in detail with data table"""
    def __init__(self, data, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Sales vs Production Details")
        self.setMinimumSize(1000, 700)  # Increase minimum size
        self.resize(1100, 800)  # Set a larger initial size
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)

        # Title with style
        title_label = QLabel("Detailed Sales vs Production Comparison")
        title_label.setStyleSheet(f"""
            font-family: 'Segoe UI';
            font-size: 22px;
            font-weight: bold;
            color: {PIRELLI_DARK};
            margin-bottom: 10px;
        """)
        layout.addWidget(title_label)

        # Large chart
        chart = QChart()
        chart.setAnimationOptions(QChart.AnimationOption.SeriesAnimations)
        chart.setTheme(QChart.ChartTheme.ChartThemeLight)
        chart.setBackgroundVisible(False)
        chart.legend().setVisible(True)
        chart.legend().setAlignment(Qt.AlignmentFlag.AlignBottom)
        chart.legend().setFont(QFont("Segoe UI", 12))

        ventas = [float(v) if v else 0 for v in data.get("ventas", [])]
        produccion = [float(p) if p else 0 for p in data.get("produccion", [])]
        categorias = data.get("categorias", [f"Item {i+1}" for i in range(max(len(ventas), len(produccion)))])

        set0 = QBarSet("Sales")
        set1 = QBarSet("Production")
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
        axis_y.setLabelsFont(QFont("Segoe UI", 10))
        chart.addAxis(axis_y, Qt.AlignmentFlag.AlignLeft)
        series.attachAxis(axis_y)

        chart_view = QChartView(chart)
        chart_view.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        chart_view.setMinimumHeight(350)
        layout.addWidget(chart_view)

        # Detailed table
        table_frame = QFrame()
        table_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {CARD_BG};
                border-radius: 12px;
                border: 1px solid {CARD_BORDER};
            }}
        """)
        table_layout = QVBoxLayout(table_frame)
        table_layout.setContentsMargins(20, 20, 20, 20)
        
        table_title = QLabel("Numerical details of sales and production")
        table_title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        table_title.setStyleSheet(f"color: {PIRELLI_DARK}; margin-bottom: 10px;")
        table_layout.addWidget(table_title)
        
        table = QTableWidget()
        table.setColumnCount(3)
        table.setHorizontalHeaderLabels(["Category", "Sales", "Production"])
        table.setRowCount(len(categorias))
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        table.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
        table.setAlternatingRowColors(True)
        table.setMinimumHeight(300)  # Minimum height for the table
        table.setStyleSheet("""
            QTableWidget {
                background-color: #FFFFFF;
                font-family: 'Segoe UI';
                font-size: 14px;
                border: none;
            }
            QHeaderView::section {
                background-color: #1A1A1A;
                color: white;
                font-weight: bold;
                font-size: 14px;
                border: none;
                padding: 8px;
            }
            QTableWidget::item {
                padding: 8px;
            }
            QTableWidget::item:selected {
                background-color: #F5F5F5;
            }
        """)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table.verticalHeader().setVisible(False)

        for row, categoria in enumerate(categorias):
            v = ventas[row] if row < len(ventas) else 0
            p = produccion[row] if row < len(produccion) else 0
            table.setItem(row, 0, QTableWidgetItem(str(categoria)))
            table.setItem(row, 1, QTableWidgetItem(f"{v:,.2f}".replace(",", ".")))
            table.setItem(row, 2, QTableWidgetItem(f"{p:,.2f}".replace(",", ".")))

        table_layout.addWidget(table)
        layout.addWidget(table_frame)

        # Close button
        close_button = QPushButton("Close")
        close_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {PIRELLI_DARK};
                color: white;
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 14px;
                min-width: 120px;
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

class MaterialDistributionDialog(QDialog):
    """Dialog to show material distribution in detail with data table"""
    def __init__(self, data, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Material Distribution Details")
        self.setMinimumSize(900, 700)  # Increase minimum size
        self.resize(1000, 800)  # Set a larger initial size
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)
        
        # Title with style
        title_label = QLabel("Detailed Material Distribution")
        title_label.setStyleSheet(f"""
            font-family: 'Segoe UI';
            font-size: 22px;
            font-weight: bold;
            color: {PIRELLI_DARK};
            margin-bottom: 10px;
        """)
        layout.addWidget(title_label)
        
        # Large chart
        chart = QChart()
        chart.setAnimationOptions(QChart.AnimationOption.SeriesAnimations)
        chart.setTheme(QChart.ChartTheme.ChartThemeLight)
        chart.setBackgroundVisible(False)
        chart.legend().setVisible(True)
        chart.legend().setAlignment(Qt.AlignmentFlag.AlignBottom)
        chart.legend().setFont(QFont("Segoe UI", 12))
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
        chart_view.setMinimumHeight(350)
        layout.addWidget(chart_view)
        
        # Detailed table
        table_frame = QFrame()
        table_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {CARD_BG};
                border-radius: 12px;
                border: 1px solid {CARD_BORDER};
            }}
        """)
        table_layout = QVBoxLayout(table_frame)
        table_layout.setContentsMargins(20, 20, 20, 20)
        
        table_title = QLabel("Numerical details of material distribution")
        table_title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        table_title.setStyleSheet(f"color: {PIRELLI_DARK}; margin-bottom: 10px;")
        table_layout.addWidget(table_title)
        
        table = QTableWidget()
        table.setColumnCount(3)
        table.setHorizontalHeaderLabels(["Material", "Value", "Percentage"])
        table.setRowCount(len(data))
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        table.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
        table.setAlternatingRowColors(True)
        table.setMinimumHeight(300)  # Minimum height for the table
        table.setStyleSheet("""
            QTableWidget {
                background-color: #FFFFFF;
                font-family: 'Segoe UI';
                font-size: 14px;
                border: none;
            }
            QHeaderView::section {
                background-color: #1A1A1A;
                color: white;
                font-weight: bold;
                font-size: 14px;
                border: none;
                padding: 8px;
            }
            QTableWidget::item {
                padding: 8px;
            }
            QTableWidget::item:selected {
                background-color: #F5F5F5;
            }
        """)

        for row, (material, valor) in enumerate(data.items()):
            val = float(valor)
            percent = (val / total * 100) if total else 0
            table.setItem(row, 0, QTableWidgetItem(str(material)))
            table.setItem(row, 1, QTableWidgetItem(f"{val:,.2f}".replace(",", ".")))
            table.setItem(row, 2, QTableWidgetItem(f"{percent:.2f}%"))

        table_layout.addWidget(table)
        layout.addWidget(table_frame)
        
        # Close button
        close_button = QPushButton("Close")
        close_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {PIRELLI_DARK};
                color: white;
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 14px;
                min-width: 120px;
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

class ChartCard(AnimatedFrame):
    """Card to display a chart with Pirelli style and advanced interaction"""
    def __init__(self, title, chart_type="pie"):
        super().__init__()
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {CARD_BG};
                border-radius: 16px;
                border: 1px solid {CARD_BORDER};
            }}
        """)
        # Shadow
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setOffset(0, 3)
        shadow.setColor(QColor(0, 0, 0, 20))
        self.setGraphicsEffect(shadow)
        # Layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        # Title
        title_layout = QHBoxLayout()
        title_label = QLabel(title)
        title_label.setStyleSheet(f"color: {PIRELLI_DARK}; font-size: 18px; font-weight: bold; font-family: 'Segoe UI';")
        title_layout.addWidget(title_label)
        
        # Expand button
        expand_btn = QPushButton()
        expand_btn.setIcon(QIcon("resources/icons/expand.png"))
        expand_btn.setFixedSize(28, 28)
        expand_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {PIRELLI_LIGHT_GRAY};
                border-radius: 14px;
                border: none;
            }}
            QPushButton:hover {{
                background-color: {PIRELLI_GRAY}40;
            }}
        """)
        title_layout.addWidget(expand_btn)
        layout.addLayout(title_layout)
        
        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet(f"background-color: {CARD_BORDER}; margin: 8px 0;")
        layout.addWidget(separator)
        
        # Create the chart
        self.chart = QChart()
        self.chart.setAnimationOptions(QChart.AnimationOption.SeriesAnimations)
        self.chart.setTheme(QChart.ChartTheme.ChartThemeLight)
        self.chart.setBackgroundVisible(False)
        self.chart.legend().setVisible(True)
        self.chart.legend().setAlignment(Qt.AlignmentFlag.AlignBottom)
        self.chart.legend().setFont(QFont("Segoe UI", 10))
        # Create chart view
        self.chart_view = QChartView(self.chart)
        self.chart_view.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        layout.addWidget(self.chart_view)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        # Properties for interactivity
        self.chart_type = chart_type
        self.material_data = None  # To store current data
        self.series = None
        # Add test data based on chart type
        if chart_type == "pie":
            self.create_pie_chart()
            expand_btn.clicked.connect(self.on_expand_pie_clicked)
        elif chart_type == "bar":
            self.create_bar_chart()
            expand_btn.clicked.connect(self.on_expand_bar_clicked)
        # Events for interaction
        self.chart_view.setMouseTracking(True)
        self.chart_view.viewport().installEventFilter(self)

    def create_pie_chart(self, data=None):
        """Creates a pie chart with real or test data and Pirelli colors"""
        self.chart.removeAllSeries()
        series = QPieSeries()
        if data:
            self.material_data = data
            colors = [PIRELLI_RED, PIRELLI_DARK, PIRELLI_YELLOW, PIRELLI_GRAY, 
                     PIRELLI_RED_LIGHT, PIRELLI_DARK_LIGHT, PIRELLI_YELLOW_LIGHT]
            for i, (material, valor) in enumerate(data.items()):
                val = float(valor)
                slice = series.append(material, val)
                # Pirelli brand colors
                color_idx = i % len(colors)
                slice.setBrush(QColor(colors[color_idx]))
                if i == 0:
                    slice.setExploded(True)
                    slice.setLabelVisible(True)
        else:
            # Test data
            series.append("Rubber", 35)
            series.append("Steel", 20)
            series.append("Chemicals", 15)
            series.append("Others", 30)
            # Pirelli brand colors
            slices = series.slices()
            if len(slices) > 0:
                slices[0].setBrush(QColor(PIRELLI_RED))
                slices[0].setExploded(True)
                slices[0].setLabelVisible(True)
            if len(slices) > 1:
                slices[1].setBrush(QColor(PIRELLI_DARK))
            if len(slices) > 2:
                slices[2].setBrush(QColor(PIRELLI_YELLOW))
            if len(slices) > 3:
                slices[3].setBrush(QColor(PIRELLI_GRAY))
        self.chart.addSeries(series)
        self.series = series
        self.chart.setTitle("")
        # Connect events
        for slice in series.slices():
            # PyQt6: hovered signal passes (bool) but we need to know the slice, so use lambda
            slice.hovered.connect(lambda state, s=slice: self.on_slice_hovered(state, s))
            slice.clicked.connect(self.on_slice_clicked)

    def eventFilter(self, obj, event):
        # Allows the chart to receive mouse events
        return super().eventFilter(obj, event)

    def on_slice_hovered(self, state, slice):
        # Show detailed tooltip on mouse hover
        if state:
            label = slice.label()
            value = slice.value()
            percent = slice.percentage() * 100
            QToolTip.showText(self.chart_view.mapToGlobal(self.chart_view.cursor().pos()),
                f"<div style='background-color: white; padding: 8px; border-radius: 6px; border: 1px solid #ddd;'>"
                f"<b style='color: {PIRELLI_DARK}; font-size: 14px;'>{label}</b><br>"
                f"<span style='color: {PIRELLI_GRAY};'>Value: {value}</span><br>"
                f"<span style='color: {PIRELLI_RED}; font-weight: bold;'>Percentage: {percent:.1f}%</span>"
                f"</div>")
        else:
            QToolTip.hideText()

    def on_slice_clicked(self):
        # Show expanded dialog on click
        self.on_expand_pie_clicked()

    def on_expand_pie_clicked(self):
        if self.material_data:
            dlg = MaterialDistributionDialog(self.material_data, self)
            dlg.exec()

    def create_bar_chart(self, data=None):
        """Creates a bar chart with real or test data and Pirelli colors"""
        self.chart.removeAllSeries()
        if data:
            ventas = [float(v) if v else 0 for v in data.get("ventas", [])]
            produccion = [float(p) if p else 0 for p in data.get("produccion", [])]
            categorias = data.get("categorias", [f"Item {i+1}" for i in range(max(len(ventas), len(produccion)))])
        else:
            ventas = [50, 65, 70, 85, 60]
            produccion = [40, 55, 65, 70, 55]
            categorias = ["Jan", "Feb", "Mar", "Apr", "May"]

        set0 = QBarSet("Sales")
        set1 = QBarSet("Production")
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
        
        # Save data for detailed dialog
        self.bar_data = {
            "ventas": ventas,
            "produccion": produccion,
            "categorias": categorias
        }
        
        # Connect click event on chart view
        self.chart_view.mousePressEvent = self.on_bar_chart_clicked
        
    def on_bar_chart_clicked(self, event):
        # Show expanded dialog on chart click
        self.on_expand_bar_clicked()
        
    def on_expand_bar_clicked(self):
        if hasattr(self, "bar_data") and self.bar_data and self.chart_type == "bar":
            dlg = SalesVsProductionDialog(self.bar_data, self)
            dlg.exec()

class AttendancePieChart(ChartCard):
    """Pie chart to show attendance"""
    def __init__(self):
        super().__init__("Monthly Attendance", "pie")
        
    def update_data(self, data):
        series = QPieSeries()
        present = data.get("presente", 0)
        absent = data.get("ausente", 0)
        late = data.get("tardanza", 0)
        
        if present > 0:
            slice = series.append("Present", present)
            slice.setColor(QColor("#4CAF50"))  # Green
            slice.setLabelVisible(True)
            slice.setExploded(True)
        
        if absent > 0:
            slice = series.append("Absent", absent)
            slice.setColor(QColor("#F44336"))  # Red
        
        if late > 0:
            slice = series.append("Late", late)
            slice.setColor(QColor("#FFC107"))  # Yellow
        
        self.chart.removeAllSeries()
        self.chart.addSeries(series)
        
        # Connect events
        for slice in series.slices():
            slice.hovered.connect(lambda state, s=slice: self.on_slice_hovered(state, s))

class TopProductsChart(ChartCard):
    """Bar chart for top selling products"""
    def __init__(self):
        super().__init__("Top Selling Products", "bar")
        
    def update_data(self, data):
        self.chart.removeAllSeries()
        
        if not data:
            return
            
        set0 = QBarSet("Sales")
        set0.setColor(QColor(PIRELLI_RED))
        
        categories = []
        for product in data:
            set0.append(product["cantidad"])
            categories.append(product["nombre"][:15] + "..." if len(product["nombre"]) > 15 else product["nombre"])
        
        series = QBarSeries()
        series.append(set0)
        self.chart.addSeries(series)
        
        axis_x = QBarCategoryAxis()
        axis_x.append(categories)
        self.chart.addAxis(axis_x, Qt.AlignmentFlag.AlignBottom)
        series.attachAxis(axis_x)

        axis_y = QValueAxis()
        max_value = max([p["cantidad"] for p in data]) if data else 10
        axis_y.setRange(0, max_value * 1.1)
        axis_y.setLabelsFont(QFont("Segoe UI", 9))
        self.chart.addAxis(axis_y, Qt.AlignmentFlag.AlignLeft)
        series.attachAxis(axis_y)

class AssetsStatusChart(ChartCard):
    """Pie chart for assets status"""
    def __init__(self):
        super().__init__("Assets Status", "pie")
        
    def update_data(self, data):
        series = QPieSeries()
        
        for item in data:
            estado = item["estado"]
            cantidad = item["cantidad"]
            
            if cantidad > 0:
                slice = series.append(estado.capitalize(), cantidad)
                
                # Assign colors based on status
                if estado == "operativo":
                    slice.setColor(QColor("#4CAF50"))  # Green
                elif estado == "mantenimiento":
                    slice.setColor(QColor("#FF9800"))  # Orange
                else:  # baja
                    slice.setColor(QColor("#F44336"))  # Red
                
                if estado == "operativo":
                    slice.setLabelVisible(True)
                    slice.setExploded(True)
        
        self.chart.removeAllSeries()
        self.chart.addSeries(series)
        
        # Connect events
        for slice in series.slices():
            slice.hovered.connect(lambda state, s=slice: self.on_slice_hovered(state, s))

class IncidentsTable(QTableWidget):
    """Table to display recent incidents"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setColumnCount(4)
        self.setHorizontalHeaderLabels(["ID", "Type", "Date", "Status"])
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.verticalHeader().setVisible(False)
        self.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
        self.setAlternatingRowColors(True)
        self.setVerticalScrollMode(QTableWidget.ScrollMode.ScrollPerPixel)  # Smooth scrolling
        self.setStyleSheet("""
            QTableWidget {
                background-color: #FFFFFF;
                font-family: 'Segoe UI';
                font-size: 13px;
                border: none;
                border-radius: 8px;
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
                border-bottom: 1px solid #EEEEEE;
            }
            QTableWidget::item:selected {
                background-color: #F5F5F5;
            }
            QScrollBar:vertical {
                border: none;
                background: #f0f0f0;
                width: 10px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background: #c1c1c1;
                min-height: 20px;
                border-radius: 5px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
        
    def load_data(self, incidents):
        self.setRowCount(len(incidents))
        for row, incident in enumerate(incidents):
            self.setItem(row, 0, QTableWidgetItem(str(incident.get("id", ""))))
            self.setItem(row, 1, QTableWidgetItem(incident.get("tipo", "").capitalize()))
            self.setItem(row, 2, QTableWidgetItem(incident.get("fecha", "")))
            
            status_item = QTableWidgetItem(incident.get("estado", "").capitalize())
            if incident.get("estado") == "resuelto":
                status_item.setForeground(QColor("#4CAF50"))
            elif incident.get("estado") == "investigacion":
                status_item.setForeground(QColor("#FFC107"))
            else:  # reportado
                status_item.setForeground(QColor("#F44336"))
            self.setItem(row, 3, status_item)

class DashboardView(QWidget):
    """Dashboard view with Pirelli style"""
    refresh_requested = pyqtSignal()

    def __init__(self, api_client):
        super().__init__()
        try:
            self.api_client = api_client
            self.api_client.data_received.connect(self.update_data)
            self.api_client.request_error.connect(self.handle_api_error)
            self.init_ui()
            self.refresh_data()
        except Exception as e:
            logging.exception("Error in DashboardView.__init__")
            self.show_error_message("Critical error initializing dashboard", str(e))

    def init_ui(self):
        """Initializes the UI with improved Pirelli style"""
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
                width: 10px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background: #c1c1c1;
                min-height: 20px;
                border-radius: 5px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(scroll_area)

        # Top Banner with Pirelli Logo
        banner_frame = QFrame()
        # Gradient for the banner
        banner_frame.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {PIRELLI_DARK}, stop:1 {PIRELLI_DARK_LIGHT});
                border-radius: 16px;
                min-height: 120px;
            }}
        """)
        banner_layout = QHBoxLayout(banner_frame)
        banner_layout.setContentsMargins(36, 24, 36, 24)
        
        # Logo with shadow effect
        logo_frame = QFrame()
        logo_frame.setFixedSize(180, 60)
        logo_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {PIRELLI_RED};
                border-radius: 10px;
            }}
        """)
        logo_layout = QHBoxLayout(logo_frame)
        logo_layout.setContentsMargins(16, 0, 16, 0)
        
        logo_label = QLabel("PIRELLI ERP")
        logo_label.setStyleSheet("""
            color: white;
            font-size: 28px;
            font-weight: bold;
            font-family: 'Segoe UI';
        """)
        logo_layout.addWidget(logo_label)
        
        # Shadow for the logo
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setOffset(0, 5)
        shadow.setColor(QColor(0, 0, 0, 80))
        logo_frame.setGraphicsEffect(shadow)
        
        banner_layout.addWidget(logo_frame)
        
        title_box = QVBoxLayout()
        title_label = QLabel("Dashboard")
        title_label.setFont(QFont("Segoe UI", 26, QFont.Weight.Bold))
        title_label.setStyleSheet("color: white;")
        subtitle_label = QLabel("Enterprise Management System")
        subtitle_label.setStyleSheet("color: #e0e0e0; font-size: 15px;")
        title_box.addWidget(title_label)
        title_box.addWidget(subtitle_label)
        banner_layout.addLayout(title_box)
        banner_layout.addStretch()
        
        # Date with better format
        date_frame = QFrame()
        date_frame.setStyleSheet(f"""
            QFrame {{
                background-color: rgba(255, 255, 255, 0.15);
                border-radius: 8px;
                padding: 8px 16px;
            }}
        """)
        date_layout = QVBoxLayout(date_frame)
        date_layout.setContentsMargins(12, 8, 12, 8)
        
        fecha_actual, hora_actual = get_formatted_date()
        self.date_label = QLabel(fecha_actual)
        self.date_label.setStyleSheet("color: white; font-size: 16px; font-weight: bold;")
        self.time_label = QLabel(hora_actual)
        self.time_label.setStyleSheet("color: #e0e0e0; font-size: 14px;")

        # Timer to update time every minute
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_time)
        self.timer.start(60000)  # 60000 ms = 1 minute

        date_layout.addWidget(self.date_label)
        date_layout.addWidget(self.time_label)
        
        banner_layout.addWidget(date_frame)
        self.main_layout.addWidget(banner_frame)

        # Improved Refresh Button and other controls
        controls_layout = QHBoxLayout()
        controls_layout.setContentsMargins(0, 10, 0, 10)
        
        # Period with better style
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
        
        period_icon = QLabel()
        period_icon.setPixmap(QIcon("resources/icons/calendar.png").pixmap(QSize(20, 20)))
        period_layout.addWidget(period_icon)
        
        period_label = QLabel("Current period: Q2 2025")
        period_label.setStyleSheet(f"color: {PIRELLI_DARK}; font-weight: bold; font-size: 14px;")
        period_layout.addWidget(period_label)
        
        controls_layout.addWidget(period_frame)
        controls_layout.addStretch()
        
        # Improved refresh button
        self.refresh_button = QPushButton(" Refresh Dashboard")
        self.refresh_button.setObjectName("refresh_button")
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
        """)
        controls_layout.addWidget(self.refresh_button)
        self.main_layout.addLayout(controls_layout)

        # Main sections
        self.create_statistic_cards()
        self.create_chart_cards()
        
        # HR and Attendance Section
        hr_title = QLabel("Human Resources Management")
        hr_title.setStyleSheet(f"color: {PIRELLI_DARK}; font-size: 22px; font-weight: bold; margin-top: 20px; margin-bottom: 10px;")
        self.main_layout.addWidget(hr_title)
        
        hr_layout = QHBoxLayout()
        hr_layout.setSpacing(24)
        
        self.attendance_chart = AttendancePieChart()
        hr_layout.addWidget(self.attendance_chart)
        
        # Pending purchase orders card
        self.pending_orders_card = StatisticCard(
            "Pending Purchase Orders",
            "0",
            "resources/icons/purchase.png",
            PIRELLI_YELLOW
        )
        hr_layout.addWidget(self.pending_orders_card)
        
        self.main_layout.addLayout(hr_layout)
        
        # Products and Sales Section
        products_title = QLabel("Products and Sales")
        products_title.setStyleSheet(f"color: {PIRELLI_DARK}; font-size: 22px; font-weight: bold; margin-top: 20px; margin-bottom: 10px;")
        self.main_layout.addWidget(products_title)
        
        products_layout = QHBoxLayout()
        products_layout.setSpacing(24)
        
        self.top_products_chart = TopProductsChart()
        products_layout.addWidget(self.top_products_chart)
        
        self.main_layout.addLayout(products_layout)
        
        # Assets and Incidents Section
        assets_title = QLabel("Assets and Incidents")
        assets_title.setStyleSheet(f"color: {PIRELLI_DARK}; font-size: 22px; font-weight: bold; margin-top: 20px; margin-bottom: 10px;")
        self.main_layout.addWidget(assets_title)
        
        assets_layout = QVBoxLayout()
        assets_layout.setSpacing(24)
        
        # Assets status chart
        assets_chart_layout = QHBoxLayout()
        assets_chart_layout.setSpacing(24)
        self.assets_chart = AssetsStatusChart()
        assets_chart_layout.addWidget(self.assets_chart)
        assets_layout.addLayout(assets_chart_layout)
        
        # Incidents table in a styled frame
        incidents_frame = QFrame()
        incidents_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {CARD_BG};
                border-radius: 16px;
                border: 1px solid {CARD_BORDER};
            }}
        """)
        incidents_shadow = QGraphicsDropShadowEffect()
        incidents_shadow.setBlurRadius(15)
        incidents_shadow.setOffset(0, 3)
        incidents_shadow.setColor(QColor(0, 0, 0, 20))
        incidents_frame.setGraphicsEffect(incidents_shadow)
        
        incidents_layout = QVBoxLayout(incidents_frame)
        incidents_layout.setContentsMargins(24, 24, 24, 24)
        
        incidents_header = QHBoxLayout()
        incidents_label = QLabel("Recent Incidents")
        incidents_label.setStyleSheet(f"color: {PIRELLI_DARK}; font-size: 18px; font-weight: bold;")
        incidents_header.addWidget(incidents_label)
        
        view_all_incidents = QPushButton("View All")
        view_all_incidents.setStyleSheet(f"""
            QPushButton {{
                color: {PIRELLI_RED};
                background-color: transparent;
                border: 1px solid {PIRELLI_RED};
                border-radius: 6px;
                padding: 6px 12px;
                font-size: 12px;
            }}
            QPushButton:hover {{
                background-color: {PIRELLI_RED};
                color: white;
            }}
        """)
        incidents_header.addWidget(view_all_incidents)
        incidents_layout.addLayout(incidents_header)
        
        # Separator
        incidents_separator = QFrame()
        incidents_separator.setFrameShape(QFrame.Shape.HLine)
        incidents_separator.setStyleSheet(f"background-color: {CARD_BORDER}; margin: 8px 0;")
        incidents_layout.addWidget(incidents_separator)
        
        self.incidents_table = IncidentsTable()
        self.incidents_table.setMinimumHeight(250)  # Minimum height for the table
        incidents_layout.addWidget(self.incidents_table)
        
        assets_layout.addWidget(incidents_frame)
        self.main_layout.addLayout(assets_layout)
        
        self.create_recent_activities()

        # Improved footer
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
        
        company_layout = QVBoxLayout()
        company_logo = QLabel("PIRELLI")
        company_logo.setStyleSheet(f"color: {PIRELLI_RED}; font-size: 18px; font-weight: bold;")
        company_text = QLabel("© 2025 Pirelli - Enterprise Management System - v.2.3.1")
        company_text.setStyleSheet(f"color: {PIRELLI_GRAY}; font-size: 12px;")
        company_layout.addWidget(company_logo)
        company_layout.addWidget(company_text)
        footer_layout.addLayout(company_layout)
        
        footer_layout.addStretch()
        
        footer_links = QHBoxLayout()
        footer_links.setSpacing(20)
        
        help_btn = QPushButton("Help")
        help_btn.setStyleSheet(f"""
            QPushButton {{
                color: {PIRELLI_GRAY};
                background-color: transparent;
                border: none;
                font-size: 13px;
            }}
            QPushButton:hover {{
                color: {PIRELLI_RED};
                text-decoration: underline;
            }}
        """)
        
        contact_btn = QPushButton("Contact")
        contact_btn.setStyleSheet(f"""
            QPushButton {{
                color: {PIRELLI_GRAY};
                background-color: transparent;
                border: none;
                font-size: 13px;
            }}
            QPushButton:hover {{
                color: {PIRELLI_RED};
                text-decoration: underline;
            }}
        """)
        
        about_btn = QPushButton("About")
        about_btn.setStyleSheet(f"""
            QPushButton {{
                color: {PIRELLI_GRAY};
                background-color: transparent;
                border: none;
                font-size: 13px;
            }}
            QPushButton:hover {{
                color: {PIRELLI_RED};
                text-decoration: underline;
            }}
        """)
        
        footer_links.addWidget(help_btn)
        footer_links.addWidget(contact_btn)
        footer_links.addWidget(about_btn)
        
        footer_layout.addLayout(footer_links)
        self.main_layout.addWidget(footer)

    def update_time(self):
        """Updates date and time in the dashboard"""
        fecha_actual, hora_actual = get_formatted_date()
        self.date_label.setText(fecha_actual)
        self.time_label.setText(hora_actual)
        
    def create_statistic_cards(self):
        """Creates statistic cards with improved Pirelli style"""
        section_title = QLabel("Key Performance Indicators")
        section_title.setStyleSheet(f"color: {PIRELLI_DARK}; font-size: 22px; font-weight: bold; margin-top: 10px; margin-bottom: 10px;")
        self.main_layout.addWidget(section_title)
        
        stats_layout = QGridLayout()
        stats_layout.setSpacing(24)
        
        self.sales_card = StatisticCard(
            "Monthly Sales",
            "$0",
            "resources/icons/sales.png",
            PIRELLI_RED
        )
        self.sales_card.setObjectName("sales_card")
        
        self.production_card = StatisticCard(
            "Monthly Production",
            "0 units",
            "resources/icons/production.png",
            PIRELLI_YELLOW
        )
        self.production_card.setObjectName("production_card")
        
        self.inventory_card = StatisticCard(
            "Inventory Level",
            "0%",
            "resources/icons/inventory.png",
            PIRELLI_DARK
        )
        self.inventory_card.setObjectName("inventory_card")
        
        self.employees_card = StatisticCard(
            "Active Employees",
            "0",
            "resources/icons/employee.png",
            PIRELLI_GRAY
        )
        self.employees_card.setObjectName("employees_card")
        
        stats_layout.addWidget(self.sales_card, 0, 0)
        stats_layout.addWidget(self.production_card, 0, 1)
        stats_layout.addWidget(self.inventory_card, 1, 0)
        stats_layout.addWidget(self.employees_card, 1, 1)
        
        self.main_layout.addLayout(stats_layout)

    def create_chart_cards(self):
        """Creates chart cards with improved Pirelli style"""
        section_title = QLabel("Performance Analysis")
        section_title.setStyleSheet(f"color: {PIRELLI_DARK}; font-size: 22px; font-weight: bold; margin-top: 20px; margin-bottom: 10px;")
        self.main_layout.addWidget(section_title)
        
        charts_layout = QHBoxLayout()
        charts_layout.setSpacing(24)
        
        self.materials_chart = ChartCard("Materials Distribution", "pie")
        self.materials_chart.setObjectName("materials_chart")
        self.materials_chart.setMinimumHeight(400)  # Minimum height for the chart
        
        self.production_chart = ChartCard("Sales vs Production", "bar")
        self.production_chart.setObjectName("production_chart")
        self.production_chart.setMinimumHeight(400)  # Minimum height for the chart
        
        charts_layout.addWidget(self.materials_chart)
        charts_layout.addWidget(self.production_chart)
        
        self.main_layout.addLayout(charts_layout)

    def create_recent_activities(self):
        """Creates recent activities section with improved Pirelli style"""
        section_title = QLabel("Recent Activities")
        section_title.setStyleSheet(f"color: {PIRELLI_DARK}; font-size: 22px; font-weight: bold; margin-top: 20px; margin-bottom: 10px;")
        self.main_layout.addWidget(section_title)
        
        self.activities_frame = QFrame()
        self.activities_frame.setFrameShape(QFrame.Shape.NoFrame)
        self.activities_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {CARD_BG};
                border-radius: 16px;
                border: 1px solid {CARD_BORDER};
            }}
        """)
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setOffset(0, 3)
        shadow.setColor(QColor(0, 0, 0, 20))
        self.activities_frame.setGraphicsEffect(shadow)
        
        self.activities_layout = QVBoxLayout(self.activities_frame)
        self.activities_layout.setContentsMargins(24, 24, 24, 24)
        self.activities_layout.setSpacing(16)
        
        activities_header = QHBoxLayout()
        activities_title = QLabel("Latest Updates")
        activities_title.setStyleSheet(f"color: {PIRELLI_DARK}; font-size: 18px; font-weight: bold;")
        activities_header.addWidget(activities_title)
        
        view_all_btn = QPushButton("View All")
        view_all_btn.setStyleSheet(f"""
            QPushButton {{
                color: {PIRELLI_RED};
                background-color: transparent;
                border: 1px solid {PIRELLI_RED};
                border-radius: 6px;
                padding: 6px 12px;
                font-size: 12px;
            }}
            QPushButton:hover {{
                background-color: {PIRELLI_RED};
                color: white;
            }}
        """)
        activities_header.addWidget(view_all_btn)
        self.activities_layout.addLayout(activities_header)
        
        # Separator
        activities_separator = QFrame()
        activities_separator.setFrameShape(QFrame.Shape.HLine)
        activities_separator.setStyleSheet(f"background-color: {CARD_BORDER}; margin: 8px 0;")
        self.activities_layout.addWidget(activities_separator)
        
        placeholder_label = QLabel("Loading recent activities...")
        placeholder_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        placeholder_label.setStyleSheet(f"color: {PIRELLI_GRAY}; font-style: italic; padding: 20px;")
        self.activities_layout.addWidget(placeholder_label)
        
        self.main_layout.addWidget(self.activities_frame)

    def update_recent_activities(self, activities):
        """Updates the list of recent activities with improved Pirelli style"""
        # Clear the layout
        while self.activities_layout.count():
            item = self.activities_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
            else:
                sub_layout = item.layout()
                if sub_layout is not None:
                    while sub_layout.count():
                        sub_item = sub_layout.takeAt(0)
                        sub_widget = sub_item.widget()
                        if sub_widget is not None:
                            sub_widget.deleteLater()
        
        # Recreate the header
        activities_header = QHBoxLayout()
        activities_title = QLabel("Latest Updates")
        activities_title.setStyleSheet(f"color: {PIRELLI_DARK}; font-size: 18px; font-weight: bold;")
        activities_header.addWidget(activities_title)
        
        view_all_btn = QPushButton("View All")
        view_all_btn.setStyleSheet(f"""
            QPushButton {{
                color: {PIRELLI_RED};
                background-color: transparent;
                border: 1px solid {PIRELLI_RED};
                border-radius: 6px;
                padding: 6px 12px;
                font-size: 12px;
            }}
            QPushButton:hover {{
                background-color: {PIRELLI_RED};
                color: white;
            }}
        """)
        activities_header.addWidget(view_all_btn)
        self.activities_layout.addLayout(activities_header)
        
        # Separator
        activities_separator = QFrame()
        activities_separator.setFrameShape(QFrame.Shape.HLine)
        activities_separator.setStyleSheet(f"background-color: {CARD_BORDER}; margin: 8px 0;")
        self.activities_layout.addWidget(activities_separator)
        
        # Add new activities
        if not activities:
            no_data_label = QLabel("No recent activities available")
            no_data_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            no_data_label.setStyleSheet(f"color: {PIRELLI_GRAY}; font-style: italic; padding: 20px;")
            self.activities_layout.addWidget(no_data_label)
        else:
            for idx, activity in enumerate(activities):
                title = activity.get("titulo", "")
                time = activity.get("tiempo", "")
                icon_path = None
                icon_color = PIRELLI_RED
                
                if "Venta" in title:
                    icon_path = "resources/icons/sales.png"
                    icon_color = PIRELLI_RED
                elif "Producción" in title:
                    icon_path = "resources/icons/production.png"
                    icon_color = PIRELLI_YELLOW
                elif "inventario" in title.lower():
                    icon_path = "resources/icons/inventory.png"
                    icon_color = PIRELLI_DARK
                elif "pedido" in title.lower():
                    icon_path = "resources/icons/order.png"
                    icon_color = PIRELLI_GRAY
                elif "envío" in title.lower() or "delivery" in title.lower():
                    icon_path = "resources/icons/delivery.png"
                    icon_color = PIRELLI_RED
                else:
                    icon_path = "resources/icons/order.png"
                    icon_color = PIRELLI_GRAY
                
                # Activity card
                activity_frame = AnimatedFrame()
                activity_frame.setStyleSheet(f"""
                    QFrame {{
                        background-color: #ffffff;
                        border-radius: 12px;
                        padding: 5px;
                        border: 1px solid {CARD_BORDER};
                    }}
                    QFrame:hover {{
                        background-color: #f8f8f8;
                        border-color: {PIRELLI_GRAY}50;
                    }}
                """)
                activity_layout = QHBoxLayout(activity_frame)
                activity_layout.setContentsMargins(16, 16, 16, 16)
                
                if icon_path:
                    icon_label = QLabel()
                    icon_label.setPixmap(QIcon(icon_path).pixmap(QSize(24, 24)))
                    icon_label.setFixedSize(40, 40)
                    icon_label.setStyleSheet(f"""
                        background-color: {icon_color}20;
                        border-radius: 20px;
                        padding: 8px;
                    """)
                    activity_layout.addWidget(icon_label)
                
                info_layout = QVBoxLayout()
                info_layout.setSpacing(4)
                
                title_label = QLabel(title)
                title_label.setStyleSheet(f"color: {PIRELLI_DARK}; font-weight: bold; font-size: 14px;")
                
                time_label = QLabel(time)
                time_label.setStyleSheet(f"color: {PIRELLI_GRAY}; font-size: 12px;")
                
                info_layout.addWidget(title_label)
                info_layout.addWidget(time_label)
                activity_layout.addLayout(info_layout)
                activity_layout.addStretch()
                
                details_btn = QPushButton("Details")
                details_btn.setStyleSheet(f"""
                    QPushButton {{
                        color: {PIRELLI_RED};
                        background-color: transparent;
                        border: 1px solid {PIRELLI_RED};
                        border-radius: 4px;
                        padding: 5px 10px;
                        font-size: 12px;
                    }}
                    QPushButton:hover {{
                        background-color: {PIRELLI_RED};
                        color: white;
                    }}
                """)
                activity_layout.addWidget(details_btn)
                
                self.activities_layout.addWidget(activity_frame)
                
                # Spacer between activities
                if idx < len(activities) - 1:
                    spacer = QSpacerItem(20, 10, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
                    self.activities_layout.addItem(spacer)

    def refresh_data(self):
        logging.info("Requesting dashboard data from backend...")
        if hasattr(self, "refresh_button"):
            self.refresh_button.setEnabled(False)
            self.refresh_button.setText(" Updating...")
            
            # Add loading animation
            self.refresh_button.setStyleSheet(f"""
                QPushButton {{
                    background-color: {PIRELLI_GRAY};
                    color: white;
                    border-radius: 8px;
                    padding: 12px 28px;
                    font-weight: bold;
                    font-family: 'Segoe UI';
                    font-size: 14px;
                }}
            """)
            
        try:
            self.api_client.get_dashboard_data()
        except Exception as e:
            logging.exception("Error requesting dashboard data")
            self.show_error_message("Could not update dashboard", str(e))
            if hasattr(self, "refresh_button"):
                self.refresh_button.setEnabled(True)
                self.refresh_button.setText(" Refresh Dashboard")
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
                """)

    def update_data(self, data):
        logging.info(f"Data received in update_data: {data}")
        # Only process if it's dashboard data
        if not (isinstance(data, dict) and data.get('type') == 'dashboard' and 'data' in data):
            logging.info("update_data ignored: not dashboard type.")
            if hasattr(self, "refresh_button"):
                self.refresh_button.setEnabled(True)
                self.refresh_button.setText(" Refresh Dashboard")
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
                """)
            return
            
        data = data['data']
        
        def format_number(val, decimals=0, prefix="", suffix=""):
            try:
                if val is None or val == "" or (isinstance(val, (int, float)) and val == 0):
                    return "No data"
                if isinstance(val, str):
                    val = float(val)
                if decimals == 0:
                    return f"{prefix}{int(val):,}{suffix}".replace(",", ".")
                else:
                    return f"{prefix}{val:,.{decimals}f}{suffix}".replace(",", ".")
            except Exception:
                return "No data"
                
        try:
            # Animation to update values
            def animate_value_update(label, new_value):
                # Create animation to make the value appear with an effect
                label.setStyleSheet(f"color: {PIRELLI_RED}; font-family: 'Segoe UI'; letter-spacing: -0.5px; font-size: 28px; font-weight: bold;")
                label.setText(new_value)
                
                # Schedule a timer to restore the style after animation
                QTimer.singleShot(500, lambda: label.setStyleSheet(f"color: {PIRELLI_RED}; font-family: 'Segoe UI'; letter-spacing: -0.5px; font-size: 28px; font-weight: bold;"))
            
            ventas = data.get('ventas_mensuales', 0)
            prod = data.get('produccion_mensual', 0)
            inventario = data.get('nivel_inventario', 0)
            empleados = data.get('empleados_activos', 0)
            
            ventas_str = format_number(ventas, 2, "$")
            prod_str = format_number(prod, 0, "", " units")
            inventario_str = format_number(inventario, 0, "", "%")
            empleados_str = format_number(empleados, 0)
            
            # Update with animation
            animate_value_update(self.sales_card.findChild(QLabel, "value_label"), ventas_str)
            animate_value_update(self.production_card.findChild(QLabel, "value_label"), prod_str)
            animate_value_update(self.inventory_card.findChild(QLabel, "value_label"), inventario_str)
            animate_value_update(self.employees_card.findChild(QLabel, "value_label"), empleados_str)
            
        except Exception as e:
            logging.exception("Error updating statistics cards")
            self.show_error_message("Error updating dashboard data", str(e))
            
        try:
            # Materials pie chart
            if 'distribucion_materiales' in data:
                materials_chart = self.findChild(ChartCard, "materials_chart")
                if materials_chart and hasattr(materials_chart, 'chart'):
                    # Use the improved method that handles interactivity
                    materials_chart.create_pie_chart(data['distribucion_materiales'])
                    has_data = any(float(v) > 0 for v in data['distribucion_materiales'].values())
                    if not has_data:
                        materials_chart.chart.setTitle("Materials Distribution (No data)")
                    else:
                        materials_chart.chart.setTitle("")
                        
            # Sales vs production bar chart
            if 'ventas_vs_produccion' in data:
                production_chart = self.findChild(ChartCard, "production_chart")
                if production_chart and hasattr(production_chart, 'chart'):
                    # Use the improved method to create the bar chart
                    production_chart.create_bar_chart(data['ventas_vs_produccion'])
                    
                    # Check if there's data to show an appropriate title
                    ventas_list = data['ventas_vs_produccion'].get('ventas', [])
                    prod_list = data['ventas_vs_produccion'].get('produccion', [])
                    if all(float(v) if isinstance(v, (int, float, str)) and str(v).strip() else 0 == 0 for v in ventas_list) and \
                       all(float(p) if isinstance(p, (int, float, str)) and str(p).strip() else 0 == 0 for p in prod_list):
                        production_chart.chart.setTitle("Sales vs Production Comparison (No data)")
                    else:
                        production_chart.chart.setTitle("")
                        
            if 'actividades_recientes' in data:
                self.update_recent_activities(data['actividades_recientes'])
                
            # Update new components
            if 'asistencias_data' in data:
                self.attendance_chart.update_data(data['asistencias_data'])
                
            if 'productos_mas_vendidos' in data:
                self.top_products_chart.update_data(data['productos_mas_vendidos'])
                
            if 'activos_estado' in data:
                self.assets_chart.update_data(data['activos_estado'])
                
            if 'ordenes_compra_pendientes' in data:
                animate_value_update(
                    self.pending_orders_card.findChild(QLabel, "value_label"),
                    str(data['ordenes_compra_pendientes'])
                )
                
            if 'incidentes_recientes' in data:
                self.incidents_table.load_data(data['incidentes_recientes'])
                
            if hasattr(self.parent(), 'statusBar'):
                self.parent().parent().statusBar().showMessage("Dashboard updated", 3000)
                
            if hasattr(self, "refresh_button"):
                self.refresh_button.setEnabled(True)
                self.refresh_button.setText(" Refresh Dashboard")
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
                """)
                
        except Exception as e:
            logging.exception("Error updating charts or activities")
            self.show_error_message("Error updating charts or activities", str(e))
            if hasattr(self, "refresh_button"):
                self.refresh_button.setEnabled(True)
                self.refresh_button.setText(" Refresh Dashboard")
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
                """)

    def handle_api_error(self, error_msg):
        logging.error(f"API error received: {error_msg}")
        self.show_error_message("API Error", error_msg)
        if hasattr(self, "refresh_button"):
            self.refresh_button.setEnabled(True)
            self.refresh_button.setText(" Refresh Dashboard")
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
            """)

    def show_error_message(self, title, message):
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