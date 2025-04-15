from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
                            QTableWidgetItem, QPushButton, QLabel, QComboBox,
                            QLineEdit, QHeaderView, QMessageBox)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QIcon

class SalesListView(QWidget):
    """Vista de listado de ventas"""
    
    def __init__(self, api_client):
        super().__init__()
        
        self.api_client = api_client
        
        # Conectar señales del API
        self.api_client.data_received.connect(self.on_request_success)

        self.api_client.request_error.connect(self.on_request_error)
        
        self.init_ui()
        
        # Cargar datos al inicializar
        self.refresh_data()
    
    def init_ui(self):
        """Inicializa la interfaz de usuario"""
        # Layout principal
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Título
        title_label = QLabel("Gestión de Ventas")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        
        # Barra de herramientas
        toolbar_layout = QHBoxLayout()
        
        # Filtros
        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["Todos", "Pendiente", "Completada", "Cancelada"])
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Buscar por cliente o ID...")
        self.search_input.textChanged.connect(self.apply_filters)
        
        search_btn = QPushButton("Buscar")
        search_btn.clicked.connect(self.apply_filters)
        
        # Botones de acción
        self.add_btn = QPushButton("Nueva Venta")
        self.add_btn.setIcon(QIcon("resources/icons/add.png"))
        self.add_btn.clicked.connect(self.add_sale)
        
        self.refresh_btn = QPushButton("Actualizar")
        self.refresh_btn.setIcon(QIcon("resources/icons/refresh.png"))
        self.refresh_btn.clicked.connect(self.refresh_data)
        
        # Agregar widgets a la barra de herramientas
        toolbar_layout.addWidget(QLabel("Filtrar por estado:"))
        toolbar_layout.addWidget(self.filter_combo)
        toolbar_layout.addWidget(self.search_input)
        toolbar_layout.addWidget(search_btn)
        toolbar_layout.addStretch()
        toolbar_layout.addWidget(self.add_btn)
        toolbar_layout.addWidget(self.refresh_btn)
        
        # Tabla de ventas
        self.sales_table = QTableWidget()
        self.sales_table.setColumnCount(7)
        self.sales_table.setHorizontalHeaderLabels([
            "ID", "Cliente", "Fecha", "Total", "Estado", "Creado por", "Acciones"
        ])
        
        # Configurar tabla
        self.sales_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.sales_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.sales_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.sales_table.setAlternatingRowColors(True)
        
        # Agregar widgets al layout principal
        main_layout.addWidget(title_label)
        main_layout.addLayout(toolbar_layout)
        main_layout.addWidget(self.sales_table)
        
        self.setLayout(main_layout)
    
    def refresh_data(self):
        """Carga los datos de ventas desde la API"""
        # Mostrar indicador de carga
        self.sales_table.setRowCount(0)
        
        # Solicitar datos al backend
        self.api_client.get_sales()
    
    def on_request_success(self, endpoint, data):
        """Maneja la respuesta exitosa de la API"""
        if endpoint != "ventas":
            return
            
        # Limpiar tabla
        self.sales_table.setRowCount(0)
        
        # Filtrar datos si es necesario
        filtered_data = self.filter_data(data)
        
        # Llenar tabla con datos
        for row, sale in enumerate(filtered_data):
            self.sales_table.insertRow(row)
            
            # ID
            self.sales_table.setItem(row, 0, QTableWidgetItem(str(sale.get("id_venta", ""))))
            
            # Cliente
            cliente = sale.get("cliente", {}).get("nombre", "N/A")
            self.sales_table.setItem(row, 1, QTableWidgetItem(cliente))
            
            # Fecha
            self.sales_table.setItem(row, 2, QTableWidgetItem(sale.get("fecha", "")))
            
            # Total
            total = f"${sale.get('total', 0):,.2f}"
            total_item = QTableWidgetItem(total)
            total_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.sales_table.setItem(row, 3, total_item)
            
            # Estado
            estado = sale.get("estado", "").capitalize()
            estado_item = QTableWidgetItem(estado)
            
            # Colorear según estado
            if estado == "Completada":
                estado_item.setForeground(Qt.GlobalColor.darkGreen)
            elif estado == "Pendiente":
                estado_item.setForeground(Qt.GlobalColor.darkBlue)
            elif estado == "Cancelada":
                estado_item.setForeground(Qt.GlobalColor.darkRed)
                
            self.sales_table.setItem(row, 4, estado_item)
            
            # Usuario
            self.sales_table.setItem(row, 5, QTableWidgetItem(sale.get("usuario", {}).get("nombre", "N/A")))
            
            # Botones de acción
            actions_layout = QHBoxLayout()
            actions_layout.setContentsMargins(0, 0, 0, 0)
            actions_layout.setSpacing(5)
            
            view_btn = QPushButton()
            view_btn.setIcon(QIcon("resources/icons/view.png"))
            view_btn.setToolTip("Ver detalles")
            view_btn.clicked.connect(lambda checked, s=sale: self.view_sale(s))
            view_btn.setFixedSize(30, 30)
            
            edit_btn = QPushButton()
            edit_btn.setIcon(QIcon("resources/icons/edit.png"))
            edit_btn.setToolTip("Editar")
            edit_btn.clicked.connect(lambda checked, s=sale: self.edit_sale(s))
            edit_btn.setFixedSize(30, 30)
            
            delete_btn = QPushButton()
            delete_btn.setIcon(QIcon("resources/icons/delete.png"))
            delete_btn.setToolTip("Eliminar")
            delete_btn.clicked.connect(lambda checked, s=sale: self.delete_sale(s))
            delete_btn.setFixedSize(30, 30)
            
            actions_layout.addWidget(view_btn)
            actions_layout.addWidget(edit_btn)
            actions_layout.addWidget(delete_btn)
            
            # Deshabilitar botones según el estado
            if estado == "Completada" or estado == "Cancelada":
                edit_btn.setEnabled(False)
                delete_btn.setEnabled(False)
            
            # Agregar botones a la celda
            actions_widget = QWidget()
            actions_widget.setLayout(actions_layout)
            self.sales_table.setCellWidget(row, 6, actions_widget)
    
    def filter_data(self, data):
        """Filtra los datos según los criterios seleccionados"""
        filtered_data = data
        
        # Filtrar por estado
        estado_filtro = self.filter_combo.currentText()
        if estado_filtro != "Todos":
            filtered_data = [sale for sale in filtered_data if sale.get("estado", "").capitalize() == estado_filtro]
        
        # Filtrar por búsqueda
        search_text = self.search_input.text().lower()
        if search_text:
            filtered_data = [
                sale for sale in filtered_data
                if (
                    search_text in str(sale.get("id_venta", "")).lower() or
                    search_text in sale.get("cliente", {}).get("nombre", "").lower()
                )
            ]
        
        return filtered_data
    
    def apply_filters(self):
        """Aplica los filtros actuales a los datos"""
        # Volver a solicitar los datos con los filtros
        self.refresh_data()
    
    def add_sale(self):
        """Abre el formulario para agregar una nueva venta"""
        QMessageBox.information(self, "Información", "Funcionalidad pendiente: Agregar nueva venta")
        # Aquí se abriría el formulario de ventas
        # from views.sales.sales_form import SalesForm
        # form = SalesForm(self.api_client)
        # form.exec()
        # self.refresh_data()
    
    def view_sale(self, sale):
        """Abre la vista de detalle de una venta"""
        QMessageBox.information(self, "Información", f"Funcionalidad pendiente: Ver venta {sale.get('id_venta')}")
        # Aquí se abriría la vista detallada
        # from views.sales.sales_detail import SalesDetailView
        # detail_view = SalesDetailView(self.api_client, sale.get('id_venta'))
        # detail_view.exec()
    
    def edit_sale(self, sale):
        """Abre el formulario para editar una venta"""
        QMessageBox.information(self, "Información", f"Funcionalidad pendiente: Editar venta {sale.get('id_venta')}")
        # Aquí se abriría el formulario de ventas en modo edición
        # from views.sales.sales_form import SalesForm
        # form = SalesForm(self.api_client, sale.get('id_venta'))
        # form.exec()
        # self.refresh_data()
    
    def delete_sale(self, sale):
        """Elimina una venta"""
        reply = QMessageBox.question(
            self, 
            "Confirmar eliminación", 
            f"¿Está seguro que desea eliminar la venta #{sale.get('id_venta')}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Solicitar eliminación al backend
            self.api_client.delete(f"ventas/{sale.get('id_venta')}")
            
            # Actualizar la tabla
            self.refresh_data()
    
    def on_request_error(self, error_message):
        """Maneja errores de la API"""
        QMessageBox.critical(self, "Error", f"Error al cargar datos: {error_message}")