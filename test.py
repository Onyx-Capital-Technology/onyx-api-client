from onyx_api_client.websocket import OnyxWebsocketClient
import asyncio
import dotenv
import logging


logger = logging.getLogger(__name__)


async def test_websocket():
    workflow = Workflow()
    client = OnyxWebsocketClient(
        on_response=workflow.on_response, on_event=workflow.on_event
    )
    await client.run()


class Workflow:
    dashboard: bool = False
    tickers: bool = False

    def on_response(self, cli: OnyxWebsocketClient, data: dict):
        if data["method"] == "auth":
            if data.get("error"):
                raise RuntimeError(data["message"])
            else:
                logger.info("authenticated - subscribe to server_info")
                cli.subscribe("server_info")

    def on_event(self, cli: OnyxWebsocketClient, data: dict):
        logger.info("received event: %s", data)
        if not self.dashboard:
            self.dashboard = True
            cli.subscribe("dashboards")
        if not self.tickers:
            self.tickers = True
            # cli.subscribe("tickers", product_groups=["crude"])
            cli.subscribe(
                "tickers", products=["brteusw1"], product_groups=["crude1", "foo"]
            )


if __name__ == "__main__":
    dotenv.load_dotenv()
    logging.basicConfig(level=logging.DEBUG)
    asyncio.get_event_loop().run_until_complete(test_websocket())
