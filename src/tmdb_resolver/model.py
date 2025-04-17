from typing import Annotated

from pydantic import BaseModel, HttpUrl, StringConstraints


class ResolveByLinkRequest(BaseModel):
    link: HttpUrl


class CoverMetadata(BaseModel):
    url: HttpUrl
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
