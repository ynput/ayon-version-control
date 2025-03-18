"""Widgets for the changes viewer."""
from __future__ import annotations

from typing import TYPE_CHECKING

from ayon_core.tools.utils import TreeView
from ayon_core.tools.utils.delegates import PrettyTimeDelegate
from qtpy import QtCore, QtWidgets

from .model import CHANGE_ROLE, ChangesModel, CustomSortProxyModel

if TYPE_CHECKING:
    from ayon_perforce.changes_viewer.control import ChangesViewerController


class ChangesDetailWidget(QtWidgets.QWidget):
    """Table printing list of changes from Perforce."""
    sync_triggered = QtCore.Signal()

    def __init__(self, controller: ChangesViewerController,
                 parent: QtWidgets.QWidget = None):
        """Initialize ChangesDetailWidget."""
        super().__init__(parent)

        model = ChangesModel(controller=controller, parent=self)
        proxy = CustomSortProxyModel()
        proxy.setSourceModel(model)
        proxy.setFilterCaseSensitivity(QtCore.Qt.CaseInsensitive)

        changes_view = TreeView(self)
        changes_view.setSelectionMode(
            QtWidgets.QAbstractItemView.ExtendedSelection
        )
        changes_view.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        changes_view.setSortingEnabled(True)
        changes_view.setAlternatingRowColors(True)
        changes_view.setModel(proxy)
        changes_view.setIndentation(0)

        changes_view.setColumnWidth(0, 70)
        changes_view.setColumnWidth(1, 430)
        changes_view.setColumnWidth(2, 100)
        changes_view.setColumnWidth(3, 120)

        time_delegate = PrettyTimeDelegate()
        changes_view.setItemDelegateForColumn(3, time_delegate)

        message_label_widget = QtWidgets.QLabel(self)

        sync_btn = QtWidgets.QPushButton("Sync to", self)

        self._block_changes = False
        self._editable = False
        self._item_id = None

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(changes_view, 1)
        layout.addWidget(message_label_widget, 0,
                         QtCore.Qt.AlignLeft | QtCore.Qt.AlignBottom)
        layout.addWidget(sync_btn, 0, QtCore.Qt.AlignRight)

        sync_btn.clicked.connect(self._on_sync_clicked)

        self._model = model
        self._controller = controller
        self._changes_view = changes_view
        self.sync_btn = sync_btn
        self._thread: QtCore.QThread = None
        self._time_delegate = time_delegate
        self._message_label_widget = message_label_widget

    def reset(self) -> None:
        """Reset the widget."""
        self._model.refresh()

    def _on_sync_clicked(self) -> None:
        """Sync to selected change."""
        selection_model = self._changes_view.selectionModel()
        current_index = selection_model.currentIndex()
        if not current_index.isValid():
            return

        change_id = current_index.data(CHANGE_ROLE)

        self._message_label_widget.setText(f"Syncing to '{change_id}'...")

        self.sync_btn.setEnabled(False)
        thread = SyncThread(self._controller, change_id)
        thread.finished.connect(lambda: self._on_thread_finished(change_id))
        thread.start()

        self._thread = thread

    def _on_thread_finished(self, change_id: int) -> None:
        """Handle thread finished event."""
        self._message_label_widget.setText(
            f"Synced to '{change_id}'. "
            "Please close Viewer to continue."
        )
        self.sync_btn.setEnabled(True)


class SyncThread(QtCore.QThread):
    """Thread for syncing to a specific change."""

    def __init__(
            self, controller: ChangesViewerController, change_id: int):
        """Initialize SyncThread."""
        super().__init__()
        self._controller = controller
        self._change_id = change_id

    def run(self) -> None:
        """Run SyncThread."""
        self._controller.sync_to(self._change_id)
