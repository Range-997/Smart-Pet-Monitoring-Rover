import time
import serial


class CarSerial:
    def __init__(self, port='/dev/ttyUSB0', baudrate=9600, timeout=1.0):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.ser = None

    def connect(self):
        try:
            self.ser = serial.Serial(self.port, self.baudrate, timeout=self.timeout)
            time.sleep(2.0)  # Arduino resets after USB serial opens
            return True
        except serial.SerialException as err:
            print(f'Serial connection failed on {self.port}: {err}')
            self.ser = None
            return False

    def is_ready(self):
        return self.ser is not None and self.ser.is_open

    def send_command(self, cmd):
        if not cmd:
            return False
        if not self.is_ready() and not self.connect():
            return False
        try:
            self.ser.write(cmd[0].encode('utf-8'))
            self.ser.flush()
            return True
        except serial.SerialException as err:
            print(f'Serial write failed: {err}')
            try:
                self.ser.close()
            except Exception:
                pass
            self.ser = None
            return False

    def close(self):
        if self.ser is not None and self.ser.is_open:
            self.ser.close()
