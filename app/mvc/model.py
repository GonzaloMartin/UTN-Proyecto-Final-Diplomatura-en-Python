"""
model.py
    Este módulo contiene la clase Model que se encarga de la lógica de la aplicación.
    Tiene funciones inherentes a la base de datos y a la manipulación de los datos.
    Se vincula con el controlador y la vista para realizar las operaciones necesarias.
    Se usa el decorador @logs para registrar las operaciones realizadas en la base de datos.
"""

import sqlite3
from utils.utils import logs, obtener_mes_actual
from .database import conectar_base_de_datos, desconectar_base_de_datos, crear_tabla


class Model:
    def __init__(self):
        """
        Initializes the Model instance by establishing a database connection.
        The connection is stored as an instance attribute for use in other methods.
        """
        self.conn = conectar_base_de_datos()
        

    def initialize_database(self):
        """
        Initializes the database by creating necessary tables if they do not exist.
        This method leverages the 'crear_tabla' function, using the established
        database connection.
        """
        crear_tabla(self.conn)
        

    def close_connection(self):
        """
        Closes the database connection cleanly. This method should be called
        when the database operations are complete to ensure all resources are
        properly freed and the connection is closed safely.
        """
        desconectar_base_de_datos(self.conn)


    @logs
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


    @logs
    def baja_bd(self, id_registro):
        """
        Elimina un registro de la base de datos.
        La base de datos es records.db
        
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


    @logs
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

            subtotal = int(valores['cantidad']) * float(valores['monto']) * 100 / 100.0
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
