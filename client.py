import os
import pickle
import rsa
import socket
import threading
from cryptography.fernet import Fernet

from scripts import encryption
from scripts.consts import MessageTypes
from scripts.exceptions import ServerClosedError

# IP = socket.gethostbyname(socket.gethostname())
IP = 'localhost'
PORT = 8004


class Client:
    socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def __init__(self, nickname):
        self.nickname = nickname
        self.connected = False
        self.generate_keys()
        self.connect_to_server()

    def generate_keys(self):
        keys = encryption.generate_asymmetric_keys()
        self.public_key = keys[0]
        self.private_key = keys[1]
        self.key_hash = keys[2]

    def connect_to_server(self):
        print('[SERVER]: Connecting...')
        self.socket.connect((IP, PORT))
        print('[SERVER]: Connected')

    def handle_login(self):
        while not self.connected:
            self._handle_login_data()

    def _handle_login_data(self):
        data = self.socket.recv(1024)
        if not data:
            raise ServerClosedError('Server closed unexpectedly')

        res = pickle.loads(data)

        if res['type'] == MessageTypes.PUBLIC_KEY:
            self._send_public_key()

        elif res['type'] == MessageTypes.SYM_KEY:
            self._decrypt_sym_key(res['payload'])

        elif res['type'] == MessageTypes.USERNAME:
            self.send_to_server(MessageTypes.USERNAME, self.nickname)

        elif res['type'] == MessageTypes.PASSWORD:
            self.send_to_server(MessageTypes.USERNAME, 'admin')

        elif res['type'] == MessageTypes.CONNECTED:
            self.connected = True
            return True

        elif res['type'] == MessageTypes.SERVER_CLOSED:
            raise ServerClosedError

        else:
            print('[SERVER]: UNEXPECTED RESPONSE TYPE:')
            print(res)

    def _send_public_key(self):
        self.send_to_server(
            MessageTypes.PUBLIC_KEY,
            (self.public_key, self.key_hash)
        )

    def _decrypt_sym_key(self, payload):
        encrypted_key, key_hash = payload
        hash_matches = encryption.check_key_hash(encrypted_key, key_hash)

        if hash_matches:
            self.sym_key = rsa.decrypt(encrypted_key, self.private_key)
            self.cipher = Fernet(self.sym_key)

            self.send_to_server(MessageTypes.SYM_KEY, True)
        else:
            self.send_to_server(MessageTypes.SYM_KEY, False)

    def send_to_server(self, msg_type, payload, **kwargs):
        self.socket.send(pickle.dumps({
            'type': msg_type,
            'payload': payload,
            **kwargs
        }))

    def message_listener(self):
        while self.connected:
            self._handle_message_data()

    def start_message_listener(self):
        # This function puts the listener in it's own thread
        # The server has now accepted our connection, and we can listen for messages while being able to chat freely

        thread = threading.Thread(target=self.message_listener)
        thread.daemon = True
        thread.start()

    def _handle_message_data(self):
        data = self.socket.recv(1024)
        if not data:
            raise ServerClosedError('Server closed unexpectedly')

        res = pickle.loads(data)

        if res['type'] == MessageTypes.MESSAGE:
            msg = self._decrypt_msg(res['payload'])
            print(msg)

        elif res['type'] == MessageTypes.SERVER_CLOSED:
            quit()

        else:
            print('[SERVER]: UNEXPECTED RESPONSE TYPE:')
            print(res)

    def chat_loop(self):
        while self.connected:
            msg = input()

            if (msg == 'q' or msg == 'quit'):
                self.connected = False
                break

            self._send_msg(msg)

    def _send_msg(self, msg):
        encrypted_msg = self.cipher.encrypt(pickle.dumps(msg))
        self.send_to_server(MessageTypes.MESSAGE, encrypted_msg)

    def _decrypt_msg(self, msg):
        msg = pickle.loads(self.cipher.decrypt(msg))
        return msg


if __name__ == '__main__':
    try:
        nickname = input('Choose a nickname: ')
        client = Client(nickname)
        client.handle_login()

        os.system('clear')
        print('[SERVER]: Chat opened.')
        client.start_message_listener()
        client.chat_loop()

    except ServerClosedError as err:
        client.socket.close()
    except ConnectionRefusedError:
        print('Server is not currently runnning.')
    except KeyboardInterrupt:
        pass
