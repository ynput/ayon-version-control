"""Websocket server for communication with Perforce module."""
from __future__ import annotations

import asyncio
import logging
import os
import socket
import threading
from contextlib import closing
from typing import TYPE_CHECKING, Union

from aiohttp import web

from ayon_perforce.backend import PerforceModuleRestAPI

if TYPE_CHECKING:
    from asyncio import AbstractEventLoop

    from aiohttp.web import Request


log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


class WebServer:
    """Websocket server for communication with Perforce module."""

    def __init__(self):
        """Initializes WebServer."""
        self.client = None

        self.loop: AbstractEventLoop = asyncio.new_event_loop()
        self.app = web.Application(loop=self.loop)
        # self.port = self.find_free_port()
        self.port = 64111
        self.websocket_thread = WebServerThread(self,
            self.port, loop=self.loop
        )

    @property
    def server_is_running(self) -> bool:
        """Returns True if server is running."""
        return self.websocket_thread.server_is_running

    def add_route(self, *args: Union[str, Request],
                  **kwargs: Union[str, Request, None]) -> None:
        """Adds route to the server."""
        self.app.router.add_route(*args, **kwargs)

    @staticmethod
    def find_free_port() -> int:
        """Finds free port.

        Returns:
            int: free port

        """
        with closing(
            socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ) as sock:
            sock.bind(("", 0))
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            return sock.getsockname()[1]

    def start(self) -> None:
        """Starts WebServer."""
        rest_api = PerforceModuleRestAPI(self.app.router)
        rest_api.register()
        self.websocket_thread.start()

    def stop(self) -> None:
        """Stops WebServer."""
        try:
            if self.websocket_thread.is_running:
                log.debug("Stopping websocket server")
                self.websocket_thread.is_running = False
                self.websocket_thread.stop()
        except Exception:  # noqa: BLE001
            log.warning(
                "Error has happened during Killing websocket server",
                exc_info=True
            )


class WebServerThread(threading.Thread):
    """Listener for websocket RPC requests.

    It would be probably better to "attach" this to main thread (as for
    example Harmony needs to run something on main thread), but currently
    it creates separate thread and separate asyncio event loop.
    """

    runner: web.AppRunner
    site: web.TCPSite

    def __init__(self,
                 webserver: WebServer, port: int, loop: AbstractEventLoop):
        """Initializes WebServerThread."""
        super().__init__()
        self.is_running = False
        self.server_is_running = False
        self.port = port
        self.webserver = webserver
        self.loop: AbstractEventLoop = loop
        self.tasks: list = []

    def run(self) -> None:
        """Runs WebServerThread."""
        self.is_running = True

        try:
            self._run_webserver_loop()
        except Exception:  # noqa: BLE001
            log.warning(
                "Websocket Server service has failed", exc_info=True
            )
        finally:
            self.server_is_running = False
            # optional
            self.loop.close()

        self.is_running = False
        log.info("Websocket server stopped")

    def _run_webserver_loop(self) -> None:
        log.debug("Starting websocket server")

        self.loop.run_until_complete(self.start_server())

        webserver_url = f"http://localhost:{self.port}"
        log.info(
            "Running Websocket server on URL: %s", webserver_url
        )
        os.environ["PERFORCE_WEBSERVER_URL"] = webserver_url

        task = asyncio.ensure_future(self.check_shutdown(), loop=self.loop)
        task.add_done_callback(self.tasks.remove)

        self.server_is_running = True
        self.loop.run_forever()

    async def start_server(self) -> None:
        """Starts runner and TCPsite."""
        self.runner = web.AppRunner(self.webserver.app)
        await self.runner.setup()
        self.site = web.TCPSite(self.runner, "localhost", self.port)
        await self.site.start()

    def stop(self) -> None:
        """Stops WebServerThread.

        Sets is_running flag to false, 'check_shutdown' shuts server .

        """
        self.is_running = False

    async def check_shutdown(self) -> None:
        """Checks if server is running.

        Future that is running and checks if server should be running
        periodically.

        """
        while self.is_running:
            while self.tasks:
                task = self.tasks.pop(0)
                log.debug("waiting for task %s", task)
                await task
                log.debug("returned value %s", task.result)

            await asyncio.sleep(0.5)

        log.debug("## Server shutdown started")

        await self.site.stop()
        log.debug("# Site stopped")
        await self.runner.cleanup()
        log.debug("# Server runner stopped")
        tasks = [
            task for task in asyncio.all_tasks()
            if task is not asyncio.current_task()
        ]
        [task.cancel() for task in tasks]  # cancel all the tasks
        results = await asyncio.gather(*tasks, return_exceptions=True)
        log.debug(
            "Finished awaiting cancelled tasks, results: %s...",
            results)
        await self.loop.shutdown_asyncgens()
        # to really make sure everything else has time to stop
        await asyncio.sleep(0.07)
        self.loop.stop()
