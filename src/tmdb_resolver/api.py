import logging
from contextlib import asynccontextmanager
from typing import Literal

from fastapi import FastAPI, HTTPException, Request, status

from tmdb_resolver import model
from tmdb_resolver.client import IoException, TmdbClient
from tmdb_resolver.config import load_config
from tmdb_resolver.state import StateStorageLoader, init_state_storage_loader

_logger = logging.getLogger(__name__)


config = load_config()
client: TmdbClient = None  # type: ignore
state_storage_loader: StateStorageLoader = None  # type: ignore


@asynccontextmanager
async def lifespan(_: FastAPI):
    global client, state_storage_loader
    state_storage_loader = await init_state_storage_loader()
    client = await TmdbClient.init(config.tmdb, state_storage_loader)

    yield

    await client.close()


app = FastAPI(lifespan=lifespan)


@app.exception_handler(IoException)
async def validation_exception_handler(request: Request, exc: IoException):
    return HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail=f"Temporarily unavailable: {exc}",
    )


@app.post("/by_id/{movie_id}")
async def movie_by_id(
    movie_id: str,
    external_source: Literal["imdb"] | None = None,
) -> model.Movie:
    _logger.info(
        "Looking up movie by ID %s (external source: %s)", movie_id, external_source
    )

    match external_source:
        case "imdb":
            movie = await client.get_movie_by_imdb_id(movie_id)
        case None:
            movie = await client.get_movie_by_id(movie_id)
        case invalid:
            raise HTTPException(
                status_code=400,
                detail=f"could not extract movie ID: {invalid}",
            )

    if not movie:
        raise HTTPException(
            status_code=404,
            detail=f"ID couldn't be found: {movie_id} (external source: {external_source})",
        )

    if not movie.cover:
        _logger.info("Retrieving cover metadata for movie %s", movie.id)
        movie.cover = await client.get_cover_metadata(movie.id)

    return movie


@app.post("/by_link")
async def movie_by_link(req: model.ResolveByLinkRequest) -> model.Movie:
    _logger.info("Searching movie for link %s", req.link)
    tmdb_id = client.url_parser.extract_tmdb_id(req.link)

    if tmdb_id:
        movie = await client.get_movie_by_id(tmdb_id)
    elif imdb_id := client.url_parser.extract_imdb_id(req.link):
        movie = await client.get_movie_by_imdb_id(imdb_id)
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"could not extract movie ID: {req.link}",
        )

    if not movie:
        raise HTTPException(
            status_code=404,
            detail=f"link couldn't be resolved to a movie: {req.link}",
        )

    if not movie.cover:
        _logger.info("Retrieving cover metadata for movie %s", movie.id)
        movie.cover = await client.get_cover_metadata(movie.id)

    return movie
