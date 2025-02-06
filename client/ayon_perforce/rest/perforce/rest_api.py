from aiohttp.web_response import Response
from ayon_core.lib import Logger

from ayon_perforce.backends.perforce import rest_routes


class PerforceModuleRestAPI:
    """
    REST API endpoint used for Perforce operations
    """

    def __init__(self, server_manager):
        self._log = None
        self.server_manager = server_manager
        self.prefix = "/perforce"

    @property
    def log(self):
        if self._log is None:
            self._log = Logger.get_logger(self.__class__.__name__)
        return self._log

    def register(self):
        login = rest_routes.LoginEndpoint()
        self.server_manager.add_route(
            "POST",
            self.prefix + "/login",
            login.dispatch
        )

        is_in_any_workspace = rest_routes.IsPathInAnyWorkspace()
        self.server_manager.add_route(
            "POST",
            self.prefix + "/is_in_any_workspace",
            is_in_any_workspace.dispatch
        )

        add_file = rest_routes.AddEndpoint()
        self.server_manager.add_route(
            "POST",
            self.prefix + "/add",
            add_file.dispatch
        )

        sync_latest_version = rest_routes.SyncLatestEndpoint()
        self.server_manager.add_route(
            "POST",
            self.prefix + "/sync_latest_version",
            sync_latest_version.dispatch
        )

        sync_to_version = rest_routes.SyncVersionEndpoint()
        self.server_manager.add_route(
            "POST",
            self.prefix + "/sync_to_version",
            sync_to_version.dispatch
        )

        checkout = rest_routes.CheckoutEndpoint()
        self.server_manager.add_route(
            "POST",
            self.prefix + "/checkout",
            checkout.dispatch
        )

        is_checkouted = rest_routes.IsCheckoutedEndpoint()
        self.server_manager.add_route(
            "POST",
            self.prefix + "/is_checkouted",
            is_checkouted.dispatch
        )

        get_changes = rest_routes.GetChanges()
        self.server_manager.add_route(
            "POST",
            self.prefix + "/get_changes",
            get_changes.dispatch
        )

        get_last_change_list = rest_routes.GetLastChangelist()
        self.server_manager.add_route(
            "POST",
            self.prefix + "/get_last_change_list",
            get_last_change_list.dispatch
        )

        submit_change_list = rest_routes.SubmitChangelist()
        self.server_manager.add_route(
            "POST",
            self.prefix + "/submit_change_list",
            submit_change_list.dispatch
        )

        exists_on_server = rest_routes.ExistsOnServer()
        self.server_manager.add_route(
            "POST",
            self.prefix + "/exists_on_server",
            exists_on_server.dispatch
        )

        get_stream = rest_routes.GetStreamEndpoint()
        self.server_manager.add_route(
            "POST",
            self.prefix + "/get_stream",
            get_stream.dispatch
        )

        get_workspace_dir = rest_routes.GetWorkspaceDirEndpoint()
        self.server_manager.add_route(
            "POST",
            self.prefix + "/get_workspace_dir",
            get_workspace_dir.dispatch
        )
