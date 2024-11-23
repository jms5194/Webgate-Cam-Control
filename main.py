"""C1080PBM GUI Control"""

__author__ = "Justin Stasiw"
__version__ = "$Revision 0.1b$"
__date__ = "$Date: 2019/07/12"

import sys

import constants
import serial_functions
import utilities
import config_functions
from pubsub import pub
import wx
import settings


class WebgateCamControlGUI(wx.Frame):
    # Main GUI window for the program
    def __init__(self):
        super().__init__(parent=None, title="Webgate Cam Control")
        # Check for .ini config, create if does not exist. Bring settings into settings.py
        config_functions.check_configuration(config_functions.where_to_put_user_data())
        # Set size and position of window based upon .ini settings
        self.SetPosition(settings.window_loc)
        self.SetSize(settings.window_size)
        panel = wx.Panel(self)
        panel_sizer = wx.BoxSizer(wx.VERTICAL)
        panel_sizer.AddSpacer(15)
        # Select Interface Dropdown
        interface_text = wx.StaticText(panel, label="Select Serial Interface:", style=wx.ALIGN_CENTER)
        panel_sizer.Add(interface_text, 0, wx.ALL | wx.EXPAND, 0)
        self.serial_sel_wxid = wx.NewIdRef()
        self.serial_selector = wx.Choice(panel, name="ser_sel", id=self.serial_sel_wxid)
        panel_sizer.Add(self.serial_selector, 1, wx.ALL | wx.EXPAND, 10)
        # Select Baud Dropdown
        baud_text = wx.StaticText(panel, label="Select Baud Rate:", style=wx.ALIGN_CENTER)
        panel_sizer.Add(baud_text, 0, wx.ALL | wx.EXPAND, 0)
        self.baud_sel_wxid = wx.NewIdRef()
        self.baud_selector = wx.Choice(panel, name="baud_sel", id=self.baud_sel_wxid)
        panel_sizer.Add(self.baud_selector, 1, wx.ALL | wx.EXPAND, 10)
        # Select Cam ID Dropdown
        id_text = wx.StaticText(panel, label= "Select Camera ID:", style=wx.ALIGN_CENTER)
        panel_sizer.Add(id_text, 0, wx.ALL | wx.EXPAND, 0)
        self.camid_sel_wxid = wx.NewIdRef()
        self.camid_selector = wx.Choice(panel, name= "id_sel", id=self.camid_sel_wxid)
        panel_sizer.Add(self.camid_selector, 1, wx.ALL | wx.EXPAND, 10)

        #Camera menu nav buttons
        button_grid = wx.GridSizer(3, 3, 10, 10)
        nav_up_button = wx.Button(panel, label= "Up")
        nav_left_button = wx.Button(panel, label="Left")
        nav_right_button = wx.Button(panel, label="Right")
        nav_down_button = wx.Button(panel, label="Down")
        nav_enter_button = wx.Button(panel, label="Enter")
        empty_cell = (0,0)
        button_grid.Add(empty_cell, flag=wx.ALIGN_CENTER_HORIZONTAL)
        button_grid.Add(nav_up_button, flag=wx.ALIGN_CENTER_HORIZONTAL)
        button_grid.Add(empty_cell, flag=wx.ALIGN_CENTER_HORIZONTAL)
        button_grid.Add(nav_left_button, flag=wx.ALIGN_CENTER_HORIZONTAL)
        button_grid.Add(nav_enter_button, flag=wx.ALIGN_CENTER_HORIZONTAL)
        button_grid.Add(nav_right_button, flag=wx.ALIGN_CENTER_HORIZONTAL)
        button_grid.Add(empty_cell, flag=wx.ALIGN_CENTER_HORIZONTAL)
        button_grid.Add(nav_down_button, flag=wx.ALIGN_CENTER_HORIZONTAL)
        button_grid.Add(empty_cell, flag=wx.ALIGN_CENTER_HORIZONTAL)

        panel_sizer.Add(button_grid, 0, wx.ALL | wx.EXPAND, 5)
        panel.SetSizer(panel_sizer)

        # Accelerator entries to allow for Menu access from keystrokes
        ID_NAV_LEFT = wx.ID_ANY
        ID_NAV_RIGHT = wx.ID_ANY
        ID_NAV_UP = wx.ID_ANY
        ID_NAV_DOWN = wx.ID_ANY
        ID_NAV_ENTER = wx.ID_ANY

        entries = [wx.AcceleratorEntry() for i in range(5)]
        entries[0].Set(wx.ACCEL_NORMAL, wx.WXK_LEFT, ID_NAV_LEFT)
        entries[1].Set(wx.ACCEL_NORMAL, wx.WXK_RIGHT, ID_NAV_RIGHT)
        entries[2].Set(wx.ACCEL_NORMAL, wx.WXK_UP, ID_NAV_UP)
        entries[3].Set(wx.ACCEL_NORMAL, wx.WXK_DOWN, ID_NAV_DOWN)
        entries[4].Set(wx.ACCEL_NORMAL, wx.WXK_RETURN, ID_NAV_ENTER)
        accel = wx.AcceleratorTable(entries)
        self.SetAcceleratorTable(accel)

        # Event Bindings for Accelerator Table
        self.Bind(wx.EVT_MENU, self.press_left, id=ID_NAV_LEFT)
        self.Bind(wx.EVT_MENU, self.press_right, id=ID_NAV_RIGHT)
        self.Bind(wx.EVT_MENU, self.press_up, id=ID_NAV_UP)
        self.Bind(wx.EVT_MENU, self.press_down, id=ID_NAV_DOWN)
        self.Bind(wx.EVT_MENU, self.press_enter, id=ID_NAV_ENTER)

        # Menubar
        filemenu = wx.Menu()
        m_about = filemenu.Append(wx.ID_ABOUT, "&About", "Info about this program")
        filemenu.AppendSeparator()
        m_exit = filemenu.Append(wx.ID_EXIT, "&Exit\tAlt-X", "Close window and exit program.")
        menubar = wx.MenuBar()
        menubar.Append(filemenu, "&File")
        self.SetMenuBar(menubar)

        # General UI Event Bindings
        self.Bind(wx.EVT_CLOSE, self.quit_app)
        self.Bind(wx.EVT_MENU, self.quit_app, m_exit)
        self.Bind(wx.EVT_MENU, self.on_about, m_about)
        self.Bind(wx.EVT_BUTTON, self.on_clicked)
        self.Bind(wx.EVT_CHOICE, self.update_interfaces)
        # Pull baud rates in from constants.py to populate the baud dropdown
        self.add_bauds_to_choice()
        # Subscribe to info about available serial ports to populate interface dropdown
        pub.subscribe(self.add_ports_to_choice, "AvailablePorts")
        pub.subscribe(self.add_cams_to_choice, "AvailableCams")
        # Query the system for possible serial ports
        serial_functions.serial_ports()
        utilities.cam_labels()

        #Preset the dropdowns to the last used choices:
        if settings.last_interface in self.serial_choices:
            self.serial_selector.SetSelection(self.serial_choices.index(settings.last_interface))
        if settings.last_baud in self.baud_choices:
            self.baud_selector.SetSelection(self.baud_choices.index(settings.last_baud))
        if settings.last_camID in self.camid_choices:
            self.camid_selector.SetSelection(self.camid_choices.index(settings.last_camID))

        self.Show()


    def on_about(self, event):
        # Create the About Dialog Box
        dlg = wx.MessageDialog(self, " A Controller for Webgate Camera Menus. Copyright 2025.",
                               "Webgate Cam Control", wx.OK)
        dlg.ShowModal()  # Shows it
        dlg.Destroy()  # Destroy pop-up when finished.



    def quit_app(self, event):
        # Grab the current size and position of the app
        # and update the config file.
        cur_size = self.GetTopLevelParent().GetSize()
        cur_pos = self.GetTopLevelParent().GetPosition()
        ini_path = config_functions.where_to_put_user_data()
        config_functions.update_pos_in_config(cur_pos, ini_path)
        config_functions.update_size_in_config(cur_size, ini_path)
        self.Destroy()
        sys.exit()

    def add_ports_to_choice(self, choices):
        print("received ports")
        self.serial_selector.Clear()
        self.serial_selector.Append("\n")
        for x in choices:
            self.serial_selector.Append(x, "ports")
        self.serial_choices = [""] + choices

    def add_cams_to_choice(self, choices):
        print("received cams")
        self.camid_selector.Clear()
        self.camid_selector.Append("\n")
        for x in choices:
            self.camid_selector.Append(x, "ports")
        self.camid_choices = [""] + choices
        print(self.camid_choices)
    def add_bauds_to_choice(self):
        self.baud_selector.Clear()
        self.baud_selector.Append("\n")
        for x in constants.BAUD_RATES:
            self.baud_selector.Append(x, "bauds")
        self.baud_choices = [""] + constants.BAUD_RATES

    def on_clicked(self, event):
        btn = event.GetEventObject().GetLabel()
        if btn == "Left":
            self.press_left()
        elif btn == "Right":
            self.press_right()
        elif btn == "Up":
            self.press_up()
        elif btn == "Down":
            self.press_down()
        elif btn == "Enter":
            self.press_enter()
        else:
            print("Msg not recognized")

    def press_left(self, *args):
        button_ID = "04"
        utilities.msg_builder(button_ID)
    def press_right(self, *args):
        button_ID = "02"
        utilities.msg_builder(button_ID)
    def press_up(self, *args):
        button_ID = "08"
        utilities.msg_builder(button_ID)
    def press_down(self, *args):
        button_ID = "10"
        utilities.msg_builder(button_ID)
    def press_enter(self, *args):
        button_ID = "1e"
        utilities.msg_builder(button_ID)

    def update_interfaces(self, event):
        incoming_choice_id = event.GetId()
        print(incoming_choice_id)
        if incoming_choice_id == self.serial_sel_wxid.GetId():
            chosen_port = self.serial_choices[event.Selection]
            config_functions.update_last_interface_in_config(chosen_port,
                                                             config_functions.where_to_put_user_data())
            pub.sendMessage('chosenPort', port_to_open=chosen_port)
        elif incoming_choice_id == self.baud_sel_wxid.GetId():
            baud_rate = self.baud_choices[event.Selection]
            config_functions.update_last_baud_in_config(baud_rate,
                                                        config_functions.where_to_put_user_data())
            pub.sendMessage('chosenBaud', baud_to_open=baud_rate)
        elif incoming_choice_id == self.camid_sel_wxid.GetId():
            cam_id = self.camid_choices[event.Selection]
            config_functions.update_last_cam_in_config(cam_id,
                                                       config_functions.where_to_put_user_data())


if __name__ == "__main__":
    app = wx.App()
    frame = WebgateCamControlGUI()
    app.MainLoop()


