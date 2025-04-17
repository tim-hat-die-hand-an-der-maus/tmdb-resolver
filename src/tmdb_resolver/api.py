import logging
from contextlib import asynccontextmanager
from typing import Literal

from fastapi import FastAPI, HTTPException, Request, status

from tmdb_resolver import model
from tmdb_resolver.client import IoException, TmdbClient
from tmdb_resolver.config import load_config
from tmdb_resolver.model import FullMovie
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
) -> model.FullMovie:
    _logger.info(
        "Looking up movie by ID %s (external source: %s)", movie_id, external_source
    )

    match external_source:
        case "imdb":
            api_movie = await client.get_movie_by_imdb_id(movie_id)
        case None:
            api_movie = await client.get_movie_by_id(movie_id)
        case invalid:
            raise HTTPException(
                status_code=400,
                detail=f"could not extract movie ID: {invalid}",
            )

    if not api_movie:
        raise HTTPException(
            status_code=404,
            detail=f"ID couldn't be found: {movie_id} (external source: {external_source})",
        )

    imdb_id = movie_id if external_source == "imdb" else api_movie.imdb_id

    _logger.info("Retrieving cover metadata for movie %s", api_movie.id)
    cover = await client.get_cover_metadata(api_movie.id)
    _logger.debug("Resolving TMDB URL")
    tmdb_url = await client.resolve_tmdb_url(api_movie.id)

    movie = api_movie.to_model(cover)
    return FullMovie.from_movie(movie, tmdb_url=str(tmdb_url), imdb_id=imdb_id)


@app.post("/by_link")
async def movie_by_link(req: model.ResolveByLinkRequest) -> model.FullMovie:
    _logger.info("Searching movie for link %s", req.link)
    tmdb_id = client.url_parser.extract_tmdb_id(req.link)

    imdb_id: str | None = None
    if tmdb_id:
        api_movie = await client.get_movie_by_id(tmdb_id)
    elif imdb_id := client.url_parser.extract_imdb_id(req.link):
        api_movie = await client.get_movie_by_imdb_id(imdb_id)
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"could not extract movie ID: {req.link}",
        )

    if not api_movie:
        raise HTTPException(
            status_code=404,
            detail=f"link couldn't be resolved to a movie: {req.link}",
        )

    imdb_id = imdb_id or api_movie.imdb_id

    _logger.info("Retrieving cover metadata for movie %s", api_movie.id)
    cover = await client.get_cover_metadata(api_movie.id)
    _logger.debug("Resolving TMDB URL")
    tmdb_url = await client.resolve_tmdb_url(api_movie.id)

    movie = api_movie.to_model(cover)
    return FullMovie.from_movie(movie, tmdb_url=str(tmdb_url), imdb_id=imdb_id)
