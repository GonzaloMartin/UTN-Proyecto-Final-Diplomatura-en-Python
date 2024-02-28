import sqlite3
from utils.utils import obtener_mes_actual


##############################################################################

#--------------------------------INICIO MODELO-------------------------------#

class Model:
        
    def __init__(self):
        self.conn = self.conectar_base_de_datos()

    #-----BASE DE DATOS-----#
    def conectar_base_de_datos(self):
        """
        Conecta a la base de datos y devuelve el objeto conexión
        :return: objeto conexión
        """
        conn = sqlite3.connect('database/base_de_datos.db')
        return conn

    def desconectar_base_de_datos(self):
        """
        Desconecta de la base de datos 
        :return: None
        """
        self.conn.close()

    def crear_tabla(self):
        """
        Crea la tabla si no existe en la base de datos
        :return: None
        """
        cursor = self.conn.cursor()
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
        self.conn.commit()

    def alta_bd(self, valores):
        """
        Inserta un nuevo registro en la base de datos
        y devuelve el id del registro insertado.
        :param valores: diccionario con los valores a insertar.
        :return: id del registro insertado
        """
        
        # conn = conectar_base_de_datos()
        cursor = self.conn.cursor()
        query = """INSERT INTO gastos (producto_servicio,
                cantidad,
                monto,
                responsable,
                subtotal,
                rubro, proveedor,
                medio_de_pago,
                fecha,
                vencimiento)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);"""
                
        subtotal = valores['cantidad'] * valores['monto']
        
        data = (valores['producto'], 
                valores['cantidad'], 
                valores['monto'], 
                valores['responsable'], 
                subtotal, valores['rubro'], 
                valores['proveedor'], 
                valores['medio_pago'], 
                valores['fecha'], 
                valores['vencimiento'])

        cursor.execute(query, data)
        self.conn.commit()
        ultimo_id = cursor.lastrowid 
        # desconectar_base_de_datos(conn)
        return ultimo_id

    def baja_bd(self, id_registro):
        """
        Elimina un registro de la base de datos
        :param id_registro: id del registro a eliminar
        :return: None
        """
        # conn = conectar_base_de_datos()
        cursor = self.conn.cursor()
        query = "DELETE FROM gastos WHERE id = ?;"
        cursor.execute(query, (id_registro,))
        self.conn.commit()
        # desconectar_base_de_datos(conn)

    def modificacion_bd(self, id_registro, valores):
        """
        Modifica un registro de la base de datos
        :param id_registro: id del registro a modificar
        :param valores: diccionario con los valores a modificar
        :return: None
        """
        # conn = conectar_base_de_datos()
        cursor = self.conn.cursor()
        query = """UPDATE gastos SET
                producto_servicio = ?,
                cantidad = ?,
                monto = ?,
                responsable = ?,
                subtotal = ?,
                rubro = ?,
                proveedor = ?,
                medio_de_pago = ?,
                fecha = ?,
                vencimiento = ?
                WHERE id = ?;"""

        subtotal = int(valores['cantidad'] * valores['monto'] * 100) / 100.0
        data = (valores['producto'],
                valores['cantidad'],
                valores['monto'],
                valores['responsable'],
                subtotal, valores['rubro'],
                valores['proveedor'],
                valores['medio_pago'],
                valores['fecha'],
                valores['vencimiento'],
                id_registro)

        cursor.execute(query, data)
        self.conn.commit()
        # desconectar_base_de_datos(conn)

    def consulta_bd(self, mes=None):
        # Consulta todos los registros. Pero si se especifica 1 mes, filtra por mes
        """
        Consulta todos los registros de la base de datos y devuelve una lista de tuplas
        Si se especifica un mes, filtra por ese mes.
        :param mes: (opcoinal) mes a filtrar
        :return: lista de tuplas
        """
        
        # conn = conectar_base_de_datos()
        cursor = self.conn.cursor()
        if mes is not None:
            query = "SELECT subtotal FROM gastos WHERE strftime('%m', fecha) = ?;"
            cursor.execute(query, (f"{mes:02d}",))
        else:
            query = """SELECT * FROM gastos;"""
            cursor.execute(query)
        rows = cursor.fetchall()
        # desconectar_base_de_datos(conn)
        return rows

    # conn = conectar_base_de_datos()
    # crear_tabla(conn)
    
    #-----FIN BASE DE DATOS-----#
    def obtener_datos_grafico(self, obtener_mes_actual):
        """
        Obtiene los datos para el gráfico de barras.
        :param obtener_mes_actual: función que devuelve el número de mes actual.
        :return: lista de tuplas con los datos.
        """
        cursor = self.conn.cursor()
        
        num_mes_actual = obtener_mes_actual
        if (not isinstance(num_mes_actual, int) or not (1 <= num_mes_actual <= 12)):
            print("Número de mes inválido.")
            return []
        
        mes_formateado = f"{num_mes_actual:02d}"  # formato de mes de 2 dígitos.
        
        query = f"""SELECT rubro, SUM(subtotal)
                    FROM gastos
                    WHERE strftime('%m', fecha) = '{mes_formateado}'
                    GROUP BY rubro"""
        
        cursor.execute(query)
        data = cursor.fetchall()
        return data
        
    #-----GRAFICO (DATOS)-----#
    # def obtener_datos_grafico(self):
    #     # conn = conectar_base_de_datos()
    #     cursor = self.conn.cursor()
    #     
    #     num_mes_actual = str(obtener_mes_actual())
    #     query = f"SELECT rubro, SUM(subtotal) FROM gastos WHERE strftime('%m', fecha) = '{num_mes_actual}' GROUP BY rubro"
    #     cursor.execute(query)
    #     data = cursor.fetchall()
    #     # desconectar_base_de_datos(conn)
    #     return data
    #-----FIN GRAFICO (DATOS)-----#

    #---------------------------------FIN MODELO---------------------------------#

##############################################################################
