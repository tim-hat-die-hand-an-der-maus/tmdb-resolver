import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException

from tmdb_resolver import model
from tmdb_resolver.client import TmdbClient
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


@app.post("/by_link")
async def movie_by_link(req: model.ResolveByLinkRequest) -> model.Movie:
    tmdb_id = client.url_parser.extract_tmdb_id(req.link)

    if tmdb_id:
        movie = await client.get_movie_by_id(tmdb_id)
    elif imdb_id := client.url_parser.extract_imdb_id(req.link):
        movie = await client.get_movie_by_imdb_id(imdb_id)
    else:
        raise HTTPException(
            status_code=400,
            detail=f"could not extract movie ID: {req.link}",
        )

    if not movie:
        raise HTTPException(
            status_code=404,
            detail=f"link couldn't be resolved to a movie: {req.link}",
        )

    return movie
