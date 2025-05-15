from PyQt6.QtWidgets import QMainWindow, QTabWidget

from views.production.products.product_list import ProductListView
from views.production.production_orders.production_orders_list import ProductionOrderListView
from views.production.production_recipe.production_recipe_list import ProductionRecipeListView
from views.production.quality_control.quality_control_list import QualityControlListView
from views.production.production_assets.production_assets_list import ProductionAssetListView
from views.production.maintenance.maintenance_list import MaintenanceListView

class ProductionWindow(QMainWindow):
    def __init__(self, api_client):
        super().__init__()
        self.setWindowTitle("Producción")
        self.setMinimumSize(900, 600)
        self.tab_widget = QTabWidget()
        self.setCentralWidget(self.tab_widget)

        # Agrega cada sub-vista como una pestaña
        self.tab_widget.addTab(ProductListView(api_client), "Productos")
        self.tab_widget.addTab(ProductionOrderListView(api_client), "Órdenes de Producción")
        self.tab_widget.addTab(ProductionRecipeListView(api_client), "Recetas de Producción")
        self.tab_widget.addTab(QualityControlListView(api_client), "Control de Calidad")
        self.tab_widget.addTab(ProductionAssetListView(api_client), "Activos de Producción")
        self.tab_widget.addTab(MaintenanceListView(api_client), "Mantenimiento")

    def center_window(self):
        screen = self.screen().availableGeometry()
        window_size = self.frameGeometry()
        x = screen.center().x() - window_size.width() // 2
        y = screen.center().y() - window_size.height() // 2
        self.move(x, y)