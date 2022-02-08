"""C1080PBM GUI Control"""

__author__ = "Justin Stasiw"
__version__ = "$Revision 0.1b$"
__date__ = "$Date: 2019/07/12"

import sys
import serial
import serial.tools.list_ports
import os
import PySimpleGUI as sg


class C1080ControlApp:

    def __init__(self):
        self.CamList = []
        self.Cam_ID = 1
        self.Sync_Byte = "ff"
        self.key_ID_Byte = "00"
        self.key_right_Byte = "02"
        self.key_left_Byte = "04"
        self.key_up_Byte = "08"
        self.key_down_Byte = "10"
        self.key_enter_Byte = "1e"
        self.button_ID = None
        self.interface = None
        self.ser = None
        self.cam_labels()

    def cam_labels(self):
        # Pulls camera labels from a pre-specified file:
        try:
            labelpos = os.path.expanduser("~/documents/camlabels.txt")
            camlabels = open(labelpos, "r")
            self.CamList = camlabels.readlines()
            camlabels.close()
            self.serial_ports()

        except:
            # If no file is available, then just make a list of 64 possible IDs
            cams = []
            for i in range(1, 65):
                cams.append(str(i) + ":")
            self.CamList = cams
            self.serial_ports()

    def App_Window(self, serial_interfaces):
        # This builds the Application window using PYSimpleGUI
        layout = [
            [sg.Text("Select serial interface:")],
            [sg.InputCombo(serial_interfaces, enable_events=True, readonly=True)],
            [sg.Text("Select camera:")],
            [sg.InputCombo(self.CamList, size=(32, 1), enable_events=True, readonly=True)],
            [sg.Text("OSD Control", pad=(68, 1), font=("Helvetica", 18))],
            [sg.Text("Press enter to bring up OSD.", pad=(45, 1), font=("Helvetica", 12))],
            [sg.Button("Up", size=(31, 2), button_color=("blue", "grey"), font=("Helvetica", 18, "bold"))],
            [sg.Button("Left", size=(10, 2), button_color=("blue", "grey"), font=("Helvetica", 18, "bold")),
             sg.Button("Enter", size=(10, 2), button_color=("blue", "grey"), font=("Helvetica", 18, "bold")),
             sg.Button("Right", size=(10, 2), button_color=("blue", "grey"), font=("Helvetica", 18, "bold"))],
            [sg.Button("Down", size=(31, 2), button_color=("blue", "grey"), font=("Helvetica", 18, "bold"))],
            [sg.Text("Remember to save and exit!", pad=(48, 3), font=("Helvetica", 12))]]

        window = sg.Window('C1080PBM Camera Control', layout, return_keyboard_events=True)

        while True:  # Event Loop
            event, values = window.Read(timeout=100)
            if event is None or event == 'Exit':
                break
            if event != sg.TIMEOUT_KEY:
                print(event, values)
                self.event_processor(event, values)
        if self.ser != None:
            self.ser.close()
        window.Close()

    def event_processor(self, event, values):
        if (event != 0) and (event != 1):
            if event == "Left" or event == "special 16777234":
                self.button_ID = "04"
                self.msg_builder(event, values)
            elif event == "Right" or event == "special 16777236":
                self.button_ID = "02"
                self.msg_builder(event, values)
            elif event == "Up" or event == "special 16777235":
                self.button_ID = "08"
                self.msg_builder(event, values)
            elif event == "Down" or event == "special 16777237":
                self.button_ID = "10"
                self.msg_builder(event, values)
            elif event == "Enter" or event == "special 16777220":
                self.button_ID = "1e"
                self.msg_builder(event, values)
            else:
                print("Msg not recognized")

    def msg_builder(self, event, values):
        interface_id = values[0]
        print(interface_id)
        cam_id = values[1]
        print(cam_id)
        cam_id = cam_id.split(":")
        cam_id = cam_id[0]
        self.Cam_ID = "%0.2x" % int(cam_id)

        msg_checksum = self.Calc_Checksum(self.Cam_ID, self.button_ID)

        msg_toSend = self.Sync_Byte + self.Cam_ID + self.key_ID_Byte + self.button_ID + "00" + "00" + msg_checksum
        print(msg_toSend)
        self.Send_Serial_Msg(interface_id, msg_toSend)

    def Calc_Checksum(self, Cam_ID, button_ID):

        byte_2_int = int(Cam_ID, 16)
        byte_3_int = 0
        byte_4_int = int(button_ID, 16)
        byte_5_int = 0
        byte_6_int = 0

        checksum_sum = byte_2_int + byte_3_int + byte_4_int + byte_5_int + byte_6_int
        # print checksum_sum # For Debugging
        checksum_hex = "%0.2x" % checksum_sum
        # print checksum_hex  # For Debugging
        return checksum_hex

    def serial_ports(self):
        # Lists serial port names
        comlist = serial.tools.list_ports.comports()
        connected = []
        for element in comlist:
            connected.append(element.device)
        self.App_Window(connected)

    def Send_Serial_Msg(self, interface, msg):
        # Opens serial port connection
        if self.interface == interface:
            if self.ser != None:
                if self.ser.isOpen():
                    self.ser.write(bytearray.fromhex(msg))
                else:
                    print("Serial port is not open")
            else:
                print("Serial port is not open")
        else:
            self.interface = interface
            self.close_serial()
            self.open_serial(interface)
            if self.ser != None:
                if self.ser.isOpen():
                    self.ser.write(bytearray.fromhex(msg))
                else:
                    print("Serial port is not open")

    def open_serial(self, interface):
        try:
            self.ser = serial.Serial(interface, 57600)
        except:
            print("Serial Connection Failed")

    def close_serial(self):
        if self.ser != None:
            self.ser.close()


if __name__ == "__main__":
    C1080ControlApp()