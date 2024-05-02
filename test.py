import asyncio
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from random import choice
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
    rfq: list[dict] = field(default_factory=list)
    product_risk: list[ProductRisk] = field(default_factory=list)
    dashboard: bool = False
    server_info: bool = False
    last_order: datetime | None = None
    orders_every: timedelta = timedelta(seconds=10)

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
            if self.product_risk:
                for product_risk in self.product_risk:
                    cli.subscribe("product_risk", **product_risk._asdict())
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
                        rfq,
                        timestamp.isoformat(),
                        rfq["bid"],
                        rfq["ask"],
                    )
                    self.maybe_place_order(cli, rfq)
            case _:
                logger.info("%s", json.dumps(data, indent=2))

    def maybe_place_order(self, cli: OnyxWebsocketClient, rfq: dict):
        now = datetime.now(timezone.utc)
        if self.last_order is not None and now - self.last_order < self.orders_every:
            return
        self.last_order = now
        side = choice(["buy", "sell"])
        other_side = rfq["ask"] if side == "buy" else rfq["bid"]
        cli.place_order(
            symbol=rfq["symbol"],
            side=side,
            amount=other_side["amount"],
            price=other_side["price"],
            timestamp_millis=int(1000 * now.timestamp()),
        )


async def test_websocket(workflow: Workflow):
    client = OnyxWebsocketClient(
        on_response=workflow.on_response, on_event=workflow.on_event
    )
    await client.run()


async def one_client():
    workflow = Workflow(
        rfq=[
            # dict(symbol="brtz24", size="10"),
            # dict(symbol=dict(front="brtu24", back="brtz24"), size=50),
        ],
        products=["dub"],
        # product_risk=[ProductRisk("brt", "trad33")],
    )
    try:
        await test_websocket(workflow)
    except Exception as e:
        logger.error("%s", e)


if __name__ == "__main__":
    dotenv.load_dotenv()
    logging.basicConfig(level=logging.DEBUG)
    asyncio.get_event_loop().run_until_complete(
        asyncio.gather(*[one_client() for _ in range(1)])
    )
