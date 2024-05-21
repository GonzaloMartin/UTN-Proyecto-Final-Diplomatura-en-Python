import sqlite3


def conectar_base_de_datos():
    """
    Conecta a la base de datos y devuelve el objeto conexión.
    La base de datos se encuentra en la carpeta 'database'.
    """
    try:
        conn = sqlite3.connect('database/records.db')
        return conn
    except sqlite3.Error as e:
        print(e)
        return None


def desconectar_base_de_datos(conn):
    """
    Desconecta de la base de datos.
    
    :param conn: objeto conexión a cerrar
    """
    try:
        conn.close()
    except sqlite3.Error as e:
        print(e)


def crear_tabla(conn):
    """
    Crea la tabla si no existe en la base de datos.
    
    :param conn: objeto conexión sobre el que se ejecuta la acción
    """
    try:
        cursor = conn.cursor()
        query = """CREATE TABLE IF NOT EXISTS gastos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                producto_servicio TEXT,
                cantidad INTEGER,
                monto FLOAT,
                responsable TEXT,
                subtotal FLOAT,
                rubro TEXT,
                proveedor TEXT,
                medio_de_pago TEXT,
                fecha DATE,
                vencimiento DATE
                );"""
        cursor.execute(query)
        conn.commit()
    except sqlite3.Error as e:
        print(e)
