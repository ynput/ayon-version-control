from ayon_core.lib.events import QueuedEventSystem
from ayon_core.pipeline import (
    registered_host,
)
from ayon_core.addon import AddonsManager
from version_control.rest.perforce.rest_stub import PerforceRestStub


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
        version_control_addon = manager.get("version_control")
        self._version_control_addon = version_control_addon
        self.enabled = version_control_addon and version_control_addon.enabled

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

        conn_info = self._version_control_addon.get_connection_info(
            project_name=self.get_current_project_name()
        )

        if conn_info:
            self._conn_info = conn_info
            PerforceRestStub.login(host=conn_info["host"],
                                   port=conn_info["port"],
                                   username=conn_info["username"],
                                   password=conn_info["password"],
                                   workspace=conn_info["workspace_dir"])

    def get_changes(self):
        return PerforceRestStub.get_changes()

    def sync_to(self, change_id):
        if not self.enabled:
            return

        conn_info = self._version_control_addon.get_connection_info(
            project_name=self.get_current_project_name()
        )
        if conn_info:
            self._conn_info = conn_info
            self._version_control_addon.sync_to_version(conn_info, change_id)

    def get_current_project_name(self):
        return self._current_project

    def get_current_folder_id(self):
        return self._current_folder_id

    def _create_event_system(self):
        return QueuedEventSystem()

