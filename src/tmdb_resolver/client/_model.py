import abc
from datetime import datetime

from pydantic import BaseModel

from tmdb_resolver import model


class TmdbResponse(BaseModel, abc.ABC):
    pass


class Genre(TmdbResponse):
    id: int
    name: str


class TmdbMovie(TmdbResponse):
    adult: bool
    genres: list[Genre]
    homepage: str
    id: int
    imdb_id: str
    original_language: str
    release_date: datetime
    title: str
    status: str
    vote_count: int
    vote_average: float
    runtime: int

    def to_model(self) -> model.Movie:
        return model.Movie(
            id=str(self.id),
            title=self.title,
            year=self.release_date.year,
            cover=None,
            rating=f"{self.vote_average:.1f}",
        )
