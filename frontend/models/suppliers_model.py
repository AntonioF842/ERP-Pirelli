from typing import List, Dict

class Supplier:
    def __init__(self, supplier_id: int, name: str, contact: str, phone: str, email: str, material_type: str = None):
        self.supplier_id = supplier_id
        self.name = name
        self.contact = contact
        self.phone = phone
        self.email = email
        self.material_type = material_type

class SuppliersModel:
    def __init__(self):
        self.suppliers: List[Supplier] = []
    
    @staticmethod
    def from_api_list(api_supplier_list: List[dict]) -> List[Supplier]:
        """Converts a list of dicts received from the API into Supplier objects."""
        return [
            Supplier(
                supplier_id=s['id'],
                name=s['name'],
                contact=s['contact'],
                phone=s['phone'],
                email=s['email'],
                material_type=s.get('material_type')
            )
            for s in api_supplier_list
        ]

    def load_from_api(self, api_supplier_list: List[dict]):
        """Loads and replaces suppliers using a list of dicts from the API."""
        self.suppliers = self.from_api_list(api_supplier_list)
    
    def add_supplier(self, supplier: Supplier):
        self.suppliers.append(supplier)
    
    def get_all_suppliers(self) -> List[Supplier]:
        return self.suppliers
    
    def remove_supplier(self, supplier_id: int):
        self.suppliers = [s for s in self.suppliers if s.supplier_id != supplier_id]

    def update_supplier(self, supplier_id: int, data: Dict):
        for supplier in self.suppliers:
            if supplier.supplier_id == supplier_id:
                supplier.name = data.get('name', supplier.name)
                supplier.contact = data.get('contact', supplier.contact)
                supplier.phone = data.get('phone', supplier.phone)
                supplier.email = data.get('email', supplier.email)
                supplier.material_type = data.get('material_type', supplier.material_type)
