from dataclasses import dataclass


@dataclass
class WorkspaceProfileContext:
    """Data that could be used in filtering workspace name"""
    folder_paths: str
    task_names: str
    task_types: str
