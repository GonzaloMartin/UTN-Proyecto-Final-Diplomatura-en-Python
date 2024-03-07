"""
model.py
    Este módulo contiene la clase Model que se encarga de la lógica de la aplicación.
    Tiene funciones inherentes a la base de datos y a la manipulación de los datos.
    Se vincula con el controlador y la vista para realizar las operaciones necesarias.
"""

import sqlite3
from utils.utils import obtener_mes_actual

class Model:
        
    def __init__(self):
        """
        Constructor de la clase Model.
        
        :param self: objeto Model
        :return: None
        """
        self.conn = self.conectar_base_de_datos()

    #-----BASE DE DATOS-----#
    def conectar_base_de_datos(self):
        """
        Conecta a la base de datos y devuelve el objeto conexión
        La base de datos se encuentra en la carpeta database.
        
        :param self: objeto Model
        :return: objeto conexión
        """
        
        try:
            conn = sqlite3.connect('database/registros.db')
            return conn
        except sqlite3.Error as e:
            print(e)
            return None

    def desconectar_base_de_datos(self):
        """
        Desconecta de la base de datos.
        
        :param self: objeto Model
        :return: None
        """
        try:
            self.conn.close()
        except sqlite3.Error as e:
            print(e)

    def crear_tabla(self):
        """
        Crea la tabla si no existe en la base de datos.
        La base de datos es registros.db
        
        :param self: objeto Model
        :return: None
        """
        
        try:
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
        except sqlite3.Error as e:
            print(e)

    def alta_bd(self, valores):
        """
        Inserta un nuevo registro en la base de datos
        y devuelve el id del registro insertado.
        La información a insertar se pasa por parámetro en un diccionario.
        
        :param self: objeto Model
        :param valores: diccionario con los valores a insertar.
        :return: id del registro insertado
        """
        
        try:
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
            return ultimo_id
        except sqlite3.Error as e:
            print(e)
            return None

    def baja_bd(self, id_registro):
        """
        Elimina un registro de la base de datos.
        La base de datos es registros.db
        
        :param self: objeto Model
        :param id_registro: id del registro a eliminar
        :return: None
        """
        
        try:
            cursor = self.conn.cursor()
            query = "DELETE FROM gastos WHERE id = ?;"
            cursor.execute(query, (id_registro,))
            self.conn.commit()
        except sqlite3.Error as e:
            print(e)

    def modificacion_bd(self, id_registro, valores):
        """
        Modifica un registro de la base de datos con los valores pasados por parámetro.
        Los valores son un diccionario con los campos a modificar.
        
        :param self: objeto Model        
        :param id_registro: id del registro a modificar
        :param valores: diccionario con los valores a modificar
        :return: None
        """

        try:
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
        except sqlite3.Error as e:
            print(e)
        
    def consulta_bd(self, mes=None):
        """
        Consulta todos los registros de la base de datos y devuelve una lista de tuplas
        Si se especifica un mes, filtra por ese mes.
        Además, si no se especifica un mes, devuelve todos los registros.
        
        :param self: objeto Model
        :param mes: (opcoinal) mes a filtrar.
        :return: lista de tuplas.
        """
        
        try:
            cursor = self.conn.cursor()
            if mes is not None:
                query = "SELECT subtotal FROM gastos WHERE strftime('%m', fecha) = ?;"
                cursor.execute(query, (f"{mes:02d}",))
            else:
                query = """SELECT * FROM gastos;"""
                cursor.execute(query)
            rows = cursor.fetchall()

            return rows
        except sqlite3.Error as e:
            print(e)
            return []

    
    #-----FIN BASE DE DATOS-----#
    def obtener_datos_grafico(self, obtener_mes_actual):
        """
        Obtiene los datos para el gráfico de barras.
        El gráfico muestra el total gastado por rubro en el mes actual.
        Los datos que usa el gráfico son el rubro y el total gastado.
        
        :param self: objeto Model
        :param obtener_mes_actual: función que devuelve el número de mes actual.
        :return: lista de tuplas con los datos.
        """
        try:
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
        except sqlite3.Error as e:
            print(e)
            return []
