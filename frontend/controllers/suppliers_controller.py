from models.suppliers_model import SuppliersModel, Supplier

class SuppliersController:
    def __init__(self):
        self.model = SuppliersModel()
    
    def add_supplier(self, **kwargs):
        new_supplier = Supplier(**kwargs)
        self.model.add_supplier(new_supplier)
    
    def get_suppliers(self):
        return self.model.get_all_suppliers()
    
    def remove_supplier(self, supplier_id):
        self.model.remove_supplier(supplier_id)
    
    def update_supplier(self, supplier_id, data):
        self.model.update_supplier(supplier_id, data)