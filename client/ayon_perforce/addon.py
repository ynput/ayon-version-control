"""Perforce Addon for AYON."""
from __future__ import annotations

import os
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Optional

from ayon_core.addon import AYONAddon, IPluginPaths, ITrayService
from ayon_core.lib import StringTemplate, ayon_info
from ayon_core.pipeline.template_data import get_template_data_with_names
from ayon_core.settings import get_project_settings

from .version import __version__


PERFORCE_ADDON_DIR = os.path.dirname(os.path.abspath(__file__))


@dataclass
class ConnectionInfo:
    """Connection information for Perforce."""
    host: str
    port: int
    username: str
    password: str
    workspace_name: str


@dataclass
class LaunchData:
    """Current context data."""
    project_name: str
    folder_entity: dict[str, Any]
    task_entity: dict[str, Any]
    project_settings: dict[str, Any]
    folder_path: str


class PerforceAddon(AYONAddon, ITrayService, IPluginPaths):
    """AYON Integration addon for Perforce."""

    label = "Perforce Version Control"
    name = "perforce"
    version = __version__
    webserver = None

    # Public Methods:
    def initialize(self, settings: dict[str, Any]) -> None:
        """Initialize the addon."""
        vc_settings: dict[str, Any] = settings.get(self.name)
        enabled: bool = vc_settings and vc_settings["enabled"]
        self.set_service_running_icon() if enabled else self.set_service_failed_icon()  # noqa: E501

    def get_connection_info(
        self,
        project_name: str,
        task_entity: dict,  # use ayon type hint
        folder_entity: dict,  # use ayon type hint
        folder_path: str,
        project_settings: Optional[dict] = None,
    ) -> ConnectionInfo:
        """Get connection information for Perforce.

        Args:
            project_name (str): Name of the project.
            task_entity (dict): Task entity.
            folder_entity (dict): Folder entity.
            folder_path (str): Folder path.
            project_settings (Optional[dict]): Project settings.

        Returns:
            ConnectionInfo: Connection information for Perforce.

        Raises:
            RuntimeError: If Perforce is disabled in server settings
        """
        if not project_settings:
            project_settings = get_project_settings(project_name)
        settings = project_settings["perforce"]
        if not settings["enabled"]:
            msg = "Perforce is disabled in server settings."
            raise RuntimeError(msg)

        tmpl_data = get_template_data_with_names(project_name)
        tmpl_data.update({
            "workstation": ayon_info.get_workstation_info(),
            "task": task_entity,
            "folder": folder_entity
        })
        ws_tmpl = StringTemplate(settings["workspace"]["template"])
        ws_name = ws_tmpl.format_strict(tmpl_data)

        return ConnectionInfo(
            host=settings["host_name"],
            port=settings["port"],
            username="hardcode for now",
            password="hardcode for now",  # that will come from tray login
            workspace_name=ws_name
        )

    @staticmethod
    def sync_to_version(
            conn_info: ConnectionInfo, change_id: int) -> None:
        """Sync to a specific version in Perforce.

        Args:
            conn_info: Connection information for Perforce.
            change_id: Change ID to sync to.

        """
        from ayon_perforce.backend.rest_stub import PerforceRestStub

        PerforceRestStub.login(**asdict(conn_info))

        workspace_dir = PerforceRestStub.get_workspace_dir(
            conn_info.workspace_name)
        PerforceRestStub.sync_to_version(
            f"{workspace_dir}/...", change_id)

    def tray_init(self) -> None:
        """Called when the tray is initializing."""

    def get_plugin_paths(self) -> dict[str, list[str]]:  # noqa: PLR6301
        """Called to get the plugin paths.

        Note: this implements the abstract method from IPluginPaths.
            But it does not return any plugin paths.

        Returns:
            dict[str, list[str]]: Plugin paths.

        """
        return {}

    def tray_exit(self) -> None:
        """Called when the tray is exiting."""
        if self.enabled and \
                self.webserver and self.webserver.server_is_running:
            self.webserver.stop()

    def tray_start(self) -> None:
        """Called when the tray is starting."""
        if self.enabled:
            from ayon_perforce.backend.communication_server import WebServer
            self.webserver = WebServer()
            self.webserver.start()

    # PLR6301: This method is defined by the interface
    def get_create_plugin_paths(  # noqa: PLR6301
            self, host_name: str) -> list[str]:
        """Get paths to create plugins.

        This adds host-specific paths based on runtime context.

        Args:
            host_name: Name of the host.

        Returns:
            list[str]: List of paths to create plugins.

        """
        if host_name != "unreal":
            return []
        return [f"{PERFORCE_ADDON_DIR}/plugins/create/unreal"]

    def get_publish_plugin_paths(  # noqa: PLR6301
            self, host_name: str) -> list[str]:
        """Get paths to publish plugins.

        Args:
            host_name: Name of the host.

        Returns:
            list[str]: List of paths to publish plugins.

        """
        return [
            (Path(PERFORCE_ADDON_DIR) / "plugins" / "publish").as_posix()
        ]

    def get_launch_hook_paths(self, _app: str) -> str:  # noqa: PLR6301
        """Implementation for applications launch hooks.

        Returns:
            (str): full absolute path to directory with hooks for the module

        """
        return (Path(PERFORCE_ADDON_DIR) / "launch_hooks").as_posix()


def is_perforce_enabled(
        project_settings: dict[str, Any]) -> bool:
    """Check if Perforce is enabled for the project.

    Args:
        project_settings: Project settings.

    Returns:
        bool: True if Perforce is enabled, False otherwise.

    """
    return project_settings.get("perforce", {}).get("enabled", False)
