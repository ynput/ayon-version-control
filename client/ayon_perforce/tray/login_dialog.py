from qtpy import QtCore, QtWidgets, QtGui

from ayon_core import style
from ayon_core import resources
from ayon_core.addon import AYONAddon

from ayon_perforce import lib as p4lib


class PerforceLoginDialog(QtWidgets.QDialog):
    """A QDialog that allows the person to set a Shotgrid Username.

    It also allows them to test the username against the API.
    """

    dialog_closed = QtCore.Signal()

    def __init__(
        self,
        addon: AYONAddon,
        parent: QtWidgets.QWidget = None,
    ) -> None:
        """Initialize the PerforceLoginDialog."""
        super().__init__(parent)
        self.addon = addon

        self.setWindowTitle("AYON - Perforce Login")
        icon = QtGui.QIcon(resources.get_ayon_icon_filepath())
        self.setWindowIcon(icon)

        self.setWindowFlags(
            QtCore.Qt.WindowCloseButtonHint
            | QtCore.Qt.WindowMinimizeButtonHint
        )

        self.setStyleSheet(style.load_stylesheet())
        self.setContentsMargins(2, 2, 2, 2)

        self.setup_ui()

    def closeEvent(self, event: QtCore.QEvent) -> None:
        """Clear any message when closing the dialog."""
        self.connection_message.setText("")
        self.dialog_closed.emit()
        super().closeEvent(event)

    def setup_ui(self) -> None:
        """Setup the UI for the dialog.

        # TODO: save server url to $P4PORT
        """
        server_url = self.addon.get_server_url()

        if not server_url:
            server_url = "No Perforce Server set in AYON Settings."

        server_url_label = QtWidgets.QLabel(
            "Please provide the credentials to log in into the "
            f"Perforce Server:\n{server_url}"
        )

        dialog_layout = QtWidgets.QVBoxLayout()
        dialog_layout.addWidget(server_url_label)

        username, password = p4lib.get_local_login()

        self.username_input = QtWidgets.QLineEdit()

        if username:
            self.username_input.setText(username)
        else:
            self.username_input.setPlaceholderText("jane.doe@mycompany.com")
        self.password_input = QtWidgets.QLineEdit()
        self.password_input.setEchoMode(QtWidgets.QLineEdit.Password)

        if password:
            self.password_input.setText(password)
        else:
            self.password_input.setPlaceholderText("password1234")

        dialog_layout.addWidget(QtWidgets.QLabel("Perforce Username:"))
        dialog_layout.addWidget(self.username_input)

        dialog_layout.addWidget(QtWidgets.QLabel("Perforce Password:"))
        dialog_layout.addWidget(self.password_input)

        self.check_login_button = QtWidgets.QPushButton(
            "Login into Perforce..."
        )
        self.check_login_button.clicked.connect(self.set_local_login)
        self.connection_message = QtWidgets.QLabel("")

        dialog_layout.addWidget(self.check_login_button)
        dialog_layout.addWidget(self.connection_message)

        self.setLayout(dialog_layout)

    def set_local_login(self) -> None:
        """Change Username label, save in local registry and set env var.

        # TODO: raise if user can't be logged in
        """
        username = self.username_input.text()
        password = self.password_input.text()

        if username and password:
            p4lib.save_local_login(username, password)
        else:
            p4lib.clear_local_login()
        self.close()
