from qtpy import QtCore, QtGui
from datetime import datetime

CHANGE_ROLE = QtCore.Qt.UserRole + 1
DESC_ROLE = QtCore.Qt.UserRole + 2
AUTHOR_ROLE = QtCore.Qt.UserRole + 3
CREATED_ROLE = QtCore.Qt.UserRole + 4


class ChangesModel(QtGui.QStandardItemModel):
    column_labels = [
        "Change",
        "Description",
        "Author",
        "Date submitted",
    ]

    def __init__(self, controller, *args, **kwargs):
        super(ChangesModel, self).__init__(*args, **kwargs)
        self._changes_by_item_id = {}

        controller.login()

        self._controller = controller

        self.setColumnCount(len(self.column_labels))
        for idx, label in enumerate(self.column_labels):
            self.setHeaderData(idx, QtCore.Qt.Horizontal, label)

    def refresh(self):
        self.removeRows(0, self.rowCount())  # Clear existing data
        changes = self._controller.get_changes()

        for change in changes:
            date_time = datetime.fromtimestamp(int(change["time"]))
            date_string = date_time.strftime("%Y%m%dT%H%M%SZ")

            number_item = QtGui.QStandardItem(change["change"])
            number_item.setData(int(change["change"]), CHANGE_ROLE)  # Store number for sorting
            desc_item = QtGui.QStandardItem(change["desc"])
            author_item = QtGui.QStandardItem(change["user"])
            date_item = QtGui.QStandardItem(date_string)
            self.appendRow([number_item, desc_item, author_item, date_item])

    def data(self, index, role=QtGui.Qt.DisplayRole):
        if role == CHANGE_ROLE:
            # Return actual data stored for sorting
            return index.model().item(index.row(), 0).data(CHANGE_ROLE)
        return super().data(index, role)

    def get_change_by_id(self, item_id):
        return self._changes_by_item_id.get(item_id)


class CustomSortProxyModel(QtCore.QSortFilterProxyModel):
    def lessThan(self, source_left, source_right):
        first_column = 0

        # Use different sort roles for the first column and others
        SORT_ROLE = QtGui.Qt.DisplayRole
        if source_left.column() == first_column:
            SORT_ROLE = CHANGE_ROLE

        left_data = self.sourceModel().data(source_left, SORT_ROLE)
        right_data = self.sourceModel().data(source_right, SORT_ROLE)

        return left_data < right_data
