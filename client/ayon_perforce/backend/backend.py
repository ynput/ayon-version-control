import os.path

import six

from . import api
from .. import abstract

if six.PY2:
    import pathlib2 as pathlib
else:
    import pathlib

_typing = False
if _typing:
    from typing import Any
    from typing import Sequence
del _typing


def _save_file_decorator(function):
    # type: (Callable[[str], str]) -> Callable[[str], str]

    from . import get_active_vcs

    vcs = get_active_vcs()

    @functools.wraps(function)
    def save_file_wrapper(path):
        # type: (str) -> str
        if vcs is None:
            return function(path)

        vcs.checkout(path)
        return function(path)

    return save_file_wrapper


def _open_file_decorator(function):
    # type: (Callable[[str], str]) -> Callable[[str], str]
    @functools.wraps(function)
    def open_file_wrapper(path):
        # type: (str) -> str
        return function(path)

    return open_file_wrapper


class PerforceBackend:

    # Public Properties:
    @property
    def settings(self):
        return self._settings

    @property
    def saved_change_list_descriptions(self):
        try:
            return self.settings.get_item("change_list_descriptions")
        except ValueError:
            return {}

    @property
    def host_app_name(self):
        # type: () -> str
        """
        # Property:
        Get the name of the registerd host application
        """

        return os.environ["AVALON_APP"]

    @property
    def change_list_description_prefix(self):
        # type: () -> str
        """
        # Property:
        Get the prefix to be added to any given change list description.
        It follows the following convention:
        `[art][{parent}][{asset_name}][{task_type}][{task_name}]`

        This provides tags for UnrealGameSync.

        TODO: Have this be togglable via settings.
        TODO: Have this definable via the template system.
        """

        from openpype.pipeline import legacy_io

        legacy_io.install()
        project_name = legacy_io.Session["AVALON_PROJECT"]  # type: str
        asset_name = legacy_io.Session["AVALON_ASSET"]  # type: str
        task_name = legacy_io.Session["AVALON_TASK"]  # type: str

        project_entity = legacy_io.find_one(
            {"type": "project", "name": project_name})
        assert project_entity, ("Project '{0}' was not found.").format(
            project_name)

        asset_entity = legacy_io.find_one(
            {"type": "asset", "name": asset_name,
             "parent": project_entity["_id"]}
        )
        assert asset_entity, (
            "No asset found by the name '{0}' in project '{1}'").format(
            asset_name, project_name
        )

        data = asset_entity["data"]

        asset_tasks = data.get("tasks") or {}
        task_info = asset_tasks.get(task_name) or {}
        task_type = task_info.get("type") or ""
        parents = data.get("parents") or []
        parent = "[{}]".format(parents[-1]) if parents else ""

        return "[Art]{p}[{an}][{tt}][{tn}]".format(
            p=parent, an=asset_name, tt=task_type, tn=task_name
        )

    @property
    def cached_change_list_description(self):
        # type: () -> str
        """
        # Property:
        Get the currently cached change list description for the current host.
        This will be the last description used, but only if the change list still
        exists. If the change list exists, the cached description will be returned.
        If the change list does not exists, the default change list description will
        be returned.
        """

        host_app_name = self.host_app_name
        change_list_descriptions = (
            self.saved_change_list_descriptions
        )  # type: dict[str, str] | None
        if not change_list_descriptions:
            return self._default_change_list_description

        change_list_description = change_list_descriptions.get(host_app_name)
        if not change_list_description:
            return self._default_change_list_description

        if not self.get_existing_change_list(change_list_description):
            return self._default_change_list_description

        return change_list_description

    @cached_change_list_description.setter
    def cached_change_list_description(self, value):
        # type: (str) -> None
        assert isinstance(
            value, str
        ), "cached_change_list_description must be an instance of {0}. Got: {1} of type: {type(value)}".format(
            str, value
        )

        change_list_descriptions = self.saved_change_list_descriptions
        change_list_descriptions[self.host_app_name] = value
        change_list_descriptions = self.settings.set_item(
            "change_list_descriptions", change_list_descriptions
        )

    @property
    def save_file_decorator(self):
        # type: () -> Callable[[Callable[[str], str]], Callable[[str], str]]
        return _save_file_decorator

    @property
    def open_file_decorator(self):
        # type: () -> Callable[[Callable[[str], str]], Callable[[str], str]]
        return _open_file_decorator

    @property
    def change_list_description(self):
        # type: () -> str
        """
        #Property:
        The current change list comment, if one has been set.
        This allows recovery of a change list comment if the publish process
        fails or the user chooses not to submit the change list.
        """

        _change_list_description = self._change_list_description
        if not _change_list_description:
            _change_list_description = self.cached_change_list_description

        if not _change_list_description.startswith("["):
            _change_list_description = "{0} {1}".format(
                self.change_list_description_prefix, _change_list_description
            )

        self._change_list_description = _change_list_description

        return _change_list_description

    @change_list_description.setter
    def change_list_description(self, value):
        # type: (str) -> None
        assert isinstance(
            value, str
        ), "change_list_description must be an instance of {0}. Got: {1} of type: {type(value)}".format(
            str, value
        )
        d
        if value == self._change_list_description:
            return

        if not value.startswith("["):
            value = value[1:] if value.startswith(" ") else value
            value = "{0} {1}".format(self.change_list_description_prefix,
                                     value)

        self.cached_change_list_description = value
        self._change_list_description = value



    @staticmethod
    def get_server_version(path):
        # type: (str | pathlib.Path) -> int | None | dict[str, int | None]
        result = api.get_current_server_revision(path)
        return result

    @staticmethod
    def get_local_version(path):
        # type: (pathlib.Path | str) -> int | None
        result = api.get_current_client_revision(path)
        return result

    @staticmethod
    def get_version_info(path):
        # type: (pathlib.Path | str) -> tuple[int | None, int | None]
        result = api.get_version_info(path)
        return result

    @staticmethod
    def is_latest_version(path):
        # type: (pathlib.Path | str) -> bool | None
        return api.is_latest(path)

    @staticmethod
    def is_checkedout(path):
        # type: (pathlib.Path | str) -> bool
        return api.is_checked_out(path)

    @staticmethod
    def checked_out_by(path, other_users_only=False):
        # type: (pathlib.Path | str, bool) -> list[str] | None
        return api.checked_out_by(path, other_users_only=other_users_only)

    @staticmethod
    def exists_on_server(path):
        # type: (pathlib.Path | str) -> bool
        if not api.get_stat(path, ["-m 1"]):
            return False

        return True

    @staticmethod
    def sync_latest_version(path):
        # type: (pathlib.Path | str) -> bool | None
        return api.get_latest(path)

    @staticmethod
    def sync_to_version(path, version):
        # type: (pathlib.Path | str, int) -> bool | None
        return api.get_revision(path, version)

    @staticmethod
    def add(path, comment=""):
        # type: (pathlib.Path | str, str) -> bool
        return api.add(path, change_description=comment)

    @staticmethod
    def add_to_change_list(path, comment):
        # type: (pathlib.Path | str, str) -> bool
        return api.add_to_change_list(path, comment)

    @staticmethod
    def checkout(path, comment=""):
        # type: (pathlib.Path | str, str) -> bool
        return api.checkout(path, change_description=comment)

    @staticmethod
    def revert(path):
        # type: (pathlib.Path | str) -> bool
        return api.revert(path)

    @staticmethod
    def move(path, new_path, change_description=None):
        # type: (pathlib.Path | str, pathlib.Path | str, str | None) -> bool | None
        return api.move(path, new_path, change_description=change_description)

    @staticmethod
    def get_changes():
        # type: (None) -> (list(dict)) | None
        return api.get_changes()

    @staticmethod
    def get_existing_change_list(comment):
        # type: (str) -> dict[str, Any] | None
        return api.get_existing_change_list(comment)

    @staticmethod
    def get_last_change_list():
        # type: (str) -> (list(dict)) | None
        return api.get_last_change_list()

    @staticmethod
    def get_files_in_folder_in_date_order(path, name_pattern=None, extensions=None):
        # type: (pathlib.Path | str, str | None, Sequence[str] | None) -> tuple[pathlib.Path | None]
        return tuple(
            (
                data.path for data in api.get_files_in_folder_in_date_order(
                    path, name_pattern=name_pattern, extensions=extensions
                ) or []
            )
        )

    @staticmethod
    def get_newest_file_in_folder(path, name_pattern=None, extensions=None):
        # type: (pathlib.Path | str, str | None, Sequence[str] | None) -> pathlib.Path | None
        result = api.get_newest_file_in_folder(
            path, name_pattern=name_pattern, extensions=extensions
        )
        if result is None:
            return

        return result.path

    @staticmethod
    def submit_change_list(comment):
        # type: (str) -> int | None
        return api.submit_change_list(comment)

    @staticmethod
    def update_change_list_description(comment, new_comment):
        # type: (str, str) -> bool
        return api.update_change_list_description(comment, new_comment)

    @staticmethod
    def get_stream(workspace_name):
        # type: (str) -> str
        result = api.run_command("client", ["-o", workspace_name])
        return result.get("Stream")

    @staticmethod
    def get_workspace_dir(workspace_name):
        # type: (str) -> str
        result = api.run_command("client", ["-o", workspace_name])
        return result.get("Root")

    # Public Methods:
    def is_prefix_auto_generated(self, comment=""):
        # type: (str) -> bool
        comment = comment or self.change_list_description
        if not comment.startswith("["):
            return False

        description = comment.split("]")[-1]
        current_prefix = comment.replace(description, "")
        auto_prefix = self.change_list_description_prefix
        return current_prefix == auto_prefix
