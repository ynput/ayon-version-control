"""Changes Viewer Controller."""
from __future__ import annotations

from dataclasses import asdict
from typing import TYPE_CHECKING, Callable, Optional

from ayon_core.addon import AddonsManager
from ayon_core.lib.events import QueuedEventSystem
from ayon_core.pipeline import registered_host

from ayon_perforce.backend.rest_stub import PerforceRestStub

if TYPE_CHECKING:
    from ayon_core.host import HostBase

    from ayon_perforce.addon import ConnectionInfo, LaunchData, PerforceAddon


class ChangesViewerController:
    """This is a temporary controller for AYON.

    Goal of this controller is to provide a way to get current context.
    """

    def __init__(
            self, launch_data: LaunchData, host: Optional[HostBase] = None):
        """Initialize ChangesViewerController."""
        if host is None:
            host = registered_host()
        self._host = host
        self._current_project = launch_data.project_name
        self._current_folder_id = launch_data.folder_entity["id"]

        manager = AddonsManager()
        perforce_addon = manager.get("perforce")
        self._perforce_addon: PerforceAddon = perforce_addon
        self.enabled = perforce_addon and perforce_addon.enabled

        self._conn_info: ConnectionInfo = (
            self._perforce_addon.get_connection_info(
                project_name=launch_data.project_name,
                task_entity=launch_data.task_entity,
                folder_entity=launch_data.folder_entity,
                folder_path=launch_data.folder_path,
            ))

        self._event_system = self._create_event_system()

    def emit_event(
            self, topic: str,
            data: Optional[dict] = None,
            source: Optional[str] = None) -> None:
        """Emit event."""
        if data is None:
            data = {}
        self._event_system.emit(topic, data, source)

    def register_event_callback(
            self, topic: str, callback: Callable) -> None:
        """Register event callback."""
        self._event_system.add_callback(topic, callback)

    def login(self) -> None:
        """Login to Perforce.

        Raises:
            RuntimeError: If Perforce connection information is not collected.
        """
        if not self.enabled:
            return

        if not self._conn_info:
            msg = "Missing Perforce connection information."
            raise RuntimeError(msg)

        PerforceRestStub.login(**asdict(self._conn_info)
        )

    @staticmethod
    def get_changes() -> dict:
        """Get changes from Perforce.

        Returns:
            dict: Changes from Perforce
        """
        return PerforceRestStub.get_changes()

    def sync_to(self, change_id: int):
        if not self.enabled:
            return

        if not self._conn_info:
            msg = "Missing Perforce connection information."
            raise RuntimeError(msg)

        self.login()
        PerforceRestStub.login(**asdict(self._conn_info))
        workspace_dir = PerforceRestStub.get_workspace_dir(
            self._conn_info.workspace_name)
        PerforceRestStub.sync_to_version(
            f"{workspace_dir}/...", change_id)

    def get_current_project_name(self) -> str:
        """Get current project name.

        Returns:
            str: Current project name.

        """
        return self._current_project

    def get_current_folder_id(self) -> str:
        """Get current folder id.

        Returns:
            str: Current folder id.

        """
        return self._current_folder_id

    @staticmethod
    def _create_event_system() -> QueuedEventSystem:
        """Create event system.

        Returns:
            QueuedEventSystem: Event system instance.

        """
        return QueuedEventSystem()
