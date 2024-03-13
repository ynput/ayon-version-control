from qtpy import QtCore, QtGui

CHANGE_ROLE = QtCore.Qt.UserRole + 1
DESC_ROLE = QtCore.Qt.UserRole + 2
AUTHOR_ROLE = QtCore.Qt.UserRole + 3
CREATED_ROLE = QtCore.Qt.UserRole + 4


class ChangesModel(QtGui.QStandardItemModel):
    column_labels = [
        "Change number",
        "Description",
        "Author",
        "Date submitted",
    ]

    def __init__(self, controller, *args, parent=None, **kwargs):
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
        for i, change in enumerate(changes):
            number_item = QtGui.QStandardItem(change["change"])
            number_item.setData(int(change["change"]), CHANGE_ROLE)  # Store number for sorting
            # number_item.setData(change["user"], DESC_ROLE)  # Store number for sorting
            # number_item.setData(change["user"], AUTHOR_ROLE)  # Store number for sorting
            # number_item.setData(change["time"], CREATED_ROLE)  # Store number for sorting
            # self.appendRow(number_item)
            desc_item = QtGui.QStandardItem(change["desc"])
            author_item = QtGui.QStandardItem(change["user"])
            date_item = QtGui.QStandardItem(change["time"])
            self.appendRow([number_item, desc_item, author_item, date_item])

    def data(self, index, role=QtGui.Qt.DisplayRole):
        if role == QtGui.Qt.DisplayRole:
            return super().data(index, role)
        elif role == CHANGE_ROLE:
            # Return actual data stored for sorting
            return index.model().item(index.row(), 0).data(CHANGE_ROLE)
        return None

    def sort(self, column, order=QtGui.Qt.AscendingOrder):
        if column == 0:  # Sort by number (stored in user role)
            self.sortItems(0, order, CHANGE_ROLE)
        else:
            super().sort(column, order)

    def get_change_by_id(self, item_id):
        return self._changes_by_item_id.get(item_id)
