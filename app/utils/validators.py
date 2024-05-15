import datetime
import re

from utils.utils import des_reformatear_fecha

class DataValidator:
    
    @staticmethod
    def validar_numero_positivo(valor):
        """Valida que el valor sea un número positivo."""
        try:
            valor = float(valor)
            if valor <= 0:
                raise ValueError("El valor debe ser un número positivo.")
        except ValueError as e:
            return False, f"El valor proporcionado ({valor}) no es un número válido."
        return True, "OK"
    

    @staticmethod
    def validar_campos_requeridos(**campos):
        """Valida que los campos requeridos contengan datos."""
        for campo, valor in campos.items():
            if not valor.strip():
                return False, f"El campo '{campo}' es requerido y está vacío."
        return True, "OK"
    
    
    @staticmethod
    def validar_regex(valores=None, nuevo_valor=None):
        """
        Valida que los valores ingresados cumplan con los patrones definidos.
        Las validaciones se realizan con expresiones regulares.
        
        :param valores: diccionario con los valores a validar.
        :param nuevo_valor: diccionario con los valores a validar.
        :return: True si los valores cumplen con los patrones definidos, False en caso contrario.
        """
        
        patrones = {
            'producto': r'^[a-zA-Z0-9 áéíóúÁÉÍÓÚüÜñÑ]+$',
            'cantidad': r'^\d+$',
            'monto': r'^\d+(\.\d+)?$',
            'responsable': r'^[a-zA-Z0-9 áéíóúÁÉÍÓÚüÜñÑ]+$',
            'rubro': r'^[a-zA-Z0-9 ]+$',
            'proveedor': r'^[a-zA-Z0-9 áéíóúÁÉÍÓÚüÜñÑ]+$',
            'medio_pago': r'^[a-zA-Z0-9 áéíóúÁÉÍÓÚüÜñÑ]+$',
            'fecha': r'^\d{4}-\d{2}-\d{2}$',  # Formato fecha aaaa-mm-dd
            'vencimiento': r'^(?:\d{4}-\d{2}-\d{2}|N/A)$'  # N/A o fecha
        }

        diccionario_valor = {}
        if valores:
            diccionario_valor = valores
        else:
            diccionario_valor = nuevo_valor
            diccionario_valor['fecha'] = des_reformatear_fecha(diccionario_valor['fecha'])
            diccionario_valor['vencimiento'] = des_reformatear_fecha(diccionario_valor['vencimiento']) if diccionario_valor['vencimiento'] != 'N/A' else 'N/A'

        for campo, valor in diccionario_valor.items():
            # No intenta validar campos que no tienen un patrón definido
            if campo in patrones:
                if not re.match(patrones[campo], str(valor)):
                    print(f"Campo {campo} no cumple con el patrón definido. Campo {campo}: {valor}")       
                    return False
                
        return True
