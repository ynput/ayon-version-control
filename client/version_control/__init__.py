"""
Package for interfacing with version control systems
"""

from .addon import VERSION_CONTROL_ADDON_DIR
from .addon import VersionControlAddon

__all__ = (
    "VersionControlAddon",
    "VERSION_CONTROL_ADDON_DIR",
)
