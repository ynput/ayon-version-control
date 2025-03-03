from ayon_core.lib.events import QueuedEventSystem
from ayon_core.pipeline import (
    registered_host,
    get_current_context,
)
from ayon_core.addon import AddonsManager

from ayon_perforce.rest.rest_stub import PerforceRestStub
from ayon_perforce.lib import WorkspaceProfileContext


class ChangesViewerController:
    """This is a temporary controller for AYON.

    Goal of this controller is to provide a way to get current context.
    """

    def __init__(self, launch_data, host=None):
        if host is None:
            host = registered_host()
        self._host = host
        self._current_project = launch_data["project_name"]
        self._current_folder_id = launch_data["folder_entity"]["id"]

        manager = AddonsManager()
        perforce_addon = manager.get("perforce")
        self._perforce_addon = perforce_addon
        self.enabled = perforce_addon and perforce_addon.enabled

        task_entity = launch_data["task_entity"]
        workspace_profile_context = WorkspaceProfileContext(
            folder_paths=launch_data["folder_path"],
            task_names=task_entity["name"],
            task_types=task_entity["taskType"],
        )

        conn_info = self._perforce_addon.get_connection_info(
            project_name=launch_data["project_name"],
            context=workspace_profile_context
        )
        self._conn_info = conn_info

        self._event_system = self._create_event_system()

    def emit_event(self, topic, data=None, source=None):
        if data is None:
            data = {}
        self._event_system.emit(topic, data, source)

    def register_event_callback(self, topic, callback):
        self._event_system.add_callback(topic, callback)

    def login(self):
        if not self.enabled:
            return

        if not self._conn_info:
            raise RuntimeError("Not collected conn_info")

        conn_info = self._conn_info
        PerforceRestStub.login(
            host=conn_info["host"],
            port=conn_info["port"],
            username=conn_info["username"],
            password=conn_info["password"],
            workspace_name=conn_info["workspace_name"]
        )

    def get_changes(self):
        return PerforceRestStub.get_changes()

    def sync_to(self, change_id):
        if not self.enabled:
            return

        if not self._conn_info:
            raise RuntimeError("Not collected conn_info")
        conn_info = self._conn_info
        self.login()
        PerforceRestStub.login(
            host=conn_info["host"],
            port=conn_info["port"],
            username=conn_info["username"],
            password=conn_info["password"],
            workspace_name=conn_info["workspace_name"]
        )
        workspace_dir = PerforceRestStub.get_workspace_dir(
            conn_info["workspace_name"])
        PerforceRestStub.sync_to_version(
            f"{workspace_dir}/...", change_id)


    def get_current_project_name(self):
        return self._current_project

    def get_current_folder_id(self):
        return self._current_folder_id

    def _create_event_system(self):
        return QueuedEventSystem()

