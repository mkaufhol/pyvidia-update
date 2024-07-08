import logging
import threading
import time
import datetime as dt

import wx

from pyvidia_update.source.get_current_driver_version import get_current_driver_version
from pyvidia_update.source.get_system_info import get_current_nvidia_driver_version
from pyvidia_update.ui.config import ConfigFrame
from pyvidia_update.ui.notifications import notify_new_update

logger = logging.getLogger(__name__)


class PyvidiaApp(wx.App):
    def OnInit(self):
        thread = threading.Thread(target=self.autocheck_for_updates)
        thread.daemon = True
        thread.start()

        self.frm = ConfigFrame(None, title="Pyvidia update check - Settings")
        self.frm.Show()

        self.SetTopWindow(self.frm)
        return True

    def autocheck_for_updates(self):
        start_time = dt.datetime.now()
        cycle_time = dt.datetime.now()
        notification_sent = False

        while True:
            time.sleep(60 * 60)

            # Check every Hour
            if (dt.datetime.now() - cycle_time).total_seconds() < 60 * 60:
                continue

            logger.info("Checking for update")
            current_system_version = get_current_nvidia_driver_version()
            current_version = get_current_driver_version(self.frm.dl_link)
            if current_system_version == current_version.version:
                cycle_time = dt.datetime.now()
                continue
            if notification_sent is not True:
                notify_new_update(
                    current_system_version,
                    current_version.version,
                    current_version.release_date,
                )
                logger.info("Disable Notification")
                notification_sent = True

            # Enable Notification after 6 hours
            if (dt.datetime.now() - start_time).total_seconds() > 60 * 60 * 6:
                logger.info("Enable Notification")
                notification_sent = False

    def show_frame(self):
        if not self.frm.IsShown():
            self.frm.Show()
        self.frm.Raise()


if __name__ == "__main__":
    app = PyvidiaApp(0)
    app.SetAppName("Pyvidia Update")
    app.MainLoop()
