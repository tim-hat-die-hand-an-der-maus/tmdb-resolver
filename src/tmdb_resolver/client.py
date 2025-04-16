from tmdb_resolver import model
from tmdb_resolver.config import TmdbConfig


class TmdbClient:
    def __init__(self, config: TmdbConfig) -> None:
        self._config = config

    async def get_movie_by_url(self, url: str) -> model.Movie | None:
        return None

    async def close(self) -> None:
        pass
