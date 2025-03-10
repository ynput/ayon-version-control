"""Rest routes for Perforce backend."""
from __future__ import annotations

import datetime
import json
from typing import Any, Union

from aiohttp.web import Request, Response
from ayon_core.lib import Logger
from ayon_core.tools.tray.webserver.base_routes import RestApiEndpoint

from ayon_perforce.backend import api
from ayon_perforce.backend.backend import PerforceBackend

log = Logger.get_logger("P4routes")


class PerforceRestApiEndpoint(RestApiEndpoint):
    """Base class for Perforce Rest API endpoints."""
    def __init__(self):
        """Init."""
        super().__init__()

    @staticmethod
    def json_dump_handler(value: Any) -> Union[list, str]:  # noqa: ANN401
        """Custom JSON dump handler.

        Returns:
            str: JSON dump of the value.

        Raises:
            TypeError: If value is not supported.

        """
        if isinstance(value, datetime.datetime):
            return value.isoformat()
        if isinstance(value, set):
            return list(value)
        raise TypeError(value)

    @classmethod
    def encode(cls, data: Any) -> bytes:  # noqa: ANN401
        """Encode data to JSON.

        Returns:
            bytes: Encoded JSON data.

        """
        return json.dumps(
            data,
            indent=4,
            default=cls.json_dump_handler
        ).encode("utf-8")


class LoginEndpoint(PerforceRestApiEndpoint):
    """Returns list of workspaces."""
    async def post(self, request: Request) -> Response:
        """Login to Perforce server.

        Returns:
            Response: Response object.

        """
        content = await request.json()
        result = api.login(
            content["host"],
            content["port"],
            content["username"],
            content["password"],
            content["workspace_name"]
        )
        return Response(
            status=200,
            body=self.encode(result),
            content_type="application/json"
        )


class IsPathInAnyWorkspace(PerforceRestApiEndpoint):
    """Returns list of workspaces."""
    async def post(self, request: Request) -> Response:
        """Login to Perforce server.

        Returns:
            Response: Response object.

        """
        content = await request.json()
        result = api.is_path_under_any_root(content["path"])
        return Response(
            status=200,
            body=self.encode(result),
            content_type="application/json"
        )


class AddEndpoint(PerforceRestApiEndpoint):
    """Returns list of dict with project info (id, name)."""
    async def post(self, request: Request) -> Response:
        """Add file to Perforce.

        Returns:
            Response: Response object.

        """
        log.debug("AddEndpoint called")
        content = await request.json()

        result = PerforceBackend.add(content["path"],
                                            content["comment"])
        return Response(
            status=200,
            body=self.encode(result),
            content_type="application/json"
        )


class SyncLatestEndpoint(PerforceRestApiEndpoint):
    """Returns list of dict with project info (id, name)."""
    async def post(self, request: Request) -> Response:
        """Sync latest version of file.

        Returns:
            Response: Response object.

        """
        log.debug("SyncLatestEndpoint called")
        content = await request.json()

        result = PerforceBackend.sync_latest_version(content["path"])
        return Response(
            status=200,
            body=self.encode(result),
            content_type="application/json"
        )


class SyncVersionEndpoint(PerforceRestApiEndpoint):
    """Returns list of dict with project info (id, name)."""
    async def post(self, request: Request) -> Response:
        """Sync to specific version of file.

        Returns:
            Response: Response object

        """
        log.debug("SyncVersionEndpoint called")
        content = await request.json()

        log.debug(
            "Syncing '%s' to %s", content["path"], content["version"])
        result = PerforceBackend.sync_to_version(
            content["path"], content["version"])
        log.debug("Synced")
        return Response(
            status=200,
            body=self.encode(result),
            content_type="application/json"
        )


class CheckoutEndpoint(PerforceRestApiEndpoint):
    """Returns list of dict with project info (id, name)."""
    async def post(self, request: Request) -> Response:
        """Checkout file.

        Returns:
            Response: Response object

        """
        log.debug("CheckoutEndpoint called")

        content = await request.json()

        result = PerforceBackend.checkout(content["path"],
                                                 content["comment"])
        return Response(
            status=200,
            body=self.encode(result),
            content_type="application/json"
        )


class IsCheckoutedEndpoint(PerforceRestApiEndpoint):
    """Checks if file is checkouted by sameone."""
    async def post(self, request: Request) -> Response:
        """Check if file is checked out.

        Returns:
            Response: Response object

        """
        log.debug("CheckoutEndpoint called")

        content = await request.json()

        result = PerforceBackend.is_checkedout(content["path"])
        return Response(
            status=200,
            body=self.encode(result),
            content_type="application/json"
        )


class GetChanges(PerforceRestApiEndpoint):
    """Returns list of submitted changes."""
    async def post(self, request: Request) -> Response:
        """Get list of changes.

        Returns:
            Response: Response object

        """
        log.debug("GetChanges called")
        _ = await request.json()

        result = PerforceBackend.get_changes()
        return Response(
            status=200,
            body=self.encode(result),
            content_type="application/json"
        )


class GetLastChangelist(PerforceRestApiEndpoint):
    """Returns the latest change list."""
    async def post(self, request: Request) -> Response:
        """Get the latest changelist.

        Returns:
            Response: Response object

        """
        log.debug("GetLatestChangelist called")
        _ = await request.json()

        result = PerforceBackend.get_last_change_list()
        return Response(
            status=200,
            body=self.encode(result),
            content_type="application/json"
        )


class SubmitChangelist(PerforceRestApiEndpoint):
    """Submit changelist."""
    async def post(self, request: Request) -> Response:
        """Submit changelist.

        Returns:
            Response: Response object

        """
        log.debug("SubmitChangelist called")
        content = await request.json()

        result = PerforceBackend.submit_change_list(content["comment"])
        return Response(
            status=200,
            body=self.encode(result),
            content_type="application/json"
        )


class ExistsOnServer(PerforceRestApiEndpoint):
    """Returns information about file on 'path'."""
    async def post(self, request: Request) -> Response:
        """Check if file exists on server.

        Returns:
            Response: Response object

        """
        log.debug("exists_on_server called")
        content = await request.json()

        result = PerforceBackend.exists_on_server(content["path"])
        return Response(
            status=200,
            body=self.encode(result),
            content_type="application/json"
        )


class GetServerVersionEndpoint(PerforceRestApiEndpoint):
    """Returns the version on the server."""
    async def get(self) -> Response:
        """Get server version.

        Returns:
            Response: Response object

        """
        result = PerforceBackend.get_server_version()
        return Response(
            status=200,
            body=self.encode(result),
            content_type="application/json"
        )


class GetStreamEndpoint(PerforceRestApiEndpoint):
    """Returns stream attached to workspace."""
    async def post(self, request: Request) -> Response:
        """Get stream attached to workspace.

        Returns:
            Response: Response object

        """
        content = await request.json()

        result = PerforceBackend.get_stream(content["workspace_name"])
        return Response(
            status=200,
            body=self.encode(result),
            content_type="application/json"
        )


class GetWorkspaceDirEndpoint(PerforceRestApiEndpoint):
    """Returns stream attached to workspace."""
    async def post(self, request: Request) -> Response:
        """Get workspace directory.

        Returns:
            Response: Response object

        """
        content = await request.json()

        result = PerforceBackend.get_workspace_dir(
            content["workspace_name"]
        )
        return Response(
            status=200,
            body=self.encode(result),
            content_type="application/json"
        )
