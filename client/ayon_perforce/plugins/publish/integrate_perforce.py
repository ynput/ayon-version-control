"""Integrate Perforce items."""
from __future__ import annotations

import copy
import datetime
import os.path
import shutil
from typing import ClassVar

import pyblish.api
from ayon_core.lib import StringTemplate
from ayon_perforce.backend import PerforceRestStub


class IntegratePerforce(pyblish.api.InstancePlugin):
    """Integrate perforce items.

    Commits published files as a new version in Perforce
    """

    label = "Integrate Perforce items"
    order = pyblish.api.IntegratorOrder + 0.499
    targets: ClassVar[list[str]] = ["local"]

    families: ClassVar[list[str]] = ["perforce"]

    def process(self, instance: pyblish.api.Instance) -> None:
        """Process the plugin.

        Raises:
            RuntimeError: If the instance data is missing Anatomy.
            RuntimeError: If the data is checked out by someone else.
            ValueError: If the file is not checked out.
            ValueError: If the file is not added to the changelist.
            ValueError: If the changelist is not submitted.

        """
        version_template_key = (
            instance.data.get("perforce", {})["template_name"])
        if not version_template_key:
            msg = "Instance data missing 'perforce[template_name]'"
            raise RuntimeError(msg)

        if "_" in version_template_key:
            template_area, template_name = version_template_key.split("_")
        else:
            template_area = version_template_key
            template_name = "default"
        anatomy = instance.context.data["anatomy"]
        template = anatomy.templates_obj.templates[template_area][template_name]  # noqa: E501
        if not template:
            msg = (
                "Anatomy is missing configuration "
                f"for '{version_template_key}'"
            )
            raise RuntimeError(msg)

        template_file_path = os.path.join(
            template["directory"], template["file"])
        anatomy_data = copy.deepcopy(instance.data["anatomyData"])
        anatomy_data["root"] = instance.data["perforce"]["roots"]
        # anatomy_data["output"] = ''
        # anatomy_data["frame"] = ''
        # anatomy_data["udim"] = ''

        for repre in instance.data["representations"]:
            anatomy_data["ext"] = repre["ext"]

            perforce_file_path = StringTemplate.format_template(
                template_file_path, anatomy_data
            )

            source_path = repre["published_path"]

            dirname = os.path.dirname(perforce_file_path)
            if not os.path.exists(dirname):
                os.makedirs(dirname)

            is_on_server = PerforceRestStub.exists_on_server(perforce_file_path)
            actual_time = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
            comment = os.path.basename(perforce_file_path) + actual_time
            if is_on_server:
                if PerforceRestStub.is_checkouted(perforce_file_path):
                    msg = (
                        f"{perforce_file_path} is checked out by someone "
                        "already, cannot commit right now."
                    )
                    raise RuntimeError(msg)
                if not PerforceRestStub.checkout(
                        perforce_file_path, comment):
                    msg = f"File {perforce_file_path} not checked out"
                    raise ValueError(msg)

            shutil.copy(source_path, perforce_file_path)
            if not is_on_server and not PerforceRestStub.add(
                    perforce_file_path, comment):
                msg = f"File {perforce_file_path} not added to changelist"
                raise ValueError(msg)

            if not PerforceRestStub.submit_change_list(comment):
                msg = "Changelist not submitted"
                raise ValueError(msg)
