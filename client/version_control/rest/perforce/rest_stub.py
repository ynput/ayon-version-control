import six
import os
import requests

if six.PY2:
    import pathlib2 as pathlib
else:
    import pathlib

_typing = False
if _typing:
    from typing import Any
    from typing import Sequence
del _typing


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
    def is_in_any_workspace(path):
        response = PerforceRestStub._wrap_call("is_in_any_workspace",
                                               path=path)
        return response

    @staticmethod
    def login(host, port, username, password, workspace_name):
        # type: (None | str, int, str, str, str) -> dict
        response = PerforceRestStub._wrap_call(
            "login",
            host=host,
            port=port,
            username=username,
            password=password,
            workspace_name=workspace_name)
        return response

    @staticmethod
    def add(path, comment=""):
        # type: (pathlib.Path | str, str) -> bool
        response = PerforceRestStub._wrap_call("add",
                                               path=path,
                                               comment=comment)
        return response

    @staticmethod
    def sync_latest_version(path):
        response = PerforceRestStub._wrap_call("sync_latest_version",
                                               path=path)
        return response

    @staticmethod
    def sync_to_version(path, version):
        response = PerforceRestStub._wrap_call("sync_to_version",
                                               path=path,
                                               version=version)
        return response

    @staticmethod
    def checkout(path, comment=""):
        response = PerforceRestStub._wrap_call("checkout",
                                               path=path,
                                               comment=comment)
        return response

    @staticmethod
    def is_checkouted(path):
        response = PerforceRestStub._wrap_call("is_checkouted",
                                               path=path)
        return response

    @staticmethod
    def get_last_change_list():
        # type: (None) -> dict
        response = PerforceRestStub._wrap_call("get_last_change_list")
        return response

    @staticmethod
    def get_changes():
        # type: (None) -> dict
        response = PerforceRestStub._wrap_call("get_changes")
        return response

    @staticmethod
    def submit_change_list(comment):
        response = PerforceRestStub._wrap_call("submit_change_list",
                                               comment=comment)
        return response

    @staticmethod
    def exists_on_server(path):
        response = PerforceRestStub._wrap_call("exists_on_server",
                                               path=path)
        return response

    @staticmethod
    def get_stream(workspace_name):
        response = PerforceRestStub._wrap_call("get_stream",
                                               workspace_dir=workspace_name)
        return response

    @staticmethod
    def get_workspace_dir(workspace_name):
        response = PerforceRestStub._wrap_call("get_workspace_dir",
                                               workspace_name=workspace_name)
        return response
