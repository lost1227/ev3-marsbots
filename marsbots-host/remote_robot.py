import socket
import bluetooth
import pickle


_bt_port = 3
_tcp_port = 32390  # port number is arbitrary, but must match between server and client


class RemoteRobot:
    def __init__(self, robot_info):
        self.robot_ip_addr = robot_info['ip']
        self.robot_mac_addr = robot_info['btmac']
        self.s = None

    def connect(self):
        # Try TCP first
        if not self.s and self.robot_ip_addr:
            try:
                self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.s.connect((self.robot_ip_addr, _tcp_port))
                print('Connected to robot', self.robot_ip_addr)
            except OSError as err:
                self.s = None
                print(f'Failed to open TCP connection to {self.robot_ip_addr}: {repr(err)}')

        # If no TCP connection available, try Bluetooth
        if not self.s:
            try:
                self.s = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
                self.s.connect((self.robot_mac_addr, _bt_port))
                print('Connected to robot', self.robot_mac_addr)
            except OSError as err:
                self.s = None
                print(f'Failed to open BT connection to {self.robot_mac_addr}: {repr(err)}')

    def is_connected(self):
        return self.s is not None

    def close(self):
        if self.s is not None:
            self.send_command(None)
            if self.s is not None:
                self.s.close()
            self.s = None

    def send_command(self, command):
        if self.s is not None:
            data = pickle.dumps(command, protocol=4)
            try:
                self.s.send(data)
            except OSError:
                self.s = None
                print('Robot disconnected', self.robot_ip_addr)
