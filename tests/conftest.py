import asyncio

import dotenv
import pytest

dotenv.load_dotenv(".env")


@pytest.fixture(scope="module", autouse=True)
def event_loop():
    loop = asyncio.new_event_loop()
    try:
        yield loop
    finally:
        loop.close()
