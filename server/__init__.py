"""AYON Integration addon for Perforce."""
from ayon_server.addons import BaseServerAddon

from .settings import DEFAULT_VALUES, PerforceSettings


class PerforceAddon(BaseServerAddon):
    """AYON Integration addon for Perforce."""
    settings_model = PerforceSettings

    async def get_default_settings(self):
        """Get default settings.

        Returns:
            PerforceSettings: Default settings.

        """
        settings_model_cls = self.get_settings_model()
        return settings_model_cls(**DEFAULT_VALUES)
