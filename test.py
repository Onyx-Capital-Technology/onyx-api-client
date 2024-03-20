import asyncio
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone

import dotenv

from onyx_api_client.websocket import OnyxWebsocketClient

logger = logging.getLogger(__name__)


@dataclass
class Workflow:
    products: list[str] = field(default_factory=list)
    rfq: list[dict] = field(default_factory=list)
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
            if self.rfq:
                for kwargs in self.rfq:
                    cli.subscribe("rfq", **kwargs)
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
            case "rfq":
                for rfq in data.get("message", ()):
                    timestamp = datetime.fromtimestamp(
                        0.001 * rfq["timestamp_millis"], tz=timezone.utc
                    )
                    logger.info(
                        "%s - %s - bid %s - ask %s",
                        rfq["symbol"],
                        timestamp.isoformat(),
                        rfq["bid"],
                        rfq["ask"],
                    )
            case "server_info":
                logger.info("%s", json.dumps(data, indent=2))


async def test_websocket(workflow: Workflow):
    client = OnyxWebsocketClient(
        on_response=workflow.on_response, on_event=workflow.on_event
    )
    await client.run()


if __name__ == "__main__":
    dotenv.load_dotenv()
    logging.basicConfig(level=logging.DEBUG)
    workflow = Workflow(
        rfq=[
            dict(symbol="brtz24", size="10"),
            dict(symbol=dict(front="brtu24", back="brtz24"), size=50),
        ]
    )
    asyncio.get_event_loop().run_until_complete(test_websocket(workflow))
