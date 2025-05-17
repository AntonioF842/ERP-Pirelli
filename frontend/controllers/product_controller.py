from typing import List, Dict, Any, Optional, Union
from models.product_model import Product
import logging
from PyQt6.QtCore import pyqtSignal, QObject

logger = logging.getLogger(__name__)

class ProductController(QObject):
    """Controlador para gestionar productos"""
    
    # Señales
    products_loaded = pyqtSignal(list)          # Emitida cuando se cargan productos
    product_loaded = pyqtSignal(dict)          # Emitida cuando se carga un producto
    product_created = pyqtSignal(dict)         # Emitida cuando se crea un producto
    product_updated = pyqtSignal(dict)         # Emitida cuando se actualiza un producto
    product_deleted = pyqtSignal(int)          # Emitida cuando se elimina un producto
    error_occurred = pyqtSignal(str)           # Emitida cuando ocurre un error
    
    def __init__(self, api_client):
        super().__init__()
        self.api_client = api_client
    
    async def get_products(self, filters: Optional[Dict[str, Any]] = None) -> List[Product]:
        """
        Obtiene la lista de productos con filtros opcionales
        
        Args:
            filters: Diccionario con filtros (categoria, estado, etc.)
            
        Returns:
            Lista de objetos Product
        """
        try:
            params = filters or {}
            response = await self.api_client.get('/products', params=params)
            
            if response and isinstance(response, list):
                products = [Product.from_dict(item) for item in response]
                self.products_loaded.emit(products)
                return products
                
            self.error_occurred.emit("No se recibieron datos válidos")
            return []
        except Exception as e:
            logger.error(f"Error al obtener productos: {str(e)}")
            self.error_occurred.emit(f"Error al obtener productos: {str(e)}")
            return []
    
    async def get_product(self, product_id: int) -> Optional[Product]:
        """
        Obtiene un producto por su ID
        
        Args:
            product_id: ID del producto
            
        Returns:
            Objeto Product o None si no se encuentra
        """
        try:
            response = await self.api_client.get(f'/products/{product_id}')
            
            if response:
                product = Product.from_dict(response)
                self.product_loaded.emit(response)
                return product
                
            self.error_occurred.emit(f"Producto {product_id} no encontrado")
            return None
        except Exception as e:
            logger.error(f"Error al obtener producto {product_id}: {str(e)}")
            self.error_occurred.emit(f"Error al obtener producto: {str(e)}")
            return None
    
    async def create_product(self, product_data: Dict[str, Any]) -> Optional[Product]:
        """
        Crea un nuevo producto
        
        Args:
            product_data: Datos del producto
            
        Returns:
            Producto creado o None si hay error
        """
        try:
            # Validar datos antes de enviar
            product = Product.from_dict(product_data)
            is_valid, errors = product.validate()
            
            if not is_valid:
                error_msg = "Datos del producto no válidos:\n" + "\n".join(errors.values())
                self.error_occurred.emit(error_msg)
                return None
                
            response = await self.api_client.post('/products', json=product_data)
            
            if response:
                product = Product.from_dict(response)
                self.product_created.emit(response)
                return product
                
            self.error_occurred.emit("No se pudo crear el producto")
            return None
        except Exception as e:
            logger.error(f"Error al crear producto: {str(e)}")
            self.error_occurred.emit(f"Error al crear producto: {str(e)}")
            return None
    
    async def update_product(self, product_id: int, product_data: Dict[str, Any]) -> Optional[Product]:
        """
        Actualiza un producto existente
        
        Args:
            product_id: ID del producto
            product_data: Datos actualizados
            
        Returns:
            Producto actualizado o None si hay error
        """
        try:
            # Validar datos antes de enviar
            product = Product.from_dict(product_data)
            is_valid, errors = product.validate()
            
            if not is_valid:
                error_msg = "Datos del producto no válidos:\n" + "\n".join(errors.values())
                self.error_occurred.emit(error_msg)
                return None
                
            response = await self.api_client.put(f'/products/{product_id}', json=product_data)
            
            if response:
                product = Product.from_dict(response)
                self.product_updated.emit(response)
                return product
                
            self.error_occurred.emit("No se pudo actualizar el producto")
            return None
        except Exception as e:
            logger.error(f"Error al actualizar producto {product_id}: {str(e)}")
            self.error_occurred.emit(f"Error al actualizar producto: {str(e)}")
            return None
    
    async def delete_product(self, product_id: int) -> bool:
        """
        Elimina un producto
        
        Args:
            product_id: ID del producto
            
        Returns:
            True si se eliminó correctamente, False en caso contrario
        """
        try:
            response = await self.api_client.delete(f'/products/{product_id}')
            
            if response is not None:
                self.product_deleted.emit(product_id)
                return True
                
            self.error_occurred.emit("No se pudo eliminar el producto")
            return False
        except Exception as e:
            logger.error(f"Error al eliminar producto {product_id}: {str(e)}")
            self.error_occurred.emit(f"Error al eliminar producto: {str(e)}")
            return False
    
    def validate_product_data(self, data: Dict[str, Any]) -> Dict[str, str]:
        """
        Valida los datos de un producto
        
        Args:
            data: Datos a validar
            
        Returns:
            Diccionario con errores de validación (vacío si no hay errores)
        """
        product = Product.from_dict(data)
        is_valid, errors = product.validate()
        return errors