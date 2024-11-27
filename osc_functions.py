import threading
import socket
import psutil
from pubsub import pub
from pythonosc import udp_client
from pythonosc import dispatcher
from pythonosc import osc_server

import button_functions
import config_functions
import settings
import ipaddress


class WebgateOSCReceiver:
    def __init__(self):
        self.webgate_osc_thread = None
        self.webgate_dispatcher = None
        self.webgate_client = None
        self.webgate_osc_server = None
        self.lock = threading.Lock()

    def start_threads(self):
        self.webgate_osc_thread = threading.Thread(target=self.build_webgate_osc_servers, daemon=False)
        self.webgate_osc_thread.start()

    def build_webgate_osc_servers(self):
        self.webgate_client = udp_client.SimpleUDPClient(settings.remote_ip, settings.send_port)
        self.webgate_dispatcher = dispatcher.Dispatcher()
        self.receive_webgate_osc()
        try:
            self.webgate_osc_server = osc_server.ThreadingOSCUDPServer((self.find_local_ip_in_subnet
                                                                        (settings.remote_ip),
                                                                        settings.receive_port),
                                                                       self.webgate_dispatcher)
            print("Webgate OSC Server Started")
            self.webgate_osc_server.serve_forever()
        except Exception as e:
            print(e)
            print("Unable to make OSC connection")

    def receive_webgate_osc(self):
        # Receives and distributes OSC from Digico, based on matching OSC values
        self.webgate_dispatcher.map("/ID", self.update_selected_cam)
        self.webgate_dispatcher.map("/button", self.osc_button_handler)

    def update_selected_cam(self, osc_address, new_id):
        new_cam = settings.camID_names[new_id - 1]
        config_functions.update_last_cam_in_config(new_cam,
                                                   config_functions.where_to_put_user_data())
        config_functions.set_vars_from_pref(config_functions.where_to_put_user_data())
        pub.sendMessage("OSCCamSelect", new_sel_cam=new_cam)

    @staticmethod
    def osc_button_handler(osc_address, button_pressed):
        if button_pressed == "LEFT":
            button_functions.press_left()
        elif button_pressed == "RIGHT":
            button_functions.press_right()
        elif button_pressed == "UP":
            button_functions.press_up()
        elif button_pressed == "DOWN":
            button_functions.press_down()
        elif button_pressed == "ENTER":
            button_functions.press_enter()


    @staticmethod
    def find_local_ip_in_subnet(remote_ip):
        # Find our local interface in the same network as the console interface
        ipv4_interfaces = []
        # Make a list of all the network interfaces on our machine
        for interface, snics in psutil.net_if_addrs().items():
            for snic in snics:
                if snic.family == socket.AF_INET:
                    ipv4_interfaces.append((snic.address, snic.netmask))
        # Iterate through network interfaces to see if any are in the same subnet as console
        for i in ipv4_interfaces:
            # Convert tuples to strings like 192.168.1.0/255.255.255.0 since that's what ipaddress expects
            interface_ip_string = i[0] + "/" + i[1]
            # If strict is off, then the user bits of the computer IP will be masked automatically
            # Need to add error handling here
            if ipaddress.IPv4Address(remote_ip) in ipaddress.IPv4Network(interface_ip_string, False):
                return i[0]
            else:
                pass

    def close_servers(self):
        try:
            self.webgate_osc_server.server_close()
            self.webgate_osc_server.shutdown()
            self.webgate_osc_thread.join()
        except Exception as e:
            print(e)
        return True

    def restart_servers(self):
        # Restart the OSC server threads.
        self.start_threads()
