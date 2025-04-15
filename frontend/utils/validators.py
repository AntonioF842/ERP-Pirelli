"""
Utilidades para validar entradas de formularios
"""

from PyQt6.QtCore import QRegularExpression
from PyQt6.QtGui import QValidator, QRegularExpressionValidator

class Validators:
    """Clase que proporciona validadores para campos de formulario"""
    
    @staticmethod
    def email_validator():
        """Validador para direcciones de correo electrónico"""
        regex = QRegularExpression(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
        return QRegularExpressionValidator(regex)
    
    @staticmethod
    def password_validator(min_length=8):
        """Validador para contraseñas que requiere mínimo de caracteres"""
        class PasswordValidator(QValidator):
            def validate(self, input_str, pos):
                if len(input_str) < min_length and len(input_str) > 0:
                    return QValidator.State.Intermediate, input_str, pos
                return QValidator.State.Acceptable, input_str, pos
                
            def fixup(self, input_str):
                return input_str
        
        return PasswordValidator()
    
    @staticmethod
    def numeric_validator(allow_decimals=False):
        """Validador para valores numéricos"""
        if allow_decimals:
            regex = QRegularExpression(r"^[0-9]*\.?[0-9]*$")
        else:
            regex = QRegularExpression(r"^[0-9]*$")
        return QRegularExpressionValidator(regex)
    
    @staticmethod
    def alphanumeric_validator():
        """Validador para cadenas alfanuméricas"""
        regex = QRegularExpression(r"^[a-zA-Z0-9 ]*$")
        return QRegularExpressionValidator(regex)
    
    @staticmethod
    def phone_validator():
        """Validador para números telefónicos"""
        regex = QRegularExpression(r"^[0-9+\-() ]{5,20}$")
        return QRegularExpressionValidator(regex)
    
    @staticmethod
    def date_validator():
        """Validador para fechas en formato YYYY-MM-DD"""
        regex = QRegularExpression(r"^\d{4}-\d{2}-\d{2}$")
        return QRegularExpressionValidator(regex)

def validate_form_fields(fields_dict):
    """
    Valida un conjunto de campos de formulario
    
    Args:
        fields_dict: Diccionario con pares {campo: valor}
    
    Returns:
        (bool, str): Tupla con éxito (True/False) y mensaje de error si aplica
    """
    for field_name, field_value in fields_dict.items():
        # Validar campos requeridos
        if field_value is None or (isinstance(field_value, str) and field_value.strip() == ""):
            return False, f"El campo '{field_name}' es requerido"
    
    return True, ""