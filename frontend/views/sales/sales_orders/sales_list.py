from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableView, QHeaderView, QLabel, 
    QPushButton, QLineEdit, QComboBox, QMessageBox, QMenu, QStatusBar
)
from PyQt6.QtCore import Qt, pyqtSignal, QSortFilterProxyModel
from PyQt6.QtGui import QIcon, QStandardItemModel, QStandardItem, QColor
from utils.theme import Theme
import logging

logger = logging.getLogger(__name__)

class SalesListView(QWidget):
    """Vista de listado de ventas para ERP"""

    # Señales
    sale_selected = pyqtSignal(int)  # Emitida cuando se selecciona una venta
    refresh_requested = pyqtSignal()  # Emitida cuando se solicita actualización

    def __init__(self, api_client, parent=None):
        super().__init__(parent)
        Theme.apply_window_light_theme(self)
        
        self.api_client = api_client
        self.last_sales = []
        
        # Configurar modelo de datos
        self._setup_models()
        self.init_ui()
        self._connect_signals()
        
        # Cargar datos iniciales
        self.refresh_data()

    def _setup_models(self):
        """Configura los modelos de datos para la tabla"""
        self.sales_model = QStandardItemModel()
        self.sales_model.setHorizontalHeaderLabels([
            "ID", "Cliente", "Fecha", "Total", "Estado", "Valor Estado", "Creado por"
        ])
        
        # Modelo proxy para filtrado
        self.proxy_model = QSortFilterProxyModel()
        self.proxy_model.setSourceModel(self.sales_model)
        self.proxy_model.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.proxy_model.setFilterKeyColumn(-1)  # Buscar en todas las columnas
        self.proxy_model.filterAcceptsRow = self._filter_accepts_row

    def init_ui(self):
        """Inicializa la interfaz de usuario"""
        self.setMinimumSize(800, 600)
        
        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Título de sección
        title_label = QLabel("Gestión de Ventas")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        main_layout.addWidget(title_label)

        # Barra de herramientas
        toolbar_layout = QHBoxLayout()
        
        # Filtro de estado
        self.status_filter = QComboBox()
        self.status_filter.addItem("Todos los estados", "")
        self.status_filter.addItem("Pendiente", "pendiente")
        self.status_filter.addItem("Completada", "completada")
        self.status_filter.addItem("Cancelada", "cancelada")
        
        # Campo de búsqueda
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Buscar por cliente o ID...")
        self.search_input.textChanged.connect(self.on_search_changed)

        # Botón de búsqueda
        search_btn = QPushButton("Buscar")
        search_btn.clicked.connect(self._on_filters_changed)

        # Botón para añadir
        self.add_btn = QPushButton("Nueva Venta")
        self.add_btn.setIcon(QIcon("resources/icons/add.png"))
        self.add_btn.clicked.connect(self.add_sale)

        # Botón de actualizar
        self.refresh_btn = QPushButton("Actualizar")
        self.refresh_btn.setIcon(QIcon("resources/icons/refresh.png"))
        self.refresh_btn.clicked.connect(self.refresh_data)

        # Agregar widgets a la barra de herramientas
        toolbar_layout.addWidget(QLabel("Estado:"))
        toolbar_layout.addWidget(self.status_filter)
        toolbar_layout.addWidget(self.search_input)
        toolbar_layout.addWidget(search_btn)
        toolbar_layout.addStretch()
        toolbar_layout.addWidget(self.add_btn)
        toolbar_layout.addWidget(self.refresh_btn)

        main_layout.addLayout(toolbar_layout)

        # Tabla de ventas
        self.sales_table = QTableView()
        self.sales_table.setModel(self.proxy_model)
        self.sales_table.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self.sales_table.setSelectionMode(QTableView.SelectionMode.SingleSelection)
        self.sales_table.setEditTriggers(QTableView.EditTrigger.NoEditTriggers)
        self.sales_table.setAlternatingRowColors(True)
        self.sales_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.sales_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)  # ID
        self.sales_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)  # Total
        self.sales_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)  # Estado
        self.sales_table.verticalHeader().setVisible(False)
        self.sales_table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.sales_table.customContextMenuRequested.connect(self.show_context_menu)
        self.sales_table.doubleClicked.connect(self.on_row_double_clicked)
        
        # Ocultar columnas internas
        self.sales_table.setColumnHidden(5, True)  # Valor estado
        
        main_layout.addWidget(self.sales_table)

        # Labels de totales
        summary_layout = QHBoxLayout()
        self.total_label = QLabel("Total de ventas: <b>0</b>")
        self.pending_label = QLabel("Pendientes: <b>0</b>")
        self.completed_label = QLabel("Completadas: <b>0</b>")
        self.canceled_label = QLabel("Canceladas: <b>0</b>")

        summary_layout.addWidget(self.total_label)
        summary_layout.addSpacing(30)
        summary_layout.addWidget(self.pending_label)
        summary_layout.addSpacing(30)
        summary_layout.addWidget(self.completed_label)
        summary_layout.addSpacing(30)
        summary_layout.addWidget(self.canceled_label)
        summary_layout.addStretch()
        main_layout.addLayout(summary_layout)

        # Barra de estado
        self.status_bar = QStatusBar()
        self.status_bar.showMessage("Sistema ERP - Módulo de Ventas")
        main_layout.addWidget(self.status_bar)

    def _filter_accepts_row(self, source_row, source_parent):
        """Método personalizado para determinar si una fila cumple con los filtros"""
        model = self.sales_model
        
        # Obtener valores de los filtros
        search_text = self.search_input.text().strip().lower()
        status = self.status_filter.currentData()
        
        # Si no hay filtros activos, mostrar todas las filas
        if not search_text and not status:
            return True
            
        # Obtener valores de la fila actual
        try:
            sale_id = model.item(source_row, 0).text().lower()
            cliente = model.item(source_row, 1).text().lower()
            estado_valor = model.item(source_row, 5).text().lower()
            
            # Filtro de búsqueda (cliente o ID)
            if search_text and not (search_text in cliente or search_text in sale_id):
                return False
                
            # Filtro de estado
            if status and status != estado_valor:
                return False
                
            return True
        except (AttributeError, IndexError):
            return True

    def on_search_changed(self, text):
        """Maneja el cambio en el campo de búsqueda"""
        self.proxy_model.setFilterWildcard(text)
        self.proxy_model.invalidateFilter()
        self.status_bar.showMessage(f"Filtrando ventas por: {text}" if text else "Sistema ERP - Módulo de Ventas")

    def on_status_changed(self, index):
        """Maneja el cambio en el filtro de estado"""
        self._on_filters_changed()

    def _on_filters_changed(self):
        """Se llama cuando cambia estado, para actualizar el filtrado"""
        self.proxy_model.invalidateFilter()
        status = self.status_filter.currentData()
        
        msg = "Mostrando ventas"
        if status:
            msg += f" con estado: {self.status_filter.currentText()}"
        else:
            msg = "Sistema ERP - Módulo de Ventas"
            
        self.status_bar.showMessage(msg)

    def _connect_signals(self):
        """Conecta todas las señales y slots"""
        # Conectar botones
        self.add_btn.clicked.connect(self.add_sale)
        self.refresh_btn.clicked.connect(self.refresh_data)
        
        # Conectar filtros
        self.search_input.textChanged.connect(self.on_search_changed)
        self.status_filter.currentIndexChanged.connect(self.on_status_changed)
        
        # Conectar eventos de tabla
        self.sales_table.doubleClicked.connect(self.on_row_double_clicked)
        self.sales_table.customContextMenuRequested.connect(self.show_context_menu)

    def refresh_data(self):
        """Solicita ventas al API"""
        self.status_bar.showMessage("Cargando ventas...")
        try:
            sales_data = self.api_client.get_sales()
            self.last_sales = sales_data if isinstance(sales_data, list) else sales_data.get('ventas', [])
            self.load_sales(self.last_sales)
        except Exception as e:
            self.show_error(str(e))

    def load_sales(self, sales):
        """Carga las ventas en la tabla"""
        self.sales_model.removeRows(0, self.sales_model.rowCount())
        
        if not sales:
            self.status_bar.showMessage("No se encontraron ventas")
            return
            
        count_pendiente = count_completada = count_cancelada = 0
        
        for sale in sales:
            # Contar por estado
            estado = sale.get("estado", "").lower()
            if estado == "pendiente":
                count_pendiente += 1
            elif estado == "completada":
                count_completada += 1
            elif estado == "cancelada":
                count_cancelada += 1
                
            # Crear fila
            total = float(sale.get('total', 0) or 0)
            formatted_total = f"${total:,.2f}"
            
            row = [
                QStandardItem(str(sale.get("id_venta", ""))),
                QStandardItem(sale.get("cliente_nombre", "N/A")),
                QStandardItem(sale.get("fecha", "")),
                QStandardItem(formatted_total),
                QStandardItem(sale.get("estado", "").capitalize()),
                QStandardItem(estado),
                QStandardItem(sale.get("usuario_nombre", "N/A"))
            ]
            
            # Formatear celdas
            row[0].setTextAlignment(Qt.AlignmentFlag.AlignCenter)  # ID
            row[3].setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)  # Total
            row[4].setTextAlignment(Qt.AlignmentFlag.AlignCenter)  # Estado
            
            # Color por estado
            if estado == "pendiente":
                row[4].setForeground(QColor(Theme.WARNING_COLOR))
            elif estado == "completada":
                row[4].setForeground(QColor(Theme.SUCCESS_COLOR))
            elif estado == "cancelada":
                row[4].setForeground(QColor(Theme.DANGER_COLOR))
            
            self.sales_model.appendRow(row)
        
        # Actualizar resumen
        total = len(sales)
        self.total_label.setText(f"Total: <b>{total}</b>")
        self.pending_label.setText(f"Pendientes: <b>{count_pendiente}</b>")
        self.completed_label.setText(f"Completadas: <b>{count_completada}</b>")
        self.canceled_label.setText(f"Canceladas: <b>{count_cancelada}</b>")
        
        self.status_bar.showMessage(f"Cargadas {total} ventas")

    def show_context_menu(self, position):
        """Muestra el menú contextual para una venta"""
        index = self.sales_table.indexAt(position)
        if not index.isValid():
            return
            
        # Obtener la venta seleccionada
        mapped_index = self.proxy_model.mapToSource(index)
        sale_id = int(self.sales_model.item(mapped_index.row(), 0).text())
        sale_estado = self.sales_model.item(mapped_index.row(), 5).text()
        
        menu = QMenu(self)
        
        # Acciones principales
        view_action = menu.addAction(QIcon("resources/icons/view.png"), "Ver detalles")
        edit_action = menu.addAction(QIcon("resources/icons/edit.png"), "Editar")
        delete_action = menu.addAction(QIcon("resources/icons/delete.png"), "Eliminar")
        menu.addSeparator()
        
        # Deshabilitar edición/eliminación para estados finales
        if sale_estado in ["completada", "cancelada"]:
            edit_action.setEnabled(False)
            delete_action.setEnabled(False)
        
        # Conectar acciones
        view_action.triggered.connect(lambda: self.view_sale(sale_id))
        edit_action.triggered.connect(lambda: self.edit_sale(sale_id))
        delete_action.triggered.connect(lambda: self.delete_sale(sale_id))
        
        menu.exec(self.sales_table.viewport().mapToGlobal(position))

    def add_sale(self):
        """Abre el formulario para añadir nueva venta"""
        from .sales_form import SalesForm
        dlg = SalesForm(self.api_client)
        if dlg.exec():
            self.refresh_data()

    def view_sale(self, sale_id):
        """Muestra los detalles de una venta"""
        from .sales_detail import SalesDetailView
        dlg = SalesDetailView(self.api_client, sale_id=sale_id)
        dlg.exec()

    def edit_sale(self, sale_id):
        """Abre el formulario para editar una venta existente"""
        from .sales_form import SalesForm
        dlg = SalesForm(self.api_client, sale_id=sale_id)
        if dlg.exec():
            self.refresh_data()

    def delete_sale(self, sale_id):
        """Elimina una venta con confirmación"""
        # Buscar la venta para mostrar información en el mensaje
        for sale in self.last_sales:
            if sale.get("id_venta") == sale_id:
                cliente_nombre = sale.get("cliente_nombre", "Cliente")
                break
        else:
            cliente_nombre = "Cliente"
        
        answer = QMessageBox.question(
            self, "Eliminar venta",
            f"¿Eliminar la venta #{sale_id} de {cliente_nombre}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if answer == QMessageBox.StandardButton.Yes:
            try:
                self.api_client.delete_sale(sale_id)
                self.refresh_data()
                self.status_bar.showMessage(f"Venta #{sale_id} eliminada correctamente")
            except Exception as e:
                self.show_error(f"No se pudo eliminar la venta: {e}")

    def on_row_double_clicked(self, index):
        """Maneja el doble clic en una fila"""
        mapped_index = self.proxy_model.mapToSource(index)
        sale_id = int(self.sales_model.item(mapped_index.row(), 0).text())
        self.view_sale(sale_id)

    def show_error(self, msg):
        """Muestra un mensaje de error"""
        QMessageBox.critical(self, "Error", msg)
        self.status_bar.showMessage(f"Error: {msg}")