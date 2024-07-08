import wx
import wx.adv


def notify_running_in_background():
    msg_title = "Still running"
    msg_text = (
        "Pyvidia is still availible in the system tray."
        "\nIt will check sporadically for new updated and notify you if "
        "a new driver version is availible"
    )
    nmsg = wx.adv.NotificationMessage(title=msg_title, message=msg_text)
    nmsg.SetFlags(wx.ICON_INFORMATION)
    nmsg.Show(timeout=1)


def notify_new_update(sys_version: str, version: str, release_date: str):
    msg_title = "New driver updates available"
    msg_text = (
        f"You version: {sys_version} -> New version: {version}\n\n"
        f"Release Date: {release_date}"
    )
    nmsg = wx.adv.NotificationMessage(title=msg_title, message=msg_text)
    nmsg.SetFlags(wx.ICON_INFORMATION)
    nmsg.Show(timeout=1)
