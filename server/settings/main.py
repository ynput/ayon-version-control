from pydantic import Field
from ayon_server.settings import (
    BaseSettingsModel,
    SettingsField,
    task_types_enum
)


def backend_enum():
    return [
        {"label": "Perforce", "value": "perforce"}
    ]


class CollectVersionControlProfileModel(BaseSettingsModel):
    _layout = "expanded"
    host_names: list[str] = Field(
        default_factory=list,
        title="Host names",
    )
    product_types: list[str] = Field(
        default_factory=list,
        title="Families",
    )
    task_types: list[str] = Field(
        default_factory=list,
        title="Task types",
    )
    task_names: list[str] = Field(
        default_factory=list,
        title="Task names",
    )
    add_version_control: bool = Field(
        True,
        title="Add Version Control to representations",
    )
    template_name: str = Field("", title="Template name",
                               description="Name from Anatomy to provide path and name of "
                                           "committed file")


class CollectVersionControlModel(BaseSettingsModel):
    _isGroup = True
    enabled: bool = False
    profiles: list[CollectVersionControlProfileModel] = Field(
        default_factory=list,
        title="Profiles to add version control",
    )


class WorkspaceProfileModel(BaseSettingsModel):
    _layout = "expanded"
    folder_paths: list[str] = SettingsField(
        default_factory=list,
        title="Folder paths",
        scope=["site"]
    )
    task_types: list[str] = SettingsField(
        default_factory=list,
        title="Task types",
        enum_resolver=task_types_enum,
        scope=["site"]
    )
    task_names: list[str] = SettingsField(
        default_factory=list,
        title="Task names",
        scope=["site"]
    )
    workspace_name: str = Field(
        "",
        title="My Workspace Name",
        scope=["site"]
    )


class PublishPluginsModel(BaseSettingsModel):
    CollectVersionControl: CollectVersionControlModel = Field(
        default_factory=CollectVersionControlModel,
        title="Collect Version Control",
        description=(
            "Configure which published products should be committed to P4. "
            "Keep disabled if published files should be versioned only in AYON"
        )
    )



class LocalSubmodel(BaseSettingsModel):
    """Provide artist based values"""

    username: str = Field(
        "",
        title="Username",
        scope=["site"]
    )
    password: str = Field(
        "",
        title="Password",
        scope=["site"]
    )
    workspace_profiles: list[WorkspaceProfileModel] = SettingsField(
        default_factory=list,
        scope=["site"]
    )


class VersionControlSettings(BaseSettingsModel):
    """Version Control Project Settings."""

    enabled: bool = Field(default=False)

    active_version_control_system: str = Field(
        "",
        enum_resolver=backend_enum,
        title="Backend name"
    )

    host_name: str = Field(
        "perforce",
        title="Host name"
    )

    port: int = Field(
        1666,
        title="Port"
    )

    publish: PublishPluginsModel = Field(
        default_factory=PublishPluginsModel,
        title="Publish Plugins",
    )

    local_setting: LocalSubmodel = Field(
        default_factory=LocalSubmodel,
        title="Local setting",
        scope=["site"],
        description="This setting is only applicable for artist's site",
    )


DEFAULT_VALUES = {}
