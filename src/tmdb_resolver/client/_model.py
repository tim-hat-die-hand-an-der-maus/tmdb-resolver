import abc
from datetime import datetime

from pydantic import BaseModel

from tmdb_resolver import model


class TmdbResponse(BaseModel, abc.ABC):
    pass


class Genre(TmdbResponse):
    id: int
    name: str


class Movie(TmdbResponse):
    adult: bool
    id: int
    original_language: str
    release_date: datetime
    poster_path: str
    title: str
    vote_count: int
    vote_average: float

    def to_model(self) -> model.Movie:
        return model.Movie(
            id=str(self.id),
            title=self.title,
            year=self.release_date.year,
            cover=None,
            rating=f"{self.vote_average:.1f}",
        )


class MovieResults(TmdbResponse):
    movie_results: list[Movie]
