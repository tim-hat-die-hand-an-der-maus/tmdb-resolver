from typing import Annotated

from pydantic import BaseModel, StringConstraints


class ResolveByLinkRequest(BaseModel):
    tmdbUrl: str


class CoverMetadata(BaseModel):
    url: str
    ratio: float


class Movie(BaseModel):
    id: str
    title: str
    year: int
    rating: Annotated[
        str | None,
        StringConstraints(min_length=1, pattern=r"\d{1,2}(?:\.\d)?"),
    ]
    cover: CoverMetadata | None
