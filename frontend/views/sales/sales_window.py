from PyQt6.QtWidgets import QMainWindow, QTabWidget

from views.sales.sales_orders.sales_list import SalesListView
from views.production.products.product_list  import ProductListView
from views.sales.customers.client_list import ClientListView

class VentasWindow(QMainWindow):
    def __init__(self, api_client):
        super().__init__()
        self.setWindowTitle("Ventas")
        self.setMinimumSize(900, 600)
        self.tab_widget = QTabWidget()
        self.setCentralWidget(self.tab_widget)

        # Agrega cada sub-vista como una pestaña
        self.tab_widget.addTab(SalesListView(api_client), "Ventas")
        self.tab_widget.addTab(ProductListView(api_client), "Productos")
        self.tab_widget.addTab(ClientListView(api_client), "Clientes")

    def center_window(self):
        screen = self.screen().availableGeometry()
        window_size = self.frameGeometry()
        x = screen.center().x() - window_size.width() // 2
        y = screen.center().y() - window_size.height() // 2
        self.move(x, y)