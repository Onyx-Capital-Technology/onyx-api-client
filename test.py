import asyncio
import logging
from dataclasses import dataclass, field

import dotenv

from onyx_api_client.websocket import OnyxWebsocketClient

logger = logging.getLogger(__name__)


@dataclass
class Workflow:
    products: list[str] = field(default_factory=list)
    dashboard: bool = False
    _dashboard: bool = False
    _tickers: bool = False

    def on_response(self, cli: OnyxWebsocketClient, data: dict):
        if data["method"] == "auth":
            if data.get("error"):
                raise RuntimeError(data["message"])
            else:
                logger.info("authenticated - subscribe to server_info")
                cli.subscribe("server_info")

    def on_event(self, cli: OnyxWebsocketClient, data: dict):
        if data.get("channel") == "tickers":
            for message in data.get("message", ()):
                logger.info("symbol: %s - price %s", message["symbol"], message["mid"])
        elif data.get("channel") == "server_info":
            logger.info("server info: %s", data)
        if not self._dashboard and self.dashboard:
            self.dashboard = True
            cli.subscribe("dashboards")
        if not self._tickers and self.products:
            self._tickers = True
            cli.subscribe("tickers", products=["brtspr"])


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
