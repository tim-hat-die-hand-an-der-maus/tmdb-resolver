import abc
import logging
from collections.abc import Generator

import httpx
from httpx import Request, Response
from pydantic import HttpUrl

import tmdb_resolver.client._url_parser as url_parser
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

    async def get_movie_by_tmdb_url(self, url: HttpUrl) -> model.Movie | None:
        try:
            movie_id = url_parser.extract_tmdb_id(url)
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
