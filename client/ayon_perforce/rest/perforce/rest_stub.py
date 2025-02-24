import os
import requests
import pathlib
from typing import Union, Dict


class PerforceRestStub:

    @staticmethod
    def _wrap_call(command, **kwargs):
        webserver_url = os.environ.get("PERFORCE_WEBSERVER_URL")
        if not webserver_url:
            raise RuntimeError("Uknown url for Perforce")

        action_url = f"{webserver_url}/perforce/{command}"

        response = requests.post(
            action_url, json=kwargs
        )
        if not response.ok:
            print(response.content)
            raise RuntimeError(response.text)
        return response.json()

    @staticmethod
    def is_in_any_workspace(path: Union[str, pathlib.Path]) -> Dict:
        response = PerforceRestStub._wrap_call(
            "is_in_any_workspace", path=path)
        return response

    @staticmethod
    def login(
        host: str,
        port: int,
        username: str,
        password: str,
        workspace_name: str
    ):
        response = PerforceRestStub._wrap_call(
            "login",
            host=host,
            port=port,
            username=username,
            password=password,
            workspace_name=workspace_name)
        return response

    @staticmethod
    def add(path: Union[str, pathlib.Path], comment: str="") -> Dict:
        response = PerforceRestStub._wrap_call(
            "add", path=path, comment=comment)
        return response

    @staticmethod
    def sync_latest_version(path: Union[str, pathlib.Path]) -> Dict:
        response = PerforceRestStub._wrap_call(
            "sync_latest_version", path=path)
        return response

    @staticmethod
    def sync_to_version(path: Union[str, pathlib.Path], version: int) -> Dict:
        response = PerforceRestStub._wrap_call(
            "sync_to_version", path=path, version=version)
        return response

    @staticmethod
    def checkout(path: Union[str, pathlib.Path], comment: str="") -> Dict:
        response = PerforceRestStub._wrap_call(
            "checkout", path=path, comment=comment)
        return response

    @staticmethod
    def is_checkouted(path: Union[str, pathlib.Path]) -> Dict:
        response = PerforceRestStub._wrap_call(
            "is_checkouted", path=path)
        return response

    @staticmethod
    def get_last_change_list() -> Dict:
        response = PerforceRestStub._wrap_call("get_last_change_list")
        return response

    @staticmethod
    def get_changes() -> Dict:
        response = PerforceRestStub._wrap_call("get_changes")
        return response

    @staticmethod
    def submit_change_list(comment: str) -> Dict:
        response = PerforceRestStub._wrap_call(
            "submit_change_list", comment=comment)
        return response

    @staticmethod
    def exists_on_server(path: Union[str, pathlib.Path]) -> Dict:
        response = PerforceRestStub._wrap_call(
            "exists_on_server", path=path)
        return response

    @staticmethod
    def get_stream(workspace_name: str) -> Dict:
        response = PerforceRestStub._wrap_call(
            "get_stream", workspace_name=workspace_name)
        return response

    @staticmethod
    def get_workspace_dir(workspace_name: str) -> Dict:
        response = PerforceRestStub._wrap_call(
            "get_workspace_dir", workspace_name=workspace_name)
        return response
