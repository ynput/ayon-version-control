from pydantic import Field
from ayon_server.settings import BaseSettingsModel


def backend_enum():
    return [
        {"label": "Perforce", "value": "perforce"}
    ]


class VersionControlSettings(BaseSettingsModel):
    """Version Control Project Settings."""

    enabled: bool = Field(default=True)

    backendName: str = Field(
        "backendName",
        enum_resolver=backend_enum,
        title="Backend name"
    )


DEFAULT_VALUES = {}
    
