import socket
import struct

class Server:
    def __init__(self, multicast_group, port):
        self.multicast_group = multicast_group
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def start(self):
        try:
            while True:
                message = input("Введите сообщение для отправки: ")
                if not message:
                    continue

                # Отправка сообщения в multicast группу
                self.sock.sendto(message.encode('utf-8'), (self.multicast_group, self.port))
                print(f"Сообщение отправлено: {message}")
        finally:
            self.sock.close()

if __name__ == "__main__":
    multicast_group = '233.0.0.1'
    port = 1502
    server = Server(multicast_group, port)
    server.start()
