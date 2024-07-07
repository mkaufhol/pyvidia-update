from enum import Enum

import wx
import wx.adv

from pyvidia_update.source.get_current_driver_version import get_current_driver_version
from pyvidia_update.ui.tray import PyvidiaTaskBarIcon
from pyvidia_update.source.get_data import DropdownData
from pyvidia_update.source.get_system_info import get_current_nvidia_driver_version


class DropDownHierarchy(Enum):
    PRODUCT_TYPE = 0
    PRODUCT_SERIES = 1
    PRODUCT = 2
    OS = 3
    DOWNLOAD_TYPE = 4
    LANGUAGE = 5


class ConfigFrame(wx.Frame):
    # Set the selected data keys here
    selected_product_type: str = None
    selected_product_series: str = None
    selected_product: str = None
    selected_os: str = None
    selected_dt: str = None
    selected_language: str = None

    dd = DropdownData(switch_kv=True)
    _dropdown_mapping = {
        DropDownHierarchy.PRODUCT_TYPE: {
            "data_func": dd.get_product_series_data,
            "dropdown_name": "product_series_dropdown",
            "next": {},
        }
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.SetSize((500, 500))
        screen_width = wx.GetDisplaySize()[0]
        screen_height = wx.GetDisplaySize()[1]

        x_pos = screen_width - self.GetSize()[0]
        y_pos = screen_height - self.GetSize()[1] - 50

        self.SetPosition((x_pos, y_pos))

        self.SetIcon(wx.Icon("./assets/pyvidia-logo.ico", wx.BITMAP_TYPE_ICO))
        self.tskic = PyvidiaTaskBarIcon(self)
        self.Bind(wx.EVT_CLOSE, self.on_close)

        panel = wx.Panel(self)

        # DROPDOWN FIELDS
        # ========================================================================================
        product_type_data = self.dd.get_product_type_data()
        self.product_type_dropdown_label = wx.StaticText(panel, label="Product Type")
        self.product_type_dropdown = wx.Choice(
            panel, choices=list(product_type_data.keys())
        )
        selected_product_type_index = 0
        self.product_type_dropdown.SetSelection(selected_product_type_index)
        self.selected_product_type = product_type_data[
            list(product_type_data.keys())[selected_product_type_index]
        ]
        self.product_type_dropdown.Bind(wx.EVT_CHOICE, self.on_product_type_change)

        # ---------------------------------------------------------------------------------------

        product_series_data = self.dd.get_product_series_data(
            self.selected_product_type
        )
        self.product_series_dropdown_label = wx.StaticText(
            panel, label="Product Series"
        )
        self.product_series_dropdown = wx.Choice(
            panel, choices=list(product_series_data.keys())
        )
        selected_product_series_index = 0
        self.product_series_dropdown.SetSelection(selected_product_series_index)
        self.selected_product_series = product_series_data[
            list(product_series_data.keys())[selected_product_series_index]
        ]
        self.product_series_dropdown.Bind(wx.EVT_CHOICE, self.on_product_series_change)

        # ---------------------------------------------------------------------------------------

        product_data = self.dd.get_product_data(
            self.selected_product_type, self.selected_product_series
        )
        self.product_dropdown_label = wx.StaticText(panel, label="Product")
        self.product_dropdown = wx.Choice(panel, choices=list(product_data.keys()))
        selected_product_index = 0
        self.product_dropdown.SetSelection(selected_product_index)
        self.selected_product = product_data[
            list(product_data.keys())[selected_product_index]
        ]
        self.product_dropdown.Bind(wx.EVT_CHOICE, self.on_product_change)

        # ---------------------------------------------------------------------------------------

        os_data = self.dd.get_os_data(
            self.selected_product_type,
            self.selected_product_series,
            self.selected_product,
        )
        self.os_dropdown_label = wx.StaticText(panel, label="Operating System")
        self.os_dropdown = wx.Choice(panel, choices=list(os_data.keys()))
        selected_os_index = 0
        self.os_dropdown.SetSelection(selected_os_index)
        self.selected_os = os_data[list(os_data.keys())[selected_os_index]]
        self.os_dropdown.Bind(wx.EVT_CHOICE, self.on_os_change)

        # ---------------------------------------------------------------------------------------

        dt_data = self.dd.get_dt_data(
            self.selected_product_type,
            self.selected_product_series,
            self.selected_product,
            self.selected_os,
        )
        self.dt_dropdown_label = wx.StaticText(panel, label="Download Type")
        self.dt_dropdown = wx.Choice(panel, choices=list(dt_data.keys()))
        selected_dt_index = 0
        self.dt_dropdown.SetSelection(selected_dt_index)
        self.selected_dt = dt_data[list(dt_data.keys())[selected_dt_index]]
        self.dt_dropdown.Bind(wx.EVT_CHOICE, self.on_dt_change)

        # ---------------------------------------------------------------------------------------

        lan_data = self.dd.get_language_data(
            self.selected_product_type,
            self.selected_product_series,
            self.selected_product,
            self.selected_os,
            self.selected_dt,
        )
        self.lan_dropdown_label = wx.StaticText(panel, label="Language")
        self.lan_dropdown = wx.Choice(panel, choices=list(lan_data.keys()))
        selected_lan_index = 0
        self.lan_dropdown.SetSelection(selected_lan_index)
        self.selected_language = lan_data[list(lan_data.keys())[selected_lan_index]]
        self.lan_dropdown.Bind(wx.EVT_CHOICE, self.on_lan_change)

        # ========================================================================================

        self.system_version = wx.StaticText(
            panel, label="System driver version not found!"
        )
        self.current_version = wx.StaticText(
            panel, label="Current driver version not found!"
        )
        self.current_version_date = wx.StaticText(
            panel, label="Current driver version not found!"
        )
        self.link = wx.adv.HyperlinkCtrl(panel, -1)
        self._set_download_link()

        # Panel Arrangement
        # ========================================================================================
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.product_type_dropdown_label, 0, wx.ALL | wx.EXPAND, 5)
        sizer.Add(self.product_type_dropdown, 0, wx.ALL | wx.EXPAND, 5)

        sizer.Add(self.product_series_dropdown_label, 0, wx.ALL | wx.EXPAND, 5)
        sizer.Add(self.product_series_dropdown, 0, wx.ALL | wx.EXPAND, 5)

        sizer.Add(self.product_dropdown_label, 0, wx.ALL | wx.EXPAND, 5)
        sizer.Add(self.product_dropdown, 0, wx.ALL | wx.EXPAND, 5)

        sizer.Add(self.os_dropdown_label, 0, wx.ALL | wx.EXPAND, 5)
        sizer.Add(self.os_dropdown, 0, wx.ALL | wx.EXPAND, 5)

        sizer.Add(self.dt_dropdown_label, 0, wx.ALL | wx.EXPAND, 5)
        sizer.Add(self.dt_dropdown, 0, wx.ALL | wx.EXPAND, 5)

        sizer.Add(self.lan_dropdown_label, 0, wx.ALL | wx.EXPAND, 5)
        sizer.Add(self.lan_dropdown, 0, wx.ALL | wx.EXPAND, 5)

        sizer.Add(self.system_version, 0, wx.ALL | wx.EXPAND, 5)
        sizer.Add(self.current_version, 0, wx.ALL | wx.EXPAND, 5)
        sizer.Add(self.current_version_date, 0, wx.ALL | wx.EXPAND, 5)
        sizer.Add(self.link, 0, wx.ALL | wx.EXPAND, 5)

        panel.SetSizer(sizer)

    def on_product_type_change(self, event):
        selected_option = self.product_type_dropdown.GetStringSelection()
        data = self.dd.get_product_type_data()

        if selected_option not in list(data.keys()):
            raise ValueError(
                f"Selected option {selected_option} is not in Product type data list."
            )
        self.selected_product_type = data[selected_option]
        self._fill_dropdowns(DropDownHierarchy.PRODUCT_TYPE)

    def on_product_series_change(self, event):
        selected_option = self.product_series_dropdown.GetStringSelection()
        data = self.dd.get_product_series_data(self.selected_product_type)

        if selected_option not in list(data.keys()):
            raise ValueError(
                f"Selected option {selected_option} is not in Product series data list."
            )
        self.selected_product_series = data[selected_option]
        self._fill_dropdowns(DropDownHierarchy.PRODUCT_SERIES)

    def on_product_change(self, event):
        selected_option = self.product_dropdown.GetStringSelection()
        data = self.dd.get_product_data(
            self.selected_product_type, self.selected_product_series
        )

        if selected_option not in list(data.keys()):
            raise ValueError(
                f"Selected option {selected_option} is not in Product data list"
            )
        self.selected_product = data[selected_option]
        self._fill_dropdowns(DropDownHierarchy.PRODUCT)

    def on_os_change(self, event):
        selected_option = self.os_dropdown.GetStringSelection()
        data = self.dd.get_os_data(
            self.selected_product_type,
            self.selected_product_series,
            self.selected_product,
        )

        if selected_option not in list(data.keys()):
            raise ValueError(
                f"Selected option {selected_option} is not in OS data list"
            )
        self.selected_os = data[selected_option]
        self._fill_dropdowns(DropDownHierarchy.OS)

    def on_dt_change(self, event):
        selected_option = self.dt_dropdown.GetStringSelection()
        data = self.dd.get_dt_data(
            self.selected_product_type,
            self.selected_product_series,
            self.selected_product,
            self.selected_os,
        )

        if selected_option not in list(data.keys()):
            raise ValueError(
                f"Selected option {selected_option} is not in Download Type data list"
            )
        self.selected_dt = data[selected_option]
        self._fill_dropdowns(DropDownHierarchy.DOWNLOAD_TYPE)

    def on_lan_change(self, event):
        selected_option = self.lan_dropdown.GetStringSelection()
        data = self.dd.get_language_data(
            self.selected_product_type,
            self.selected_product_series,
            self.selected_product,
            self.selected_os,
            self.selected_dt,
        )

        if selected_option not in list(data.keys()):
            raise ValueError(
                f"Selected option {selected_option} is not in Language data list"
            )
        self.selected_language = data[selected_option]

    def _fill_dropdowns(self, level: DropDownHierarchy):
        match level:
            case DropDownHierarchy.PRODUCT_TYPE:
                self._fill_product_series_dropdown()
            case DropDownHierarchy.PRODUCT_SERIES:
                self._fill_product_dropdown()
            case DropDownHierarchy.PRODUCT:
                self._fill_os_dropdown()
            case DropDownHierarchy.OS:
                self._fill_dt_dropdown()
            case DropDownHierarchy.DOWNLOAD_TYPE:
                self._fill_language_data()

    def _fill_product_series_dropdown(self):
        self.product_series_dropdown.Clear()
        product_series_data = self.dd.get_product_series_data(
            self.selected_product_type
        )
        for option in list(product_series_data.keys()):
            self.product_series_dropdown.Append(option)
        selected_product_series_index = 0
        self.product_series_dropdown.SetSelection(selected_product_series_index)
        self.selected_product_series = product_series_data[
            list(product_series_data.keys())[selected_product_series_index]
        ]
        self._fill_product_dropdown()
        self._fill_os_dropdown()

    def _fill_product_dropdown(self):
        self.product_dropdown.Clear()
        product_data = self.dd.get_product_data(
            self.selected_product_type, self.selected_product_series
        )
        for option in list(product_data.keys()):
            self.product_dropdown.Append(option)
        selected_product_index = 0
        self.product_dropdown.SetSelection(selected_product_index)
        self.selected_product = product_data[
            list(product_data.keys())[selected_product_index]
        ]
        self._fill_os_dropdown()

    def _fill_os_dropdown(self):
        self.os_dropdown.Clear()
        os_data = self.dd.get_os_data(
            self.selected_product_type,
            self.selected_product_series,
            self.selected_product,
        )
        for option in list(os_data.keys()):
            self.os_dropdown.Append(option)
        selected_os_index = 0
        self.os_dropdown.SetSelection(selected_os_index)
        self.selected_os = os_data[list(os_data.keys())[selected_os_index]]
        self._fill_dt_dropdown()

    def _fill_dt_dropdown(self):
        self.dt_dropdown.Clear()
        dt_data = self.dd.get_dt_data(
            self.selected_product_type,
            self.selected_product_series,
            self.selected_product,
            self.selected_os,
        )
        for option in list(dt_data.keys()):
            self.dt_dropdown.Append(option)
        selected_dt_index = 0
        self.dt_dropdown.SetSelection(selected_dt_index)
        self.selected_dt = dt_data[list(dt_data.keys())[selected_dt_index]]
        self._fill_language_data()

    def _fill_language_data(self):
        self.lan_dropdown.Clear()
        lan_data = self.dd.get_language_data(
            self.selected_product_type,
            self.selected_product_series,
            self.selected_product,
            self.selected_os,
            self.selected_dt,
        )
        for option in list(lan_data.keys()):
            self.lan_dropdown.Append(option)
        selected_lan_index = 0
        self.lan_dropdown.SetSelection(selected_lan_index)
        self.selected_language = lan_data[list(lan_data.keys())[selected_lan_index]]
        self._set_download_link()

    def _set_download_link(self):
        dl_link = self.dd.get_download_link(
            self.selected_product_type,
            self.selected_product_series,
            self.selected_product,
            self.selected_os,
            self.selected_dt,
            self.selected_language,
        )
        self.system_version.SetLabel(
            f"Installed version: {get_current_nvidia_driver_version()}"
        )
        if dl_link == "not_found":
            self.link.SetURL("https://www.nvidia.com/Download/index.aspx")
            self.link.SetLabel("No Download Link found, find on nvidia.com")
            self.current_version.Show(False)
            self.current_version_date.Show(False)
        else:
            self.link.SetURL(dl_link)
            self.link.SetLabel("Download Link")
            current_version = get_current_driver_version(dl_link)
            self.current_version.Show(True)
            self.current_version.SetLabel(f"Current version: {current_version.version}")
            self.current_version_date.Show(True)
            self.current_version_date.SetLabel(
                f"Release Date: {current_version.release_date}"
            )

    def on_close(self, event):
        msg_title = "Notification"
        msg_text = "Hello, World!"
        nmsg = wx.adv.NotificationMessage(title=msg_title, message=msg_text)
        nmsg.SetFlags(wx.ICON_INFORMATION)
        # nmsg.AddAction(Act_Id_1, "Cancel")
        # nmsg.AddAction(Act_Id_2, "Hold")
        nmsg.Show(timeout=5)
        self.Hide()
