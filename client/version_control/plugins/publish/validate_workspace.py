import pyblish.api
from openpype.pipeline.publish import ValidateContentsOrder
from openpype.pipeline.publish import (
    PublishXmlValidationError,
)


class ValidateWorkspaceDir(pyblish.api.InstancePlugin):
    """Validates if workspace_dir was collected

    """

    order = ValidateContentsOrder
    label = "Validate workspace dir"

    def process(self, instance):

        if "version_control" not in instance.data.keys():
            return

        workspace_dir = instance.data["version_control"]["roots"]

        if not workspace_dir:
            project_name = instance.context.data.get("projectName")
            msg = ("Please provide your local folder for workspace in "
                   "`ayon+settings://version_control:0.0.1/local_setting/workspace_dir?project={}`".format(project_name))  # noqa
            raise PublishXmlValidationError(self, msg)
