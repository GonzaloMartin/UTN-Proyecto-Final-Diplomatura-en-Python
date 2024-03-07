"""
utils.py
    Este módulo contiene funciones que son utilizadas por otros módulos.
"""

import re
from datetime import datetime

def obtener_mes_actual():
    """
    Obtiene el número de mes actual del sistema.
    
    :return: número de mes actual.
    """
    
    return datetime.now().month

def obtener_fecha_actual():
    """
    Obtiene la fecha actual del sistema con formato mm-dd-yyyy.
    
    mm: mes, 1 dígito si mes va de 1 a 9. 2 dígitos si mes va de 10 a 12.
    dd: día, 1 dígito si día va de 1 a 9. 2 dígitos si día va de 10 a 31.
    yyyy: año, 4 dígitos.
    :return: fecha actual.
    """
    
    fecha_actual = datetime.now()
    mes = str(fecha_actual.month).zfill(2)  # Rellenar con ceros a la izquierda si es necesario
    dia = str(fecha_actual.day).zfill(2)    # Rellenar con ceros a la izquierda si es necesario
    año = str(fecha_actual.year)
    return f"{mes}/{dia}/{año}"

def reformatear_fecha(fecha):
    """
    Reformatea la fecha de AAAA-MM-DD a MM/DD/AAAA.
    
    :param fecha: fecha a reformatear.
    :return: fecha reformateada.
    """
    
    año, mes, dia = fecha.split("-")
    return f"{mes}/{dia}/{año}"

def des_reformatear_fecha(fecha):
    """
    Reformatea la fecha de MM/DD/AA a AAAA-MM-DD.
    mm: mes, 1 dígito si mes va de 1 a 9. 2 dígitos si mes va de 10 a 12.
    dd: día, 1 dígito si día va de 1 a 9. 2 dígitos si día va de 10 a 31.
    yyyy: año, 4 dígitos.
    
    :param fecha: fecha a reformatear.
    :return: fecha reformateada.
    """
    try:
        fecha_objeto = datetime.strptime(fecha, "%m/%d/%y")
    except ValueError:
        try:
            fecha_objeto = datetime.strptime(fecha, "%m/%d/%Y")
        except ValueError:
            fecha_objeto = datetime.strptime(fecha, "%m/%d/%Y")
    
    return fecha_objeto.strftime("%Y-%m-%d")

def validar_regex(valores=None, nuevo_valor=None):
    """
    Valida que los valores ingresados cumplan con los patrones definidos.
    Las validaciones se realizan con expresiones regulares.
    
    :param valores: diccionario con los valores a validar.
    :param nuevo_valor: diccionario con los valores a validar.
    :return: True si los valores cumplen con los patrones definidos, False en caso contrario."""
    
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