"""Changes viewer model."""
from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any, ClassVar, Optional

from qtpy import QtCore, QtGui

if TYPE_CHECKING:
    from .control import ChangesViewerController


CHANGE_ROLE = QtCore.Qt.UserRole + 1
DESC_ROLE = QtCore.Qt.UserRole + 2
AUTHOR_ROLE = QtCore.Qt.UserRole + 3
CREATED_ROLE = QtCore.Qt.UserRole + 4
TZ_INFO = datetime.now().astimezone().tzinfo


class ChangesModel(QtGui.QStandardItemModel):
    """Model for the change viewer."""
    column_labels: ClassVar[list[str]] = [
        "Change",
        "Description",
        "Author",
        "Date submitted",
    ]
    _changes_by_item_id: dict

    def __init__(self, controller: ChangesViewerController, *args, **kwargs):
        """Initialize the model."""
        super().__init__(*args, **kwargs)
        self._changes_by_item_id = {}

        controller.login()

        self._controller = controller

        self.setColumnCount(len(self.column_labels))
        for idx, label in enumerate(self.column_labels):
            self.setHeaderData(idx, QtCore.Qt.Horizontal, label)

    def refresh(self) -> None:
        """Refresh the model."""
        self.removeRows(0, self.rowCount())  # Clear existing data
        changes = self._controller.get_changes()

        for change in changes:
            date_time = datetime.fromtimestamp(int(change["time"]), tz=TZ_INFO)
            date_string = date_time.strftime("%Y%m%dT%H%M%SZ")

            number_item = QtGui.QStandardItem(change["change"])
            # Store number for sorting
            number_item.setData(int(change["change"]), CHANGE_ROLE)
            desc_item = QtGui.QStandardItem(change["desc"])
            author_item = QtGui.QStandardItem(change["user"])
            date_item = QtGui.QStandardItem(date_string)
            self.appendRow([number_item, desc_item, author_item, date_item])

    def data(self, index: QtCore.QModelIndex,
             role: Optional[int] = QtGui.Qt.DisplayRole
    ) -> Any:  # noqa: ANN401
        """Return data for the index.

        Returns:
            Any: Data for the index.

        """
        if role == CHANGE_ROLE:
            # Return actual data stored for sorting
            return index.model().item(index.row(), 0).data(CHANGE_ROLE)
        return super().data(index, role)

    def get_change_by_id(self, item_id: int) -> dict:
        """Get change by id.

        Returns:
            dict: Change data.

        """
        return self._changes_by_item_id.get(item_id)


class CustomSortProxyModel(QtCore.QSortFilterProxyModel):
    """Custom sort proxy model."""

    def lessThan(  # noqa: N802
            self,
            source_left: QtCore.QModelIndex,
            source_right: QtCore.QModelIndex) -> bool:
        """Compare two items.

        Returns true if the value of the item referred to by the given
        index ``source_left`` is less than the value of the item referred to
        by the given index ``source_right``, otherwise returns False.

        This function is used as the < operator when sorting, and handles the
        ``QVariant`` types.

        Returns:
            bool: True if left item is less than right item, False otherwise.

        """
        first_column = 0

        # Use different sort roles for the first column and others
        sort_role = QtGui.Qt.DisplayRole
        if source_left.column() == first_column:
            sort_role = CHANGE_ROLE

        left_data = self.sourceModel().data(source_left, sort_role)
        right_data = self.sourceModel().data(source_right, sort_role)

        return left_data < right_data
