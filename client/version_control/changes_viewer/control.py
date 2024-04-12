import ayon_api

from ayon_core.lib.events import QueuedEventSystem
from ayon_core.pipeline import (
    registered_host,
    get_current_context,
)
from ayon_core.tools.common_models import HierarchyModel
from ayon_core.modules import ModulesManager
from version_control.backends.perforce.api.rest_stub import PerforceRestStub


class ChangesViewerController:
    """This is a temporary controller for AYON.

    Goal of this controller is to provide a way to get current context.
    """

    def __init__(self, host=None):
        if host is None:
            host = registered_host()
        self._host = host
        self._current_context = None
        self._current_project = None
        self._current_folder_id = None
        self._current_folder_set = False

        # Switch dialog requirements
        self._hierarchy_model = HierarchyModel(self)
        self._event_system = self._create_event_system()

    def emit_event(self, topic, data=None, source=None):
        if data is None:
            data = {}
        self._event_system.emit(topic, data, source)

    def register_event_callback(self, topic, callback):
        self._event_system.add_callback(topic, callback)

    def reset(self):
        self._current_context = None
        self._current_project = None
        self._current_folder_id = None
        self._current_folder_set = False
        self._conn_info = None

        self._hierarchy_model.reset()

    def login(self):  # TODO push to controller
        manager = ModulesManager()
        version_control_addon = manager.get("version_control")
        if not version_control_addon or not version_control_addon.enabled:
            return

        conn_info = version_control_addon.get_connection_info(
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
        manager = ModulesManager()
        version_control_addon = manager.get("version_control")
        if not version_control_addon or not version_control_addon.enabled:
            return

        conn_info = version_control_addon.get_connection_info(
            project_name=self.get_current_project_name()
        )
        if conn_info:
            self._conn_info = conn_info
            version_control_addon.sync_to_version(conn_info, change_id)

    def get_current_context(self):
        if self._current_context is None:
            if hasattr(self._host, "get_current_context"):
                self._current_context = self._host.get_current_context()
            else:
                self._current_context = get_current_context()
        return self._current_context

    def get_current_project_name(self):
        return "ayon_test"  # TEMP!!!
        if self._current_project is None:
            self._current_project = self.get_current_context()["project_name"]
        return self._current_project

    def get_current_folder_id(self):
        if self._current_folder_set:
            return self._current_folder_id

        context = self.get_current_context()
        project_name = context["project_name"]
        folder_name = context.get("asset_name")
        folder_id = None
        if folder_name:
            folder = ayon_api.get_folder_by_path(project_name, folder_name)
            if folder:
                folder_id = folder["id"]

        self._current_folder_id = folder_id
        self._current_folder_set = True
        return self._current_folder_id

    def _create_event_system(self):
        return QueuedEventSystem()
