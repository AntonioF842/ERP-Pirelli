from typing import List

class PurchaseOrderDetail:
    def __init__(self, detail_id: int, item: str, quantity: int, unit_price: float):
        self.detail_id = detail_id
        self.item = item
        self.quantity = quantity
        self.unit_price = unit_price

class PurchaseOrder:
    def __init__(self, po_id: int, supplier_id: int, date: str, status: str):
        self.po_id = po_id
        self.supplier_id = supplier_id
        self.date = date
        self.status = status
        self.details: List[PurchaseOrderDetail] = []
    
    def add_detail(self, detail: PurchaseOrderDetail):
        self.details.append(detail)