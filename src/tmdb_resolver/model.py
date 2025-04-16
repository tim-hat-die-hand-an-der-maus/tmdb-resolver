from pydantic import BaseModel


class ResolverRequest(BaseModel):
    imdbUrl: str


class CoverMetadata(BaseModel):
    url: str
    ratio: float


class Movie(BaseModel):
    id: str
    title: str
    year: int
    rating: str
    cover: CoverMetadata
    coverUrl: str
