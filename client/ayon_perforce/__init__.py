"""
Package for interfacing with version control systems
"""
from .addon import (
    PerforceAddon,
    is_perforce_enabled,
    PERFORCE_ADDON_DIR
)

__all__ = (
    "PerforceAddon",
    "is_perforce_enabled",
    "PERFORCE_ADDON_DIR",
)
