import abc
from typing import Annotated, Self

from pydantic import BaseModel, ConfigDict, HttpUrl, StringConstraints
from pydantic.alias_generators import to_camel


class ResolverModel(BaseModel, abc.ABC):
    model_config = ConfigDict(
        extra="forbid",
        alias_generator=to_camel,
        populate_by_name=True,
    )


class ResolveByLinkRequest(ResolverModel):
    link: HttpUrl


class CoverMetadata(ResolverModel):
    url: HttpUrl
    ratio: float


class Movie(ResolverModel):
    id: str
    title: str
    year: int
    rating: Annotated[
        str | None,
        StringConstraints(min_length=1, pattern=r"\d{1,2}(?:\.\d)?"),
    ]
    cover: CoverMetadata | None


class FullMovie(Movie):
    tmdb_url: HttpUrl
    imdb_url: HttpUrl | None

    @classmethod
    def from_movie(cls, movie: Movie, *, tmdb_url: str, imdb_id: str | None) -> Self:
        imdb_url = f"https://www.imdb.com/title/{imdb_id}" if imdb_id else None
        return cls(
            id=movie.id,
            title=movie.title,
            year=movie.year,
            rating=movie.rating,
            tmdb_url=tmdb_url,  # type: ignore
            imdb_url=imdb_url,  # type: ignore
            cover=movie.cover,
        )
