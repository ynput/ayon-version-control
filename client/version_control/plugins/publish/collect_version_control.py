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
        families = instance.data.setdefault("families", [])

        if profile:
            add_version_control = profile["add_version_control"]

        if not add_version_control:
            return

        result_str = "Adding"
        if version_control_family not in families:
            families.append(version_control_family)

        instance.data["version_control_template_name"] = profile["template_name"]  # noqa

        project_settings = instance.context.data["project_settings"]
        workspace_dir = (project_settings["version_control"]
                                         ["local_setting"]
                                         .get("workspace_dir"))

        instance.data["version_control_roots"] = workspace_dir

        self.log.debug("{} 'version_control' family for instance with '{}'".format(  # noqa
            result_str, family
        ))
