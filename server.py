import socket
import threading

# IP = socket.gethostbyname(socket.gethostname())
IP = 'localhost'
PORT = 8004


class Server:
    def __init__(self):
        self.active_connections = {}
        self.build_socket()

    def build_socket(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((IP, PORT))
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.listen(5)

    def get_clients(self):
        (client, address) = self.server.accept()

        address_key = str(address[0]) + str(address[1])

        self.active_connections[address_key] = client
        self.broadcast('User has entered the room.'.encode('utf-8'), address_key)

        client_thread = threading.Thread(target=self.handler, args=((client, address_key)))
        client_thread.daemon = True
        client_thread.start()

    def handler(self, client, address_key):
        while True:
            data = client.recv(1024)

            if not data:
                self.broadcast('User has left the room.'.encode('utf-8'), address_key)
                del self.active_connections[address_key]
                client.close()
                break
            else:
                self.broadcast(data, address_key)

    def broadcast(self, msg, address_key):
        for key, client in self.active_connections.items():
            if key != address_key:
                client.send(msg)

    def run(self):
        print(f'Server running on {IP}:{PORT}')

        try:
            while True:
                self.get_clients()

        except KeyboardInterrupt:
            print('Closing Server')

        finally:
            self.server.close()


if __name__ == '__main__':
    server = Server()
    server.run()
