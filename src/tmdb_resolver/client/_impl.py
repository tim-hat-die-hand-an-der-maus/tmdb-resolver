import abc
import logging
from collections.abc import Generator

import httpx
from httpx import Request, Response

from tmdb_resolver import model
from tmdb_resolver.client._model import TmdbMovie
from tmdb_resolver.config import TmdbConfig

_logger = logging.getLogger(__name__)


class ClientException(Exception, abc.ABC):
    pass


class IoException(ClientException):
    pass


class RequestException(ClientException):
    pass


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
            headers={"Accept": "application/json"},
        )

    @staticmethod
    def _extract_id_from_url(url: str) -> str:
        parsed = httpx.URL(url)
        if parsed.host not in ["themoviedb.org", "www.themoviedb.org"]:
            raise ValueError("Incorrect host")

        path = parsed.path
        path_segments = path.split("/")

        if len(path_segments) != 3:
            raise ValueError(f"Invalid URL path: {path}")

        if path_segments[0] != "" or path_segments[1] != "movie":
            raise ValueError(f"Non-movie URL: {url}")

        movie_id = path_segments[2].split("-")[0]
        try:
            int(movie_id)
        except ValueError:
            raise ValueError(f"Could not extract movie ID from URL {url}")

        return movie_id

    async def get_movie_by_url(self, url: str) -> model.Movie | None:
        try:
            movie_id = self._extract_id_from_url(url)
        except ValueError as e:
            _logger.info("Could not extract movie id from %s: %s", url, e)
            return None

        try:
            response = await self._client.get(f"/movie/{movie_id}")
        except httpx.RequestError as e:
            raise IoException from e

        if response.is_server_error:
            raise IoException("Received server error %d", response.status_code)

        if response.is_client_error:
            raise RequestException(
                "Received client error response %d: %s",
                response.status_code,
                response.text,
            )

        if not response.is_success:
            raise RequestException(
                "Received non-successful response %d", response.status_code
            )

        tmdb_movie = TmdbMovie.model_validate_json(response.text)
        return tmdb_movie.to_model()

    async def close(self) -> None:
        await self._client.aclose()
