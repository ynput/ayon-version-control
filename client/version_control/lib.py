from dataclasses import dataclass


@dataclass
class WorkspaceProfileContext:
    """Data that could be used in filtering workspace name"""
    task_names: str
    task_types: str
