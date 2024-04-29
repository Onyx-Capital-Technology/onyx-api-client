import asyncio
from dataclasses import dataclass, field

import async_timeout
import pytest

from onyx_api_client.websocket import OnyxWebsocketClient


@dataclass
class OnResponse:
    responses: asyncio.Queue[dict] = field(default_factory=asyncio.Queue)
    events: asyncio.Queue[dict] = field(default_factory=asyncio.Queue)

    def on_response(self, cli: OnyxWebsocketClient, data: dict):
        self.responses.put_nowait(data)

    def on_event(self, cli: OnyxWebsocketClient, data: dict):
        self.events.put_nowait(data)

    async def get_response(self, timeout: float = 2.0):
        async with async_timeout.timeout(timeout):
            return await self.responses.get()

    async def get_event(self, timeout: float = 2.0):
        async with async_timeout.timeout(timeout):
            return await self.events.get()


@pytest.fixture
def responses():
    return OnResponse()


@pytest.fixture
async def cli(responses: OnResponse):
    cli = OnyxWebsocketClient(
        on_response=responses.on_response, on_event=responses.on_event
    )
    read_task = asyncio.create_task(cli.run())
    # await for authentication
    await responses.get_response()
    try:
        yield cli
    finally:
        read_task.cancel()
        try:
            await read_task
        except asyncio.CancelledError:
            pass


async def test_server_info(cli: OnyxWebsocketClient, responses: OnResponse):
    cli.subscribe("server_info")
    msg = await responses.get_response()
    assert msg["method"] == "subscribe"
    assert msg["message"] == dict(Message="subscribed to server_info")
    event = await responses.get_event(timeout=10)
    assert event["channel"] == "server_info"
    assert event["message_type"] == 0
    cli.unsubscribe("server_info")
    msg = await responses.get_response()
    assert msg["method"] == "unsubscribe"
    assert msg["message"] == dict(Message="unsubscribed from server_info")
