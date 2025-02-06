"""
Package for interfacing with version control systems
"""
from .addon import (
    VersionControlAddon,
    is_version_control_enabled,
    VERSION_CONTROL_ADDON_DIR
)

__all__ = (
    "VersionControlAddon",
    "is_version_control_enabled",
    "VERSION_CONTROL_ADDON_DIR",
)
