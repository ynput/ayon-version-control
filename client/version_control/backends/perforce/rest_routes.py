import json
import datetime
from bson.objectid import ObjectId
from aiohttp.web_response import Response


from openpype.lib import Logger
from openpype.modules.webserver.base_routes import RestApiEndpoint

from version_control.backends.perforce.backend import (
    VersionControlPerforce
)
from version_control.backends.perforce import api


log = Logger.get_logger("P4routes")


class PerforceRestApiEndpoint(RestApiEndpoint):
    def __init__(self):
        super(PerforceRestApiEndpoint, self).__init__()

    @staticmethod
    def json_dump_handler(value):
        if isinstance(value, datetime.datetime):
            return value.isoformat()
        if isinstance(value, ObjectId):
            return str(value)
        if isinstance(value, set):
            return list(value)
        raise TypeError(value)

    @classmethod
    def encode(cls, data):
        return json.dumps(
            data,
            indent=4,
            default=cls.json_dump_handler
        ).encode("utf-8")


class LoginEndpoint(PerforceRestApiEndpoint):
    """Returns list of workspaces."""
    async def post(self, request) -> Response:
        content = await request.json()
        result = api.login(content["host"], content["port"],
                           content["username"], content["password"],
                           content["workspace"])
        return Response(
            status=200,
            body=self.encode(result),
            content_type="application/json"
        )


class IsPathInAnyWorkspace(PerforceRestApiEndpoint):
    """Returns list of workspaces."""
    async def post(self, request) -> Response:
        content = await request.json()
        result = api._is_path_under_any_root(content["path"])
        return Response(
            status=200,
            body=self.encode(result),
            content_type="application/json"
        )


class AddEndpoint(PerforceRestApiEndpoint):
    """Returns list of dict with project info (id, name)."""
    async def post(self, request) -> Response:
        log.info("AddEndpoint called")
        content = await request.json()

        result = VersionControlPerforce.add(content["path"],
                                            content["comment"])
        return Response(
            status=200,
            body=self.encode(result),
            content_type="application/json"
        )


class SyncLatestEndpoint(PerforceRestApiEndpoint):
    """Returns list of dict with project info (id, name)."""
    async def post(self, request) -> Response:
        log.info("SyncLatestEndpoint called")
        content = await request.json()

        result = VersionControlPerforce.sync_latest_version(content["path"])
        return Response(
            status=200,
            body=self.encode(result),
            content_type="application/json"
        )


class SyncVersionEndpoint(PerforceRestApiEndpoint):
    """Returns list of dict with project info (id, name)."""
    async def post(self, request) -> Response:
        log.info("SyncVersionEndpoint called")
        content = await request.json()

        result = VersionControlPerforce.sync_to_version(content["path"],
                                                        content["version"])
        return Response(
            status=200,
            body=self.encode(result),
            content_type="application/json"
        )


class CheckoutEndpoint(PerforceRestApiEndpoint):
    """Returns list of dict with project info (id, name)."""
    async def post(self, request) -> Response:
        log.info("CheckoutEndpoint called")

        content = await request.json()

        result = VersionControlPerforce.checkout(content["path"],
                                                 content["comment"])
        return Response(
            status=200,
            body=self.encode(result),
            content_type="application/json"
        )


class IsCheckoutedEndpoint(PerforceRestApiEndpoint):
    """Checks if file is checkouted by sameone."""
    async def post(self, request) -> Response:
        log.info("CheckoutEndpoint called")

        content = await request.json()

        result = VersionControlPerforce.is_checkedout(content["path"])
        return Response(
            status=200,
            body=self.encode(result),
            content_type="application/json"
        )


class GetLastChangelist(PerforceRestApiEndpoint):
    """Returns list of dict with project info (id, name)."""
    async def post(self, request) -> Response:
        log.info("GetLatestChangelist called")
        content = await request.json()

        result = VersionControlPerforce.get_last_change_list()
        return Response(
            status=200,
            body=self.encode(result),
            content_type="application/json"
        )


class SubmitChangelist(PerforceRestApiEndpoint):
    """Returns list of dict with project info (id, name)."""
    async def post(self, request) -> Response:
        log.info("SubmitChangelist called")
        content = await request.json()

        result = VersionControlPerforce.submit_change_list(content["comment"])
        return Response(
            status=200,
            body=self.encode(result),
            content_type="application/json"
        )


class ExistsOnServer(PerforceRestApiEndpoint):
    """Returns information about file on 'path'."""
    async def post(self, request) -> Response:
        log.info("exists_on_server called")
        content = await request.json()

        result = VersionControlPerforce.exists_on_server(content["path"])
        return Response(
            status=200,
            body=self.encode(result),
            content_type="application/json"
        )


class GetServerVersionEndpoint(PerforceRestApiEndpoint):
    """Returns list of dict with project info (id, name)."""
    async def get(self) -> Response:
        result = VersionControlPerforce.get_server_version()
        return Response(
            status=200,
            body=self.encode(result),
            content_type="application/json"
        )
