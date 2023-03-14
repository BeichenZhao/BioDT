import socket


class Device:
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def __init__(self):
        self.connected = False
        self.status = 0

    def change_status(self, _status):
        if _status == 1:
            data = bytes('RU', 'utf8')
            self.client.send(data)
        elif _status == 0:
            data = bytes('PA', 'utf8')
            self.client.send(data)

    def get_data(self):
        try:
            data = self.client.recv(512)
            data = (data.decode('UTF-8'))[:-2]
        except BlockingIOError:
            data = ''

        return data

    def sampling(self):
        data = bytes('SA', 'utf8')
        try:
            self.client.send(data)
        except ConnectionResetError:
            self.client.connect(('192.168.4.1', 9000))
            self.client.send(data)

    def change_shake(self, shake_rate):
        data = bytes('SH'+str(shake_rate), 'utf8')
        try:
            self.client.send(data)
        except ConnectionResetError:
            self.client.connect(('192.168.4.1', 9000))
            self.client.send(data)

    def change_angle(self, angle):
        data = bytes('AN'+str(angle), 'utf8')
        try:
            self.client.send(data)
        except ConnectionResetError:
            self.client.connect(('192.168.4.1', 9000))
            self.client.send(data)

    def connect(self):
        self.client.connect(('192.168.4.1', 9000))
        self.connected = True

    def disconnect(self):
        self.client.close()
        self.connected = False

    def is_connected(self):
        return self.connected


if __name__ == '__main__':
    device = Device()
    while True:
        pass
