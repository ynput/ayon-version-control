"""
Requires:
    none

Provides:
    instance     -> families ([])
"""
import pyblish.api
from openpype.lib import filter_profiles


class CollectVersionControl(pyblish.api.InstancePlugin):
    """Adds flag to instance that it should be version controlled also externally.
    """

    label = "Collect Version Control"
    order = pyblish.api.CollectorOrder + 0.4990

    profiles = None

    def process(self, instance):
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
        version_settings = (instance.context.data["project_settings"]
                                                 ["version_control"])
        local_setting = version_settings["local_setting"]
        username = local_setting["username"]
        password = local_setting["password"]
        workspace_dir = local_setting["workspace_dir"]

        instance.data["version_control"] = {}
        instance.data["version_control"]["roots"] = {"work": workspace_dir}
        instance.data["version_control"]["username"] = username
        instance.data["version_control"]["roots"] = password
        instance.data["version_control"]["template_name"] = \
            profile["template_name"]

        self.log.debug("{} 'version_control' family for instance with '{}'".format(  # noqa
            result_str, family
        ))
