"""Perforce backend."""
from __future__ import annotations

from typing import TYPE_CHECKING, Optional, Tuple, Union

from . import api

if TYPE_CHECKING:
    from pathlib import Path


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
        """Get the revision from the client of the given path.

        Returns:
            Optional[int]: Revision number or None if the file or folder
                does not exist.

        """
        return api.get_current_client_revision(path)

    @staticmethod
    def get_version_info(
        path: Union[str, Path]
    ) -> Tuple[Union[int, None], Union[int, None]]:
        """Get version information of the given path.

        Returns:
            Tuple[Union[int, None], Union[int, None]]: Tuple of two integers
                where the first one is the head revision and the second one
                is the "have revision" - the revision presently in the current
                client workspace. If the file or folder does not exist,
                the value is None.

        """
        return api.get_version_info(path)

    @staticmethod
    def is_latest_version(path: Union[str, Path]) -> bool:
        """Check if the given path is the latest version.

        Returns:
            bool: True if the file is the latest version, False otherwise.

        """
        return api.is_latest(path)

    @staticmethod
    def is_checkedout(path: Union[str, Path]) -> bool:
        """Check if the given path is checked out.

        Returns:
            bool: True if the file is checked out, False otherwise.

        """
        return api.is_checked_out(path)

    @staticmethod
    def checked_out_by(
        path: Union[str, Path],
        *,
        other_users_only: bool = False
    ) -> Optional[list[str]]:
        """Get the user who checked out the file.

        Returns:
            Optional[list[str]]: List of users who checked out the file.
                If the file is not checked out, returns None.
        """
        return api.checked_out_by(path, other_users_only=other_users_only)

    @staticmethod
    def exists_on_server(path: Union[str, Path]) -> bool:
        """Check if the given path exists on the server.

        Returns:
            bool: True if the file or folder exists, False otherwise.

        """
        return bool(api.get_stat(path, ["-m 1"]))

    @staticmethod
    def sync_latest_version(path: Union[str, Path]) -> bool:
        """Sync the latest version of the given path.

        Returns:
            bool: True if the sync was successful, False otherwise.

        """
        return api.get_latest(path)

    @staticmethod
    def sync_to_version(
        path: Union[str, Path],
        version: int
    ) -> bool:
        """Sync the given path to the specified version.

        Returns:
            bool: True if the sync was successful, False otherwise.

        """
        return api.get_revision(path, version)

    @staticmethod
    def add(path: Union[str, Path], comment: str = "") -> bool:
        """Add the given path to the changelist.

        Returns:
            bool: True if the file was added, False otherwise.

        """
        return api.add(path, change_description=comment)

    @staticmethod
    def add_to_change_list(
        path: Union[str, Path],
        comment: str
    ) -> bool:
        """Add the given path to the changelist with a comment.

        Returns:
            bool: True if the file was added, False otherwise.

        """
        return api.add_to_change_list(path, comment)

    @staticmethod
    def checkout(
        path: Union[str, Path],
        comment: str
    ) -> bool:
        """Checkout the given path.

        Returns:
            bool: True if the file was checked out, False otherwise.

        """
        return api.checkout(path, change_description=comment)

    @staticmethod
    def revert(path: Union[str, Path]) -> bool:
        """Revert the given path.

        Returns:
            bool: True if the file was reverted, False otherwise.

        """
        return api.revert(path)

    @staticmethod
    def move(
        path: Union[str, Path],
        new_path: Union[str, Path],
        change_description: Optional[str] = None
    ) -> bool:
        """Move the given path to the new path.

        Returns:
            bool: True if the file was moved, False otherwise.

        """
        return api.move(path, new_path, change_description=change_description)

    @staticmethod
    def get_changes() -> Optional[list[dict]]:
        """Get the list of changes.

        Returns:
            Optional[list[dict]]: List of changes or None if there are no
                changes.

        """
        return api.get_changes()

    @staticmethod
    def get_existing_change_list(comment: str) -> Optional[dict]:
        """Get the existing change list.

        Returns:
            Optional[dict]: Change list or None if the change list does not
                exist.

        """
        return api.get_existing_change_list(comment)

    @staticmethod
    def get_last_change_list() -> Optional[list[dict]]:
        """Get the last change list.

        Returns:
            Optional[list[dict]]: Last change list or None if there is no
                change list.

        """
        return api.get_last_change_list()

    @staticmethod
    def get_files_in_folder_in_date_order(
        path: Union[str, Path],
        name_pattern: Optional[str] = None,
        extensions: Optional[list[str]] = None
    ) -> tuple:
        """Get the files in the folder in date order.

        Returns:
            tuple: Tuple of file paths in date order.

        """
        return tuple(
                data.path for data in api.get_files_in_folder_in_date_order(
                    path, name_pattern=name_pattern, extensions=extensions
                ) or []
        )

    @staticmethod
    def get_newest_file_in_folder(
        path: Union[str, Path],
        name_pattern: Optional[str] = None,
        extensions: Optional[list[str]] = None
    ) -> Optional[Path]:
        """Get the newest file in the folder.

        Returns:
            Optional[Path]: Path to the newest file or None if there is no
                file.

        """
        result = api.get_newest_file_in_folder(
            path, name_pattern=name_pattern, extensions=extensions
        )
        return None if result is None else result.path

    @staticmethod
    def submit_change_list(comment: str) -> Optional[int]:
        """Submit the change list.

        Returns:
            int: Change list number or None if the change list was not
                submitted.

        """
        return api.submit_change_list(comment)

    @staticmethod
    def update_change_list_description(
            comment: str, new_comment: str) -> bool:
        """Update the change list description.

        Returns:
            bool: True if the change list description was updated, False
                otherwise.

        """
        return api.update_change_list_description(comment, new_comment)

    @staticmethod
    def get_stream(workspace_name: str) -> str:
        """Get the stream of the workspace.

        Returns:
            str: Stream of the workspace.

        """
        result = api.run_command("client", ["-o", workspace_name])
        return result.get("Stream")

    @staticmethod
    def get_workspace_dir(workspace_name: str) -> str:
        """Get the root directory of the workspace.

        Returns:
            str: Root directory of the workspace.

        """
        result = api.run_command("client", ["-o", workspace_name])
        return result.get("Root")
