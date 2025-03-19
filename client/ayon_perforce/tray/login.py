"""Module for Perforce login tray functionality."""

import os

from qtpy import QtWidgets

# from ayon_shotgrid.lib import credentials
from ayon_perforce.tray.login_dialog import PerforceLoginDialog


class PerforceLoginTray:
    """Shotgrid menu entry for the AYON tray.

    Displays the Shotgrid URL specified in the Server Addon Settings and
    allows the person to set a username to be used with the API.

    There's the option to check if said user has permissions to connect to the
    API.
    """

    def __init__(self, addon):
        self.addon = addon

        server_url = self.addon.get_server_url()
        if not server_url:
            server_url = "No Perforce Server set in AYON Settings."

        self.p4_host_action = QtWidgets.QAction(f"Server: {server_url}")
        self.p4_host_action.setDisabled(True)
        self.p4_username_action = QtWidgets.QAction("")
        self.p4_username_action.triggered.connect(self.show_p4_username_dialog)

        self.p4_username_dialog = PerforceLoginDialog(self.addon)
        self.p4_username_dialog.dialog_closed.connect(self.set_username_label)

    def show_p4_username_dialog(self) -> None:
        """Display the Shotgrid Username dialog.

        Used to set a Shotgrid Username, that will then be used by any API call
        and to check that the user can access the Shotgrid API.
        """
        self.p4_username_dialog.show()
        self.p4_username_dialog.activateWindow()
        self.p4_username_dialog.raise_()

    def tray_menu(self, tray_menu):
        """Add Shotgrid Submenu to AYON tray.

        A non-actionable action displays the Shotgrid URL and the other
        action allows the person to set and check their Shotgrid username.

        Args:
            tray_menu (QtWidgets.QMenu): The AYON Tray menu.
        """
        p4_tray_menu = QtWidgets.QMenu("Perforce", tray_menu)
        p4_tray_menu.addAction(self.p4_host_action)
        p4_tray_menu.addSeparator()
        p4_tray_menu.addAction(self.p4_username_action)
        tray_menu.addMenu(p4_tray_menu)

    def set_username_label(self) -> None:
        """Set the Username Label based on local login setting.

        Depending on the login credentiasl we want to display one message or
        another in the Shotgrid submenu action.
        """
        # sg_username, _ = credentials.get_local_login()  # TODO: use AYONSecureRegistry directly
        p4_username = None
        if p4_username:
            self.p4_username_action.setText(
                "Username: {} (Click to change)".format(p4_username)
            )
            os.environ["AYON_SG_USERNAME"] = p4_username
        else:
            self.p4_username_action.setText("Specify a Username...")
            os.environ["P4USER"] = ""
            self.show_p4_username_dialog()
