import datetime


def obtener_mes_actual():
    """
    Obtiene el número de mes actual del sistema.
    :return: número de mes actual.
    """
    return datetime.datetime.now().month
