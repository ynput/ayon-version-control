"""
Requires:
    none

Provides:
    context.data     -> "perforce" ({})
"""

import pyblish.api

from ayon_common.utils import get_local_site_id

from ayon_perforce.rest.perforce.rest_stub import PerforceRestStub
from ayon_perforce import is_perforce_enabled
from ayon_perforce.lib import WorkspaceProfileContext


class CollectPerforceLogin(pyblish.api.ContextPlugin):
    """Collect connection info and login with it.

    Do not fail explicitly if version control connection info is missing.
    Not all artists need to have credentials, not all DCCs should use
    version control.
    """

    label = "Collect Perforce Connection Info"
    order = pyblish.api.CollectorOrder + 0.4990
    targets = ["local"]

    def process(self, context):
        project_name = context.data["projectName"]
        project_settings = context.data["project_settings"]
        if not is_perforce_enabled(project_settings):
            self.log.info(
                "Perforce addon is not enabled"
                f" for project '{project_name}'"
            )
            return

        perforce_addon = (
            context.data.get("ayonAddonsManager", {}).get("perforce"))
        conn_info = self._get_conn_info(
            project_name, perforce_addon, project_settings, context)

        if not conn_info:
            return

        context.data["perforce"] = conn_info

        PerforceRestStub.login(
            conn_info["host"],
            conn_info["port"],
            conn_info["username"],
            conn_info["password"],
            conn_info["workspace_name"]
        )

        stream = PerforceRestStub.get_stream(
            workspace_name=conn_info["workspace_name"])
        context.data["perforce"]["stream"] = stream
        self.log.debug(f"stream::{stream}")

        workspace_dir = PerforceRestStub.get_workspace_dir(
            workspace_name=conn_info["workspace_name"])
        context.data["perforce"]["workspace_dir"] = workspace_dir

    def _get_conn_info(
        self,
        project_name,
        perforce_addon,
        project_settings,
        context
    ):
        """Gets and check credentials for version-control

        Args:
            project_name (str)
            perforce_addon (Union[AYONAddon, Any]): addon from AddonsManager
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
        conn_info = perforce_addon.get_connection_info(
            project_name, project_settings, workspace_context)

        missing_creds = False
        if not all([
            conn_info["username"],
            conn_info["password"],
            conn_info["workspace_name"]
        ]):
            site_name = get_local_site_id()
            sett_str = (
                "ayon+settings://perforce?project="
                f"{project_name}&site={site_name}"
            )
            self.log.warning(
                "Required credentials are missing. "
                f"Please go to `{sett_str}` to fill it.")
            missing_creds = True

        if not all([conn_info["host"], conn_info["port"]]):
            sett_str = (
                f"ayon+settings://perforce?project={project_name}"
            )
            self.log.warning(
                "Required Perforce settings are missing. "
                f"Please ask your AYON admin to fill `{sett_str}`.")
            missing_creds = True

        if missing_creds:
            return None

        return conn_info
