"""Collects latest changelist from Perforce.

Requires:
    instance.context.data["perforce"] - credentials
    instance.data["perforce"] - instance based data for extractions.

Provides:
    instance.data["perforce"]["change_info"]["user"] - author of submit
                                            ["change"] - id of submit
                                            ["desc"] - description
                                            ["time"] - when created
"""
from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

import pyblish.api
from ayon_perforce.rest.rest_stub import PerforceRestStub

if TYPE_CHECKING:
    import logging


class CollectLatestChangeList(pyblish.api.InstancePlugin):
    """Looks for latest change list to store it later."""

    label = "Collect Latest Changelist"
    order = pyblish.api.CollectorOrder + 0.4995
    targets: ClassVar[list[str]] = ["local"]
    families: ClassVar[list[str]] = ["changelist_metadata"]
    log: logging.Logger

    def process(self, instance: pyblish.api.Instance) -> None:
        """Process the plugin."""
        if not instance.context.data.get("perforce"):
            self.log.info("No version control collected, skipping.")
            return

        change_info = PerforceRestStub.get_last_change_list()
        if not change_info:
            self.log.info("No changelist was found, "
                          "extraction of it not possible.")

        if not instance.data.get("perforce"):
            instance.data["perforce"] = {}

        usable_info = {
            "change": change_info["change"],
            "user": change_info["user"],
            "desc": change_info["desc"],
            "time": change_info["time"],
        }
        instance.data["perforce"]["change_info"] = usable_info

        self.log.debug("Latest changelist info: %s",
                       usable_info)
