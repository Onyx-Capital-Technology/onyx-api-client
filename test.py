from onyx_api_client.websocket import OnyxWebsocketClient
import asyncio
import dotenv
import logging


logger = logging.getLogger(__name__)


async def test_websocket():
    client = OnyxWebsocketClient(on_response=on_response)
    await client.run()


def on_response(cli: OnyxWebsocketClient, data: dict):
    if data["method"] == "auth":
        if data.get("error"):
            raise RuntimeError(data["message"])
        else:
            logger.info("authenticated - subscribe to server_info")
            cli.subscribe("server_info")


if __name__ == "__main__":
    dotenv.load_dotenv()
    logging.basicConfig(level=logging.DEBUG)
    asyncio.get_event_loop().run_until_complete(test_websocket())
