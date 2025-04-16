
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QGridLayout, QSizePolicy, QScrollArea, QMessageBox,
    QGraphicsDropShadowEffect, QSpacerItem, QDialog, QToolTip,
    QTableWidget, QTableWidgetItem, QHeaderView
)
from PyQt6.QtCore import Qt, QSize, pyqtSignal
from PyQt6.QtGui import QFont, QIcon, QPainter, QColor
from PyQt6.QtCharts import QChart, QChartView, QPieSeries, QBarSeries, QBarSet, QBarCategoryAxis, QValueAxis
import logging

# Configuración básica de logging: solo errores y advertencias
logging.basicConfig(level=logging.WARNING, format='%(asctime)s %(levelname)s %(message)s')

# Colores de Pirelli
PIRELLI_RED = "#D50000"
PIRELLI_YELLOW = "#FFCD00"
PIRELLI_DARK = "#1A1A1A"
PIRELLI_GRAY = "#666666"
PIRELLI_LIGHT_GRAY = "#E6E6E6"
CARD_BG = "#FAFAFA"  # Fondo suave para tarjetas

class StatisticCard(QFrame):
    """Tarjeta para mostrar una estadística con mejor visual según estética Pirelli"""
    def __init__(self, title, value, icon_path=None, color=PIRELLI_RED):
        super().__init__()
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {CARD_BG};
                border-radius: 14px;
                border: none;
            }}
        """)
        # Sombra
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(18)
        shadow.setOffset(0, 4)
        shadow.setColor(QColor(0, 0, 0, 30))
        self.setGraphicsEffect(shadow)
        # Layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(22, 22, 22, 22)
        # Icono circular
        if icon_path:
            icon_label = QLabel()
            pixmap = QIcon(icon_path).pixmap(QSize(38, 38))
            icon_label.setPixmap(pixmap)
            icon_label.setFixedSize(54, 54)
            icon_label.setStyleSheet(f"""
                background-color: {color}22;
                border-radius: 27px;
                margin-right: 18px;
                padding: 8px;
            """)
            layout.addWidget(icon_label)
        # Contenido
        text_layout = QVBoxLayout()
        text_layout.setSpacing(7)
        title_label = QLabel(title)
        title_label.setStyleSheet(f"color: {PIRELLI_GRAY}; font-size: 15px; font-family: 'Segoe UI'; font-weight: 500;")
        self.value_label = QLabel(value)
        self.value_label.setFont(QFont("Segoe UI", 26, QFont.Weight.Bold))
        self.value_label.setObjectName("value_label")
        self.value_label.setStyleSheet(f"color: {color}; font-family: 'Segoe UI'; letter-spacing: -0.5px;")
        text_layout.addWidget(title_label)
        text_layout.addWidget(self.value_label)
        layout.addLayout(text_layout)
        layout.addStretch()
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setMinimumHeight(110)

class SalesVsProductionDialog(QDialog):
    """Diálogo para mostrar el gráfico de ventas vs producción en grande y tabla detallada."""
    def __init__(self, data, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Detalle de Ventas vs Producción")
        self.setMinimumSize(800, 500)
        layout = QVBoxLayout(self)

        # Gráfico grande
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
        axis_y.setLabelsFont(QFont("Segoe UI", 10))
        chart.addAxis(axis_y, Qt.AlignmentFlag.AlignLeft)
        series.attachAxis(axis_y)

        chart.setTitle("Comparación Detallada Ventas vs Producción")
        chart_view = QChartView(chart)
        chart_view.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        layout.addWidget(chart_view)

        # Tabla detallada
        table = QTableWidget()
        table.setColumnCount(3)
        table.setHorizontalHeaderLabels(["Categoría", "Ventas", "Producción"])
        table.setRowCount(len(categorias))
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        table.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
        table.setAlternatingRowColors(True)
        table.setStyleSheet("""
            QTableWidget {
                background-color: #FAFAFA;
                font-family: 'Segoe UI';
                font-size: 14px;
            }
            QHeaderView::section {
                background-color: #1A1A1A;
                color: white;
                font-weight: bold;
                font-size: 14px;
                border: none;
                padding: 6px;
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

        layout.addSpacing(12)
        label = QLabel("Detalle numérico de ventas y producción")
        label.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        layout.addWidget(label)
        layout.addWidget(table)

class MaterialDistributionDialog(QDialog):
    """Diálogo para mostrar la distribución de materiales en grande y detallado, con tabla."""
    def __init__(self, data, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Detalle de Distribución de Materiales")
        self.setMinimumSize(700, 500)
        layout = QVBoxLayout(self)
        # Gráfico grande
        chart = QChart()
        chart.setAnimationOptions(QChart.AnimationOption.SeriesAnimations)
        chart.setTheme(QChart.ChartTheme.ChartThemeLight)
        chart.setBackgroundVisible(False)
        chart.legend().setVisible(True)
        chart.legend().setAlignment(Qt.AlignmentFlag.AlignBottom)
        chart.legend().setFont(QFont("Segoe UI", 12))
        series = QPieSeries()
        total = sum(float(v) for v in data.values() if v)
        for i, (material, valor) in enumerate(data.items()):
            val = float(valor)
            slice = series.append(f"{material}: {val} ({val/total*100:.1f}%)", val)
            # Colores de marca Pirelli
            if i == 0:
                slice.setBrush(QColor(PIRELLI_RED))
            elif i == 1:
                slice.setBrush(QColor(PIRELLI_DARK))
            elif i == 2:
                slice.setBrush(QColor(PIRELLI_YELLOW))
            elif i == 3:
                slice.setBrush(QColor(PIRELLI_GRAY))
            slice.setLabelVisible(True)
        chart.addSeries(series)
        chart.setTitle("Distribución Detallada de Materiales")
        chart_view = QChartView(chart)
        chart_view.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        layout.addWidget(chart_view)
        
        # Tabla detallada
        table = QTableWidget()
        table.setColumnCount(3)
        table.setHorizontalHeaderLabels(["Material", "Valor", "Porcentaje"])
        table.setRowCount(len(data))
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        table.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
        table.setAlternatingRowColors(True)
        table.setStyleSheet("""
            QTableWidget {
                background-color: #FAFAFA;
                font-family: 'Segoe UI';
                font-size: 14px;
            }
            QHeaderView::section {
                background-color: #1A1A1A;
                color: white;
                font-weight: bold;
                font-size: 14px;
                border: none;
                padding: 6px;
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

        layout.addSpacing(12)
        label = QLabel("Detalle numérico de la distribución de materiales")
        label.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        layout.addWidget(label)
        layout.addWidget(table)

class ChartCard(QFrame):
    """Tarjeta para mostrar un gráfico con estilo Pirelli e interacción avanzada"""
    def __init__(self, title, chart_type="pie"):
        super().__init__()
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {CARD_BG};
                border-radius: 14px;
                border: none;
            }}
        """)
        # Sombra
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(18)
        shadow.setOffset(0, 4)
        shadow.setColor(QColor(0, 0, 0, 30))
        self.setGraphicsEffect(shadow)
        # Layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        # Título
        title_label = QLabel(title)
        title_label.setStyleSheet(f"color: {PIRELLI_DARK}; font-size: 17px; font-weight: bold; font-family: 'Segoe UI'; margin-bottom: 8px;")
        layout.addWidget(title_label)
        # Crear el gráfico
        self.chart = QChart()
        self.chart.setAnimationOptions(QChart.AnimationOption.SeriesAnimations)
        self.chart.setTheme(QChart.ChartTheme.ChartThemeLight)
        self.chart.setBackgroundVisible(False)
        self.chart.legend().setVisible(True)
        self.chart.legend().setAlignment(Qt.AlignmentFlag.AlignBottom)
        self.chart.legend().setFont(QFont("Segoe UI", 9))
        # Crear vista del gráfico
        self.chart_view = QChartView(self.chart)
        self.chart_view.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        layout.addWidget(self.chart_view)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        # Propiedades para interactividad
        self.chart_type = chart_type
        self.material_data = None  # Para guardar los datos actuales
        self.series = None
        # Agregar datos de prueba según el tipo de gráfico
        if chart_type == "pie":
            self.create_pie_chart()
        elif chart_type == "bar":
            self.create_bar_chart()
        # Eventos para interacción
        self.chart_view.setMouseTracking(True)
        self.chart_view.viewport().installEventFilter(self)

    def create_pie_chart(self, data=None):
        """Crea un gráfico de pastel con datos reales o de prueba y colores de Pirelli"""
        self.chart.removeAllSeries()
        series = QPieSeries()
        if data:
            self.material_data = data
            for i, (material, valor) in enumerate(data.items()):
                val = float(valor)
                slice = series.append(material, val)
                # Colores de marca Pirelli
                if i == 0:
                    slice.setBrush(QColor(PIRELLI_RED))
                    slice.setExploded(True)
                elif i == 1:
                    slice.setBrush(QColor(PIRELLI_DARK))
                elif i == 2:
                    slice.setBrush(QColor(PIRELLI_YELLOW))
                elif i == 3:
                    slice.setBrush(QColor(PIRELLI_GRAY))
                if i == 0:
                    slice.setLabelVisible(True)
        else:
            # Datos de prueba
            series.append("Caucho", 35)
            series.append("Acero", 20)
            series.append("Químicos", 15)
            series.append("Otros", 30)
            # Colores de marca Pirelli
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
        self.chart.setTitle("Distribución de Materiales")
        # Conectar eventos
        for slice in series.slices():
            # PyQt6: hovered signal pasa (bool) pero necesitamos saber el slice, así que usamos lambda
            slice.hovered.connect(lambda state, s=slice: self.on_slice_hovered(state, s))
            slice.clicked.connect(self.on_slice_clicked)

    def eventFilter(self, obj, event):
        # Permite que el gráfico reciba eventos de mouse
        return super().eventFilter(obj, event)

    def on_slice_hovered(self, state, slice):
        # Mostrar tooltip detallado al pasar el mouse
        if state:
            label = slice.label()
            value = slice.value()
            percent = slice.percentage() * 100
            QToolTip.showText(self.chart_view.mapToGlobal(self.chart_view.cursor().pos()),
                f"<b>{label}</b><br>Valor: {value}<br>Porcentaje: {percent:.1f}%")
        else:
            QToolTip.hideText()

    def on_slice_clicked(self):
        # Mostrar diálogo ampliado al hacer clic
        if self.material_data:
            dlg = MaterialDistributionDialog(self.material_data, self)
            dlg.exec()

    def create_bar_chart(self, data=None):
        """Crea un gráfico de barras con datos reales o de prueba y colores de Pirelli"""
        self.chart.removeAllSeries()
        if data:
            ventas = [float(v) if v else 0 for v in data.get("ventas", [])]
            produccion = [float(p) if p else 0 for p in data.get("produccion", [])]
            categorias = data.get("categorias", [f"Item {i+1}" for i in range(max(len(ventas), len(produccion)))])
        else:
            ventas = [50, 65, 70, 85, 60]
            produccion = [40, 55, 65, 70, 55]
            categorias = ["Ene", "Feb", "Mar", "Abr", "May"]

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
        axis_y.setLabelsFont(QFont("Segoe UI", 8))
        self.chart.addAxis(axis_y, Qt.AlignmentFlag.AlignLeft)
        series.attachAxis(axis_y)
        self.chart.setTitle("Comparación Ventas vs Producción")
        
        # Guardar los datos para el diálogo detallado
        self.bar_data = {
            "ventas": ventas,
            "produccion": produccion,
            "categorias": categorias
        }
        
        # Conectar evento de clic en la vista del gráfico
        self.chart_view.mousePressEvent = self.on_bar_chart_clicked
        
    def on_bar_chart_clicked(self, event):
        # Mostrar diálogo ampliado al hacer clic en el gráfico de barras
        if hasattr(self, "bar_data") and self.bar_data and self.chart_type == "bar":
            dlg = SalesVsProductionDialog(self.bar_data, self)
            dlg.exec()

class DashboardView(QWidget):
    """Vista del dashboard con estilo Pirelli"""
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
            logging.exception("Error en DashboardView.__init__")
            self.show_error_message("Error crítico al inicializar el dashboard", str(e))

    def init_ui(self):
        """Inicializa la interfaz de usuario con estilo Pirelli"""
        main_container = QWidget()
        main_container.setStyleSheet(f"""
            QWidget {{
                background-color: #f5f5f5;
                font-family: 'Segoe UI';
            }}
        """)
        self.main_layout = QVBoxLayout(main_container)
        self.main_layout.setSpacing(28)
        self.main_layout.setContentsMargins(32, 32, 32, 32)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(main_container)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: #f5f5f5;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(scroll_area)

        # Banner Superior con Logo Pirelli
        banner_frame = QFrame()
        banner_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {PIRELLI_DARK};
                border-radius: 14px;
                min-height: 100px;
            }}
        """)
        banner_layout = QHBoxLayout(banner_frame)
        banner_layout.setContentsMargins(32, 20, 32, 20)
        logo_label = QLabel("PIRELLI ERP")
        logo_label.setStyleSheet(f"""
            color: white;
            font-size: 28px;
            font-weight: bold;
            font-family: 'Segoe UI';
            padding: 0 14px;
            background-color: {PIRELLI_RED};
            border-radius: 7px;
        """)
        banner_layout.addWidget(logo_label)
        title_box = QVBoxLayout()
        title_label = QLabel("Panel de Control")
        title_label.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        title_label.setStyleSheet("color: white;")
        subtitle_label = QLabel("Sistema de Gestión Empresarial")
        subtitle_label.setStyleSheet("color: #cccccc; font-size: 14px;")
        title_box.addWidget(title_label)
        title_box.addWidget(subtitle_label)
        banner_layout.addLayout(title_box)
        banner_layout.addStretch()
        date_label = QLabel("15 de Abril, 2025")
        date_label.setStyleSheet("color: white; font-size: 14px;")
        banner_layout.addWidget(date_label)
        self.main_layout.addWidget(banner_frame)

        # Botón de Actualizar mejorado y otros controles
        controls_layout = QHBoxLayout()
        self.refresh_button = QPushButton(" Actualizar Dashboard")
        self.refresh_button.setObjectName("refresh_button")
        self.refresh_button.setIcon(QIcon("resources/icons/refresh.png"))
        self.refresh_button.clicked.connect(self.refresh_data)
        self.refresh_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {PIRELLI_RED};
                color: white;
                border-radius: 6px;
                padding: 12px 26px;
                font-weight: bold;
                font-family: 'Segoe UI';
                font-size: 14px;
            }}
            QPushButton:hover {{
                background-color: #B20000;
            }}
            QPushButton:pressed {{
                background-color: #800000;
            }}
        """)
        period_label = QLabel("Período actual: Q2 2025")
        period_label.setStyleSheet(f"color: {PIRELLI_DARK}; font-weight: bold; font-size: 14px;")
        controls_layout.addWidget(period_label)
        controls_layout.addStretch()
        controls_layout.addWidget(self.refresh_button)
        self.main_layout.addLayout(controls_layout)

        # Secciones principales
        self.create_statistic_cards()
        self.create_chart_cards()
        self.create_recent_activities()

        # Pie de página
        footer = QFrame()
        footer.setStyleSheet(f"""
            QFrame {{
                background-color: transparent;
                margin-top: 10px;
            }}
        """)
        footer_layout = QHBoxLayout(footer)
        footer_layout.setContentsMargins(0, 18, 0, 0)
        footer_text = QLabel("© 2025 Pirelli - Sistema de Gestión ERP - v.2.3.1")
        footer_text.setStyleSheet(f"color: {PIRELLI_GRAY}; font-size: 12px;")
        footer_layout.addWidget(footer_text)
        footer_layout.addStretch()
        help_btn = QPushButton("Ayuda")
        help_btn.setStyleSheet(f"""
            QPushButton {{
                color: {PIRELLI_GRAY};
                background-color: transparent;
                border: none;
                font-size: 12px;
            }}
            QPushButton:hover {{
                color: {PIRELLI_RED};
                text-decoration: underline;
            }}
        """)
        footer_layout.addWidget(help_btn)
        self.main_layout.addWidget(footer)

    def create_statistic_cards(self):
        """Crea las tarjetas estadísticas con estilo Pirelli"""
        section_title = QLabel("Indicadores Clave de Rendimiento")
        section_title.setStyleSheet(f"color: {PIRELLI_DARK}; font-size: 20px; font-weight: bold; margin-top: 10px; margin-bottom: 8px;")
        self.main_layout.addWidget(section_title)
        stats_layout = QGridLayout()
        stats_layout.setSpacing(22)
        self.ventas_card = StatisticCard(
            "Ventas Mensuales",
            "$0",
            "resources/icons/sales.png",
            PIRELLI_RED
        )
        self.ventas_card.setObjectName("ventas_card")
        self.produccion_card = StatisticCard(
            "Producción Mensual",
            "0 unidades",
            "resources/icons/production.png",
            PIRELLI_YELLOW
        )
        self.produccion_card.setObjectName("produccion_card")
        self.inventario_card = StatisticCard(
            "Nivel de Inventario",
            "0%",
            "resources/icons/inventory.png",
            PIRELLI_DARK
        )
        self.inventario_card.setObjectName("inventario_card")
        self.empleados_card = StatisticCard(
            "Empleados Activos",
            "0",
            "resources/icons/employee.png",
            PIRELLI_GRAY
        )
        self.empleados_card.setObjectName("empleados_card")
        stats_layout.addWidget(self.ventas_card, 0, 0)
        stats_layout.addWidget(self.produccion_card, 0, 1)
        stats_layout.addWidget(self.inventario_card, 1, 0)
        stats_layout.addWidget(self.empleados_card, 1, 1)
        self.main_layout.addLayout(stats_layout)

    def create_chart_cards(self):
        """Crea las tarjetas para gráficos con estilo Pirelli"""
        section_title = QLabel("Análisis de Rendimiento")
        section_title.setStyleSheet(f"color: {PIRELLI_DARK}; font-size: 20px; font-weight: bold; margin-top: 18px; margin-bottom: 8px;")
        self.main_layout.addWidget(section_title)
        charts_layout = QHBoxLayout()
        charts_layout.setSpacing(22)
        self.materials_chart = ChartCard("Distribución de Materiales", "pie")
        self.materials_chart.setObjectName("materials_chart")
        self.production_chart = ChartCard("Ventas vs Producción", "bar")
        self.production_chart.setObjectName("production_chart")
        charts_layout.addWidget(self.materials_chart)
        charts_layout.addWidget(self.production_chart)
        self.main_layout.addLayout(charts_layout)

    def create_recent_activities(self):
        """Crea la sección de actividades recientes con estilo Pirelli"""
        section_title = QLabel("Actividades Recientes")
        section_title.setStyleSheet(f"color: {PIRELLI_DARK}; font-size: 20px; font-weight: bold; margin-top: 18px; margin-bottom: 8px;")
        self.main_layout.addWidget(section_title)
        self.activities_frame = QFrame()
        self.activities_frame.setFrameShape(QFrame.Shape.NoFrame)
        self.activities_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {CARD_BG};
                border-radius: 14px;
                border: none;
            }}
        """)
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(18)
        shadow.setOffset(0, 4)
        shadow.setColor(QColor(0, 0, 0, 30))
        self.activities_frame.setGraphicsEffect(shadow)
        self.activities_layout = QVBoxLayout(self.activities_frame)
        self.activities_layout.setContentsMargins(24, 24, 24, 24)
        self.activities_layout.setSpacing(14)
        activities_header = QHBoxLayout()
        activities_title = QLabel("Últimas Actualizaciones")
        activities_title.setStyleSheet(f"color: {PIRELLI_DARK}; font-size: 16px; font-weight: bold;")
        activities_header.addWidget(activities_title)
        view_all_btn = QPushButton("Ver Todo")
        view_all_btn.setStyleSheet(f"""
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
        activities_header.addWidget(view_all_btn)
        self.activities_layout.addLayout(activities_header)
        placeholder_label = QLabel("Cargando actividades recientes...")
        placeholder_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        placeholder_label.setStyleSheet(f"color: {PIRELLI_GRAY}; font-style: italic; padding: 20px;")
        self.activities_layout.addWidget(placeholder_label)
        self.main_layout.addWidget(self.activities_frame)

    def update_recent_activities(self, activities):
        """Actualiza la lista de actividades recientes con estilo Pirelli"""
        # Limpia el layout
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
        # Recrear el encabezado
        activities_header = QHBoxLayout()
        activities_title = QLabel("Últimas Actualizaciones")
        activities_title.setStyleSheet(f"color: {PIRELLI_DARK}; font-size: 16px; font-weight: bold;")
        activities_header.addWidget(activities_title)
        view_all_btn = QPushButton("Ver Todo")
        view_all_btn.setStyleSheet(f"""
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
        activities_header.addWidget(view_all_btn)
        self.activities_layout.addLayout(activities_header)
        # Agrega las nuevas actividades
        if not activities:
            no_data_label = QLabel("No hay actividades recientes disponibles")
            no_data_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            no_data_label.setStyleSheet(f"color: {PIRELLI_GRAY}; font-style: italic; padding: 20px;")
            self.activities_layout.addWidget(no_data_label)
        else:
            for idx, actividad in enumerate(activities):
                title = actividad.get("titulo", "")
                time = actividad.get("tiempo", "")
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
                # Tarjeta de actividad
                activity_frame = QFrame()
                activity_frame.setStyleSheet(f"""
                    QFrame {{
                        background-color: #ffffff;
                        border-radius: 10px;
                        padding: 5px;
                        border: none;
                    }}
                    QFrame:hover {{
                        background-color: #f0f0f0;
                    }}
                """)
                activity_layout = QHBoxLayout(activity_frame)
                activity_layout.setContentsMargins(12, 12, 12, 12)
                if icon_path:
                    icon_label = QLabel()
                    icon_label.setPixmap(QIcon(icon_path).pixmap(QSize(22, 22)))
                    icon_label.setFixedSize(32, 32)
                    icon_label.setStyleSheet(f"""
                        background-color: {icon_color}25;
                        border-radius: 16px;
                        padding: 5px;
                    """)
                    activity_layout.addWidget(icon_label)
                info_layout = QVBoxLayout()
                info_layout.setSpacing(3)
                title_label = QLabel(title)
                title_label.setStyleSheet(f"color: {PIRELLI_DARK}; font-weight: bold; font-size: 13px;")
                time_label = QLabel(time)
                time_label.setStyleSheet(f"color: {PIRELLI_GRAY}; font-size: 12px;")
                info_layout.addWidget(title_label)
                info_layout.addWidget(time_label)
                activity_layout.addLayout(info_layout)
                activity_layout.addStretch()
                details_btn = QPushButton("Detalles")
                details_btn.setStyleSheet(f"""
                    QPushButton {{
                        color: {PIRELLI_GRAY};
                        background-color: transparent;
                        border: none;
                        font-size: 12px;
                    }}
                    QPushButton:hover {{
                        color: {PIRELLI_RED};
                        text-decoration: underline;
                    }}
                """)
                activity_layout.addWidget(details_btn)
                self.activities_layout.addWidget(activity_frame)
                # Espaciador entre actividades
                if idx < len(activities) - 1:
                    spacer = QSpacerItem(20, 10, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
                    self.activities_layout.addItem(spacer)

    def refresh_data(self):
        logging.info("Solicitando datos del dashboard al backend...")
        if hasattr(self, "refresh_button"):
            self.refresh_button.setEnabled(False)
            self.refresh_button.setText(" Actualizando...")
        try:
            self.api_client.get_dashboard_data()
        except Exception as e:
            logging.exception("Error al solicitar datos del dashboard")
            self.show_error_message("No se pudo actualizar el dashboard", str(e))
            if hasattr(self, "refresh_button"):
                self.refresh_button.setEnabled(True)
                self.refresh_button.setText(" Actualizar Dashboard")

    def update_data(self, data):
        logging.info(f"Datos recibidos en update_data: {data}")
        # Solo procesa si es dashboard
        if not (isinstance(data, dict) and data.get('type') == 'dashboard' and 'data' in data):
            logging.info("update_data ignorado: no es tipo dashboard.")
            if hasattr(self, "refresh_button"):
                self.refresh_button.setEnabled(True)
                self.refresh_button.setText(" Actualizar Dashboard")
            return
        data = data['data']
        def format_number(val, decimals=0, prefix="", suffix=""):
            try:
                if val is None or val == "" or (isinstance(val, (int, float)) and val == 0):
                    return "Sin datos"
                if isinstance(val, str):
                    val = float(val)
                if decimals == 0:
                    return f"{prefix}{int(val):,}{suffix}".replace(",", ".")
                else:
                    return f"{prefix}{val:,.{decimals}f}{suffix}".replace(",", ".")
            except Exception:
                return "Sin datos"
        try:
            ventas = data.get('ventas_mensuales', 0)
            prod = data.get('produccion_mensual', 0)
            inventario = data.get('nivel_inventario', 0)
            empleados = data.get('empleados_activos', 0)
            ventas_str = format_number(ventas, 2, "$")
            prod_str = format_number(prod, 0, "", " unidades")
            inventario_str = format_number(inventario, 0, "", "%")
            empleados_str = format_number(empleados, 0)
            self.ventas_card.findChild(QLabel, "value_label").setText(ventas_str)
            self.produccion_card.findChild(QLabel, "value_label").setText(prod_str)
            self.inventario_card.findChild(QLabel, "value_label").setText(inventario_str)
            self.empleados_card.findChild(QLabel, "value_label").setText(empleados_str)
        except Exception as e:
            logging.exception("Error al actualizar las tarjetas de estadísticas")
            self.show_error_message("Error al actualizar los datos del dashboard", str(e))
        try:
            # Pie chart de materiales
            if 'distribucion_materiales' in data:
                materials_chart = self.findChild(ChartCard, "materials_chart")
                if materials_chart and hasattr(materials_chart, 'chart'):
                    # Usar el método mejorado que maneja interactividad
                    materials_chart.create_pie_chart(data['distribucion_materiales'])
                    has_data = any(float(v) > 0 for v in data['distribucion_materiales'].values())
                    if not has_data:
                        materials_chart.chart.setTitle("Distribución de Materiales (Sin datos)")
                    else:
                        materials_chart.chart.setTitle("Distribución de Materiales")
            # Bar chart de ventas vs producción
            if 'ventas_vs_produccion' in data:
                production_chart = self.findChild(ChartCard, "production_chart")
                if production_chart and hasattr(production_chart, 'chart'):
                    # Usar el método mejorado para crear el gráfico de barras
                    production_chart.create_bar_chart(data['ventas_vs_produccion'])
                    
                    # Verificar si hay datos para mostrar un título adecuado
                    ventas_list = data['ventas_vs_produccion'].get('ventas', [])
                    prod_list = data['ventas_vs_produccion'].get('produccion', [])
                    if all(float(v) if isinstance(v, (int, float, str)) and str(v).strip() else 0 == 0 for v in ventas_list) and \
                       all(float(p) if isinstance(p, (int, float, str)) and str(p).strip() else 0 == 0 for p in prod_list):
                        production_chart.chart.setTitle("Comparación Ventas vs Producción (Sin datos)")
                    else:
                        production_chart.chart.setTitle("Comparación Ventas vs Producción")
            if 'actividades_recientes' in data:
                self.update_recent_activities(data['actividades_recientes'])
            if hasattr(self.parent(), 'statusBar'):
                self.parent().parent().statusBar().showMessage("Dashboard actualizado", 3000)
            if hasattr(self, "refresh_button"):
                self.refresh_button.setEnabled(True)
                self.refresh_button.setText(" Actualizar Dashboard")
        except Exception as e:
            logging.exception("Error al actualizar los gráficos o actividades")
            self.show_error_message("Error al actualizar los gráficos o actividades", str(e))
            if hasattr(self, "refresh_button"):
                self.refresh_button.setEnabled(True)
                self.refresh_button.setText(" Actualizar Dashboard")

    def handle_api_error(self, error_msg):
        logging.error(f"Error recibido de la API: {error_msg}")
        self.show_error_message("Error de la API", error_msg)
        if hasattr(self, "refresh_button"):
            self.refresh_button.setEnabled(True)
            self.refresh_button.setText(" Actualizar Dashboard")

    def show_error_message(self, title, message):
        QMessageBox.critical(self, title, message)