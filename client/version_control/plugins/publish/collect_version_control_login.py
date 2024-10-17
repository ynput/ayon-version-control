"""
Requires:
    none

Provides:
    context.data     -> "version_control" ({})
"""

import pyblish.api

from ayon_core.addon import AddonsManager

from version_control.rest.perforce.rest_stub import PerforceRestStub


class CollectVersionControlLogin(pyblish.api.ContextPlugin):
    """Collect connection info and login with it."""

    label = "Collect Version Control Connection Info"
    order = pyblish.api.CollectorOrder + 0.4990
    targets = ["local"]

    def process(self, context):
        version_control = AddonsManager().get("version_control")
        project_name = context.data["projectName"]
        project_settings = context.data["project_settings"]
        if not self._is_addon_enabled(version_control, project_settings):
            self.log.info("No version control enabled")
            return

        project_name = context.data["projectName"]
        project_setting = context.data["project_settings"]
        conn_info = version_control.get_connection_info(project_name,
                                                        project_setting)

        context.data["version_control"] = conn_info

        PerforceRestStub.login(conn_info["host"], conn_info["port"],
                               conn_info["username"],
                               conn_info["password"],
                               conn_info["workspace_dir"])

        stream = PerforceRestStub.get_stream(conn_info["workspace_dir"])
        context.data["version_control"]["stream"] = stream
        self.log.debug(f"stream::{stream}")

    def _is_addon_enabled(self, version_control, project_settings):
        """Check if addon is enabled for this project.

        Args:
            version_control Union[AYONAddon, Any]: addon returned from manager
            project_settings (Dict[str, Any]): Prepared project settings.

        Returns
            (bool)
        """
        project_enabled = project_settings[version_control.name]["enabled"]
        return version_control and version_control.enabled and project_enabled
