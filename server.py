import os
import pickle
import socket
import threading
from cryptography.fernet import Fernet

from app.scripts import encryption
from app.consts import MessageTypes

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

    def broadcast(self, msg, address_key):
        for key, client in self.active_connections.items():
            if key != address_key:
                pass
                # SEND MESSAGE

    def get_clients(self):
        (client, address) = self.server.accept()

        address_key = str(address[0]) + str(address[1])

        self.active_connections[address_key] = {
            'client': client,
            'username': None,
            'sym_key': None,
            'cipher': None,
            'logged_in': False,
        }

        client_thread = threading.Thread(
            target=self.get_client_messages,
            args=((client, address_key))
        )
        client_thread.daemon = True
        client_thread.start()

    def get_client_messages(self, client, address_key):
        self.send_to_client(client, MessageTypes.PUBLIC_KEY)

        while True:
            data = client.recv(1024)

            if not data:
                self.broadcast('User has left the room.', address_key)
                del self.active_connections[address_key]
                client.close()
                break
            else:
                self.handle_data(address_key, pickle.loads(data))

    def handle_data(self, address_key, data):
        client_info = self.active_connections[address_key]

        if data['type'] == MessageTypes.PUBLIC_KEY:
            public_key, pub_key_hash = data['payload']
            key_info = self.generate_sym_key(address_key, public_key, pub_key_hash)
            client_info['sym_key'] = key_info[0]
            client_info['cipher'] = Fernet(key_info[0])
            self.send_sym_key(client_info['client'], key_info)

        elif data['type'] == MessageTypes.SYM_KEY:
            if data['payload']:
                self.send_to_client(client_info['client'], MessageTypes.USERNAME)
            else:
                print('KEY REJECTED')

        elif data['type'] == MessageTypes.USERNAME:
            client_info['username'] = data['payload']
            client_info['logged_in'] = True
            self.send_to_client(client_info['client'], MessageTypes.CONNECTED)

        elif data['type'] == MessageTypes.MESSAGE:
            self.decode_message(client_info, data['payload'])

    def generate_sym_key(self, address_key, public_key, pub_key_hash):
        hash_matches = encryption.check_key_hash(pickle.dumps(public_key), pub_key_hash)

        if hash_matches:
            key_info = encryption.generate_symmetric_keys(public_key)
            return key_info

    def send_sym_key(self, client, key_info):
        self.send_to_client(
            client,
            MessageTypes.SYM_KEY,
            payload=key_info[1:]
        )

    def send_to_client(self, client, msg_type, payload=None, **kwargs):
        client.send(pickle.dumps({
            'type': msg_type,
            'payload': payload,
            **kwargs
        }))

    def decode_message(self, client_info, message):
        cipher = client_info['cipher']
        msg = pickle.loads(cipher.decrypt(message))
        print(f'[{client_info["username"]}]: {msg}')

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
