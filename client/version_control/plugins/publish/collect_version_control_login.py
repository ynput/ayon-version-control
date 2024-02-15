"""
Requires:
    none

Provides:
    context.data     -> "version_control" ({})
"""

import pyblish.api

from openpype.modules import ModulesManager

from version_control.backends.perforce.api.rest_stub import PerforceRestStub


class CollectVersionControlLogin(pyblish.api.ContextPlugin):
    """Collect connection info and login with it."""

    label = "Collect Version Control Connection Info"
    order = pyblish.api.CollectorOrder + 0.4990

    def process(self, context):
        version_control = ModulesManager().get("version_control")
        if not version_control or not version_control.enabled:
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
