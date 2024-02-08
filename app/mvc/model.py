import sqlite3
from typing import Optional, List, Tuple
from controller import obtener_mes_actual


##############################################################################

#--------------------------------INICIO MODELO-------------------------------#

class ModelClass:

    #-----BASE DE DATOS-----#
    def conectar_base_de_datos():
        conn = sqlite3.connect('BD/base_de_datos.db')
        return conn


    def desconectar_base_de_datos(conn):
        conn.close()


    def crear_tabla(conn):
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


    def alta_bd(conn, valores):
        conn = conectar_base_de_datos()
        cursor = conn.cursor()

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
        conn.commit()
        ultimo_id = cursor.lastrowid 
        desconectar_base_de_datos(conn)
        return ultimo_id
        

    def baja_bd(id_registro):
        conn = conectar_base_de_datos()
        cursor = conn.cursor()
        query = "DELETE FROM gastos WHERE id = ?;"
        cursor.execute(query, (id_registro,))
        conn.commit()
        desconectar_base_de_datos(conn)


    def modificacion_bd(id_registro, valores):
        conn = conectar_base_de_datos()
        cursor = conn.cursor()
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
        conn.commit()
        desconectar_base_de_datos(conn)

        
    def consulta_bd(mes=None):
        # Consulta todos los registros. Pero si se especifica 1 mes, filtra por mes
        
        conn = conectar_base_de_datos()
        cursor = conn.cursor()
        if mes is not None:
            query = "SELECT subtotal FROM gastos WHERE strftime('%m', fecha) = ?;"
            cursor.execute(query, (f"{mes:02d}",))
        else:
            query = """SELECT * FROM gastos;"""
            cursor.execute(query)
        rows = cursor.fetchall()
        desconectar_base_de_datos(conn)
        return rows


    conn = conectar_base_de_datos()
    crear_tabla(conn)
    #-----FIN BASE DE DATOS-----#

    #-----GRAFICO (DATOS)-----#
    def obtener_datos_grafico():
        conn = conectar_base_de_datos()
        cursor = conn.cursor()
        num_mes_actual = str(obtener_mes_actual())
        query = f"SELECT rubro, SUM(subtotal) FROM gastos WHERE strftime('%m', fecha) = '{num_mes_actual}' GROUP BY rubro"
        cursor.execute(query)
        data = cursor.fetchall()
        desconectar_base_de_datos(conn)
        return data
    #-----FIN GRAFICO (DATOS)-----#

    #---------------------------------FIN MODELO---------------------------------#

##############################################################################
