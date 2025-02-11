import os.path
import copy
import shutil
import datetime

import pyblish.api

from ayon_core.lib import StringTemplate

from ayon_perforce.rest.perforce.rest_stub import PerforceRestStub


class IntegratePerforce(pyblish.api.InstancePlugin):
    """Integrate perforce items

    Commits published files as a new version in Perforce
    """

    label = "Integrate Perforce items"
    order = pyblish.api.IntegratorOrder + 0.499
    targets = ["local"]

    families = ["perforce"]

    def process(self, instance):
        version_template_key = (
            instance.data.get("perforce", {})["template_name"])
        if not version_template_key:
            raise RuntimeError("Instance data missing 'perforce[template_name]'")   # noqa

        if "_" in version_template_key:
            template_area, template_name = version_template_key.split("_")
        else:
            template_area = version_template_key
            template_name = "default"
        anatomy = instance.context.data["anatomy"]
        template = anatomy.templates_obj.templates[template_area][template_name]  # noqa
        if not template:
            raise RuntimeError("Anatomy is missing configuration for '{}'".
                               format(version_template_key))

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
                    raise RuntimeError(
                        f"{perforce_file_path} is checkouted by someone "
                        f"already, cannot commit right now."
                    )
                if not PerforceRestStub.checkout(
                        perforce_file_path, comment):
                    raise ValueError(
                        f"File {perforce_file_path} not checkouted"
                    )

            shutil.copy(source_path, perforce_file_path)
            if not is_on_server:
                if not PerforceRestStub.add(perforce_file_path,
                                            comment):
                    raise ValueError(
                        f"File {perforce_file_path} not added to changelist"
                    )

            if not PerforceRestStub.submit_change_list(comment):
                raise ValueError("Changelist not submitted")
