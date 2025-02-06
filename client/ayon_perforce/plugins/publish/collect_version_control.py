"""
Requires:
    instance.context.data["perforce"] - connection info for VC

Provides:
    instance     -> families ([])
"""
import pyblish.api
from ayon_core.lib import filter_profiles

from ayon_perforce.rest.perforce.rest_stub import PerforceRestStub


class CollectVersionControl(pyblish.api.InstancePlugin):
    """Mark instance to be submitted."""

    label = "Collect Version Control Submission Info"
    order = pyblish.api.CollectorOrder + 0.4992
    targets = ["local"]

    profiles = None

    def process(self, instance):
        conn_info = instance.context.data.get("perforce")
        if not conn_info:
            self.log.info("No Version control set and enabled")

        if not self.profiles:
            self.log.warning("No profiles present for adding "
                             "version_control family")
            return

        version_control_family = "perforce"

        host_name = instance.context.data["hostName"]
        product_type = instance.data["productType"]
        task_name = instance.data.get("task")

        filtering_criteria = {
            "hosts": host_name,
            "product_types": product_type,
            "tasks": task_name
        }
        profile = filter_profiles(
            self.profiles,
            filtering_criteria,
            logger=self.log
        )

        add_version_control = False

        if profile:
            add_version_control = profile["add_version_control"]

        if not add_version_control:
            return

        families = instance.data.setdefault("families", [])
        if not version_control_family in families:
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

        self.log.debug(f"{result_str} 'version_control' product_type "
                       f"for instance with '{product_type}' product type.")
