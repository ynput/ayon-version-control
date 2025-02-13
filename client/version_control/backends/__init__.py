"""
Package for interfacing with version control systems
"""

# This is a clever hack to get python to import in a lazy (sensible) way
# whilst allowing static analysis to work correctly.
# Effectively this is forcing python to see these sub-packages without
# importing any packages until they are needed, this also helps
# avoid triggering potential dependency loops.
# The module level __getattr__ will handle lazy imports in this syntax:

# ```
# import version_control
# version_control.backends.perforce.sync
# ```

import importlib
import pathlib

_typing = False
if _typing:
    from typing import Any

    from . import abstract
    from . import perforce
del _typing

# this avoids having to import every sub-package to find where
# the object should be imported from:
_object_import_map = {
    "VERSION_CONTROL_ADDON_DIR": "addon",
    "VersionControlAddon": "addon"
}

def __getattr__(name):
    # type: (str) -> Any
    if name in _object_import_map:
        package_name = _object_import_map[name]
        module = importlib.import_module("{0}.{1}".format(__package__, package_name))
        return getattr(module, name)

    current_file = pathlib.Path(__file__)
    current_directory = current_file.parent
    for path in current_directory.iterdir():
        if path.stem != name:
            continue

        return importlib.import_module("{0}.{1}".format(__package__, name))

    raise AttributeError("{0} has no attribute named: {0}".format(__package__, name))


__all__ = ("abstract", "perforce")
