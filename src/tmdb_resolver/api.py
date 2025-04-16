import logging

from fastapi import FastAPI, HTTPException

from tmdb_resolver import model
from tmdb_resolver.config import load_config

_logger = logging.getLogger(__name__)


config = load_config()
app = FastAPI()


@app.post("/")
def movie_by_link(req: model.ResolverRequest) -> model.Movie:
    movie: model.Movie | None = None

    if not movie:
        raise HTTPException(
            status_code=404,
            detail=f"link ({req.imdbUrl}) couldn't be resolved to a movie",
        )
    else:
        return movie
