"""Validate if Perforce stream is collected."""
from __future__ import annotations

from typing import ClassVar

import pyblish.api
from ayon_core.pipeline.publish import (
    PublishValidationError,
    ValidateContentsOrder,
)


class ValidateStream(pyblish.api.InstancePlugin):
    """Validates if Perforce stream is collected.

    Current Deadline implementation requires P4 depots to be of type 'stream'
    and workspace to be assigned to a stream
    """

    order = ValidateContentsOrder
    label = "Validate P4 Stream"
    families: ClassVar[list[str]] = ["changelist_metadata"]
    targets: ClassVar[list[str]] = ["local"]

    def process(  # noqa: PLR6301
            self, instance: pyblish.api.Instance) -> None:
        """Process the plugin.

        Raises:
            PublishValidationError: If stream is not collected.

        """
        stream = instance.context.data["perforce"]["stream"]

        if not stream:
            msg = (
                "Deadline implementation require depot with `streams`. "
                "Please let your Perforce admin set up your workspace with "
                "stream connected."
            )
            raise PublishValidationError(msg)
