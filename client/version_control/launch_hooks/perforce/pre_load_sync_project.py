"""Shows dialog to sync Unreal project

Requires:
    None

Provides:
    self.data["last_workfile_path"]

"""
import os

from ayon_applications import (
    PreLaunchHook,
    LaunchTypes,
)

from ayon_core.tools.utils import qt_app_context
from ayon_core.addon import AddonsManager

from version_control.changes_viewer import ChangesWindows
from version_control import is_version_control_enabled
from version_control.lib import WorkspaceProfileContext
from version_control.rest.perforce.rest_stub import PerforceRestStub


class SyncUnrealProject(PreLaunchHook):
    """Show dialog for artist to sync to specific change list.

    It is triggered before Unreal launch as syncing inside would likely
    lead to locks.
    It is called before `pre_workfile_preparation` which is using
    self.data["last_workfile_path"].

    It is expected that workspace would be created, connected
    and first version of project would be synced before.
    """

    order = -5
    app_groups = ["unreal"]
    launch_types = {LaunchTypes.local}

    def execute(self):
        version_control_addon = self._get_enabled_version_control_addon()
        if not version_control_addon:
            self.log.info("Version control is not enabled, skipping")
            return

        self.data["last_workfile_path"] = self._get_unreal_project_path(
            version_control_addon, self.data)

        with qt_app_context():
            changes_tool = ChangesWindows(launch_data=self.data)
            changes_tool.show()
            changes_tool.raise_()
            changes_tool.activateWindow()
            changes_tool.showNormal()

            changes_tool.exec_()

    def _get_unreal_project_path(self, version_control_addon, launch_data):
        task_entity = launch_data["task_entity"]
        workspace_profile_context = WorkspaceProfileContext(
            task_names=task_entity["name"],
            task_types=task_entity["taskType"],
        )
        conn_info = version_control_addon.get_connection_info(
            project_name=self.data["project_name"],
            project_settings=launch_data["project_settings"],
            context=workspace_profile_context
        )

        PerforceRestStub.login(
            host=conn_info["host"],
            port=conn_info["port"],
            username=conn_info["username"],
            password=conn_info["password"],
            workspace_name=conn_info["workspace_name"])

        workspace_dir = PerforceRestStub.get_workspace_dir(
            workspace_name=conn_info["workspace_name"])
        if not os.path.exists(workspace_dir):
            raise RuntimeError(f"{workspace_dir} must exists for using version"
                               " control")
        project_files = self._find_uproject_files(workspace_dir)
        if len(project_files) != 1:
            raise RuntimeError("Found unexpected number of projects "
                               f"'{project_files}.\n"
                               "Expected only single Unreal project.")
        return project_files[0]

    def _get_enabled_version_control_addon(self):
        if is_version_control_enabled(self.data["project_settings"]):
            manager = AddonsManager()
            return manager["version_control"]
        return None

    def _find_uproject_files(self, start_dir):
        """
        This function searches for files with the .uproject extension recursively
        within a starting directory and its subdirectories.

        Args:
            start_dir: The starting directory from where the search begins.

        Returns:
            A list of full paths to all the found .uproject files.
        """
        uproject_files = []
        for dirpath, dirnames, filenames in os.walk(start_dir):
            for filename in filenames:
                if filename.endswith(".uproject"):
                    uproject_files.append(os.path.join(dirpath, filename))
        return uproject_files
