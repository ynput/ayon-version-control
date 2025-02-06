import os.path
import copy
import shutil
import datetime

import pyblish.api

from ayon_core.lib import StringTemplate

from ayon_perforce.rest.perforce.rest_stub import (
    PerforceRestStub
)


class IntegratePerforce(pyblish.api.InstancePlugin):
    """Integrate perforce items
    """

    label = "Integrate Perforce items"
    order = pyblish.api.IntegratorOrder + 0.499
    targets = ["local"]

    families = ["perforce"]

    def process(self, instance):
        version_template_key = (
            instance.data.get("perforce", {})["template_name"])
        if not version_template_key:
            raise RuntimeError("Instance data missing 'version_control[template_name]'")   # noqa

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

        template_file_path = os.path.join(template["directory"],
                                          template["file"])
        anatomy_data = copy.deepcopy(instance.data["anatomyData"])
        anatomy_data["root"] = instance.data["perforce"]["roots"]
        # anatomy_data["output"] = ''
        # anatomy_data["frame"] = ''
        # anatomy_data["udim"] = ''

        for repre in instance.data["representations"]:
            anatomy_data["ext"] = repre["ext"]

            version_control_path = StringTemplate.format_template(
                template_file_path, anatomy_data
            )

            source_path = repre["published_path"]

            dirname = os.path.dirname(version_control_path)
            if not os.path.exists(dirname):
                os.makedirs(dirname)

            is_on_server = PerforceRestStub.exists_on_server(version_control_path)
            actual_time = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
            comment = os.path.basename(version_control_path) + actual_time
            if is_on_server:
                if PerforceRestStub.is_checkouted(version_control_path):
                    raise RuntimeError("{} is checkouted by someone already, "
                                       "cannot commit right now.".format(
                                        version_control_path))
                if not PerforceRestStub.checkout(version_control_path,
                                                 comment):
                    raise ValueError("File {} not checkouted".
                                     format(version_control_path))

            shutil.copy(source_path, version_control_path)
            if not is_on_server:
                if not PerforceRestStub.add(version_control_path,
                                            comment):
                    raise ValueError("File {} not added to changelist".
                                     format(version_control_path))

            if not PerforceRestStub.submit_change_list(comment):
                raise ValueError("Changelist not submitted")
