import socket
import threading

# IP = socket.gethostbyname(socket.gethostname())
IP = 'localhost'
PORT = 8004


class Client:
    socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def __init__(self, nickname):
        self.nickname = nickname
        self.socket.connect((IP, PORT))
        self.start_listener()

    def start_listener(self):
        thread = threading.Thread(target=self._listener)
        thread.daemon = True
        thread.start()

    def send_msg(self, msg):
        msg = f'{self.nickname}: {msg}'
        self.socket.send(msg.encode('utf-8'))

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
        print('Chat opened.')

        while True:
            msg = input()

            if (msg == 'q' or msg == 'quit'):
                break

            client.send_msg(msg)
    except ConnectionRefusedError:
        print('Server is not currently runnning.')
    except KeyboardInterrupt:
        pass
