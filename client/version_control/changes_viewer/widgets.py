import json
from qtpy import QtWidgets, QtCore

from ayon_core.tools.utils import TreeView


class ChangesDetail(QtWidgets.QWidget):
    """Table printing list of changes from Perforce"""
    save_triggered = QtCore.Signal()

    def __init__(self, model, parent=None):
        super(ChangesDetail, self).__init__(parent)

        changes_view = TreeView(self)
        changes_view.setSelectionMode(
            QtWidgets.QAbstractItemView.ExtendedSelection
        )
        changes_view.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        changes_view.setSortingEnabled(True)
        changes_view.setAlternatingRowColors(True)
        changes_view.setModel(model)

        sync_btn = QtWidgets.QPushButton("Sync to", self)

        self._block_changes = False
        self._editable = False
        self._item_id = None

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(changes_view, 1)
        layout.addWidget(sync_btn, 0, QtCore.Qt.AlignRight)

        sync_btn.clicked.connect(self._on_sync_clicked)
        # changes_view.textChanged.connect(self._on_text_change)

        self._changes_view = changes_view
        self.sync_btn = sync_btn

    def _on_sync_clicked(self):
        if self.is_valid():
            self.save_triggered.emit()

    def item_id(self):
        return self._item_id

    def is_valid(self):
        if not self._item_id:
            return True

        value = self._details_widget.toPlainText()
        valid = False
        try:
            jsoned = json.loads(value)
            if jsoned and isinstance(jsoned, dict):
                valid = True

        except Exception:
            pass
        return valid

    def _on_text_change(self):
        if self._block_changes or not self._item_id:
            return

        valid = self.is_valid()
        self.update_state(valid)
