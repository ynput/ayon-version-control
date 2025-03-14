from pydantic import Field
from ayon_server.settings import (
    BaseSettingsModel,
    SettingsField,
    task_types_enum
)


class CollectPerforceProfileModel(BaseSettingsModel):
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
    add_perforce_control: bool = Field(
        True,
        title="Commit representations to Perforce",
    )
    template_name: str = Field(
        "",
        title="Template name",
        description="Name from Anatomy to provide path and name of "
                    "committed file")


class CollectPerforceControlModel(BaseSettingsModel):
    _isGroup = True
    enabled: bool = False
    profiles: list[CollectPerforceProfileModel] = Field(
        default_factory=list,
        title="Profiles to trigger Perforce commit",
        description="Provide profile in which context representation should be"
         " tracked outside of AYON with Perforce commit"
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
    CollectPerforceControl: CollectPerforceControlModel = Field(
        default_factory=CollectPerforceControlModel,
        title="Collect Perforce Control",
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


class PerforceSettings(BaseSettingsModel):
    """Version Control Project Settings."""

    enabled: bool = Field(default=False)

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
