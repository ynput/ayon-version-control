"""
Requires:
    none

Provides:
    context.data     -> "version_control" ({})
"""

import pyblish.api

from ayon_common.utils import get_local_site_id

from version_control.rest.perforce.rest_stub import PerforceRestStub
from version_control import is_version_control_enabled
from version_control.lib import WorkspaceProfileContext


class CollectVersionControlLogin(pyblish.api.ContextPlugin):
    """Collect connection info and login with it.

    Do not fail explicitly if version control connection info is missing.
    Not all artists need to have credentials, not all DCCs should use
    version control.
    """

    label = "Collect Version Control Connection Info"
    order = pyblish.api.CollectorOrder + 0.4990
    targets = ["local"]

    def process(self, context):
        project_name = context.data["projectName"]
        project_settings = context.data["project_settings"]
        if not is_version_control_enabled(project_settings):
            self.log.info(
                "Version control addon is not enabled"
                f" for project '{project_name}'"
            )
            return

        version_control = (
            context.data.get("ayonAddonsManager", {}).get("version_control"))
        conn_info = self._get_conn_info(
            project_name, version_control, project_settings, context)

        if not conn_info:
            return

        context.data["version_control"] = conn_info

        PerforceRestStub.login(
            conn_info["host"],
            conn_info["port"],
            conn_info["username"],
            conn_info["password"],
            conn_info["workspace_name"]
        )

        stream = PerforceRestStub.get_stream(
            workspace_name=conn_info["workspace_name"])
        context.data["version_control"]["stream"] = stream
        self.log.debug(f"stream::{stream}")

        workspace_dir = PerforceRestStub.get_workspace_dir(
            workspace_name=conn_info["workspace_name"])
        context.data["version_control"]["workspace_dir"] = workspace_dir

    def _get_conn_info(
        self,
        project_name,
        version_control,
        project_settings,
        context
    ):
        """Gets and check credentials for version-control

        Args:
            project_name (str)
            version_control (Union[AYONAddon, Any]): addon from AddonsManager
            project_settings (Dict[str, Any]): Prepared project settings.

        Returns:
            dict[str, str]: Connection info or None if validation failed
        """
        task_entity = context.data.get("taskEntity")
        task_name = task_type = None
        if task_entity:
            task_name = task_entity["name"]
            task_type = task_entity["taskType"]

        workspace_context = WorkspaceProfileContext(
            folder_paths=context.data["folderPath"],
            task_names=task_name,
            task_types=task_type
        )
        conn_info = version_control.get_connection_info(
            project_name, project_settings, workspace_context)

        missing_creds = False
        if not all([
            conn_info["username"],
            conn_info["password"],
            conn_info["workspace_name"]
        ]):
            site_name = get_local_site_id()
            sett_str = (
                "ayon+settings://version_control?project="
                f"{project_name}&site={site_name}"
            )
            self.log.warning(
                "Required credentials are missing. "
                f"Please go to `{sett_str}` to fill it.")
            missing_creds = True

        if not all([conn_info["host"], conn_info["port"]]):
            sett_str = (
                f"ayon+settings://version_control?project={project_name}"
            )
            self.log.warning(
                "Required version control settings are missing. "
                f"Please ask your AYON admin to fill `{sett_str}`.")
            missing_creds = True

        if missing_creds:
            return None

        return conn_info
