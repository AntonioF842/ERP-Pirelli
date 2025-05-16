from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableView, QHeaderView, QLineEdit, QComboBox, QFrame,
    QMessageBox, QMenu, QDialog, QFormLayout, QDialogButtonBox,
    QAbstractItemView, QSplitter, QToolBar, QStatusBar, QSizePolicy,
    QDateEdit
)
from PyQt6.QtCore import Qt, pyqtSignal, QSortFilterProxyModel, QThread, QSize, QDate
from PyQt6.QtGui import QIcon, QAction, QStandardItemModel, QStandardItem, QFont, QColor
from utils.theme import Theme

class RDProjectListView(QWidget):
    """Vista de listado de proyectos I+D para ERP Pirelli"""

    # Señales
    project_selected = pyqtSignal(int)  # Emitida cuando se selecciona un proyecto

    def __init__(self, api_client):
        super().__init__()
        from utils.theme import Theme
        Theme.apply_window_light_theme(self)

        self.api_client = api_client

        # Conectar señales del cliente API
        self.api_client.data_received.connect(self.on_data_loaded)
        self.api_client.request_error.connect(self.on_request_error)

        # Modelo para la tabla
        self.project_model = QStandardItemModel()
        self.project_model.setHorizontalHeaderLabels([
            "ID", "Nombre", "Descripción", "Fecha Inicio", "Fecha Fin Est.", 
            "Presupuesto", "Estado", "Estado Valor"
        ])

        # Modelo proxy para filtrado
        self.proxy_model = QSortFilterProxyModel()
        self.proxy_model.setSourceModel(self.project_model)
        self.proxy_model.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.proxy_model.setFilterKeyColumn(-1)  # Buscar en todas las columnas

        self.init_ui()
        self.refresh_data()

    def init_ui(self):
        """Inicializa la interfaz de usuario"""
        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # Título de sección
        title_label = QLabel("Gestión de Proyectos I+D")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        main_layout.addWidget(title_label)

        # Barra de herramientas
        toolbar_layout = QHBoxLayout()

        # Filtro de estado
        self.status_filter = QComboBox()
        self.status_filter.addItem("Todos los estados", "")
        self.status_filter.addItem("Planificación", "planificacion")
        self.status_filter.addItem("En Desarrollo", "en_desarrollo")
        self.status_filter.addItem("Completado", "completado")
        self.status_filter.addItem("Cancelado", "cancelado")
        self.status_filter.currentIndexChanged.connect(self.on_status_changed)

        # Campo de búsqueda
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Buscar por nombre...")
        self.search_input.textChanged.connect(self.on_search_changed)

        # Filtro de fecha
        self.date_filter = QDateEdit()
        self.date_filter.setDisplayFormat("yyyy-MM-dd")
        self.date_filter.setDate(QDate.currentDate())
        self.date_filter.setCalendarPopup(True)
        self.date_filter.dateChanged.connect(self.on_date_changed)

        # Botón para añadir
        self.add_btn = QPushButton("Nuevo Proyecto")
        self.add_btn.setIcon(QIcon("resources/icons/add.png"))
        self.add_btn.clicked.connect(self.on_add_project)

        # Botón de actualizar
        self.refresh_btn = QPushButton("Actualizar")
        self.refresh_btn.setIcon(QIcon("resources/icons/refresh.png"))
        self.refresh_btn.clicked.connect(self.refresh_data)

        # Agregar widgets a la barra de herramientas
        toolbar_layout.addWidget(QLabel("Filtrar por estado:"))
        toolbar_layout.addWidget(self.status_filter)
        toolbar_layout.addWidget(QLabel("Buscar:"))
        toolbar_layout.addWidget(self.search_input)
        toolbar_layout.addWidget(QLabel("Fecha:"))
        toolbar_layout.addWidget(self.date_filter)
        toolbar_layout.addStretch()
        toolbar_layout.addWidget(self.add_btn)
        toolbar_layout.addWidget(self.refresh_btn)

        main_layout.addLayout(toolbar_layout)

        # Tabla de proyectos
        self.project_table = QTableView()
        self.project_table.setModel(self.proxy_model)
        self.project_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.project_table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.project_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.project_table.setAlternatingRowColors(True)
        self.project_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.project_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)  # ID
        self.project_table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)  # Presupuesto
        self.project_table.horizontalHeader().setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)  # Estado
        self.project_table.verticalHeader().setVisible(False)
        self.project_table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.project_table.customContextMenuRequested.connect(self.show_context_menu)
        self.project_table.doubleClicked.connect(self.on_row_double_clicked)
        
        main_layout.addWidget(self.project_table)

        # Barra de estado
        self.status_bar = QStatusBar()
        self.status_bar.showMessage("Sistema ERP Pirelli - Módulo de I+D")
        main_layout.addWidget(self.status_bar)

    def refresh_data(self):
        """Actualiza los datos de la tabla desde la API"""
        self.status_bar.showMessage("Actualizando datos de proyectos I+D...")
        self.api_client.get_r_d_projects()

    def load_projects(self, projects):
        """Carga los proyectos recibidos en la tabla"""
        self.project_model.removeRows(0, self.project_model.rowCount())

        for project in projects:
            row = []

            # ID
            id_item = QStandardItem(str(project.id_proyecto))
            id_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            row.append(id_item)

            # Nombre
            name_item = QStandardItem(project.nombre)
            font = QFont()
            font.setBold(True)
            name_item.setFont(font)
            row.append(name_item)

            # Descripción
            desc_item = QStandardItem(project.descripcion_display)
            row.append(desc_item)

            # Fecha Inicio
            fecha_inicio = QStandardItem(project.fecha_inicio if project.fecha_inicio else "N/A")
            fecha_inicio.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            row.append(fecha_inicio)

            # Fecha Fin Estimada
            fecha_fin = QStandardItem(project.fecha_fin_estimada if project.fecha_fin_estimada else "N/A")
            fecha_fin.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            row.append(fecha_fin)

            # Presupuesto
            presupuesto = QStandardItem(f"${project.presupuesto:,.2f}")
            presupuesto.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            row.append(presupuesto)

            # Estado (display)
            estado_item = QStandardItem(project.get_estado_display())
            estado_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            
            # Colorear según estado
            if project.estado == "completado":
                estado_item.setForeground(QColor(Theme.SUCCESS_COLOR))
            elif project.estado == "cancelado":
                estado_item.setForeground(QColor(Theme.DANGER_COLOR))
            elif project.estado == "en_desarrollo":
                estado_item.setForeground(QColor(Theme.INFO_COLOR))
            
            row.append(estado_item)

            # Estado (valor interno, columna oculta)
            estado_valor_item = QStandardItem(project.estado)
            row.append(estado_valor_item)

            self.project_model.appendRow(row)
            
        # Ocultar columna de valor interno de estado
        self.project_table.setColumnHidden(7, True)

    def on_data_loaded(self, data):
        """Maneja los datos cargados desde la API"""
        if data.get("type") == "r_d_projects":
            from models.rd_project_model import RDProject
            projects = [RDProject.from_dict(item) for item in data.get("data", [])]
            self.load_projects(projects)
            self.status_bar.showMessage(f"Se han cargado {len(projects)} proyectos I+D")
        elif data.get("type") == "r_d_project_created":
            QMessageBox.information(self, "Éxito", "Proyecto creado correctamente")
            self.refresh_data()
        elif data.get("type") == "r_d_project_updated":
            QMessageBox.information(self, "Éxito", "Proyecto actualizado correctamente")
            self.refresh_data()
        elif data.get("type") == "r_d_project_deleted":
            QMessageBox.information(self, "Éxito", "Proyecto eliminado correctamente")
            self.refresh_data()

    def on_request_error(self, error_message):
        """Maneja errores de la API"""
        QMessageBox.critical(self, "Error", f"Error al cargar proyectos: {error_message}")
        self.status_bar.showMessage(f"Error: {error_message}")

    def on_search_changed(self, text):
        """Maneja el cambio en el campo de búsqueda"""
        self.proxy_model.setFilterWildcard(text)
        self.proxy_model.invalidateFilter()

    def on_status_changed(self, index):
        """Maneja el cambio en el filtro de estado"""
        status = self.status_filter.currentData()
        if status:
            self.proxy_model.setFilterRegularExpression(status)
            self.proxy_model.setFilterKeyColumn(7)  # Filtrar por columna de estado valor
        else:
            self.proxy_model.setFilterWildcard("")
        self.proxy_model.invalidateFilter()

    def on_date_changed(self, date):
        """Maneja el cambio en el filtro de fecha"""
        # Implementar lógica de filtrado por fecha si es necesario
        pass

    def on_row_double_clicked(self, index):
        """Maneja el doble clic en una fila"""
        mapped_index = self.proxy_model.mapToSource(index)
        row = mapped_index.row()
        project_id = int(self.project_model.item(row, 0).text())
        self.project_selected.emit(project_id)
        self.on_view_project(project_id)

    def show_context_menu(self, position):
        """Muestra menú contextual para una fila"""
        index = self.project_table.indexAt(position)
        if not index.isValid():
            return

        context_menu = QMenu(self)
        view_action = QAction(QIcon("resources/icons/view.png"), "Ver detalles", self)
        edit_action = QAction(QIcon("resources/icons/edit.png"), "Editar", self)
        delete_action = QAction(QIcon("resources/icons/delete.png"), "Eliminar", self)
        progress_action = QAction(QIcon("resources/icons/progress.png"), "Actualizar progreso", self)
        report_action = QAction(QIcon("resources/icons/report.png"), "Generar reporte", self)

        context_menu.addAction(view_action)
        context_menu.addAction(edit_action)
        context_menu.addSeparator()
        context_menu.addAction(progress_action)
        context_menu.addAction(report_action)
        context_menu.addSeparator()
        context_menu.addAction(delete_action)

        mapped_index = self.proxy_model.mapToSource(index)
        row = mapped_index.row()
        project_id = int(self.project_model.item(row, 0).text())

        view_action.triggered.connect(lambda: self.on_view_project(project_id))
        edit_action.triggered.connect(lambda: self.on_edit_project(project_id))
        delete_action.triggered.connect(lambda: self.on_delete_project(project_id))
        progress_action.triggered.connect(lambda: self.on_update_progress(project_id))
        report_action.triggered.connect(lambda: self.on_generate_report(project_id))

        context_menu.exec(self.project_table.viewport().mapToGlobal(position))

    def on_add_project(self):
        """Muestra el diálogo para añadir un nuevo proyecto"""
        from .rd_project_form import RDProjectForm
        dialog = RDProjectForm(self.api_client)
        dialog.project_saved.connect(self._handle_project_save)
        dialog.exec()

    def on_view_project(self, project_id):
        """Muestra detalles de un proyecto"""
        from .rd_project_detail import RDProjectDetailView
        project = self._get_project_by_id(project_id)
        if project:
            dialog = RDProjectDetailView(self.api_client, project.to_dict())
            dialog.exec()

    def on_edit_project(self, project_id):
        """Abre el formulario de edición de un proyecto"""
        project = self._get_project_by_id(project_id)
        if project:
            from .rd_project_form import RDProjectForm
            dialog = RDProjectForm(self.api_client, project.to_dict())
            dialog.project_saved.connect(self._handle_project_save)
            dialog.exec()

    def on_delete_project(self, project_id):
        """Elimina un proyecto"""
        reply = QMessageBox.question(
            self,
            "Confirmar eliminación",
            f"¿Está seguro que desea eliminar el proyecto ID: {project_id}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.api_client.delete_r_d_project(project_id)
            self.status_bar.showMessage(f"Eliminando proyecto ID: {project_id}...")

    def on_update_progress(self, project_id):
        """Actualiza el progreso de un proyecto"""
        self.status_bar.showMessage(f"Actualizando progreso del proyecto ID: {project_id}...")

    def on_generate_report(self, project_id):
        """Genera un reporte para un proyecto"""
        self.status_bar.showMessage(f"Generando reporte para proyecto ID: {project_id}...")

    def _get_project_by_id(self, project_id):
        """Busca un proyecto por su ID en el modelo actual"""
        for row in range(self.project_model.rowCount()):
            if int(self.project_model.item(row, 0).text()) == project_id:
                from models.rd_project_model import RDProject
                project_data = {
                    "id_proyecto": self.project_model.item(row, 0).text(),
                    "nombre": self.project_model.item(row, 1).text(),
                    "descripcion": self.project_model.item(row, 2).text(),
                    "fecha_inicio": self.project_model.item(row, 3).text(),
                    "fecha_fin_estimada": self.project_model.item(row, 4).text(),
                    "presupuesto": self.project_model.item(row, 5).text().replace("$", "").replace(",", ""),
                    "estado": self.project_model.item(row, 7).text()
                }
                return RDProject.from_dict(project_data)
        return None

    def _handle_project_save(self, project_data):
        """Maneja el guardado de un proyecto (nuevo o editado)"""
        if "id_proyecto" in project_data and project_data["id_proyecto"]:
            # Actualizar proyecto
            self.api_client.update_r_d_project(project_data["id_proyecto"], project_data)
            self.status_bar.showMessage(f"Actualizando proyecto ID: {project_data['id_proyecto']}...")
        else:
            # Crear proyecto
            self.api_client.create_r_d_project(project_data)
            self.status_bar.showMessage("Creando nuevo proyecto...")