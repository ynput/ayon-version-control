"""Controller for the changes viewer."""
from __future__ import annotations

import os
from logging import getLogger
from typing import TYPE_CHECKING, Union

import requests

if TYPE_CHECKING:
    import pathlib


log = getLogger(__name__)


class PerforceRestStub:
    """Perforce REST API stub."""

    @staticmethod
    def _wrap_call(
            command: str,
            **kwargs: Union[str, int, pathlib.Path]) -> dict:
        """Wrap the call to the Perforce REST API.

        Args:
            command (str): Command to call.
            kwargs: Arguments for the command.

        Returns:
            dict: Response from the server.

        Raises:
            RuntimeError: If the server response is not OK.

        """
        webserver_url = os.environ.get("PERFORCE_WEBSERVER_URL")
        if not webserver_url:
            msg = "Unknown url for Perforce"
            raise RuntimeError(msg)

        action_url = f"{webserver_url}/perforce/{command}"

        response = requests.post(
            action_url, json=kwargs, timeout=10
        )
        if not response.ok:
            log.debug(response.content)
            raise RuntimeError(response.text)
        return response.json()

    @staticmethod
    def is_in_any_workspace(path: Union[str, pathlib.Path]) -> dict:
        """Check if the path is in any workspace.

        Args:
            path (str): Path to check.

        Returns:
            dict: Response from the server.

        """
        return PerforceRestStub._wrap_call(
            "is_in_any_workspace", path=path)

    @staticmethod
    def login(
        host: str,
        port: int,
        username: str,
        password: str,
        workspace_name: str
    ) -> dict:
        """Login to Perforce server.

        Args:
            host (str): Host name.
            port (int): Port number.
            username (str): Username.
            password (str): Password.
            workspace_name (str): Workspace name.

        Returns:
            dict: Response from the server.

        """
        return PerforceRestStub._wrap_call(
            "login",
            host=host,
            port=port,
            username=username,
            password=password,
            workspace_name=workspace_name)

    @staticmethod
    def add(path: Union[str, pathlib.Path], comment: str = "") -> dict:
        """Add file to Perforce.

        Args:
            path (str): Path to the file.
            comment (str): Comment for the change list.

        Returns:
            dict: Response from the server.

        """
        return PerforceRestStub._wrap_call(
            "add", path=path, comment=comment)

    @staticmethod
    def sync_latest_version(path: Union[str, pathlib.Path]) -> dict:
        """Sync to the latest version of the file.

        Args:
            path (str): Path to the file.

        Returns:
            dict: Response from the server.

        """
        return PerforceRestStub._wrap_call(
            "sync_latest_version", path=path)

    @staticmethod
    def sync_to_version(path: Union[str, pathlib.Path], version: int) -> dict:
        """Sync to a specific version of the file.

        Args:
            path (str): Path to the file.
            version (int): Version to sync to.

        Returns:
            dict: Response from the server.

        """
        return PerforceRestStub._wrap_call(
            "sync_to_version", path=path, version=version)

    @staticmethod
    def checkout(path: Union[str, pathlib.Path], comment: str = "") -> dict:
        """Checkout file from Perforce.

        Args:
            path (str): Path to the file.
            comment (str): Comment for the change list.

        Returns:
            dict: Response from the server.

        """
        return PerforceRestStub._wrap_call(
            "checkout", path=path, comment=comment)

    @staticmethod
    def is_checkouted(path: Union[str, pathlib.Path]) -> dict:
        """Check if the file is checked out.

        Args:
            path (str): Path to the file.

        Returns:
            dict: Response from the server.

        """
        return PerforceRestStub._wrap_call(
            "is_checkouted", path=path)

    @staticmethod
    def get_last_change_list() -> dict:
        """Get the last change list.

        Returns:
            dict: Response from the server.

        """
        return PerforceRestStub._wrap_call("get_last_change_list")

    @staticmethod
    def get_changes() -> dict:
        """Get changes from Perforce.

        Returns:
            dict: Changes from Perforce

        """
        return PerforceRestStub._wrap_call("get_changes")

    @staticmethod
    def submit_change_list(comment: str) -> dict:
        """Submit the change list.

        Args:
            comment (str): Comment for the change list.

        Returns:
            dict: Response from the server.

        """
        return PerforceRestStub._wrap_call(
            "submit_change_list", comment=comment)

    @staticmethod
    def exists_on_server(path: Union[str, pathlib.Path]) -> dict:
        """Check if the file exists on the server.

        Returns:
            dict: Response from the server.

        """
        return PerforceRestStub._wrap_call(
            "exists_on_server", path=path)

    @staticmethod
    def get_stream(workspace_name: str) -> dict:
        """Get stream for the workspace.

        Args:
            workspace_name (str): Name of the workspace.

        Returns:
            dict: Response from the server.

        """
        return PerforceRestStub._wrap_call(
            "get_stream", workspace_name=workspace_name)

    @staticmethod
    def get_workspace_dir(workspace_name: str) -> dict:
        """Get workspace directory.

        Args:
            workspace_name (str): Name of the workspace.

        Returns:
            dict: Response from the server.

        """
        return PerforceRestStub._wrap_call(
            "get_workspace_dir", workspace_name=workspace_name)
