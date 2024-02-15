"""
Requires:
    instance.context.data["version_control"] - credentials
    instance.data["version_control"] - instance based data for extractions

Provides:
    instance.data["version_control"]["change_info"]["user"] - author of submit
                                                   ["change"] - id of submit
                                                   ["desc"] - description
                                                   ["time"] - when created
"""
import pyblish.api

from version_control.backends.perforce.api.rest_stub import (
    PerforceRestStub
)


class CollectLatestChangeList(pyblish.api.InstancePlugin):
    """Looks for latest change list to store it later."""

    label = "Collect Latest Changelist"
    order = pyblish.api.CollectorOrder + 0.4995

    families = ["publish_commit"]

    def process(self, instance):
        if not instance.context.data.get("version_control"):
            self.log.info("No version control collected, skipping.")
            return

        change_info = PerforceRestStub.get_last_change_list()
        if not change_info:
            self.log.info("No changelist was found, "
                          "extraction of it not possible.")

        if not instance.data.get("version_control"):
            instance.data["version_control"] = {}

        usable_info = {}
        usable_info["change"] = change_info["change"]
        usable_info["user"] = change_info["user"]
        usable_info["desc"] = change_info["desc"]
        usable_info["time"] = change_info["time"]

        instance.data["version_control"]["change_info"] = usable_info

        self.log.debug(f"Latest changelist info: {usable_info}")
