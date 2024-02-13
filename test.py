import asyncio
import json
import logging
from dataclasses import dataclass, field

import dotenv

from onyx_api_client.websocket import OnyxWebsocketClient

logger = logging.getLogger(__name__)


@dataclass
class Workflow:
    products: list[str] = field(default_factory=list)
    dashboard: bool = False
    server_info: bool = False

    def on_response(self, cli: OnyxWebsocketClient, data: dict):
        if data["method"] == "auth":
            if data.get("error"):
                raise RuntimeError(data["message"])
            if self.server_info:
                cli.subscribe("server_info")
            if self.dashboard:
                cli.subscribe("dashboards")
            if self.products:
                cli.subscribe("tickers", products=self.products)

    def on_event(self, cli: OnyxWebsocketClient, data: dict):
        if data.get("channel") == "tickers":
            for message in data.get("message", ()):
                logger.info("symbol: %s - price %s", message["symbol"], message["mid"])
        elif data.get("channel") == "server_info":
            logger.info("%s", json.dumps(data, indent=2))


async def test_websocket(workflow: Workflow):
    client = OnyxWebsocketClient(
        on_response=workflow.on_response, on_event=workflow.on_event
    )
    await client.run()


if __name__ == "__main__":
    dotenv.load_dotenv()
    logging.basicConfig(level=logging.DEBUG)
    workflow = Workflow(products=["ebob"])
    asyncio.get_event_loop().run_until_complete(test_websocket(workflow))
