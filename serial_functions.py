import serial
import serial.tools.list_ports
from pubsub import pub

import settings


#Need to repair all the class based self linkages in here:

ser_port = None

def serial_ports():
    # Lists serial port names
    comlist = serial.tools.list_ports.comports()
    available_ports = []
    for element in comlist:
        available_ports.append(element.device)
    pub.sendMessage("AvailablePorts", choices=available_ports)

def Send_Serial_Msg(interface, msg):
    # Opens serial port connection
    global ser_port
    if settings.last_interface == interface:
        if ser_port != None:
            if ser_port.isOpen():
                ser_port.write(bytearray.fromhex(msg))
            else:
                print("Serial port is not open")
        else:
            print("Serial port is not open")
    else:
        settings.last_interface = interface
        ser_port.close_serial()
        ser_port.open_serial(interface)
        if ser_port != None:
            if ser_port.isOpen():
                ser_port.write(bytearray.fromhex(msg))
            else:
                print("Serial port is not open")

def open_serial(interface):
    try:
        ser_port = serial.Serial(interface, int(settings.last_baud))
    except:
        print("Serial Connection Failed")

def close_serial():
    if ser_port != None:
        ser_port.close()