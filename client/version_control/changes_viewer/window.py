import os
import sys

from qtpy import QtWidgets, QtCore
import qtawesome

from ayon_core import style
from ayon_core.pipeline import registered_host
from ayon_core.tools.utils import PlaceholderLineEdit
from ayon_core.tools.utils.lib import (
    iter_model_rows,
    qt_app_context
)
from ayon_core.tools.utils.models import RecursiveSortFilterProxyModel
from .control import ChangesViewerController
from .model import (
    ChangesModel,
)
from .widgets import ChangesDetail


module = sys.modules[__name__]
module.window = None


class ChangesWindows(QtWidgets.QDialog):
    def __init__(self, controller=None, parent=None):
        super(ChangesWindows, self).__init__(parent=parent)
        self.setWindowTitle("Changes Viewer")
        self.setObjectName("ChangesViewer")
        if not parent:
            self.setWindowFlags(
                self.windowFlags() | QtCore.Qt.WindowStaysOnTopHint
            )

        self.resize(780, 430)

        if controller is None:
            controller = ChangesViewerController()

        # Trigger refresh on first called show
        self._first_show = True

        model = ChangesModel(controller=controller, parent=self)
        proxy = RecursiveSortFilterProxyModel()
        proxy.setSourceModel(model)
        proxy.setFilterCaseSensitivity(QtCore.Qt.CaseInsensitive)

        details_widget = ChangesDetail(proxy, self)
        details_widget.save_triggered.connect(self._on_sync_to)

        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(details_widget, stretch=1)
        self.setLayout(layout)

        self._controller = controller
        self._model = model
        self._proxy = proxy
        self._details_widget = details_widget

    def _on_refresh_clicked(self):
        self.refresh()

    def _on_sync_to(self):
        current_index = self._details_widget.selectionModel().currentIndex()
        if not current_index.isValid():
            return

        item_id = current_index.data(0)
        if item_id != self._details_widget.item_id():
            return

        # sync to X change list

    def refresh(self):
        self._model.refresh()

    def showEvent(self, *args, **kwargs):
        super(ChangesWindows, self).showEvent(*args, **kwargs)
        if self._first_show:
            self._first_show = False
            self.setStyleSheet(style.load_stylesheet())
            self.refresh()


def show(root=None, debug=False, parent=None):
    """Display Change Viewer GUI

    Arguments:
        debug (bool, optional): Run in debug-mode,
            defaults to False
        parent (QtCore.QObject, optional): When provided parent the interface
            to this QObject.

    """

    try:
        module.window.close()
        del module.window
    except (RuntimeError, AttributeError):
        pass

    with qt_app_context():
        window = ChangesWindows(parent)
        window.show()

        module.window = window

        # Pull window to the front.
        module.window.raise_()
        module.window.activateWindow()
