import wx
from wx.adv import TaskBarIcon

from pyvidia_update.source.get_files import get_packaged_files_path
from pyvidia_update.ui.notifications import notify_running_in_background

get_packaged_files_path = get_packaged_files_path()


class PyvidiaTaskBarIcon(TaskBarIcon):
    def __init__(self, frame: wx.Frame):
        super().__init__()

        self.frame: wx.Frame = frame

        self.SetIcon(
            wx.Icon(
                f"{get_packaged_files_path}/assets/pyvidia-logo.ico", wx.BITMAP_TYPE_ICO
            ),
            "Pyvidia Updater",
        )

        self.Bind(wx.EVT_MENU, self.on_task_bar_activate, id=1)
        self.Bind(wx.EVT_MENU, self.on_task_bar_deactivate, id=2)
        self.Bind(wx.EVT_MENU, self.on_task_bar_close, id=3)
        self.Bind(wx.adv.EVT_TASKBAR_LEFT_DCLICK, self.on_task_bar_activate)

    def CreatePopupMenu(self):
        menu = wx.Menu()
        menu.Append(1, "Show")
        menu.Append(2, "Hide")
        menu.Append(3, "Quit")

        return menu

    def on_task_bar_close(self, event):
        self.frame.Destroy()
        self.Destroy()

    def on_task_bar_activate(self, event):
        if not self.frame.IsShown():
            self.frame.Show()
        self.frame.Raise()

    def on_task_bar_deactivate(self, event):
        if self.frame.IsShown():
            self.frame.Hide()
            notify_running_in_background()
