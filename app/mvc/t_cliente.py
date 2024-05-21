"""
t_cliente.py
    Este módulo contiene la implementación de un cliente UDP que se comunica con un servidor UDP.
    El cliente envía un mensaje al servidor y recibe un mensaje de respuesta.
    
    El cliente se ejecuta con el siguiente comando:
        python t_cliente.py [mensaje opcional]
    
    Parámetros:
        mensaje: mensaje opcional que se enviará al servidor.
        
    Ejemplo:
        python t_cliente.py "Hola, servidor UDP!"
    
    El cliente se conecta al servidor en el puerto 9999.
    El servidor debe estar en ejecución para que el cliente pueda establecer la conexión.
"""

import socket
import sys

try:
    HOST, PORT = "localhost", 9999
    data = " ".join(sys.argv[1:])
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    if data != "":
        mensaje = data
    else:
        mensaje = f"Hola, soy el cliente {HOST}."

    sock.sendto(mensaje.encode("UTF-8"), (HOST, PORT))
    
    print(f"[Cliente UDP iniciado]")
    
    received = sock.recvfrom(1024)

    print(f"[Cliente] Conexión establecida con Servidor: {received[1][0]} | Puerto: {received[1][1]}")
    print(f"[Cliente] Mensaje enviado al Servidor: '{mensaje}'")
    print(f"[Cliente] Bytes enviados: {len(mensaje.encode('UTF-8'))} bytes.")
    print(f"[Cliente] Mensaje recibido del Servidor: '{received[0].decode('UTF-8')}'")
    print(f"[Cliente] Bytes recibidos: {len(received[0])} bytes.")

except Exception as e:
    print(f"Error: {e}")
finally:
    sock.close()
    print("[Conexión terminada]")