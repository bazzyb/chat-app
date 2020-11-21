import json
import os
import socket
import threading
from cryptography.fernet import Fernet

# IP = socket.gethostbyname(socket.gethostname())
IP = 'localhost'
PORT = 8004


class Client:
    socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def __init__(self, nickname):
        self.nickname = nickname
        self.socket.connect((IP, PORT))

    def get_encryption_key(self):
        is_file = os.path.isfile('chat_key.key')
        if is_file:
            key_file = open('chat_key.key', 'rb')
            self.encryption_key = key_file.read()
            key_file.close()
        else:
            self._generate_encryption_key()

    def start_listener(self):
        thread = threading.Thread(target=self._listener)
        thread.daemon = True
        thread.start()

    def chat_loop(self):
        while True:
            msg = input()

            if (msg == 'q' or msg == 'quit'):
                break

            self._send_msg(msg)

    def _generate_encryption_key(self):
        self.encryption_key = Fernet.generate_key()
        key_file = open('chat_key.key', 'wb')
        key_file.write(self.encryption_key)
        key_file.close()

    def _send_msg(self, msg):
        msg = {
            "type": "message",
            "user": self.nickname,
            "data": msg
        }
        encrypted_msg = self._encrypt_payload(msg)
        self.socket.send(encrypted_msg)

    def _encrypt_payload(self, payload):
        if type(payload) == dict:
            payload = json.dumps(payload).encode('utf-8')

        fernet = Fernet(self.encryption_key)
        encrypted = fernet.encrypt(payload)
        return encrypted

    def _listener(self):
        while True:
            data = self.socket.recv(1024)

            if not data:
                print('Server closed')
                break
            else:
                print(data.decode('utf-8'))


if __name__ == '__main__':
    try:
        nickname = input('Choose a nickname: ')
        client = Client(nickname)
        client.get_encryption_key()
        client.start_listener()
        client.chat_loop()
        print('Chat opened.')
    except ConnectionRefusedError:
        print('Server is not currently runnning.')
    except KeyboardInterrupt:
        pass
