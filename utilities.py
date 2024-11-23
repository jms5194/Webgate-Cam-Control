import serial_functions
import os

import settings


def msg_builder(button_ID):
    Sync_Byte = "ff"
    key_ID_Byte = "00"
    # For reference below:
    key_right_Byte = "02"
    key_left_Byte = "04"
    key_up_Byte = "08"
    key_down_Byte = "10"
    key_enter_Byte = "1e"

    interface_id = settings.last_interface
    print(interface_id)
    cam_id = settings.last_camID.split(":")[0]
    hex_cam_id = "00"
    try:
        hex_cam_id = "%0.2x" % int(cam_id)
    except ValueError as e:
        print("Invalid Camera Selected")

    msg_checksum = Calc_Checksum(hex_cam_id, button_ID)

    msg_toSend = Sync_Byte + hex_cam_id + key_ID_Byte + button_ID + "00" + "00" + msg_checksum
    print(msg_toSend)
    serial_functions.Send_Serial_Msg(interface_id, msg_toSend)


def Calc_Checksum(Cam_ID, button_ID):

    byte_2_int = int(Cam_ID, 16)
    byte_3_int = 0
    byte_4_int = int(button_ID, 16)
    byte_5_int = 0
    byte_6_int = 0

    checksum_sum = byte_2_int + byte_3_int + byte_4_int + byte_5_int + byte_6_int
    checksum_hex = "%0.2x" % checksum_sum
    return checksum_hex

def cam_labels():
    # Pulls camera labels from a pre-specified file:
    try:
        labelpos = os.path.expanduser("~/documents/camlabels.txt")
        camlabels = open(labelpos, "r")
        self.CamList = camlabels.readlines()
        camlabels.close()
        serial_functions.serial_ports()

    except:
        # If no file is available, then just make a list of 64 possible IDs
        cams = []
        for i in range(1, 65):
            cams.append(str(i) + ":")
        self.CamList = cams
        serial_functions.serial_ports()
