"""
Requires:
    none

Provides:
    context.data     -> "version_control" ({})
"""

import pyblish.api

from ayon_core.addon import AddonsManager
from ayon_core.pipeline.publish import PublishError
from ayon_common.utils import get_local_site_id

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
            self.log.info(
                "Version control addon is not enabled"
                f" for project '{project_name}'"
            )
            return

        conn_info = self._get_conn_info(
            project_name, version_control, project_settings)
        context.data["version_control"] = conn_info

        PerforceRestStub.login(
            conn_info["host"],
            conn_info["port"],
            conn_info["username"],
            conn_info["password"],
            conn_info["workspace_dir"]
        )

        stream = PerforceRestStub.get_stream(conn_info["workspace_dir"])
        context.data["version_control"]["stream"] = stream
        self.log.debug(f"stream::{stream}")

    def _is_addon_enabled(self, version_control, project_settings):
        """Check if addon is enabled for this project.

        Args:
            version_control (AYONAddon): Version control addon from manager.
            project_settings (Dict[str, Any]): Prepared project settings.

        Returns
            bool: Addon is enabled or not.
        """
        project_enabled = project_settings[version_control.name]["enabled"]
        return version_control and project_enabled

    def _get_conn_info(self, project_name, version_control, project_settings):
        """Gets and check credentials for version-control

        Args:
            project_name (str)
            version_control (Union[AYONAddon, Any]): addon from AddonsManager
            project_settings (Dict[str, Any]): Prepared project settings.

        Returns:
            dict[str, str]: Connection info.

        Raises:
            (PublishError): When credentials are missing.
        """
        conn_info = version_control.get_connection_info(
            project_name, project_settings)

        if not all([
            conn_info["username"],
            conn_info["password"],
            conn_info["workspace_dir"]
        ]):
            site_name = get_local_site_id()
            sett_str = (
                "ayon+settings://version_control?project="
                f"{project_name}&site={site_name}"
            )
            raise PublishError(
                "Required credentials are missing. "
                f"Please go to `{sett_str}` to fill it.")

        if not all([conn_info["host"], conn_info["port"]]):
            sett_str = (
                f"ayon+settings://version_control?project={project_name}"
            )
            raise PublishError(
                "Required version control settings are missing. "
                f"Please ask your AYON admin to fill `{sett_str}`.")

        return conn_info
