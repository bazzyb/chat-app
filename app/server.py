import json
import os
import socket
import threading
from cryptography.fernet import Fernet

# IP = socket.gethostbyname(socket.gethostname())
IP = 'localhost'
PORT = 8004


class Server:
    def __init__(self):
        self.active_connections = {}
        self.check_for_key()
        self.build_socket()

    def check_for_key(self):
        is_file = os.path.isfile('chat_key.key')
        if is_file:
            key_file = open('chat_key.key', 'rb')
            self.encryption_key = key_file.read()
            key_file.close()
        else:
            self.generate_encryption_key()

    def generate_encryption_key(self):
        self.encryption_key = Fernet.generate_key()
        key_file = open('chat_key.key', 'wb')
        key_file.write(self.encryption_key)
        key_file.close()

    def build_socket(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((IP, PORT))
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.listen(5)

    def get_clients(self):
        (client, address) = self.server.accept()

        address_key = str(address[0]) + str(address[1])

        self.active_connections[address_key] = client
        self.broadcast('User has entered the room.', address_key)

        client_thread = threading.Thread(target=self.handler, args=((client, address_key)))
        client_thread.daemon = True
        client_thread.start()

    def broadcast(self, msg, address_key):
        for key, client in self.active_connections.items():
            if key != address_key:
                client.send(msg.encode('utf-8'))

    def handler(self, client, address_key):
        while True:
            data = client.recv(1024)

            if not data:
                self.broadcast('User has left the room.', address_key)
                del self.active_connections[address_key]
                client.close()
                break
            else:
                payload = self.decrypt_payload(data)
                if payload['type'] == 'message':
                    msg = f'{payload["user"]}: {payload["data"]}'
                    self.broadcast(msg, address_key)

    def decrypt_payload(self, data):
        f = Fernet(self.encryption_key)
        data_string = f.decrypt(data).decode('utf-8')
        payload = json.loads(data_string)
        return payload

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
