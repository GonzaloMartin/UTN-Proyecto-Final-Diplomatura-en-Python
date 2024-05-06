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
    def validar_fecha(fecha):
        """Valida que la fecha tenga un formato correcto y sea lógica."""
        try:
            datetime.datetime.strptime(fecha, "%Y-%m-%d")
        except ValueError:
            return False, "Formato de fecha inválido. El formato correcto es YYYY-MM-DD."
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

'''
Este metodo no parece ser utilizado, pero se menciona en views.py linea 303.
TODO: Verificar la necesidad de implementacion o eliminacion de este metodo.

    @staticmethod
    def validar_campos(view):
        """
        Valida que todos los campos de la vista no tengan inconsistencias.
        
        :param view: Objeto View que contiene las variables y controles de entrada.
        :return: True si los valores cumplen con los patrones definidos, False en caso contrario.
        """
        campos_var = [view.var_producto, view.var_cantidad, view.var_monto, view.var_proveedor, view.var_fecha, view.var_vencimiento]
        campos_cb = [view.cb_responsable, view.cb_rubro, view.cb_medio_pago]

        # Validación de campos de entrada
        for var in campos_var:
            if isinstance(var, (str, int)) and not var:
                return False

        for cb in campos_cb:
            if not cb:
                return False

        # Validaciones Regex:
        valores = { 'producto': view.var_producto, 'cantidad': view.var_cantidad, 'monto': view.var_monto,
                    'proveedor': view.var_proveedor, 'fecha': view.var_fecha, 'vencimiento': view.var_vencimiento,
                    'responsable': view.cb_responsable.get(), 'rubro': view.cb_rubro.get(), 'medio_pago': view.cb_medio_pago.get()}
        if not DataValidator.validar_regex(valores=valores):
            return False

        return True
'''