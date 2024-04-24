from __future__ import annotations

import asyncio
import logging
import os
from dataclasses import dataclass, field
from typing import Any, Callable

from aiohttp import ClientSession, ClientWebSocketResponse, WSMsgType

logger = logging.getLogger(__name__)


def on_response(cli: OnyxWebsocketClient, data: dict) -> None:
    logger.info("received response: %s", data)


def on_event(cli: OnyxWebsocketClient, data: dict) -> None:
    logger.info("received event: %s", data)


@dataclass
class OnyxWebsocketClient:
    api_token: str = field(default_factory=lambda: os.getenv("ONYX_API_TOKEN", ""))
    ws_url: str = field(
        default_factory=lambda: os.getenv(
            "ONYX_WS_URL", "wss://ws.onyxhub.co/stream/v1"
        )
    )
    ws: ClientWebSocketResponse | None = None
    on_response: Callable = on_response
    on_event: Callable = on_event
    queue: asyncio.Queue = field(default_factory=asyncio.Queue)
    _task: asyncio.Task | None = None
    _write_task: asyncio.Task | None = None
    msg_id: int = 0

    def subscribe(self, channel: str, **kwargs: Any) -> None:
        channel_data = {channel: kwargs} if kwargs else channel
        self.send(
            dict(
                id=self.new_id(),
                method="subscribe",
                channel=channel_data,
            )
        )

    def unsubscribe(self, channel: str, **kwargs: Any) -> None:
        channel_data = {channel: kwargs} if kwargs else channel
        self.send(
            dict(
                id=self.new_id(),
                method="unsubscribe",
                channel=channel_data,
            )
        )

    def auth_msg(self) -> dict:
        return dict(id=self.new_id(), method="auth", token=self.api_token)

    def send(self, msg: dict) -> None:
        self.queue.put_nowait(msg)

    def new_id(self) -> str:
        self.msg_id += 1
        return f"msg:{self.msg_id}"

    def place_order(self, **kwargs: Any) -> None:
        self.send(
            dict(
                id=self.new_id(),
                method="order",
                **kwargs,
            )
        )

    async def run(self) -> None:
        self._write_task = asyncio.create_task(self.write_loop())
        try:
            await self.read_loop()
        finally:
            self._write_task.cancel()

    async def read_loop(self) -> None:
        async with ClientSession() as session:
            logger.info("connecting with %s", self.ws_url)
            async with session.ws_connect(self.ws_url) as ws:
                self.ws = ws
                logger.info("connected to websocket")
                self.send(self.auth_msg())
                async for msg in ws:
                    if msg.type == WSMsgType.TEXT:
                        data = msg.json()
                        if "method" in data:
                            self.on_response(self, data)
                        elif "channel" in data:
                            self.on_event(self, data)
                        else:
                            logger.warn(f"received unknown message: {data}")
                    elif msg.type == WSMsgType.CLOSED:
                        logger.info("websocket closed")
                        break
                    else:
                        logger.info(f"unhandled message type: {msg.type}")
                        break
            logger.warn("exiting read loop")

    async def write_loop(self) -> None:
        while True:
            msg = await self.queue.get()
            if self.ws:
                logger.debug("sending message: %s", msg)
                await self.ws.send_json(msg)
            else:
                logger.warn("websocket not connected, dropping message: %s", msg)
