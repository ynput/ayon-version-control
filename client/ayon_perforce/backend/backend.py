"""Perforce backend."""
from __future__ import annotations
from pathlib import Path

from . import api

from typing import Union, Optional, Tuple


class PerforceBackend:  # noqa: PLR0904
    """Perforce backend."""
    # Public Properties:
    @staticmethod
    def get_server_version(
        path: Union[str, Path]
    ) -> Union[int, dict[str, int], None]:
        """Get the revision from the server of the given path.

        Args:
            path (Union[str, Path]): Path to the file or folder.

        Returns:
            Union[int, dict[str, int], None]: Revision number or None 
                if the file or folder does not exist.

        """
        return api.get_current_server_revision(path)

    @staticmethod
    def get_local_version(path: Union[str, Path]) -> Optional[int]:
        return api.get_current_client_revision(path)

    @staticmethod
    def get_version_info(
        path: Union[str, Path]
    ) -> Tuple[Union[int, None], Union[int, None]]:
        return api.get_version_info(path)

    @staticmethod
    def is_latest_version(path: Union[str, Path]) -> bool:
        return api.is_latest(path)

    @staticmethod
    def is_checkedout(path: Union[str, Path]) -> bool:
        return api.is_checked_out(path)

    @staticmethod
    def checked_out_by(
        path: Union[str, pathlib.Path],
        other_users_only: bool=False
    ) -> Optional[list[str]]:
        return api.checked_out_by(path, other_users_only=other_users_only)

    @staticmethod
    def exists_on_server(path: Union[str, pathlib.Path]) -> bool:
        if not api.get_stat(path, ["-m 1"]):
            return False

        return True

    @staticmethod
    def sync_latest_version(path: Union[str, pathlib.Path]) -> bool:
        return api.get_latest(path)

    @staticmethod
    def sync_to_version(
        path: Union[str, pathlib.Path],
        version: int
    ) -> bool:
        return api.get_revision(path, version)

    @staticmethod
    def add(path: Union[str, pathlib.Path], comment:str ="") -> bool:
        return api.add(path, change_description=comment)

    @staticmethod
    def add_to_change_list(
        path: Union[str, pathlib.Path],
        comment: str
    ) -> bool:
        return api.add_to_change_list(path, comment)

    @staticmethod
    def checkout(
        path: Union[str, pathlib.Path],
        comment: str
    ) -> bool:
        return api.checkout(path, change_description=comment)

    @staticmethod
    def revert(path: Union[str, pathlib.Path]) -> bool:
        return api.revert(path)

    @staticmethod
    def move(
        path: Union[str, pathlib.Path],
        new_path: Union[str, pathlib.Path],
        change_description: Optional[str]=None
    ) -> bool:
        return api.move(path, new_path, change_description=change_description)

    @staticmethod
    def get_changes() -> Optional[list[dict]]:
        return api.get_changes()

    @staticmethod
    def get_existing_change_list(comment: str) -> Optional[dict]:
        return api.get_existing_change_list(comment)

    @staticmethod
    def get_last_change_list() -> Optional[list[dict]]:
        return api.get_last_change_list()

    @staticmethod
    def get_files_in_folder_in_date_order(
        path: Union[str, pathlib.Path],
        name_pattern: Optional[str]=None,
        extensions: Optional[list[str]]=None
    ) -> tuple:
        return tuple(
            (
                data.path for data in api.get_files_in_folder_in_date_order(
                    path, name_pattern=name_pattern, extensions=extensions
                ) or []
            )
        )

    @staticmethod
    def get_newest_file_in_folder(
        path: Union[str, pathlib.Path],
        name_pattern: Optional[str] = None,
        extensions: Optional[list[str]] = None
    ) -> Optional[pathlib.Path]:
        result = api.get_newest_file_in_folder(
            path, name_pattern=name_pattern, extensions=extensions
        )
        if result is None:
            return

        return result.path

    @staticmethod
    def submit_change_list(comment: str) -> int:
        return api.submit_change_list(comment)

    @staticmethod
    def update_change_list_description(comment: str, new_comment: str) -> bool:
        return api.update_change_list_description(comment, new_comment)

    @staticmethod
    def get_stream(workspace_name: str) -> str:
        result = api.run_command("client", ["-o", workspace_name])
        return result.get("Stream")

    @staticmethod
    def get_workspace_dir(workspace_name: str) -> str:
        result = api.run_command("client", ["-o", workspace_name])
        return result.get("Root")
