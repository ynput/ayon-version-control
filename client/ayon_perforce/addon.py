import os
from typing import Any

from ayon_core.addon import AYONAddon, ITrayService, IPluginPaths
from ayon_core.settings import get_project_settings
from ayon_core.lib import filter_profiles

from .version import __version__
from .lib import WorkspaceProfileContext


PERFORCE_ADDON_DIR = os.path.dirname(os.path.abspath(__file__))


class PerforceAddon(AYONAddon, ITrayService, IPluginPaths):
    
    label = "Perforce"
    name = "ayon_perforce"
    version = __version__
    
    # _icon_name = "mdi.jira"
    # _icon_scale = 1.3
    webserver = None

    # Properties:
    @property
    def name(self) -> str:
        return "perforce"

    @property
    def label(self) -> str:
        return f"Perforce Version Control"

    # Public Methods:
    def initialize(self, settings: dict[str, Any]):
        vc_settings = settings.get(self.name)  # type: dict[str, Any]
        enabled = vc_settings and vc_settings["enabled"]  # type: bool
        self.set_service_running_icon() if enabled else self.set_service_failed_icon()

    def get_global_environments(self):
        return {}

    def get_connection_info(
        self,
        project_name: str,
        project_settings: dict = None,
        context: WorkspaceProfileContext = None
    ):
        if not project_settings:
            project_settings = get_project_settings(project_name)

        settings = project_settings["perforce"]
        local_setting = settings["local_setting"]

        workspace_name = None
        filtering_criteria = {
            "folder_paths": None,
            "task_names": None,
            "task_types": None
        }
        if context:
            filtering_criteria = {
                "folder_paths": context.folder_paths,
                "task_names": context.task_names,
                "task_types": context.task_types
            }
        profile = filter_profiles(
            local_setting["workspace_profiles"],
            filtering_criteria,
            logger=self.log
        )
        if profile:
            workspace_name = profile["workspace_name"]

        return {
            "host": settings["host_name"],
            "port": settings["port"],
            "username": local_setting["username"],
            "password": local_setting["password"],
            "workspace_name": workspace_name
        }

    def sync_to_version(self, conn_info, change_id):
        from ayon_perforce.rest.perforce.rest_stub import PerforceRestStub

        PerforceRestStub.login(
            host=conn_info["host"],
            port=conn_info["port"],
            username=conn_info["username"],
            password=conn_info["password"],
            workspace=conn_info["workspace_dir"]
        )
        PerforceRestStub.sync_to_version(
            f"{conn_info['workspace_dir']}/...", change_id)
        return

    def tray_exit(self):
        if self.enabled and \
                self.webserver and self.webserver.server_is_running:
            self.webserver.stop()

    def tray_init(self):
        return

    def tray_start(self):
        if self.enabled:
            from ayon_perforce.rest.communication_server import WebServer
            self.webserver = WebServer()
            self.webserver.start()

    def get_plugin_paths(self):
        return {}

    def get_create_plugin_paths(self, host_name):
        if host_name != "unreal":
            return []
        return ["{}/plugins/create/unreal".format(PERFORCE_ADDON_DIR)]

    def get_publish_plugin_paths(self, host_name):
        return [os.path.join(PERFORCE_ADDON_DIR, "plugins", "publish")]

    def get_launch_hook_paths(self, _app):
        """Implementation for applications launch hooks.

        Returns:
            (str): full absolute path to directory with hooks for the module
        """

        return os.path.join(PERFORCE_ADDON_DIR, "launch_hooks")


def is_perforce_enabled(project_settings):
    return project_settings.get("perforce", {}).get("enabled", False)
