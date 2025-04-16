from pydantic import BaseModel


class ResolveByLinkRequest(BaseModel):
    tmdbUrl: str


class CoverMetadata(BaseModel):
    url: str
    ratio: float


class Movie(BaseModel):
    id: str
    title: str
    year: int
    rating: str | None
    cover: CoverMetadata | None
