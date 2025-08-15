"""Webgate GUI Control"""

__author__ = "Justin Stasiw"
__version__ = "$Revision 1.1$"
__date__ = "$Date: 2024/11/27"

import sys

import constants
import serial_functions
import config_functions
from pubsub import pub
import wx
import wx.lib.mixins.listctrl as listmix
import settings
import button_functions
import ipaddress
from osc_functions import WebgateOSCReceiver
from serial_functions import persistent_serial_connection


class WebgateCamControlGUI(wx.Frame):
    # Main GUI window for the program

    osc_functions = WebgateOSCReceiver()
    def __init__(self):
        super().__init__(parent=None, title="Webgate Cam Control")
        self.baud_choices = None
        self.camid_choices = None
        self.serial_choices = None
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
        id_text = wx.StaticText(panel, label="Select Camera ID:", style=wx.ALIGN_CENTER)
        panel_sizer.Add(id_text, 0, wx.ALL | wx.EXPAND, 0)
        self.camid_sel_wxid = wx.NewIdRef()
        self.camid_selector = wx.Choice(panel, name="id_sel", id=self.camid_sel_wxid)
        panel_sizer.Add(self.camid_selector, 1, wx.ALL | wx.EXPAND, 10)

        # Camera menu nav buttons
        panel_sizer.AddSpacer(5)
        menu_controls_text = wx.StaticText(panel, label="Menu Controls", style=wx.ALIGN_CENTER)
        panel_sizer.Add(menu_controls_text, 0, wx.ALL | wx.EXPAND, 0)
        panel_sizer.AddSpacer(5)
        button_grid = wx.GridSizer(3, 3, 10, 10)
        nav_up_button = wx.Button(panel, label="Up")
        nav_left_button = wx.Button(panel, label="Left")
        nav_right_button = wx.Button(panel, label="Right")
        nav_down_button = wx.Button(panel, label="Down")
        nav_enter_button = wx.Button(panel, label="Enter")
        empty_cell = (0, 0)
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

        # Direct Access buttons
        panel_sizer.AddSpacer(10)
        direct_controls_text = wx.StaticText(panel, label="Direct Controls", style=wx.ALIGN_CENTER)
        panel_sizer.Add(direct_controls_text, 0, wx.ALL | wx.EXPAND, 0)
        panel_sizer.AddSpacer(5)
        button_grid2 = wx.GridSizer(1, 3, 10, 10)
        b_w_button = wx.Button(panel, label="B/W")
        auto_button = wx.Button(panel, label="Auto")
        color_button = wx.Button(panel, label="Color")
        button_grid2.Add(b_w_button, flag=wx.ALIGN_CENTER_HORIZONTAL)
        button_grid2.Add(auto_button, flag=wx.ALIGN_CENTER_HORIZONTAL)
        button_grid2.Add(color_button, flag=wx.ALIGN_CENTER_HORIZONTAL)
        panel_sizer.Add(button_grid2, 0, wx.ALL | wx.EXPAND, 5)
        button_grid3 = wx.GridSizer(1, 2, 10, 10)
        brightness_down_button = wx.Button(panel, label="Brightness -")
        brightnes_up_button = wx.Button(panel, label="Brightness +")
        button_grid3.Add(brightness_down_button, flag=wx.ALIGN_CENTER_HORIZONTAL)
        button_grid3.Add(brightnes_up_button, flag=wx.ALIGN_CENTER_HORIZONTAL)
        panel_sizer.Add(button_grid3, 0, wx.ALL | wx.EXPAND, 5)
        button_grid4 = wx.GridSizer(1, 3, 10, 10)
        agc_down_button = wx.Button(panel, label="AGC -")
        agc_mid_button = wx.Button(panel, label="AGC Middle")
        agc_up_button = wx.Button(panel, label="AGC +")
        button_grid4.Add(agc_down_button, flag=wx.ALIGN_CENTER_HORIZONTAL)
        button_grid4.Add(agc_mid_button, flag=wx.ALIGN_CENTER_HORIZONTAL)
        button_grid4.Add(agc_up_button, flag=wx.ALIGN_CENTER_HORIZONTAL)
        panel_sizer.Add(button_grid4, 0, wx.ALL | wx.EXPAND, 5)

        panel.SetSizer(panel_sizer)

        # Accelerator entries to allow for Menu access from keystrokes
        id_nav_left = wx.ID_ANY
        id_nav_right = wx.ID_ANY
        id_nav_up = wx.ID_ANY
        id_nav_down = wx.ID_ANY
        id_nav_enter = wx.ID_ANY

        entries = [wx.AcceleratorEntry() for i in range(5)]
        entries[0].Set(wx.ACCEL_NORMAL, wx.WXK_LEFT, id_nav_left)
        entries[1].Set(wx.ACCEL_NORMAL, wx.WXK_RIGHT, id_nav_right)
        entries[2].Set(wx.ACCEL_NORMAL, wx.WXK_UP, id_nav_up)
        entries[3].Set(wx.ACCEL_NORMAL, wx.WXK_DOWN, id_nav_down)
        entries[4].Set(wx.ACCEL_NORMAL, wx.WXK_RETURN, id_nav_enter)
        accel = wx.AcceleratorTable(entries)
        self.SetAcceleratorTable(accel)

        # Event Bindings for Accelerator Table
        self.Bind(wx.EVT_MENU, button_functions.press_left, id=id_nav_left)
        self.Bind(wx.EVT_MENU, button_functions.press_right, id=id_nav_right)
        self.Bind(wx.EVT_MENU, button_functions.press_up, id=id_nav_up)
        self.Bind(wx.EVT_MENU, button_functions.press_down, id=id_nav_down)
        self.Bind(wx.EVT_MENU, button_functions.press_enter, id=id_nav_enter)

        # Menubar
        filemenu = wx.Menu()
        m_about = filemenu.Append(wx.ID_ABOUT, "&About", "Info about this program")
        filemenu.AppendSeparator()
        m_exit = filemenu.Append(wx.ID_EXIT, "&Exit\tAlt-X", "Close window and exit program.")
        properties_menuitem = filemenu.Append(wx.ID_PROPERTIES, "Properties", "Program Settings")
        menubar = wx.MenuBar()
        menubar.Append(filemenu, "&File")
        self.SetMenuBar(menubar)

        # General UI Event Bindings
        self.Bind(wx.EVT_CLOSE, self.quit_app)
        self.Bind(wx.EVT_MENU, self.quit_app, m_exit)
        self.Bind(wx.EVT_MENU, self.on_about, m_about)
        self.Bind(wx.EVT_MENU, self.launch_prefs, properties_menuitem)
        self.Bind(wx.EVT_BUTTON, self.on_clicked)
        self.Bind(wx.EVT_CHOICE, self.update_interfaces)
        # Pull baud rates in from constants.py to populate the baud dropdown
        self.add_bauds_to_choice()
        # Subscribe to info about available serial ports to populate interface dropdown
        pub.subscribe(self.add_ports_to_choice, "AvailablePorts")
        pub.subscribe(self.add_cams_to_choice, "AvailableCams")
        pub.subscribe(self.update_cam_select_from_osc, "OSCCamSelect")
        # Query the system for possible serial ports
        serial_functions.serial_ports()
        config_functions.cam_labels()
        self.osc_functions.start_threads()

        # Preset the dropdowns to the last used choices:
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

    def launch_prefs(self, event):
        # Open the preferences frame
        PrefsWindow(parent=wx.GetTopLevelParent(self), title="Webgate Cam Control Properties")

    def quit_app(self, event):
        # Grab the current size and position of the app
        # and update the config file.
        cur_size = self.GetTopLevelParent().GetSize()
        cur_pos = self.GetTopLevelParent().GetPosition()
        ini_path = config_functions.where_to_put_user_data()
        config_functions.update_pos_in_config(cur_pos, ini_path)
        config_functions.update_size_in_config(cur_size, ini_path)
        serial_functions.persistent_serial_connection.close_serial()
        closed_complete = self.GetTopLevelParent().osc_functions.close_servers()
        if closed_complete:
            try:
                self.GetTopLevelParent().Destroy()
            except Exception as e:
                print(e)

    def add_ports_to_choice(self, choices):
        # Receiving the available ports list and adding it to the dropdown
        self.serial_selector.Clear()
        self.serial_selector.Append("\n")
        for x in choices:
            self.serial_selector.Append(x, "ports")
        self.serial_choices = [""] + choices

    def add_cams_to_choice(self, choices):
        # Receiving the Cam ID list and adding it to the dropdown
        self.camid_selector.Clear()
        self.camid_selector.Append("\n")
        for x in choices:
            self.camid_selector.Append(x, "ports")
        self.camid_choices = [""] + choices

    def add_bauds_to_choice(self):
        # Receiving the possible Baud rates and adding it to the dropdown
        self.baud_selector.Clear()
        self.baud_selector.Append("\n")
        for x in constants.BAUD_RATES:
            self.baud_selector.Append(x, "bauds")
        self.baud_choices = [""] + constants.BAUD_RATES

    @staticmethod
    def on_clicked(event):
        # Handlers for the button presses in the UI
        btn = event.GetEventObject().GetLabel()
        if btn == "Left":
            button_functions.press_left()
        elif btn == "Right":
            button_functions.press_right()
        elif btn == "Up":
            button_functions.press_up()
        elif btn == "Down":
            button_functions.press_down()
        elif btn == "Enter":
            button_functions.press_enter()
        elif btn == "B/W":
            button_functions.press_bw()
        elif btn == "Auto":
            button_functions.press_auto()
        elif btn == "Color":
            button_functions.press_color()
        elif btn == "Brightness -":
            button_functions.press_brightness_down()
        elif btn == "Brightness +":
            button_functions.press_brightness_up()
        elif btn == "AGC -":
            button_functions.press_agc_down()
        elif btn == "AGC Middle":
            button_functions.press_agc_mid()
        elif btn == "AGC +":
            button_functions.press_agc_up()
        else:
            print("Msg not recognized")

    def update_cam_select_from_osc(self, new_sel_cam):
        #
        if new_sel_cam in self.camid_choices:
            wx.CallAfter(self.camid_selector.SetSelection, self.camid_choices.index(settings.last_camID))


    def update_interfaces(self, event):
        # When any dropdown is changed, this def is called to deal with the change
        incoming_choice_id = event.GetId()
        if incoming_choice_id == self.serial_sel_wxid.GetId():
            chosen_port = self.serial_choices[event.Selection]
            config_functions.update_last_interface_in_config(chosen_port,
                                                             config_functions.where_to_put_user_data())
            config_functions.set_vars_from_pref(config_functions.where_to_put_user_data())
            # Interface config has changed so reopen the serial port
            pub.sendMessage('chosenPort', port_to_open=chosen_port)
        elif incoming_choice_id == self.baud_sel_wxid.GetId():
            baud_rate = self.baud_choices[event.Selection]
            config_functions.update_last_baud_in_config(baud_rate,
                                                        config_functions.where_to_put_user_data())
            config_functions.set_vars_from_pref(config_functions.where_to_put_user_data())
            # Interface config has changed so reopen the serial port
            pub.sendMessage('chosenBaud', baud_to_open=baud_rate)
        elif incoming_choice_id == self.camid_sel_wxid.GetId():
            cam_id = self.camid_choices[event.Selection]
            config_functions.update_last_cam_in_config(cam_id,
                                                       config_functions.where_to_put_user_data())
            config_functions.set_vars_from_pref(config_functions.where_to_put_user_data())


