from ayon_core.pipeline import (
    CreatedInstance
)
from ayon_core.client import get_asset_by_name
import unreal

try:
    from ayon_core.hosts.unreal.api.plugin import UnrealBaseAutoCreator
    from ayon_core.hosts.unreal.api.pipeline import (
        create_publish_instance, imprint)
except ImportError:
    # should be used after splitting unreal host to separate addon
    from ayon_unreal.api.plugin import UnrealBaseAutoCreator
    from ayon_unreal.api.pipeline import create_publish_instance, imprint


class UnrealPublishCommit(UnrealBaseAutoCreator):
    """Auto creator to mark current version of project as published.

    It should store identification of latest submitchange to highlight it as
    "publish" version. (Not all submits are created equally.)

    This logic should be eventually moved to UnrealBaseAutoCreator class in
    unreal addon andd only be imported from there.
    """
    identifier = "io.ayon.creators.unreal.publish_commit"
    product_type = "publish_commit"
    label = "Publish commit"

    default_variant = ""

    def create(self, options=None):
        existing_instance = None
        for instance in self.create_context.instances:
            if instance.product_type == self.product_type:
                existing_instance = instance
                break

        context = self.create_context
        project_name = context.get_current_project_name()
        asset_name = context.get_current_asset_name()
        task_name = context.get_current_task_name()
        host_name = context.host_name
        if existing_instance is None:
            existing_instance_asset = None
        else:
            existing_instance_asset = existing_instance["folderPath"]
        if existing_instance is None:
            asset_doc = get_asset_by_name(project_name, asset_name)
            product_name = self.get_product_name(
                project_name, asset_doc, task_name, self.default_variant,
                host_name
            )
            data = {
                "folderPath": asset_name,
                "task": task_name,
                "variant": self.default_variant
            }
            data.update(self.get_dynamic_data(
                self.default_variant, task_name, asset_doc,
                project_name, host_name, None
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
            pub_instance.set_editor_property('add_external_assets', True)
            assets = pub_instance.get_editor_property('asset_data_external')

            ar = unreal.AssetRegistryHelpers.get_asset_registry()

            imprint(f"{self.root}/{instance_name}",
                    new_instance.data_to_store())

            return pub_instance

        elif (
                existing_instance_asset != asset_name
                or existing_instance["task"] != task_name
        ):
            asset_doc = get_asset_by_name(project_name, asset_name)
            product_name = self.get_product_name(
                project_name, asset_doc, task_name, self.default_variant,
                host_name
            )
            existing_instance["folderPath"] = asset_name
            existing_instance["task"] = task_name
            existing_instance["product_name"] = product_name
