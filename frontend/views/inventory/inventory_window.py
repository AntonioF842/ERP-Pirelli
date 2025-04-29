from PyQt6.QtWidgets import QMainWindow, QTabWidget

# Importar las sub-vistas de cada dominio (crea los archivos posteriormente dentro de cada carpeta)
from views.inventory.inventory.inventory_list import InventoryListView
from views.inventory.materials.material_list import MaterialListView
from views.inventory.purchase_orders.purchase_orders_list import PurchaseOrderListView
from views.inventory.suppliers.suppliers_list import SuppliersListView

class InventoryWindow(QMainWindow):
    def __init__(self, api_client):
        super().__init__()
        self.setWindowTitle("Inventario y Compras")
        self.setMinimumSize(900, 600)
        self.tab_widget = QTabWidget()
        self.setCentralWidget(self.tab_widget)

        # Agrega cada sub-vista como una pestaña
        self.tab_widget.addTab(InventoryListView(api_client), "Inventario")
        self.tab_widget.addTab(MaterialListView(api_client), "Materiales")
        self.tab_widget.addTab(PurchaseOrderListView(api_client), "Órdenes de Compra")
        self.tab_widget.addTab(SuppliersListView(api_client), "Proveedores")

    def center_window(self):
        screen = self.screen().availableGeometry()
        window_size = self.frameGeometry()
        x = screen.center().x() - window_size.width() // 2
        y = screen.center().y() - window_size.height() // 2
        self.move(x, y)