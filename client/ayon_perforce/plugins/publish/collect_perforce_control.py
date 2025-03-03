"""
Requires:
    instance.context.data["perforce"] - connection info for VC

Provides:
    instance     -> families ([])
"""
import pyblish.api
from ayon_core.lib import filter_profiles

from ayon_perforce.rest.rest_stub import PerforceRestStub


class CollectPerforceControl(pyblish.api.InstancePlugin):
    """Mark instance to be submitted to Perforce.

    AYON provides version control itself, this plugin duplicates and commits
    selected published files directly to Perforce as a changelist.
    """

    label = "Collect Perforce Submission Info"
    order = pyblish.api.CollectorOrder + 0.4992
    targets = ["local"]

    settings_category = "perforce"

    profiles = None

    def process(self, instance):
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

        self.log.debug(
            f"{result_str} 'perforce' product_type "
            f"for instance with '{product_type}' product type."
        )
