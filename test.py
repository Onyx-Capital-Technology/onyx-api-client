import asyncio
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import NamedTuple

import dotenv

from onyx_api_client.websocket import OnyxWebsocketClient

logger = logging.getLogger(__name__)


class ProductRisk(NamedTuple):
    product_symbol: str
    account_id: float


@dataclass
class Workflow:
    products: list[str] = field(default_factory=list)
    server_info: bool = False

    def on_response(self, cli: OnyxWebsocketClient, data: dict):
        if data["method"] == "auth":
            if data.get("error"):
                raise RuntimeError(data["message"])
            if self.server_info:
                cli.subscribe("server_info")
            if self.products:
                cli.subscribe("tickers", products=self.products)
        else:
            logger.info("%s", json.dumps(data, indent=2))

    def on_event(self, cli: OnyxWebsocketClient, data: dict):
        channel = data.get("channel")
        match channel:
            case "tickers":
                for ticker in data.get("message", ()):
                    timestamp = datetime.fromtimestamp(
                        0.001 * ticker["timestamp_millis"], tz=timezone.utc
                    )
                    logger.info(
                        "%s - %s - %s",
                        ticker["symbol"],
                        timestamp.isoformat(),
                        ticker["mid"],
                    )
            case _:
                logger.info("%s", json.dumps(data, indent=2))


async def test_websocket(workflow: Workflow):
    client = OnyxWebsocketClient(
        on_response=workflow.on_response, on_event=workflow.on_event
    )
    await client.run()


async def one_client():
    workflow = Workflow(
        products=["dub"],
    )
    try:
        await test_websocket(workflow)
    except Exception as e:
        logger.error("%s", e)


if __name__ == "__main__":
    dotenv.load_dotenv()
    logging.basicConfig(level=logging.DEBUG)
    asyncio.get_event_loop().run_until_complete(one_client())
