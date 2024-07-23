import pyblish.api

from ayon_core.pipeline.publish import ValidateContentsOrder
from ayon_core.pipeline import PublishXmlValidationError


class ValidateStream(pyblish.api.InstancePlugin):
    """Validates if Perforce stream is collected.

    Current Deadline implementation requires P4 depots to be of type 'stream'
    and workspace to be assigned to a stream
    """

    order = ValidateContentsOrder
    label = "Validate P4 Stream"
    families = ["publish_commit"]
    targets = ["local"]

    def process(self, instance):
        stream = instance.context.data["version_control"]["stream"]

        if not stream:
            msg = (
                "Deadline implementation require depot with `streams`. "
                "Please let your Perforce admin set up your workspace with "
                "stream connected."
            )
            raise PublishXmlValidationError(self, msg)