class EditableListCtrl(wx.ListCtrl, listmix.TextEditMixin, listmix.ListCtrlAutoWidthMixin):
    # TextEditMixin allows any column to be edited.
    def __init__(self, parent, wxid=wx.ID_ANY, pos=wx.DefaultPosition,
                 size=wx.DefaultSize, style=0):
        # Constructor
        wx.ListCtrl.__init__(self, parent, wxid, pos, size, style)
        # Initialize mixin ability to edit in all fields
        listmix.TextEditMixin.__init__(self)
        # Initialize mixin ability to automatically set width
        listmix.ListCtrlAutoWidthMixin.__init__(self)
        self.Bind(wx.EVT_LIST_BEGIN_LABEL_EDIT, self.on_begin_label_edit)

    @staticmethod
    def on_begin_label_edit(event):
        # Veto all edits occuring in the first column
        if event.GetColumn() == 0:
            event.Veto()
        else:
            event.Skip()


class PrefsWindow(wx.Frame):
    # This is our preferences window pane
    def __init__(self, title, parent):
        wx.Frame.__init__(self, parent=parent, size=(400, 600), title=title)
        panel = PrefsPanel(parent=wx.GetTopLevelParent(self))
        self.Fit()
        self.Show()


class PrefsPanel(wx.Panel):
    def __init__(self, parent):
        self.ip_inspected = False
        wx.Panel.__init__(self, parent)
        panel_sizer = wx.BoxSizer(wx.VERTICAL)
        # UI for Camera Labeling
        cam_label_text = wx.StaticText(self, label="Cam Labels", style=wx.ALIGN_CENTER)
        panel_sizer.Add(cam_label_text, 0, wx.ALL | wx.EXPAND, 5)
        self.cam_label_list = EditableListCtrl(self, size=(-1, 150), style=wx.LC_REPORT | wx.BORDER_SUNKEN)
        self.cam_label_list.InsertColumn(0, "Cam ID", width=50, format=wx.LIST_FORMAT_CENTRE)
        self.cam_label_list.InsertColumn(1, "Name", width=175, format=wx.LIST_FORMAT_CENTRE)
        panel_sizer.Add(self.cam_label_list, 1, wx.ALL | wx.EXPAND, 5)
        panel_sizer.AddSpacer(15)
        # UI for Remote OSC IP
        remote_ip_text = wx.StaticText(self, label="Remote IP", style=wx.ALIGN_CENTER)
        panel_sizer.Add(remote_ip_text, 0, wx.ALL | wx.EXPAND, 5)
        # Remote IP Input
        self.remote_ip_control = wx.TextCtrl(self, style=wx.TE_CENTER)
        self.remote_ip_control.SetMaxLength(15)
        self.remote_ip_control.SetValue(settings.remote_ip)
        panel_sizer.Add(self.remote_ip_control, 0, wx.ALL | wx.EXPAND, 5)
        panel_sizer.Add(0, 10)

        # Ports Preference Selectors
        ports_grid = wx.GridSizer(2, 2, -1, 10)
        send_port_text = wx.StaticText(self, label="Send to Device", style=wx.ALIGN_CENTER)
        ports_grid.Add(send_port_text, 0, wx.ALL | wx.EXPAND, 5)
        rcv_port_text = wx.StaticText(self, label="Receive from Device", style=wx.ALIGN_CENTER)
        ports_grid.Add(rcv_port_text, 0, wx.ALL | wx.EXPAND, 5)
        self.send_port_control = wx.TextCtrl(self, style=wx.TE_CENTER)
        self.send_port_control.SetMaxLength(5)
        self.send_port_control.SetValue(str(settings.send_port))
        ports_grid.Add(self.send_port_control, 0, wx.ALL | wx.EXPAND, -1)
        self.rcv_port_control = wx.TextCtrl(self, style=wx.TE_CENTER)
        self.rcv_port_control.SetMaxLength(5)
        self.rcv_port_control.SetValue(str(settings.receive_port))
        ports_grid.Add(self.rcv_port_control, 0, wx.ALL | wx.EXPAND, -1)
        panel_sizer.Add(ports_grid, 0, wx.ALL | wx.EXPAND, 5)
        # Update Preferences button
        update_prefs_button = wx.Button(self, label="Update Preferences")
        panel_sizer.Add(update_prefs_button, 0, wx.ALL | wx.EXPAND, 5)

        self.name_index = 0
        self.populate_camid_prefs_list()
        self.SetSizer(panel_sizer)
        self.Bind(wx.EVT_LIST_END_LABEL_EDIT, self.on_cam_names_update)
        self.Bind(wx.EVT_BUTTON, self.push_prefs_update)
        self.remote_ip_control.Bind(wx.EVT_TEXT, self.changed_remote_ip)
        self.remote_ip_control.Bind(wx.EVT_KILL_FOCUS, self.check_ip)

        self.Fit()
        self.Show()

    def populate_camid_prefs_list(self):
        for x in settings.camID_names:
            item_split = x.split(":")
            wx.CallAfter(self.cam_label_list.InsertItem, self.name_index, item_split[0])
            wx.CallAfter(self.cam_label_list.SetItem, self.name_index, 1, item_split[1])
            self.name_index += 1

    def on_cam_names_update(self, event):
        row_id = event.GetIndex()  # Get the current row
        col_id = event.GetColumn()  # Get the current column
        new_data = event.GetLabel()  # Get the changed data
        # Set the new data in the listctrl
        self.cam_label_list.SetItem(row_id, col_id, new_data)

    def changed_remote_ip(self, e):
        # Flag to know if the console IP has been modified in the prefs window
        self.ip_inspected = False

    def check_ip(self, e):
        # Validates input into the console IP address field
        # Use the ip_address function from the ipaddress module to check if the input is a valid IP address
        ip = self.remote_ip_control.GetValue()

        if not self.ip_inspected:
            self.ip_inspected = True
            try:
                ipaddress.ip_address(ip)
            except ValueError:
                # If the input is not a valid IP address, catch the exception and show a dialog
                dlg = wx.MessageDialog(self, "This is not a valid IP address for the remote. Please try again",
                                       "Webgate Cam Control", wx.OK)
                dlg.ShowModal()  # Shows it
                dlg.Destroy()  # Destroy pop-up when finished.
                # Put the focus back on the bad field
                wx.CallAfter(self.remote_ip_control.SetFocus)

    def push_prefs_update(self, event):
        btn = event.GetEventObject().GetLabel()
        if btn == "Update Preferences":
            cols = self.cam_label_list.GetColumnCount()  # Get the total number of columns
            rows = self.cam_label_list.GetItemCount()  # Get the total number of rows
            # Create a list of the new camera names
            new_cam_names = []
            for row in range(rows):
                row_data = (":".join([self.cam_label_list.GetItem(row, col).GetText() for col in range(cols)]))
                new_cam_names.append(row_data)
            config_functions.update_cam_names_in_config(new_cam_names, config_functions.where_to_put_user_data())
            config_functions.update_ip_in_config(self.remote_ip_control.GetValue(),
                                                 self.send_port_control.GetValue(),
                                                 self.rcv_port_control.GetValue(),
                                                 config_functions.where_to_put_user_data())
            config_functions.set_vars_from_pref(config_functions.where_to_put_user_data())
            pub.sendMessage("AvailableCams", choices=new_cam_names)
            WebgateCamControlGUI.osc_functions.close_servers()
            WebgateCamControlGUI.osc_functions.restart_servers()

            self.Parent.Destroy()


if __name__ == "__main__":
    app = wx.App()
    frame = WebgateCamControlGUI()
    app.MainLoop()
