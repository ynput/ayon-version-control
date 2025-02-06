"""
Package for interfacing with version control systems
"""
from .addon import (
    PerforceAddon,
    is_version_control_enabled,
    PERFORCE_ADDON_DIR
)

__all__ = (
    "PerforceAddon",
    "is_version_control_enabled",
    "PERFORCE_ADDON_DIR",
)
