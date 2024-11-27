import serial
import serial.tools.list_ports
from pubsub import pub
import settings


def serial_ports():
    # Lists serial port names
    comlist = serial.tools.list_ports.comports()
    available_ports = []
    for element in comlist:
        available_ports.append(element.device)
    pub.sendMessage("AvailablePorts", choices=available_ports)


class SerialConnection:

    def __init__(self):
        self.ser_port = None

    def send_serial_msg(self, interface, msg):
        # Send a serial message

        if settings.last_interface == interface:
            print("=")
            if self.ser_port is not None:
                if self.ser_port.isOpen():
                    self.ser_port.write(bytearray.fromhex(msg))
            else:
                self.open_serial(interface)
                if self.ser_port is not None:
                    if self.ser_port.isOpen():
                        try:
                            self.ser_port.write(bytearray.fromhex(msg))
                            self.ser_port.close()
                        except SerialTimeoutException as e:
                            print(e)
        else:
            settings.last_interface = interface
            self.ser_port.close()
            self.open_serial(interface)
            if self.ser_port is not None:
                if self.ser_port.isOpen():
                    try:
                        self.ser_port.write(bytearray.fromhex(msg))
                        self.ser_port.close()
                    except SerialTimeoutException as e:
                        print(e)

    def open_serial(self, interface):
        # Opens a specified serial port interface
        try:
            self.ser_port = serial.Serial(interface, int(settings.last_baud), write_timeout=0)
        except Exception as e:
            print(e)
            print("Serial Connection Failed")
