import logging
import re

from pydantic import HttpUrl

_logger = logging.getLogger(__name__)


# noinspection PyMethodMayBeStatic
class UrlParser:
    __IMDB_REGEX = re.compile(r"/(tt\d+)")

    def extract_tmdb_id(self, url: HttpUrl) -> int | None:
        if url.host not in ["themoviedb.org", "www.themoviedb.org"]:
            _logger.info("Incorrect host: %s", url.host)
            return None

        path = url.path or ""
        path_segments = path.split("/")

        if len(path_segments) != 3:
            _logger.info("Invalid URL path: %s", path)
            return None

        if path_segments[0] != "" or path_segments[1] != "movie":
            _logger.info("Non-movie URL: %s", path)
            return None

        movie_id = path_segments[2].split("-")[0]
        try:
            return int(movie_id)
        except ValueError:
            _logger.info("Non-integer movie ID %s", url)
            return None

    def extract_imdb_id(self, url: HttpUrl) -> str | None:
        if url.host not in ["imdb.com", "www.imdb.com"]:
            _logger.info("Incorrect host: %s", url.host)
            return None

        path = url.path
        if not path:
            _logger.info("Empty path %s", url)
            return None

        match = self.__IMDB_REGEX.search(path)
        if not match:
            _logger.info("Could not extract IMDb ID from path %s", path)
            return None

        return match.group(1)
