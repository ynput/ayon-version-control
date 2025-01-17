from fastapi import Response

from ayon_server.addons import BaseServerAddon
from ayon_server.events import dispatch_event

from .settings import VersionControlSettings, DEFAULT_VALUES

from ayon_server.types import Field, OPModel

class ChangeSubmitModel(OPModel):
    user: str
    changelist: int
    client: str


class VersionControlAddon(BaseServerAddon):
    #settings_model: Type[VersionControlSettings] = VersionControlSettings
    settings_model = VersionControlSettings

    def initialize(self) -> None:

        self.add_endpoint(
            "/change_submit",
            self.change_submit,
            method="POST",
        )

    async def get_default_settings(self):
        settings_model_cls = self.get_settings_model()
        return settings_model_cls(**DEFAULT_VALUES)

    async def change_submit(
        self,
        post_data: ChangeSubmitModel,
    ) -> Response:

        topic = "perforce.change_submit"

        payload = {
            "perforce_user": post_data.user,
            "changelist": post_data.changelist,
            "client": post_data.client
        }
        try:
            await dispatch_event(
                topic,
                description=f"{post_data.user} "
                            f"commited {post_data.changelist}",
                payload=payload,
            )
        except Exception:
            m = f"Unable to dispatch commit info"
            # do not use the logger, if you don't like recursion
            print(m, flush=True)

        return Response(status_code=204)