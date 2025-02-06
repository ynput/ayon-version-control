import os

import pyblish.api
from ayon_core.pipeline.publish import ValidateContentsOrder
from ayon_core.pipeline import PublishXmlValidationError


class ValidateWorkspaceDir(pyblish.api.InstancePlugin):
    """Validates if workspace_dir was collected and is valid.

    Used for committing to P4 directly from AYON.
    """

    order = ValidateContentsOrder
    label = "Validate P4 workspace dir"
    families = ["version_control"]
    targets = ["local"]


    def process(self, instance):
        # TODO implement multiple roots
        workspace_dir = instance.data["version_control"]["roots"]["work"]

        if not workspace_dir or not os.path.exists(workspace_dir):
            project_name = instance.context.data.get("projectName")
            msg = ("Please provide your local folder for workspace in "
                   "`ayon+settings://version_control/local_setting/workspace_dir?project={}`".format(project_name))  # noqa
            raise PublishXmlValidationError(self, msg)
