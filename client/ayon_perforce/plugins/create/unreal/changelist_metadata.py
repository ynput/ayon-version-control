"""Change list auto creator for Unreal Engine."""
from __future__ import annotations

from typing import Optional

from ayon_api import get_folder_by_path
from ayon_core.pipeline import CreatedInstance
from ayon_unreal.api.pipeline import create_publish_instance, imprint
from ayon_unreal.api.plugin import UnrealBaseAutoCreator


class UnrealPublishCommit(UnrealBaseAutoCreator):
    """Auto creator to mark current version of project as published.

    It should store identification of latest submit change to highlight it as
    "publish" version. (Not all submits are created equally.)

    This logic should be eventually moved to UnrealBaseAutoCreator class in
    unreal addon and only be imported from there.
    """
    identifier = "io.ayon.creators.unreal.changelist_metadata"
    product_type = "changelist_metadata"
    label = "Publish Changelist Metadata"
    host_name = "unreal"

    default_variant = "Main"

    def create(
            self,
            options: Optional[dict] = None) -> Optional[CreatedInstance]:
        """Create a new instance of the product.

        Returns:
            CreatedInstance: The created instance.

        """
        existing_instance = None
        for instance in self.create_context.instances:
            if instance.product_type == self.product_type:
                existing_instance = instance
                break

        context = self.create_context
        project_name = context.get_current_project_name()
        folder_path = context.get_current_folder_path()
        folder_entity = get_folder_by_path(project_name, folder_path)
        task_entity = context.get_current_task_entity()
        task_name = task_entity["name"]
        host_name = context.host_name
        if existing_instance is None:

            product_name = self.get_product_name(
                project_name, folder_entity, task_entity, self.default_variant,
                host_name
            )

            data = {
                "folderPath": folder_path,
                "task": task_name,
                "variant": self.default_variant,
                "productName": product_name
            }

            data.update(self.get_dynamic_data(
                project_name,
                folder_entity,
                task_entity,
                self.default_variant,
                host_name,
                None
            ))

            # TODO enable when Settings available
            # if not self.active_on_create:
            #     data["active"] = False

            new_instance = CreatedInstance(
                self.product_type, product_name, data, self
            )
            self._add_instance_to_context(new_instance)
            instance_name = f"{product_name}{self.suffix}"

            pub_instance = create_publish_instance(instance_name, self.root)
            pub_instance.set_editor_property("add_external_assets", True)

            imprint(f"{self.root}/{instance_name}",
                    new_instance.data_to_store())

            return pub_instance

        if (
                existing_instance["folderPath"] != folder_path
                or existing_instance.get("task") != task_name
        ):
            product_name = self.get_product_name(
                project_name, folder_entity, task_entity, self.default_variant,
                host_name
            )
            existing_instance["folderPath"] = folder_path
            existing_instance["task"] = task_name

            return existing_instance
        return None
