"""Extract change list info as a json file.

Requires:
    instance.context.data["perforce"]["change_info"] - info about
        change list

Provides:
    new representation with name == "changelist_metadata"
"""
from __future__ import annotations

import json
import os
import tempfile
from typing import TYPE_CHECKING, ClassVar

from ayon_core.pipeline import publish

if TYPE_CHECKING:
    from logging import Logger

    import pyblish.api


class ExtractChangeListInfo(publish.Extractor):
    """Store change list info into a json file to be integrated later."""

    order = publish.Extractor.order
    label = "Extract Change List Info"
    families: ClassVar[list[str]] = ["changelist_metadata"]
    targets: ClassVar[list[str]] = ["local"]
    log: Logger

    def process(self, instance: pyblish.api.Instance) -> None:
        """Process the plugin."""
        change_info = instance.data.get("perforce", {}).get("change_info")
        if not change_info:
            self.log.warning("No change_list info collected, skipping.")

        staging_dir = tempfile.mkdtemp()

        file_name = f"{change_info['change']}.json"
        change_list_path = os.path.join(staging_dir, file_name)
        with open(change_list_path, "w", encoding="utf-8") as fp:
            json.dump(change_info, fp)

        repre_data = {
            "name": "changelist_metadata",
            "ext": "json",
            "files": file_name,
            "stagingDir": staging_dir
        }

        instance.data["representations"].append(repre_data)
