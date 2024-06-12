import json
import os
from dataclasses import dataclass, field
from inspect import Traceback
from typing import Any, Callable, Self, Type

from aiohttp import ClientResponse, ClientSession


class HttpResponseError(RuntimeError):
    def __init__(self, response: ClientResponse, data: Any) -> None:
        self.response = response
        self.data = {
            "response": data,
            "request_url": response.url,
            "request_method": response.method,
            "response_status": self.status_code,
        }

    @property
    def status_code(self) -> int:
        return self.response.status

    def __str__(self) -> str:
        return json.dumps(self.data, indent=4)


@dataclass
class OnyxRestClient:
    """Onyx Rest API client"""

    api_token: str = field(default_factory=lambda: os.getenv("ONYX_API_TOKEN", ""))
    """API token for Onyx API authentication
    get your token from https://app.dev.onyxhub.co/manage-account
    """
    url: str = field(
        default_factory=lambda: os.getenv("ONYX_REST_URL", "https://api.onyxhub.co/v1")
    )
    session: ClientSession | None = None
    content_type: str = "application/json"
    default_headers: dict[str, str] = field(
        default_factory=lambda: {
            "user-agent": os.getenv("ONYX_REST_USER_AGENT", "Onyx/Python"),
        }
    )
    ResponseError: type[HttpResponseError] = field(
        default=HttpResponseError, repr=False
    )

    def get_session(self) -> ClientSession:
        if self.session is None:
            self.session = ClientSession()
        return self.session

    async def close(self) -> None:
        if self.session is not None:
            await self.session.close()
            self.session = None

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(
        self,
        exc_type: Type,
        exc: Type[BaseException],
        tb: Traceback,
    ) -> None:
        await self.close()

    async def get(self, url: str, **kwargs: Any) -> Any:
        return await self.request("GET", url, **kwargs)

    async def post(self, url: str, **kwargs: Any) -> Any:
        return await self.request("POST", url, **kwargs)

    async def delete(self, url: str, **kwargs: Any) -> Any:
        return await self.request("DELETE", url, **kwargs)

    async def request(
        self,
        method: str,
        url: str,
        *,
        headers: dict | None = None,
        callback: Callable | bool | None = None,
        **kw: Any,
    ) -> Any:
        session = self.get_session()
        _headers = self.get_default_headers()
        _headers.update(headers or ())
        response = await session.request(
            method,
            url,
            headers=_headers,
            **kw,
        )
        if callback:
            if callback is True:
                return response
            else:
                return await callback(response)
        if response.status == 200:
            data = await self.response_data(response)
        elif response.status == 204:
            data = {}
        else:
            await self.response_error(response)
        return data

    def get_default_headers(self) -> dict[str, str]:
        headers = self.default_headers.copy()
        if self.content_type:
            headers["accept"] = self.content_type
        if self.api_token:
            headers["Authorization"] = f"Bearer {self.api_token}"
        return headers

    @classmethod
    async def response_data(cls, response: ClientResponse) -> Any:
        if "text/csv" in response.headers["content-type"]:
            return await response.text()
        return await response.json()

    @classmethod
    async def response_error(cls, response: ClientResponse) -> None:
        try:
            data = await cls.response_data(response)
        except Exception:
            data = {"message": await response.text()}
        raise cls.ResponseError(response, data)
