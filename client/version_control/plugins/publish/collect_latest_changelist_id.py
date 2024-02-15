"""
Requires:
    none

Provides:
    instance     -> families ([])
"""
import pyblish.api

from version_control.backends.perforce.api.rest_stub import (
    PerforceRestStub
)


class CollectLatestChangeList(pyblish.api.InstancePlugin):
    """Looks for id of latest change list to store it later."""

    label = "Collect Latest Changelist ID"
    order = pyblish.api.CollectorOrder + 0.4995

    families = ["publish_commit"]

    def process(self, instance):

        changelist_value = PerforceRestStub.get_last_change_list_number()
        self.log.debug(f"Latest changelist value:{changelist_value}")
