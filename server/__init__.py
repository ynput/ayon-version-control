#from typing import Type

from ayon_server.addons import BaseServerAddon

from .settings import VersionControlSettings, DEFAULT_VALUES
from .version import __version__


class VersionControlAddon(BaseServerAddon):
    name = "version_control"
    title = "Version Control"
    version = __version__
    #settings_model: Type[VersionControlSettings] = VersionControlSettings
    settings_model = VersionControlSettings


    async def get_default_settings(self):
        settings_model_cls = self.get_settings_model()
        return settings_model_cls(**DEFAULT_VALUES)
