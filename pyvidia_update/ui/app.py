import wx

from pyvidia_update.ui.config import ConfigFrame


class PyvidiaApp(wx.App):
    def OnInit(self):
        frm = ConfigFrame(None, title="Pyvidia update check - Settings")
        frm.Show()

        self.SetTopWindow(frm)
        return True


if __name__ == "__main__":
    app = PyvidiaApp(0)
    app.MainLoop()
