import os

import pyblish.api
from openpype.pipeline.publish import ValidateContentsOrder
from openpype.pipeline.publish import (
    PublishXmlValidationError,
)

from version_control.backends.perforce.api.rest_stub import PerforceRestStub


class ValidateWorkspaceDir(pyblish.api.InstancePlugin):
    """Validates if workspace_dir was collected and is valid.

    Login will overrride P4CONFIG env variables if present on systems with
    P4V installed.
    """

    order = ValidateContentsOrder
    label = "Validate P4 workspace dir"
    families = ["version_control"]

    def process(self, instance):
        workspace_dir = instance.data["version_control"]["roots"]

        if not workspace_dir:
            project_name = instance.context.data.get("projectName")
            msg = ("Please provide your local folder for workspace in "
                   "`ayon+settings://version_control/local_setting/workspace_dir?project={}`".format(project_name))  # noqa
            raise PublishXmlValidationError(self, msg)

        workspace = os.path.basename(workspace_dir)
        username = instance.data["version_control"]["username"]
        password = instance.data["version_control"]["password"]

        PerforceRestStub.login(username=username,
                               password=password,
                               workspace=workspace)
