"""Mark instance to be submitted to Perforce.

Requires:
    instance.context.data["perforce"] - connection info for VC

Provides:
    instance     -> families ([])
"""
from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

import pyblish.api
from ayon_core.lib import filter_profiles
from ayon_perforce.backend.rest_stub import PerforceRestStub

if TYPE_CHECKING:
    import logging


class CollectPerforceControl(pyblish.api.InstancePlugin):
    """Mark instance to be submitted to Perforce.

    AYON provides version control itself, this plugin duplicates and commits
    selected published files directly to Perforce as a changelist.
    """

    label = "Collect Perforce Submission Info"
    order = pyblish.api.CollectorOrder + 0.4992
    targets: ClassVar[list[str]] = ["local"]
    # TODO (antirotor): https://github.com/ynput/ayon-perforce/issues/15
    #    because of this issue, limit this plugin to Unreal hosts only
    hosts: ClassVar[list[str]] = ["unreal"]

    settings_category = "perforce"

    profiles = None
    log: logging.Logger

    def process(self, instance: pyblish.api.Instance) -> None:
        """Process the plugin."""
        conn_info = instance.context.data.get("perforce")
        if not conn_info:
            self.log.info("No Perforce control set and enabled")

        if not self.profiles:
            self.log.warning(
                "No profiles present for adding perforce family")
            return

        version_control_family = "perforce"

        host_name = instance.context.data["hostName"]
        product_type = instance.data["productType"]
        task_entity = instance.data["taskEntity"]
        task_name = task_type = None
        if task_entity:
            task_name = task_entity["name"]
            task_type = task_entity["taskType"]

        filtering_criteria = {
            "host_names": host_name,
            "product_types": product_type,
            "task_names": task_name,
            "task_types": task_type
        }
        profile = filter_profiles(
            self.profiles,
            filtering_criteria,
            logger=self.log
        )

        add_perforce_control = False

        if profile:
            add_perforce_control = profile["add_perforce_control"]

        if not add_perforce_control:
            return

        families = instance.data.setdefault("families", [])
        if version_control_family not in families:
            instance.data["families"].append(version_control_family)

        result_str = "Adding"
        username = conn_info["username"]
        password = conn_info["password"]

        workspace_dir = PerforceRestStub.get_workspace_dir(
            conn_info["workspace_name"])

        instance.data["perforce"] = {}
        instance.data["perforce"]["roots"] = {"work": workspace_dir}
        instance.data["perforce"]["username"] = username
        instance.data["perforce"]["password"] = password
        instance.data["perforce"]["template_name"] = \
                profile["template_name"]

        self.log.debug(
            "%s 'perforce' product_type "
                 "for instance with '%s' product type.",
            result_str, product_type
        )
