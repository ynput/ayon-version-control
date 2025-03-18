"""Validate if workspace_dir was collected and is valid."""
from __future__ import annotations

import os
from typing import ClassVar

import pyblish.api
from ayon_core.pipeline import PublishXmlValidationError
from ayon_core.pipeline.publish import ValidateContentsOrder


class ValidateWorkspaceDir(pyblish.api.InstancePlugin):
    """Validates if workspace_dir was collected and is valid.

    Used for committing to P4 directly from AYON.
    """

    order = ValidateContentsOrder
    label = "Validate P4 workspace dir"
    families: ClassVar[list[str]] = ["perforce"]
    targets: ClassVar[list[str]] = ["local"]

    def process(self, instance: pyblish.api.Instance) -> None:
        """Process the plugin.

        Raises:
            PublishXmlValidationError: If workspace_dir is not collected.

        """
        # TODO(antirotor): implement multiple roots
        workspace_dir = instance.data["perforce"]["roots"]["work"]

        if not workspace_dir or not os.path.exists(workspace_dir):
            project_name = instance.context.data.get("projectName")
            msg = (
                "Please provide your local folder for workspace in "
                "`ayon+settings://perforce/local_setting/"
                f"workspace_dir?project={project_name}`")
            raise PublishXmlValidationError(self, msg)
