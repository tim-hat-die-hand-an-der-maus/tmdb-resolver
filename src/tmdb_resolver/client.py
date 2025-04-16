from collections.abc import Generator

import httpx
from httpx import Request, Response

from tmdb_resolver import model
from tmdb_resolver.config import TmdbConfig


class _BearerAuth(httpx.Auth):
    def __init__(self, token: str):
        self.__token = token

    def auth_flow(self, request: Request) -> Generator[Request, Response]:
        request.headers["Authorization"] = f"Bearer {self.__token}"
        yield request


class TmdbClient:
    def __init__(self, config: TmdbConfig) -> None:
        self._config = config
        self._client = httpx.AsyncClient(
            auth=_BearerAuth(config.api_token),
            base_url="https://api.themoviedb.org/3",
        )

    async def get_movie_by_url(self, url: str) -> model.Movie | None:
        return model.Movie(
            id="615665",
            title="Holidate",
            year=2020,
            rating="4.8",
            cover=None,
        )

    async def close(self) -> None:
        await self._client.aclose()
