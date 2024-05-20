import socketserver


class MyUDPHandler(socketserver.BaseRequestHandler):
    def handle(self):
        try:
            data = self.request[0].strip()
            socket = self.request[1]
            
            print(f"[Servidor] Conexión establecida con Cliente: {self.client_address[0]} | Puerto: {self.client_address[1]}")
            print("[Servidor] Mensaje recibido: '{}'".format(data.decode("UTF-8")))

            
            mensaje = f"Mensaje recibido, {self.client_address[0]}!"
            socket.sendto(mensaje.encode("UTF-8"), self.client_address)
                    
            print(f"[Servidor] Mensaje enviado: '{mensaje}'")
            print(f"[Servidor] Bytes enviados: {len(mensaje.encode('UTF-8'))} bytes.")
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    HOST, PORT = "localhost", 9999
    with socketserver.UDPServer((HOST, PORT), MyUDPHandler) as server:
        print("[Servidor UDP iniciado]")
        server.serve_forever()
