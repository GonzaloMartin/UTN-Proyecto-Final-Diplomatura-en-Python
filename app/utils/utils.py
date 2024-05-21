"""
utils.py
    Este módulo contiene funciones que son utilizadas por otros módulos.
"""

import re
import os
from pathlib import Path
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
    
    :param mm: mes, 1 dígito si mes va de 1 a 9. 2 dígitos si mes va de 10 a 12.
    :param dd: día, 1 dígito si día va de 1 a 9. 2 dígitos si día va de 10 a 31.
    :param yyyy: año, 4 dígitos.
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
    
    :param mm: mes, 1 dígito si mes va de 1 a 9. 2 dígitos si mes va de 10 a 12.
    :param dd: día, 1 dígito si día va de 1 a 9. 2 dígitos si día va de 10 a 31.
    :param yyyy: año, 4 dígitos.
    :param fecha: fecha a reformatear.
    :return: fecha reformateada.
    """
    
    try:
        fecha_objeto = datetime.strptime(fecha, "%m/%d/%y")
        fecha_reformateada = fecha_objeto.strftime("%Y-%m-%d")
    except ValueError as e:
        pass  # No es necesario hacer nada si ocurre un error
    
    return fecha_reformateada


def logs(func):
    """
    Decoraador que registra acciones tomadas por las funciones decoradas.

    :param func: función a aplicar decoradores.
    :return: función wrapper que incluye capacidades de registro.
    """
    
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)

        if func.__name__ == 'alta_bd':
            valores = args[1]
            print(f"Nuevo registro ingresado: {valores}")
        elif func.__name__ == 'baja_bd':
            id_registro = args[1]
            print(f"Registro eliminado con ID: {id_registro}")
        elif func.__name__ == 'modificacion_bd':
            id_registro = args[1]
            valores = args[2]
            print(f"Registro actualizado con ID: {id_registro} y datos: {valores}")

        return result
    return wrapper

def obtener_ruta(valor):
    """
    Obtiene la ruta del servidor donde se está ejecutando la aplicación.
    
    :param valor: valor a obtener.
    :return: ruta del servidor.
    """
    
    ruta_script = os.path.abspath(__file__)
    ruta_repositorio = os.path.dirname(os.path.dirname(ruta_script))
    
    if valor == 'cliente':
        return os.path.join(ruta_repositorio, 'mvc', 't_cliente.py')
    elif valor == 'servidor':
        return os.path.join(ruta_repositorio, 'mvc', 't_servidor.py')
