from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableView, QHeaderView, QLineEdit, QComboBox, QFrame,
    QMessageBox, QMenu, QDialog, QFormLayout, QDialogButtonBox,
    QAbstractItemView, QSplitter, QToolBar, QStatusBar, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal, QSortFilterProxyModel, QThread, QSize
from PyQt6.QtGui import QIcon, QAction, QStandardItemModel, QStandardItem, QFont, QColor
from utils.theme import Theme
from datetime import datetime

from .production_orders_detail import ProductionOrderDetailView
from .production_orders_form import ProductionOrderForm
from models.production_order_model import ProductionOrder


class ProductionOrderListView(QWidget):
    """Vista de listado de órdenes de producción para ERP Pirelli"""

    # Señales
    order_selected = pyqtSignal(int)  # Emitida cuando se selecciona una orden

    def __init__(self, api_client):
        super().__init__()
        from utils.theme import Theme
        Theme.apply_window_light_theme(self)

        self.api_client = api_client

        # Conectar señales del cliente API
        self.api_client.data_received.connect(self.on_data_loaded)
        self.api_client.request_error.connect(self.on_request_error)

        # Modelo para la tabla
        self.order_model = QStandardItemModel()
        self.order_model.setHorizontalHeaderLabels([
            "ID", "Producto", "Cantidad", "Fecha Inicio", "Fecha Fin", 
            "Estado", "Estado Valor", "Usuario"
        ])

        # Modelo proxy para filtrado avanzado
        self.proxy_model = QSortFilterProxyModel()
        self.proxy_model.setSourceModel(self.order_model)
        self.proxy_model.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.proxy_model.setFilterKeyColumn(-1)  # Buscar en todas las columnas
        self.setup_filter_proxy()

        # Colores corporativos Pirelli
        self.pirelli_red = Theme.SECONDARY_COLOR
        self.pirelli_yellow = Theme.ACCENT_COLOR
        self.pirelli_dark = Theme.PRIMARY_COLOR
        self.pirelli_light = Theme.LIGHT_BG

        self.init_ui()

        # Cargar datos iniciales
        self.refresh_data()

    def init_ui(self):
        """Inicializa la interfaz de usuario"""
        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # Título de sección
        title_label = QLabel("Gestión de Órdenes de Producción")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        main_layout.addWidget(title_label)

        # Barra de herramientas
        toolbar_layout = QHBoxLayout()

        # Filtro de estado
        self.status_filter = QComboBox()
        self.status_filter.addItem("Todos los estados", "")
        self.status_filter.addItem("Planificada", "planificada")
        self.status_filter.addItem("En Proceso", "en_proceso")
        self.status_filter.addItem("Completada", "completada")
        self.status_filter.addItem("Cancelada", "cancelada")
        self.status_filter.currentIndexChanged.connect(self.on_status_changed)

        # Campo de búsqueda
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Buscar por producto...")
        self.search_input.textChanged.connect(self.on_search_changed)

        # Botón de búsqueda
        search_btn = QPushButton("Buscar")
        search_btn.clicked.connect(self._on_filters_changed)

        # Botón para añadir
        self.add_btn = QPushButton("Nueva Orden")
        self.add_btn.setIcon(QIcon("resources/icons/add.png"))
        self.add_btn.clicked.connect(self.on_add_order)

        # Botón de actualizar
        self.refresh_btn = QPushButton("Actualizar")
        self.refresh_btn.setIcon(QIcon("resources/icons/refresh.png"))
        self.refresh_btn.clicked.connect(self.refresh_data)

        # Agregar widgets a la barra de herramientas
        toolbar_layout.addWidget(QLabel("Filtrar por estado:"))
        toolbar_layout.addWidget(self.status_filter)
        toolbar_layout.addWidget(self.search_input)
        toolbar_layout.addWidget(search_btn)
        toolbar_layout.addStretch()
        toolbar_layout.addWidget(self.add_btn)
        toolbar_layout.addWidget(self.refresh_btn)

        main_layout.addLayout(toolbar_layout)

        # Tabla de órdenes
        self.order_table = QTableView()
        self.order_table.setModel(self.proxy_model)
        self.order_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.order_table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.order_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.order_table.setAlternatingRowColors(True)
        self.order_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.order_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)  # ID
        self.order_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)  # Cantidad
        self.order_table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)  # Estado
        self.order_table.verticalHeader().setVisible(False)
        self.order_table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.order_table.customContextMenuRequested.connect(self.show_context_menu)
        self.order_table.doubleClicked.connect(self.on_row_double_clicked)
        
        main_layout.addWidget(self.order_table)

        # Labels de totales
        summary_layout = QHBoxLayout()
        self.total_label = QLabel("Total de órdenes: <b>0</b>")
        self.planned_label = QLabel("Planificadas: <b>0</b>")
        self.in_progress_label = QLabel("En Proceso: <b>0</b>")
        self.completed_label = QLabel("Completadas: <b>0</b>")

        summary_layout.addWidget(self.total_label)
        summary_layout.addSpacing(30)
        summary_layout.addWidget(self.planned_label)
        summary_layout.addSpacing(30)
        summary_layout.addWidget(self.in_progress_label)
        summary_layout.addSpacing(30)
        summary_layout.addWidget(self.completed_label)
        summary_layout.addStretch()
        main_layout.addLayout(summary_layout)

        # Barra de estado
        self.status_bar = QStatusBar()
        self.status_bar.showMessage("Sistema ERP Pirelli - Módulo de Producción v2.1")
        main_layout.addWidget(self.status_bar)

    def setup_filter_proxy(self):
        """Configura el modelo proxy para filtrado avanzado"""
        self.proxy_model.filterAcceptsRow = self._filter_accepts_row
    
    def _filter_accepts_row(self, source_row, source_parent):
        """Método personalizado para determinar si una fila cumple con los filtros"""
        model = self.order_model
        
        # Obtener valores de los filtros
        search_text = self.search_input.text().strip().lower()
        status = self.status_filter.currentData()
        
        # Si no hay filtros activos, mostrar todas las filas
        if not search_text and not status:
            return True
            
        # Obtener valores de la fila actual
        try:
            producto = model.item(source_row, 1).text().lower()
            estado_valor = model.item(source_row, 6).text().lower()  # columna oculta con valor interno
            
            # Filtro de búsqueda (producto)
            if search_text and search_text not in producto:
                return False
                
            # Filtro de estado (compara valor interno exacto)
            if status and status != estado_valor:
                return False
                
            return True
        except (AttributeError, IndexError):
            return True

    def on_search_changed(self, text):
        """Maneja el cambio en el campo de búsqueda"""
        self.proxy_model.setFilterWildcard(text)
        self.proxy_model.invalidateFilter()
        self.status_bar.showMessage(f"Filtrando órdenes por: {text}" if text else "Sistema ERP Pirelli - Módulo de Producción v2.1")

    def on_status_changed(self, index):
        """Maneja el cambio en el filtro de estado"""
        self._on_filters_changed()

    def _on_filters_changed(self):
        """Se llama cuando cambia estado, para actualizar el filtrado"""
        self.proxy_model.invalidateFilter()
        status = self.status_filter.currentData()
        
        msg = "Mostrando órdenes"
        if status:
            msg += f" con estado: {self.status_filter.currentText()}"
        else:
            msg = "Sistema ERP Pirelli - Módulo de Producción v2.1"
            
        self.status_bar.showMessage(msg)

    def refresh_data(self):
        """Actualiza los datos de la tabla desde la API"""
        self.status_bar.showMessage("Actualizando datos de órdenes de producción...")
        self.api_client.get_production_orders()

    def load_orders(self, orders):
        """Carga las órdenes recibidas en la tabla y actualiza estadísticas"""
        self.order_model.removeRows(0, self.order_model.rowCount())
        count_planned = count_in_progress = count_completed = 0

        for order in orders:
            row = []

            # ID
            id_item = QStandardItem(str(order.id_orden_produccion))
            id_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            row.append(id_item)

            # Producto
            producto_name = order.producto.get('nombre', 'N/A') if hasattr(order, 'producto') and isinstance(order.producto, dict) else 'N/A'
            producto_item = QStandardItem(producto_name)
            row.append(producto_item)

            # Cantidad
            cantidad_item = QStandardItem(str(order.cantidad))
            cantidad_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            row.append(cantidad_item)

            # Fecha Inicio
            fecha_inicio = order.fecha_inicio.strftime("%d/%m/%Y") if hasattr(order, 'fecha_inicio') and order.fecha_inicio else "N/A"
            fecha_inicio_item = QStandardItem(fecha_inicio)
            row.append(fecha_inicio_item)

            # Fecha Fin
            fecha_fin = order.fecha_fin.strftime("%d/%m/%Y") if hasattr(order, 'fecha_fin') and order.fecha_fin else "N/A"
            fecha_fin_item = QStandardItem(fecha_fin)
            row.append(fecha_fin_item)

            # Estado (display)
            estado_display = order.get_estado_display() if hasattr(order, 'get_estado_display') else "N/A"
            estado_item = QStandardItem(estado_display)
            
            # Colorear según estado
            if order.estado == "planificada":
                estado_item.setForeground(QColor(Theme.INFO_COLOR))
                count_planned += 1
            elif order.estado == "en_proceso":
                estado_item.setForeground(QColor(Theme.WARNING_COLOR))
                count_in_progress += 1
            elif order.estado == "completada":
                estado_item.setForeground(QColor(Theme.SUCCESS_COLOR))
                count_completed += 1
            elif order.estado == "cancelada":
                estado_item.setForeground(QColor(Theme.DANGER_COLOR))
            row.append(estado_item)

            # Estado (valor interno, columna oculta)
            estado_valor_item = QStandardItem(order.estado)
            row.append(estado_valor_item)

            # Usuario
            usuario_name = order.usuario.get('nombre', 'N/A') if hasattr(order, 'usuario') and isinstance(order.usuario, dict) else 'N/A'
            usuario_item = QStandardItem(usuario_name)
            row.append(usuario_item)

            self.order_model.appendRow(row)
            
        # Ocultar columna de valor interno de estado
        self.order_table.setColumnHidden(6, True)

        total = len(orders)
        self.total_label.setText(f"Total de órdenes: <b>{total}</b>")
        self.planned_label.setText(f"Planificadas: <b>{count_planned}</b>")
        self.in_progress_label.setText(f"En Proceso: <b>{count_in_progress}</b>")
        self.completed_label.setText(f"Completadas: <b>{count_completed}</b>")
        self.status_bar.showMessage(f"Se han cargado {total} órdenes de producción")

    # Añade este método a la clase si no existe
    def get_estado_display(self, estado):
        """Obtiene el nombre para mostrar del estado"""
        estados = {
            "planificada": "Planificada",
            "en_proceso": "En Proceso",
            "completada": "Completada",
            "cancelada": "Cancelada"
        }
        return estados.get(estado, "Desconocido")

    def on_data_loaded(self, data):
        """Maneja los datos cargados desde la API"""
        if data.get("type") == "production_orders":
            # Convertir los datos del API a objetos ProductionOrder
            orders = [ProductionOrder.from_dict(item) for item in data.get("data", [])]
            self.load_orders(orders)
        elif data.get("type") == "production_order_created":
            QMessageBox.information(self, "Éxito", "Orden de producción creada correctamente")
            self.refresh_data()
        elif data.get("type") == "production_order_updated":
            QMessageBox.information(self, "Éxito", "Orden de producción actualizada correctamente")
            self.refresh_data()
        elif data.get("type") == "production_order_deleted":
            QMessageBox.information(self, "Éxito", "Orden de producción eliminada correctamente")
            self.refresh_data()

    def on_request_error(self, error_message):
        """Maneja errores de la API"""
        QMessageBox.critical(self, "Error", f"Error al cargar órdenes: {error_message}")
        self.status_bar.showMessage(f"Error: {error_message}")

    def on_row_double_clicked(self, index):
        """Maneja el doble clic en una fila"""
        mapped_index = self.proxy_model.mapToSource(index)
        row = mapped_index.row()
        order_id = int(self.order_model.item(row, 0).text())
        self.order_selected.emit(order_id)
        self.on_view_order(order_id)

    def show_context_menu(self, position):
        """Muestra menú contextual para una fila"""
        index = self.order_table.indexAt(position)
        if not index.isValid():
            return

        context_menu = QMenu(self)
        view_action = QAction(QIcon("resources/icons/view.png"), "Ver detalles", self)
        edit_action = QAction(QIcon("resources/icons/edit.png"), "Editar", self)
        delete_action = QAction(QIcon("resources/icons/delete.png"), "Eliminar", self)

        context_menu.addAction(view_action)
        context_menu.addAction(edit_action)
        context_menu.addSeparator()
        context_menu.addAction(delete_action)

        mapped_index = self.proxy_model.mapToSource(index)
        row = mapped_index.row()
        order_id = int(self.order_model.item(row, 0).text())

        view_action.triggered.connect(lambda: self.on_view_order(order_id))
        edit_action.triggered.connect(lambda: self.on_edit_order(order_id))
        delete_action.triggered.connect(lambda: self.on_delete_order(order_id))

        context_menu.exec(self.order_table.viewport().mapToGlobal(position))

    def on_view_order(self, order_id):
        """Muestra detalles de una orden"""
        order = self._get_order_by_id(order_id)
        if order:
            # Using relative import
            dialog = ProductionOrderDetailView(self.api_client, order.to_dict())
            dialog.exec()
        else:
            QMessageBox.warning(self, "Error", "No se pudo cargar la orden")

    def on_add_order(self):
        """Muestra el diálogo para añadir una nueva orden"""
        # Using relative import
        dialog = ProductionOrderForm(self.api_client)
        dialog.order_saved.connect(self._handle_order_save)
        dialog.exec()

    def on_edit_order(self, order_id):
        """Abre el formulario de edición de una orden"""
        order = self._get_order_by_id(order_id)
        if order:
            # Using relative import
            dialog = ProductionOrderForm(self.api_client, order)
            dialog.order_saved.connect(self._handle_order_save)
            dialog.exec()
        else:
            QMessageBox.warning(self, "Error", "No se pudo cargar la orden")

    def _get_order_by_id(self, order_id):
        """Busca una orden por su ID en el modelo actual"""
        for row in range(self.order_model.rowCount()):
            if int(self.order_model.item(row, 0).text()) == order_id:
                from models.production_order_model import ProductionOrder
                return ProductionOrder.from_dict({
                    "id_orden_produccion": self.order_model.item(row, 0).text(),
                    "id_producto": "",  # Se cargará del API en el formulario
                    "cantidad": self.order_model.item(row, 2).text(),
                    "fecha_inicio": self.order_model.item(row, 3).text(),
                    "fecha_fin": self.order_model.item(row, 4).text(),
                    "estado": self.order_model.item(row, 6).text(),
                    "id_usuario": ""  # Se cargará del API en el formulario
                })
        return None

    def _show_edit_form(self, order):
        """Muestra el formulario de edición con los datos de la orden"""
        from .production_orders_form import ProductionOrderForm  # Importación relativa
        if order:
            dialog = ProductionOrderForm(self.api_client, order.to_dict())
            dialog.order_saved.connect(self._handle_order_save)
            dialog.exec()
        else:
            QMessageBox.warning(self, "Error", "No se pudo cargar la orden")

    def _handle_order_save(self, order_data):
        """Maneja el guardado de una orden (nueva o editada)"""
        if "id_orden_produccion" in order_data and order_data["id_orden_produccion"]:
            # Actualizar orden
            self.api_client.update_production_order(order_data["id_orden_produccion"], order_data)
        else:
            # Crear orden
            self.api_client.create_production_order(order_data)

    def on_delete_order(self, order_id):
        """Elimina una orden"""
        reply = QMessageBox.question(
            self,
            "Confirmar eliminación",
            f"¿Está seguro que desea eliminar la orden ID: {order_id}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.api_client.delete_production_order(order_id)
            self.status_bar.showMessage(f"Eliminando orden ID: {order_id}...")

    def on_start_order(self, order_id):
        """Cambia el estado de una orden a 'en_proceso'"""
        self._change_order_status(order_id, "en_proceso", "Iniciando producción...")

    def on_complete_order(self, order_id):
        """Cambia el estado de una orden a 'completada'"""
        reply = QMessageBox.question(
            self,
            "Confirmar completado",
            "¿Está seguro que desea marcar esta orden como completada?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self._change_order_status(order_id, "completada", "Marcando como completada...")

    def on_cancel_order(self, order_id):
        """Cambia el estado de una orden a 'cancelada'"""
        reply = QMessageBox.question(
            self,
            "Confirmar cancelación",
            "¿Está seguro que desea cancelar esta orden?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self._change_order_status(order_id, "cancelada", "Cancelando orden...")

    def _change_order_status(self, order_id, new_status, message):
        """Cambia el estado de una orden de producción
        
        Args:
            order_id: ID de la orden a modificar
            new_status: Nuevo estado a asignar
            message: Mensaje para mostrar en la barra de estado
        """
        try:
            # Obtener la orden actual para preservar otros campos
            current_order = self._get_order_by_id(order_id)
            if not current_order:
                QMessageBox.warning(self, "Error", "No se encontró la orden")
                return

            # Preparar datos para la actualización
            order_data = {
                "id_orden_produccion": order_id,
                "estado": new_status,
                # Mantener los demás campos sin cambios
                "id_producto": current_order.id_producto,
                "cantidad": current_order.cantidad,
                "fecha_inicio": current_order.fecha_inicio.strftime('%Y-%m-%d') if current_order.fecha_inicio else None,
                "fecha_fin": current_order.fecha_fin.strftime('%Y-%m-%d') if current_order.fecha_fin else None,
                "id_usuario": current_order.id_usuario,
                "notas": getattr(current_order, 'notas', None)
            }

            # Mostrar mensaje de progreso
            self.status_bar.showMessage(message)

            # Llamar al API client para actualizar
            response = self.api_client.update_production_order(order_id, order_data)
            
            if response:
                QMessageBox.information(self, "Éxito", f"Orden {order_id} actualizada a estado: {new_status}")
                self.refresh_data()
            else:
                QMessageBox.warning(self, "Error", "No se pudo actualizar el estado de la orden")
                
        except Exception as e:
            QMessageBox.critical(
                self, 
                "Error", 
                f"Error al cambiar estado:\n{str(e)}"
            )
            self.status_bar.showMessage("Error al cambiar estado de la orden")