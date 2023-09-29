import os.path

import pyblish.api
import shutil

from version_control.backends.perforce.api.rest_stub import (
    PerforceRestStub
)


class IntegratePerforce(pyblish.api.InstancePlugin):
    """Integrate perforce items
    """

    label = "Integrate Perforce items"
    order = pyblish.api.IntegratorOrder + 0.5

    families = ["version_control"]

    def process(self, instance):
        # PerforceRestStub.checkout("c:/projects/!perforce_workspace/text.txt")
        self.log.info(f"{instance.data}")

        version_template_key = (
            instance.data.get("version_control_template_name"))
        if not version_template_key:
            raise RuntimeError("Instance data missing 'version_control_template_name'")   # noqa

        anatomy = instance.context.data["anatomy"]
        template = anatomy.templates.get(version_template_key)
        if not template:
            raise RuntimeError("Anatomy is missing configuration for '{}'".
                               format(version_template_key))

        version_control_path = self.get_publish_dir(instance,
                                                    version_template_key)


        # workfile_path = instance.context.data["currentFile"]
        # basename = os.path.basename(version_control_path)
        # perforce_file_path = \
        #     os.path.join("c:/Users/pypeclub/Perforce/perforce_workspace",
        #                  basename)
        # shutil.copy(workfile_path, perforce_file_path)
        # if not PerforceRestStub.add(workfile_path, "Init commit"):
        #     raise ValueError("File {} not added to changelist".
        #                      format(perforce_file_path))
        # if not PerforceRestStub.submit_change_list("Init commit"):
        #     raise ValueError("Changelist not submitted")
