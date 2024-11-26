import socket
import struct

class Client:
    def __init__(self, multicast_group, port):
        self.multicast_group = multicast_group
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
        # Привязываем сокет к указанному порту
        self.sock.bind(('', port))

        # Настраиваем сокет для присоединения к multicast группе
        group = socket.inet_aton(multicast_group)
        mreq = struct.pack('4sL', group, socket.INADDR_ANY)
        self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

    def start(self):
        try:
            print("Ожидание сообщений...")
            while True:
                data, address = self.sock.recvfrom(1024)
                print(f"Получено сообщение: {data.decode('utf-8')} от {address}")
        finally:
            self.sock.close()

if __name__ == "__main__":
    multicast_group = '233.0.0.1'
    port = 1502
    client = Client(multicast_group, port)
    client.start()
