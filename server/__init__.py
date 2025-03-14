from ayon_server.addons import BaseServerAddon

from .settings import PerforceSettings, DEFAULT_VALUES


class PerforceAddon(BaseServerAddon):
    settings_model = PerforceSettings


    async def get_default_settings(self):
        settings_model_cls = self.get_settings_model()
        return settings_model_cls(**DEFAULT_VALUES)
