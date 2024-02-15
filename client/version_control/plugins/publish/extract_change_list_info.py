"""
Requires:
    instance.context.data["version_control"]["change_info"] - info about
        change list

Provides:
    new representation with name == "publish_commit"
"""

import os
import json
import tempfile

from openpype.pipeline import publish


class ExtractChangeListInfo(publish.Extractor):
    """Store change list info into a json file to be integrated later."""

    order = publish.Extractor.order
    label = "Extract Change List Info"
    families = ["publish_commit"]

    def process(self, instance):
        change_info = instance.data.get("version_control", {}).get("change_info")  # noqa
        if not change_info:
            self.log.warning("No change_list info collected, skipping.")

        staging_dir = tempfile.mkdtemp()

        file_name = f"{change_info['change']}.json"
        change_list_path = os.path.join(staging_dir, file_name)
        with open(change_list_path, "w") as fp:
            json.dump(change_info, fp)

        repre_data = {
            "name": "publish_commit",
            "ext": "json",
            "files": file_name,
            "stagingDir": staging_dir
        }

        instance.data["representations"].append(repre_data)
