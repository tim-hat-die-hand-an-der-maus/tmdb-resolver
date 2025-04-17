import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException

from tmdb_resolver import model
from tmdb_resolver.client import TmdbClient
from tmdb_resolver.config import load_config

_logger = logging.getLogger(__name__)


config = load_config()
client: TmdbClient = None  # type: ignore


@asynccontextmanager
async def lifespan(_: FastAPI):
    global client
    client = TmdbClient(config.tmdb)

    yield

    await client.close()


app = FastAPI(lifespan=lifespan)


@app.post("/by_link")
async def movie_by_link(req: model.ResolveByLinkRequest) -> model.Movie:
    movie = await client.get_movie_by_tmdb_url(req.link)

    if not movie:
        raise HTTPException(
            status_code=404,
            detail=f"link couldn't be resolved to a movie: {req.link}",
        )

    return movie
