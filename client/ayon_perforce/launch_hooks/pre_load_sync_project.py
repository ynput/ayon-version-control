"""Shows dialog to sync Unreal project.

Requires:
    None

Provides:
    self.data["last_workfile_path"]

"""
from __future__ import annotations

import os
from dataclasses import asdict
from typing import TYPE_CHECKING, ClassVar, Optional

from ayon_applications import (
    LaunchTypes,
    PreLaunchHook,
)
from ayon_core.addon import AddonsManager
from ayon_core.tools.utils import qt_app_context
from ayon_perforce import is_perforce_enabled
from ayon_perforce.addon import LaunchData
from ayon_perforce.changes_viewer import ChangesWindows
from ayon_perforce.lib import WorkspaceProfileContext
from ayon_perforce.rest.rest_stub import PerforceRestStub

if TYPE_CHECKING:
    from ayon_perforce.addon import ConnectionInfo, PerforceAddon


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
    app_groups: ClassVar = ["unreal"]
    launch_types: ClassVar = {LaunchTypes.local}

    def execute(self) -> None:
        """Show dialog to sync Unreal project."""
        perforce_addon = self._get_enabled_perforce_addon()
        if not perforce_addon:
            self.log.info("Perforce Addon is not enabled, skipping")
            return
        launch_data = LaunchData(
            project_name=self.data["project_name"],
            folder_entity=self.data["folder_entity"],
            task_entity=self.data["task_entity"],
            project_settings=self.data["project_settings"],
            folder_path=self.data["folder_path"],
        )

        self.data["last_workfile_path"] = self._get_unreal_project_path(
            perforce_addon, launch_data)

        with qt_app_context():
            changes_tool = ChangesWindows(launch_data=launch_data)
            changes_tool.show()
            changes_tool.raise_()
            changes_tool.activateWindow()
            changes_tool.showNormal()

            changes_tool.exec_()

    def _get_unreal_project_path(self,
            perforce_addon: PerforceAddon, launch_data: LaunchData) -> str:
        """Get path to Unreal project file.

        Args:
            perforce_addon: PerforceAddon instance.
            launch_data: Launch data dictionary.

        Returns:
            str: Path to Unreal project file.

        Raises:
            RuntimeError: If workspace or project file is not

        """
        task_entity = launch_data.task_entity
        workspace_profile_context = WorkspaceProfileContext(
            folder_paths=launch_data.folder_path,
            task_names=task_entity["name"],
            task_types=task_entity["taskType"],
        )
        conn_info: ConnectionInfo = perforce_addon.get_connection_info(
            project_name=launch_data.project_name,
            project_settings=launch_data.project_settings,
            context=workspace_profile_context
        )

        if not conn_info or not conn_info.workspace_name:
            msg = "Cannot find workspace for this context."
            raise RuntimeError(msg)

        PerforceRestStub.login(**asdict(conn_info))

        workspace_dir = PerforceRestStub.get_workspace_dir(
            workspace_name=conn_info.workspace_name)
        if not os.path.exists(workspace_dir):
            msg = f"Workspace '{workspace_dir}' does not exists."
            raise RuntimeError(msg)
        project_files = self._find_uproject_files(workspace_dir)
        if len(project_files) != 1:
            msg = (
                f"Found unexpected number of projects '{project_files}.\n"
                "Expected only single Unreal project.")
            raise RuntimeError(msg)

        return project_files[0]

    def _get_enabled_perforce_addon(self) -> Optional[PerforceAddon]:
        if is_perforce_enabled(self.data["project_settings"]):
            manager = AddonsManager()
            return manager["perforce"]
        return None

    @staticmethod
    def _find_uproject_files(start_dir: str) -> list[str]:
        """Find all .uproject files in the given directory.

        This function searches for files with the .uproject
        extension recursively within a starting directory and its
        subdirectories.

        Args:
            start_dir: The starting directory from where the search begins.

        Returns:
            A list of full paths to all the found .uproject files.

        """
        uproject_files = []
        for dirpath, _, filenames in os.walk(start_dir):
            uproject_files.extend(
                os.path.join(dirpath, filename)
                for filename in filenames if filename.endswith(".uproject")
            )
        return uproject_files
