"""
Requires:
    instance.context.data["version_control"] - connection info for VC

Provides:
    instance     -> families ([])
"""
import pyblish.api
from openpype.lib import filter_profiles


class CollectVersionControl(pyblish.api.InstancePlugin):
    """Mark instance to be submitted."""

    label = "Collect Version Control Submission Info"
    order = pyblish.api.CollectorOrder + 0.4992
    targets = ["local"]

    profiles = None

    def process(self, instance):
        conn_info = instance.context.data.get("version_control")
        if not conn_info:
            self.log.info("No Version control set and enabled")

        if not self.profiles:
            self.log.warning("No profiles present for adding "
                             "version_control family")
            return

        version_control_family = "version_control"

        host_name = instance.context.data["hostName"]
        family = instance.data["family"]
        task_name = instance.data.get("task")

        filtering_criteria = {
            "hosts": host_name,
            "product_types": family,
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
        workspace_dir = conn_info["workspace_dir"]

        instance.data["version_control"] = {}
        instance.data["version_control"]["roots"] = {"work": workspace_dir}
        instance.data["version_control"]["username"] = username
        instance.data["version_control"]["password"] = password
        instance.data["version_control"]["template_name"] = \
            profile["template_name"]

        self.log.debug("{} 'version_control' family for instance with '{}'".format(  # noqa
            result_str, family
        ))
