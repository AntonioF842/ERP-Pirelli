from PyQt6.QtWidgets import QMessageBox

class PurchaseOrderController:
    def __init__(self, api_client):
        self.api_client = api_client

    def create_purchase_order(self, order_data):
        try:
            # Validar los datos antes de enviar
            is_valid, error_msg = self.api_client.validate_purchase_order(order_data)
            if not is_valid:
                QMessageBox.warning(None, "Error de validación", error_msg)
                return None
                
            # Enviar al API
            return self.api_client.create_purchase_order(order_data)
        except Exception as e:
            QMessageBox.critical(None, "Error", f"No se pudo crear la orden: {str(e)}")
            return None

    def update_purchase_order(self, order_id, order_data):
        try:
            # Validar los datos antes de enviar
            is_valid, error_msg = self.api_client.validate_purchase_order(order_data)
            if not is_valid:
                QMessageBox.warning(None, "Error de validación", error_msg)
                return None
                
            # Enviar al API
            return self.api_client.update_purchase_order(order_id, order_data)
        except Exception as e:
            QMessageBox.critical(None, "Error", f"No se pudo actualizar la orden: {str(e)}")
            return None

    def delete_purchase_order(self, order_id):
        try:
            return self.api_client.delete_purchase_order(order_id)
        except Exception as e:
            QMessageBox.critical(None, "Error", f"No se pudo eliminar la orden: {str(e)}")
            return None