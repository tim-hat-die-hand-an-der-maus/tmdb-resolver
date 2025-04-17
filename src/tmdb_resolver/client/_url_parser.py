import re

from pydantic import HttpUrl


def extract_tmdb_id(url: HttpUrl) -> str:
    if url.host not in ["themoviedb.org", "www.themoviedb.org"]:
        raise ValueError("Incorrect host")

    path = url.path or ""
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


_IMDB_REGEX = re.compile(r"/(tt\d+)")


def extract_imdb_id(url: HttpUrl) -> str:
    if url.host not in ["imdb.com", "www.imdb.com"]:
        raise ValueError("Incorrect host")

    path = url.path
    if not path:
        raise ValueError("Empty URL path")

    match = _IMDB_REGEX.match(path)
    if not match:
        raise ValueError(f"Could not extract movie ID from URL {url}")

    return match.group(1)
