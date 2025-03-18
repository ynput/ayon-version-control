"""Changes Viewer Window."""

from __future__ import annotations

import contextlib
import sys
from typing import TYPE_CHECKING, Optional

from ayon_core import style
from ayon_core.tools.utils.lib import qt_app_context
from qtpy import QtCore, QtWidgets

from .control import ChangesViewerController
from .widgets import ChangesDetailWidget

if TYPE_CHECKING:
    from ayon_perforce.addon import LaunchData


module = sys.modules[__name__]
module.window = None


class ChangesWindows(QtWidgets.QDialog):
    """Changes Viewer Window."""
    def __init__(
            self,
            controller: Optional[ChangesViewerController] = None,
            parent: Optional[QtWidgets.QtWidget] = None,
            launch_data: Optional[LaunchData] = None):
        """Initialize ChangesWindows."""
        super().__init__(parent=parent)
        self.setWindowTitle("Changes Viewer")
        self.setObjectName("ChangesViewer")
        if not parent:
            self.setWindowFlags(
                self.windowFlags() | QtCore.Qt.WindowStaysOnTopHint
            )

        self.resize(780, 430)

        if controller is None:
            controller = ChangesViewerController(launch_data=launch_data)

        self._first_show = True

        details_widget = ChangesDetailWidget(controller, self)

        layout = QtWidgets.QHBoxLayout(self)
        layout.addWidget(details_widget, stretch=1)

        self._controller = controller
        self._details_widget = details_widget

    def showEvent(self, *args, **kwargs) -> None:  # noqa: N802, ANN002, ANN003
        """Show event."""
        super().showEvent(*args, **kwargs)
        if self._first_show:
            self._first_show = False
            self.setStyleSheet(style.load_stylesheet())
            self._details_widget.reset()


def show(parent: Optional[QtWidgets.QtWidget] = None) -> None:
    """Display Change Viewer GUI.

    Args:
        parent (QtWidgets.QtWidget, optional): When provided parent
            the interface to this QObject.

    """
    with contextlib.suppress(RuntimeError, AttributeError):
        module.window.close()
        del module.window
    with qt_app_context():
        window = ChangesWindows(parent)
        window.show()

        module.window = window

        # Pull window to the front.
        module.window.raise_()
        module.window.activateWindow()
