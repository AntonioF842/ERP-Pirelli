from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QLabel,
    QHBoxLayout, QPushButton, QLineEdit, QMessageBox, QHeaderView, QDialog,
    QFormLayout, QDialogButtonBox, QComboBox
)
from PyQt6.QtGui import QIcon
from controllers.users_controller import UsersController

class UsersListView(QWidget):
    """
    Vista PyQt para listar usuarios con filtro, botón de agregar y acciones (editar/eliminar).
    """
    def __init__(self, api_client, parent=None):
        super().__init__(parent)
        self.api_client = api_client
        self.controller = UsersController(api_client)
        self.last_users = []
        self.setup_ui()
        self.refresh_data()

    def setup_ui(self):
        """Configura los elementos de la interfaz de usuario"""
        main_layout = QVBoxLayout(self)
        
        # Título de la vista
        title_label = QLabel("Usuarios")
        title_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        main_layout.addWidget(title_label)
        
        # Barra de herramientas (filtros y botón añadir)
        toolbar_layout = QHBoxLayout()
        
        # Filtro por rol
        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["Todos", "admin", "supervisor", "empleado"])
        self.filter_combo.currentIndexChanged.connect(self.apply_filters)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Buscar por nombre o email...")
        self.search_input.textChanged.connect(self.apply_filters)
        
        add_btn = QPushButton("Agregar Usuario")
        add_btn.setIcon(QIcon("resources/icons/add.png"))
        add_btn.clicked.connect(self.add_user_dialog)
        
        toolbar_layout.addWidget(QLabel("Rol:"))
        toolbar_layout.addWidget(self.filter_combo)
        toolbar_layout.addStretch()
        toolbar_layout.addWidget(self.search_input)
        toolbar_layout.addWidget(add_btn)
        main_layout.addLayout(toolbar_layout)
        
        # Tabla de usuarios
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "Nombre", "Email", "Rol", "Acciones"])
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        main_layout.addWidget(self.table)
        
        self.setLayout(main_layout)

    def refresh_data(self):
        """Obtiene los datos de usuarios y actualiza la tabla"""
        try:
            self.last_users = self.controller.fetch_users()
            self.apply_filters()
        except Exception as e:
            self.show_error(str(e))
    
    def apply_filters(self):
        """Aplica los filtros de rol y búsqueda a la lista de usuarios"""
        rol = self.filter_combo.currentText().lower()
        buscar = self.search_input.text().strip().lower()
        
        filtered = self.last_users
        if rol != "todos":
            filtered = [u for u in filtered if u.get('rol', '').lower() == rol]
        
        if buscar:
            filtered = [
                u for u in filtered
                if buscar in (u.get("nombre", "") or "").lower() or
                   buscar in (u.get("email", "") or "").lower()
            ]
        
        self.display_rows(filtered)
        
    def display_rows(self, data):
        """Muestra los datos en la tabla"""
        self.table.setRowCount(len(data))
        
        # Llenar la tabla con datos
        for row_idx, user in enumerate(data):
            self.table.setItem(row_idx, 0, QTableWidgetItem(str(user.get('id_usuario', ''))))
            self.table.setItem(row_idx, 1, QTableWidgetItem(user.get('nombre', '')))
            self.table.setItem(row_idx, 2, QTableWidgetItem(user.get('email', '')))
            self.table.setItem(row_idx, 3, QTableWidgetItem(user.get('rol', '')))
            
            # Columna acciones: Botones con iconos
            action_widget = QWidget()
            action_layout = QHBoxLayout()
            action_layout.setContentsMargins(0, 0, 0, 0)
            action_layout.setSpacing(5)
            
            view_btn = QPushButton()
            view_btn.setIcon(QIcon("resources/icons/view.png"))
            view_btn.setToolTip("Ver detalles")
            view_btn.setFixedSize(30, 30)
            view_btn.clicked.connect(lambda _=None, u=user: self.view_user_details(u))
            
            edit_btn = QPushButton()
            edit_btn.setIcon(QIcon("resources/icons/edit.png"))
            edit_btn.setToolTip("Editar usuario")
            edit_btn.setFixedSize(30, 30)
            edit_btn.clicked.connect(lambda _=None, u=user: self.edit_user_dialog(u))
            
            delete_btn = QPushButton()
            delete_btn.setIcon(QIcon("resources/icons/delete.png"))
            delete_btn.setToolTip("Eliminar usuario")
            delete_btn.setFixedSize(30, 30)
            delete_btn.clicked.connect(lambda _=None, u=user: self.delete_user(u))
            
            action_layout.addWidget(view_btn)
            action_layout.addWidget(edit_btn)
            action_layout.addWidget(delete_btn)
            action_widget.setLayout(action_layout)
            self.table.setCellWidget(row_idx, 4, action_widget)

    def view_user_details(self, user):
        """Muestra los detalles de un usuario"""
        # Aquí se implementaría la vista de detalles
        QMessageBox.information(self, "Detalles de Usuario", 
                               f"Detalles del usuario: {user.get('nombre', '')}")
        
    def add_user_dialog(self):
        """Abre un diálogo para agregar un nuevo usuario"""
        class UserFormDialog(QDialog):
            def __init__(self):
                super().__init__()
                self.setWindowTitle("Agregar Usuario")
                self.layout = QFormLayout(self)
                self.name = QLineEdit()
                self.email = QLineEdit()
                self.role = QLineEdit()
                self.password = QLineEdit()
                self.password.setEchoMode(QLineEdit.EchoMode.Password)
                self.layout.addRow("Nombre:", self.name)
                self.layout.addRow("Email:", self.email)
                self.layout.addRow("Rol:", self.role)
                self.layout.addRow("Password:", self.password)
                self.buttons = QDialogButtonBox(
                    QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
                )
                self.buttons.accepted.connect(self.accept)
                self.buttons.rejected.connect(self.reject)
                self.layout.addWidget(self.buttons)

            def get_data(self):
                return {
                    "nombre": self.name.text().strip(),
                    "email": self.email.text().strip(),
                    "rol": self.role.text().strip(),
                    "password": self.password.text().strip()
                }

        dialog = UserFormDialog()
        if dialog.exec():
            data = dialog.get_data()
            if not data["nombre"] or not data["email"] or not data["rol"] or not data["password"]:
                QMessageBox.warning(self, "Error", "Todos los campos son obligatorios.")
                return
            msg = self.controller.add_user(data)
            QMessageBox.information(self, "Usuario agregado", 
                                   "Usuario creado con éxito." if msg else "Error al crear usuario.")
            self.refresh_data()
            
    def edit_user_dialog(self, user):
        """Abre un diálogo para editar un usuario existente"""
        class UserEditDialog(QDialog):
            def __init__(self, user):
                super().__init__()
                self.setWindowTitle("Editar Usuario")
                self.layout = QFormLayout(self)
                self.name = QLineEdit()
                self.name.setText(user.get("nombre", ""))
                self.email = QLineEdit()
                self.email.setText(user.get("email", ""))
                self.role = QLineEdit()
                self.role.setText(user.get("rol", ""))
                self.layout.addRow("Nombre:", self.name)
                self.layout.addRow("Email:", self.email)
                self.layout.addRow("Rol:", self.role)
                self.buttons = QDialogButtonBox(
                    QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
                )
                self.buttons.accepted.connect(self.accept)
                self.buttons.rejected.connect(self.reject)
                self.layout.addWidget(self.buttons)

            def get_data(self):
                return {
                    "nombre": self.name.text().strip(),
                    "email": self.email.text().strip(),
                    "rol": self.role.text().strip()
                }

        dialog = UserEditDialog(user)
        if dialog.exec():
            data = dialog.get_data()
            user_id = user.get('id_usuario')
            if not data["nombre"] or not data["email"] or not data["rol"]:
                QMessageBox.warning(self, "Error", "Todos los campos son obligatorios.")
                return
            msg = self.controller.edit_user(user_id, data)
            QMessageBox.information(self, "Usuario editado", 
                                   "Usuario actualizado." if msg else "Error al editar usuario.")
            self.refresh_data()
            
    def delete_user(self, user):
        """Elimina un usuario después de confirmar"""
        user_id = user.get('id_usuario')
        nombre = user.get('nombre')
        confirm = QMessageBox.question(
            self,
            "Eliminar Usuario",
            f"¿Seguro que deseas eliminar a {nombre}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if confirm == QMessageBox.StandardButton.Yes:
            ok = self.controller.remove_user(user_id)
            QMessageBox.information(self, "Usuario eliminado", 
                                   "Usuario eliminado." if ok else "Error al eliminar usuario.")
            self.refresh_data()
    
    def show_error(self, msg):
        """Muestra un mensaje de error"""
        QMessageBox.critical(self, "Error", msg)


# Para pruebas independientes
if __name__ == '__main__':
    import sys
    from PyQt6.QtWidgets import QApplication
    from utils.api_client import ApiClient
    
    api_client = ApiClient()
    app = QApplication(sys.argv)
    window = UsersListView(api_client)
    window.setWindowTitle("Gestión de Usuarios")
    window.resize(950, 500)
    window.show()
    sys.exit(app.exec())
