import abc
import logging
from collections.abc import Generator

import httpx
from httpx import Request, Response

from tmdb_resolver import model
from tmdb_resolver.client._model import Movie, MovieResults
from tmdb_resolver.client._url_parser import UrlParser
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

    @property
    def url_parser(self) -> UrlParser:
        return UrlParser()

    @staticmethod
    def validate_response(response: httpx.Response) -> None:
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

    async def get_movie_by_id(self, tmdb_id: str | int) -> model.Movie | None:
        try:
            response = await self._client.get(f"/movie/{tmdb_id}")
        except httpx.RequestError as e:
            raise IoException from e

        self.validate_response(response)

        tmdb_movie = Movie.model_validate_json(response.content)
        return tmdb_movie.to_model()

    async def get_movie_by_imdb_id(self, imdb_id: str) -> model.Movie | None:
        try:
            response = await self._client.get(
                f"/find/{imdb_id}",
                params=dict(
                    external_source="imdb_id",
                ),
            )
        except httpx.RequestError as e:
            raise IoException from e

        self.validate_response(response)

        results = MovieResults.model_validate_json(response.text)
        if not results.movie_results:
            return None

        if len(results.movie_results) > 1:
            _logger.warning("Received more than one result for IMDb ID %s", imdb_id)

        return results.movie_results[0].to_model()

    async def close(self) -> None:
        await self._client.aclose()
