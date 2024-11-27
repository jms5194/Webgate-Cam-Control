import appdirs
import os.path
import configparser
from configupdater import ConfigUpdater
from pubsub import pub
import constants
import settings


def where_to_put_user_data():
    # Find a home for our preferences file
    appname = "Webgate Cam Control"
    appauthor = "Justin Stasiw"
    config_dir = appdirs.user_config_dir(appname, appauthor)
    if os.path.isdir(config_dir):
        pass
    else:
        os.makedirs(config_dir)
    ini_prefs_path = config_dir + "/settings.ini"
    return ini_prefs_path


def check_configuration(ini_prefs_path):
    # Checking if a .ini config already exists for this app, if not call
    # build_initial_ini
    try:
        if os.path.isfile(ini_prefs_path):
            set_vars_from_pref(ini_prefs_path)
        else:
            build_initial_ini(ini_prefs_path)
    except Exception as e:
        print(e)
        build_initial_ini(ini_prefs_path)


def build_initial_ini(ini_prefs_path):
    # Builds a .ini configuration file with default settings.
    # What should our defaults be? All zeros? Something technically valid?
    config = configparser.ConfigParser()
    config["main"] = {}
    config["main"]["last_interface"] = ""
    config["main"]["last_baud"] = "0"
    config["main"]["last_cam"] = "1:"
    config["main"]["window_size_x"] = "403"
    config["main"]["window_size_y"] = "472"
    config["main"]["window_pos_x"] = "400"
    config["main"]["window_pos_y"] = "222"
    config["main"]["cam_names"] = ",".join(constants.DEFAULT_CAM_LABELS)
    config["main"]["remote_ip"] = "192.168.10.100"
    config["main"]["send_port"] = "9999"
    config["main"]["receive_port"] = "9998"

    with open(ini_prefs_path, "w") as configfile:
        config.write(configfile)
    set_vars_from_pref(ini_prefs_path)


def set_vars_from_pref(config_file_loc):
    # Bring in the vars to fill out settings.py from the preferences file
    config = configparser.ConfigParser()
    config.read(config_file_loc)
    settings.window_size = (int(config["main"]["window_size_x"]), int(config["main"]["window_size_y"]))
    settings.window_loc = (int(config["main"]["window_pos_x"]), int(config["main"]["window_pos_y"]))
    settings.last_interface = config["main"]["last_interface"]
    settings.last_baud = config["main"]["last_baud"]
    settings.last_camID = config["main"]["last_cam"]
    settings.camID_names = config["main"]["cam_names"].split(",")
    settings.remote_ip = config["main"]["remote_ip"]
    settings.send_port = int(config["main"]["send_port"])
    settings.receive_port = int(config["main"]["receive_port"])


def update_pos_in_config(win_pos_tuple, ini_prefs_path):
    # Receives the position of the window from the UI and stores it in the preferences file
    updater = ConfigUpdater()
    updater.read(ini_prefs_path)
    try:
        updater["main"]["window_pos_x"] = str(win_pos_tuple[0])
        updater["main"]["window_pos_y"] = str(win_pos_tuple[1])
    except Exception as e:
        print(e)
    updater.update_file()


def update_size_in_config(win_size_tuple, ini_prefs_path):
    # Receives the position of the window from the UI and stores it in the preferences file
    updater = ConfigUpdater()
    updater.read(ini_prefs_path)
    try:
        updater["main"]["window_size_x"] = str(win_size_tuple[0])
        updater["main"]["window_size_y"] = str(win_size_tuple[1])
    except Exception as e:
        print(e)
    updater.update_file()


def update_last_interface_in_config(last_interface, ini_prefs_path):
    updater = ConfigUpdater()
    updater.read(ini_prefs_path)
    try:
        updater["main"]["last_interface"] = last_interface
    except Exception as e:
        print(e)
    updater.update_file()


def update_last_baud_in_config(last_baud, ini_prefs_path):
    updater = ConfigUpdater()
    updater.read(ini_prefs_path)
    try:
        updater["main"]["last_baud"] = str(last_baud)
    except Exception as e:
        print(e)
    updater.update_file()


def update_last_cam_in_config(last_cam, ini_prefs_path):
    updater = ConfigUpdater()
    updater.read(ini_prefs_path)
    try:
        updater["main"]["last_cam"] = str(last_cam)
    except Exception as e:
        print(e)
    updater.update_file()


def update_cam_names_in_config(cam_names, ini_prefs_path):
    updater = ConfigUpdater()
    updater.read(ini_prefs_path)
    try:
        updater["main"]["cam_names"] = ",".join(cam_names)
    except Exception as e:
        print(e)
    updater.update_file()

def update_ip_in_config(remote_ip, send_port, receive_port, ini_prefs_path):
    updater = ConfigUpdater()
    updater.read(ini_prefs_path)
    try:
        updater["main"]["remote_ip"] = remote_ip
        updater["main"]["send_port"] = send_port
        updater["main"]["receive_port"] = receive_port
    except Exception as e:
        print(e)
    updater.update_file()


def cam_labels():
    cam_list = settings.camID_names
    pub.sendMessage("AvailableCams", choices=cam_list)
