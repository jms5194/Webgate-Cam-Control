import serial_functions
import settings


def msg_builder(key_id, button_id, preset_id):
    sync_byte = "ff"
    interface_id = settings.last_interface
    cam_id = settings.last_camID.split(":")[0]
    hex_cam_id = "00"
    try:
        hex_cam_id = "%0.2x" % int(cam_id)
    except ValueError as e:
        print(e)
    hex_preset_id = "00"
    try:
        hex_preset_id = "%0.2x" % int(preset_id)
    except ValueError as e:
        print(e)

    byte_5 = 0

    msg_checksum = calc_checksum(hex_cam_id, key_id, button_id, byte_5, hex_preset_id)

    msg_to_send = sync_byte + hex_cam_id + key_id + button_id + "00" + hex_preset_id + msg_checksum
    print(msg_to_send)
    msg_sender = serial_functions.SerialConnection()
    msg_sender.send_serial_msg(interface_id, msg_to_send)


def calc_checksum(cam_id, key_id, button_id, byte_5, preset_id):

    byte_2_int = int(cam_id, 16)
    byte_3_int = int(key_id, 16)
    byte_4_int = int(button_id, 16)
    byte_5_int = byte_5
    byte_6_int = int(preset_id, 16)

    checksum_sum = byte_2_int + byte_3_int + byte_4_int + byte_5_int + byte_6_int
    checksum_hex = "%0.2x" % checksum_sum
    return checksum_hex
